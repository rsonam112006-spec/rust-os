//! Cooperative Kernel Mutex with Wait Queue
//!
//! If a task attempts to lock an occupied mutex, it yields CPU execution and
//! transitions into a BLOCKED state until the lock holder releases the resource.

use crate::task::{TaskId, TaskManager, TaskState, BlockReason, ReadyQueue};

pub struct KernelMutex {
    id: u32,
    is_locked: bool,
    owner_task: Option<TaskId>,
    wait_queue: ReadyQueue,
}

impl KernelMutex {
    pub const fn new(id: u32) -> Self {
        Self {
            id,
            is_locked: false,
            owner_task: None,
            wait_queue: ReadyQueue::new(),
        }
    }

    /// Attempts to acquire the mutex.
    /// If locked, transitions the calling task to BLOCKED and returns false.
    pub fn acquire(&mut self, task_id: TaskId, task_manager: &mut TaskManager, current_tick: u64) -> bool {
        if !self.is_locked {
            self.is_locked = true;
            self.owner_task = Some(task_id);
            true
        } else {
            // Block current task and place onto the mutex's wait queue
            if let Some(tcb) = task_manager.get_task_mut(task_id) {
                let _ = tcb.transition_to(TaskState::Blocked(BlockReason::Lock(self.id)), current_tick);
                let _ = self.wait_queue.enqueue(task_id);
            }
            false
        }
    }

    /// Releases the mutex, waking up the next waiting task if present
    pub fn release(&mut self, task_manager: &mut TaskManager, current_tick: u64) -> Option<TaskId> {
        if let Some(woken_task_id) = self.wait_queue.dequeue() {
            if let Some(tcb) = task_manager.get_task_mut(woken_task_id) {
                let _ = tcb.transition_to(TaskState::Ready, current_tick);
            }
            self.owner_task = Some(woken_task_id);
            Some(woken_task_id)
        } else {
            self.is_locked = false;
            self.owner_task = None;
            None
        }
    }

    pub fn is_locked(&self) -> bool {
        self.is_locked
    }

    pub fn owner(&self) -> Option<TaskId> {
        self.owner_task
    }
}
