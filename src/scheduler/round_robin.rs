//! Round Robin CPU Scheduler (Layer 5 & Layer 6)
//!
//! Enforces fixed-time-quantum preemptive scheduling. Maintains the ready queue,
//! decrements task remaining burst time, and rotates tasks when the quantum expires.

use crate::task::{ReadyQueue, TaskId, TaskManager, TaskState};
use crate::{kinfo, ktrace};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ScheduleEvent {
    Dispatched { task_id: TaskId },
    Preempted { old_id: TaskId, new_id: TaskId },
    Completed { task_id: TaskId, next_id: Option<TaskId> },
    Continued { task_id: TaskId, remaining: u64 },
    Idle,
}

pub struct RoundRobinScheduler {
    pub quantum: u64,
    pub current_quantum_ticks: u64,
    pub current_task_id: Option<TaskId>,
    pub ready_queue: ReadyQueue,
    pub total_context_switches: u64,
    pub total_idle_ticks: u64,
}

impl RoundRobinScheduler {
    pub const fn new(quantum: u64) -> Self {
        Self {
            quantum,
            current_quantum_ticks: 0,
            current_task_id: None,
            ready_queue: ReadyQueue::new(),
            total_context_switches: 0,
            total_idle_ticks: 0,
        }
    }

    /// Enqueues a task into the ready queue
    pub fn add_task(&mut self, task_id: TaskId, task_manager: &mut TaskManager, current_tick: u64) -> Result<(), &'static str> {
        let tcb = task_manager.get_task_mut(task_id).ok_or("Task not found")?;
        let _ = tcb.transition_to(TaskState::Ready, current_tick);
        self.ready_queue.enqueue(task_id).map_err(|_| "Ready queue overflow")?;
        kinfo!("SCHEDULER", "Task {} ('{}') entered READY queue", task_id, tcb.name_as_str());
        Ok(())
    }

    /// Core timer-driven scheduling step invoked on every system tick.
    pub fn tick(&mut self, task_manager: &mut TaskManager, current_tick: u64) -> ScheduleEvent {
        // Case 1: A task is currently running
        if let Some(active_id) = self.current_task_id {
            let (is_completed, remaining) = {
                let tcb = match task_manager.get_task_mut(active_id) {
                    Some(t) => t,
                    None => {
                        self.current_task_id = None;
                        return ScheduleEvent::Idle;
                    }
                };

                tcb.remaining_ticks = tcb.remaining_ticks.saturating_sub(1);
                (tcb.remaining_ticks == 0, tcb.remaining_ticks)
            };

            self.current_quantum_ticks += 1;

            if is_completed {
                // Task has finished execution
                let tcb = task_manager.get_task_mut(active_id).unwrap();
                let _ = tcb.transition_to(TaskState::Terminated, current_tick);
                let turnaround = tcb.turnaround_time().unwrap_or(0);
                let wait = tcb.total_waiting_ticks;
                kinfo!(
                    "SCHEDULER",
                    "Task {} ('{}') TERMINATED. Burst: {}, Wait: {} ticks, Turnaround: {} ticks",
                    active_id,
                    tcb.name_as_str(),
                    tcb.burst_ticks,
                    wait,
                    turnaround
                );

                // Pick next runnable task
                if let Some(next_id) = self.ready_queue.dequeue() {
                    let next_tcb = task_manager.get_task_mut(next_id).unwrap();
                    let _ = next_tcb.transition_to(TaskState::Running, current_tick);
                    next_tcb.context_switches += 1;
                    self.total_context_switches += 1;
                    self.current_task_id = Some(next_id);
                    self.current_quantum_ticks = 0;
                    kinfo!("SCHEDULER", "Dispatched next Task {} ('{}') to RUNNING", next_id, next_tcb.name_as_str());
                    ScheduleEvent::Completed { task_id: active_id, next_id: Some(next_id) }
                } else {
                    self.current_task_id = None;
                    self.current_quantum_ticks = 0;
                    kinfo!("SCHEDULER", "Ready queue empty. CPU transitioning to IDLE");
                    ScheduleEvent::Completed { task_id: active_id, next_id: None }
                }
            } else if self.current_quantum_ticks >= self.quantum {
                // Quantum expired: Preemption check
                if !self.ready_queue.is_empty() {
                    // Preempt current task
                    let tcb = task_manager.get_task_mut(active_id).unwrap();
                    let _ = tcb.transition_to(TaskState::Ready, current_tick);
                    let _ = self.ready_queue.enqueue(active_id);

                    // Dequeue next task
                    let next_id = self.ready_queue.dequeue().unwrap();
                    let next_tcb = task_manager.get_task_mut(next_id).unwrap();
                    let _ = next_tcb.transition_to(TaskState::Running, current_tick);
                    next_tcb.context_switches += 1;
                    self.total_context_switches += 1;

                    self.current_task_id = Some(next_id);
                    self.current_quantum_ticks = 0;

                    kinfo!(
                        "SCHEDULER",
                        "PREEMPTION: Quantum expired (Q={}). Switched Task {} -> Task {} (remaining: {} ticks)",
                        self.quantum,
                        active_id,
                        next_id,
                        next_tcb.remaining_ticks
                    );

                    ScheduleEvent::Preempted { old_id: active_id, new_id: next_id }
                } else {
                    // No other tasks waiting; grant another quantum to current task
                    self.current_quantum_ticks = 0;
                    ktrace!("SCHEDULER", "Quantum refreshed for Task {} (single runnable task)", active_id);
                    ScheduleEvent::Continued { task_id: active_id, remaining }
                }
            } else {
                // Quantum not yet exhausted; continue execution
                ScheduleEvent::Continued { task_id: active_id, remaining }
            }
        } else {
            // Case 2: No task is currently running; attempt dispatch from ready queue
            if let Some(next_id) = self.ready_queue.dequeue() {
                let next_tcb = task_manager.get_task_mut(next_id).unwrap();
                let _ = next_tcb.transition_to(TaskState::Running, current_tick);
                next_tcb.context_switches += 1;
                self.total_context_switches += 1;
                self.current_task_id = Some(next_id);
                self.current_quantum_ticks = 0;
                kinfo!("SCHEDULER", "Dispatched initial Task {} ('{}') to RUNNING", next_id, next_tcb.name_as_str());
                ScheduleEvent::Dispatched { task_id: next_id }
            } else {
                self.total_idle_ticks += 1;
                ScheduleEvent::Idle
            }
        }
    }
}
