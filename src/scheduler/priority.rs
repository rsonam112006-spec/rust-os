//! Priority CPU Scheduler with Dynamic Aging (Track A Specialization)
//!
//! Implements preemptive priority scheduling augmented with dynamic aging to
//! mathematically prevent starvation of low-priority workloads.

use crate::task::{TaskId, TaskManager, TaskState, MAX_TASKS};
use crate::{kinfo, ktrace};

pub struct PriorityScheduler {
    pub current_task_id: Option<TaskId>,
    pub aging_interval_ticks: u64,
    pub total_context_switches: u64,
    pub total_idle_ticks: u64,
}

impl PriorityScheduler {
    pub const fn new(aging_interval_ticks: u64) -> Self {
        Self {
            current_task_id: None,
            aging_interval_ticks,
            total_context_switches: 0,
            total_idle_ticks: 0,
        }
    }

    /// Finds the highest-priority runnable task (lowest dynamic_priority number)
    fn select_highest_priority_task(&self, task_manager: &TaskManager) -> Option<TaskId> {
        let mut best_id = None;
        let mut best_priority = u8::MAX;

        for slot in task_manager.tasks_slice().iter() {
            if let Some(ref tcb) = slot {
                if tcb.state == TaskState::Ready {
                    if tcb.dynamic_priority < best_priority {
                        best_priority = tcb.dynamic_priority;
                        best_id = Some(tcb.id);
                    }
                }
            }
        }

        best_id
    }

    /// Applies dynamic aging to all waiting READY tasks to prevent starvation
    pub fn apply_aging(&mut self, task_manager: &mut TaskManager, current_tick: u64) {
        let interval = self.aging_interval_ticks;
        for slot in task_manager.tasks_slice().iter() {
            if let Some(ref tcb) = slot {
                if tcb.state == TaskState::Ready {
                    let wait = current_tick.saturating_sub(tcb.last_ready_tick);
                    if wait > 0 && wait % interval == 0 && tcb.dynamic_priority > 0 {
                        let id = tcb.id;
                        let old_prio = tcb.dynamic_priority;
                        let new_prio = old_prio.saturating_sub(1);
                        // Mutate
                        let mutable_tcb = task_manager.get_task_mut(id).unwrap();
                        mutable_tcb.dynamic_priority = new_prio;
                        kinfo!(
                            "AGING",
                            "ANTI-STARVATION: Task {} ('{}') aged: priority {} -> {} (waited {} ticks)",
                            id,
                            mutable_tcb.name_as_str(),
                            old_prio,
                            new_prio,
                            wait
                        );
                    }
                }
            }
        }
    }

    /// Single scheduler step
    pub fn tick(&mut self, task_manager: &mut TaskManager, current_tick: u64) {
        // 1. Age waiting tasks
        self.apply_aging(task_manager, current_tick);

        // 2. Manage current running task
        if let Some(active_id) = self.current_task_id {
            let is_finished = {
                let tcb = match task_manager.get_task_mut(active_id) {
                    Some(t) => t,
                    None => {
                        self.current_task_id = None;
                        return;
                    }
                };

                tcb.remaining_ticks = tcb.remaining_ticks.saturating_sub(1);
                tcb.remaining_ticks == 0
            };

            if is_finished {
                let tcb = task_manager.get_task_mut(active_id).unwrap();
                let _ = tcb.transition_to(TaskState::Terminated, current_tick);
                kinfo!(
                    "PRIO_SCHED",
                    "Task {} ('{}') completed burst. Terminating.",
                    active_id,
                    tcb.name_as_str()
                );
                self.current_task_id = None;
            } else {
                // Check if a strictly higher priority task has arrived or aged into readiness
                if let Some(candidate_id) = self.select_highest_priority_task(task_manager) {
                    let candidate_prio = task_manager.get_task(candidate_id).unwrap().dynamic_priority;
                    let current_prio = task_manager.get_task(active_id).unwrap().dynamic_priority;

                    if candidate_prio < current_prio {
                        // Preempt active task
                        let active_tcb = task_manager.get_task_mut(active_id).unwrap();
                        let _ = active_tcb.transition_to(TaskState::Ready, current_tick);

                        let candidate_tcb = task_manager.get_task_mut(candidate_id).unwrap();
                        let _ = candidate_tcb.transition_to(TaskState::Running, current_tick);
                        candidate_tcb.context_switches += 1;
                        self.total_context_switches += 1;

                        kinfo!(
                            "PRIO_SCHED",
                            "PRIORITY PREEMPTION: Task {} (prio {}) preempted by Task {} (prio {})",
                            active_id,
                            current_prio,
                            candidate_id,
                            candidate_prio
                        );

                        self.current_task_id = Some(candidate_id);
                        return;
                    }
                }
            }
        }

        // 3. If idle, dispatch highest priority
        if self.current_task_id.is_none() {
            if let Some(next_id) = self.select_highest_priority_task(task_manager) {
                let tcb = task_manager.get_task_mut(next_id).unwrap();
                let _ = tcb.transition_to(TaskState::Running, current_tick);
                tcb.context_switches += 1;
                self.total_context_switches += 1;
                self.current_task_id = Some(next_id);
                kinfo!("PRIO_SCHED", "Dispatched Task {} (prio {}) to RUNNING", next_id, tcb.dynamic_priority);
            } else {
                self.total_idle_ticks += 1;
            }
        }
    }
}
