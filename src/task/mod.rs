//! Task Subsystem: Management, Creation, and State Machine

pub mod tcb;
pub mod queue;

pub use tcb::{TaskControlBlock, TaskId, TaskState, BlockReason, ExecutionContext, STACK_SIZE};
pub use queue::{ReadyQueue, QueueError, MAX_TASKS};

pub struct TaskManager {
    tasks: [Option<TaskControlBlock>; MAX_TASKS],
    next_id: TaskId,
}

impl TaskManager {
    pub const fn new() -> Self {
        const INIT_TASK: Option<TaskControlBlock> = None;
        Self {
            tasks: [INIT_TASK; MAX_TASKS],
            next_id: 1,
        }
    }

    /// Spawns a new task and returns its assigned TaskId
    pub fn spawn_task(&mut self, name: &str, priority: u8, burst_ticks: u64, current_tick: u64) -> Result<TaskId, &'static str> {
        let id = self.next_id;
        for slot in self.tasks.iter_mut() {
            if slot.is_none() {
                let tcb = TaskControlBlock::new(id, name, priority, burst_ticks, current_tick);
                *slot = Some(tcb);
                self.next_id += 1;
                return Ok(id);
            }
        }
        Err("Task table full: cannot spawn task")
    }

    pub fn get_task(&self, id: TaskId) -> Option<&TaskControlBlock> {
        for slot in self.tasks.iter() {
            if let Some(ref tcb) = slot {
                if tcb.id == id {
                    return Some(tcb);
                }
            }
        }
        None
    }

    pub fn get_task_mut(&mut self, id: TaskId) -> Option<&mut TaskControlBlock> {
        for slot in self.tasks.iter_mut() {
            if let Some(ref mut tcb) = slot {
                if tcb.id == id {
                    return Some(tcb);
                }
            }
        }
        None
    }

    pub fn active_count(&self) -> usize {
        self.tasks.iter().filter(|slot| {
            if let Some(tcb) = slot {
                tcb.state != TaskState::Terminated
            } else {
                false
            }
        }).count()
    }

    pub fn all_completed(&self) -> bool {
        let mut any_task = false;
        for slot in self.tasks.iter() {
            if let Some(ref tcb) = slot {
                any_task = true;
                if tcb.state != TaskState::Terminated {
                    return false;
                }
            }
        }
        any_task
    }

    pub fn tasks_slice(&self) -> &[Option<TaskControlBlock>; MAX_TASKS] {
        &self.tasks
    }
}
