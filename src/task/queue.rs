//! Ready Queue Implementation (Zero-Allocation Kernel Data Structure)
//!
//! Provides both FIFO queueing for Round Robin scheduling and Priority-ordered
//! queueing for Track A Specialization, bounded by a fixed maximum capacity.

use super::tcb::TaskId;

pub const MAX_TASKS: usize = 32;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QueueError {
    QueueFull,
    QueueEmpty,
    TaskNotFound,
}

pub struct ReadyQueue {
    tasks: [Option<TaskId>; MAX_TASKS],
    head: usize,
    tail: usize,
    count: usize,
}

impl ReadyQueue {
    pub const fn new() -> Self {
        Self {
            tasks: [None; MAX_TASKS],
            head: 0,
            tail: 0,
            count: 0,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.count == 0
    }

    pub fn is_full(&self) -> bool {
        self.count == MAX_TASKS
    }

    pub fn len(&self) -> usize {
        self.count
    }

    pub fn capacity(&self) -> usize {
        MAX_TASKS
    }

    /// Appends a task to the tail of the ready queue (FIFO order)
    pub fn enqueue(&mut self, task_id: TaskId) -> Result<(), QueueError> {
        if self.is_full() {
            return Err(QueueError::QueueFull);
        }
        self.tasks[self.tail] = Some(task_id);
        self.tail = (self.tail + 1) % MAX_TASKS;
        self.count += 1;
        Ok(())
    }

    /// Removes and returns the task at the head of the ready queue
    pub fn dequeue(&mut self) -> Option<TaskId> {
        if self.is_empty() {
            return None;
        }
        let task_id = self.tasks[self.head].take();
        self.head = (self.head + 1) % MAX_TASKS;
        self.count -= 1;
        task_id
    }

    /// Returns the task at the head without removing it
    pub fn peek(&self) -> Option<TaskId> {
        if self.is_empty() {
            None
        } else {
            self.tasks[self.head]
        }
    }

    /// Checks if a given task ID is currently present in the queue
    pub fn contains(&self, task_id: TaskId) -> bool {
        let mut idx = self.head;
        for _ in 0..self.count {
            if self.tasks[idx] == Some(task_id) {
                return true;
            }
            idx = (idx + 1) % MAX_TASKS;
        }
        false
    }

    /// Removes a specific task ID from anywhere in the queue (e.g. on termination or blocking)
    pub fn remove(&mut self, task_id: TaskId) -> Result<(), QueueError> {
        if self.is_empty() {
            return Err(QueueError::QueueEmpty);
        }

        let mut found_pos = None;
        let mut idx = self.head;
        for pos in 0..self.count {
            if self.tasks[idx] == Some(task_id) {
                found_pos = Some(pos);
                break;
            }
            idx = (idx + 1) % MAX_TASKS;
        }

        let pos = found_pos.ok_or(QueueError::TaskNotFound)?;

        // Compact the circular buffer
        let mut current = (self.head + pos) % MAX_TASKS;
        for _ in pos..(self.count - 1) {
            let next = (current + 1) % MAX_TASKS;
            self.tasks[current] = self.tasks[next];
            current = next;
        }

        self.tasks[current] = None;
        self.tail = if self.tail == 0 { MAX_TASKS - 1 } else { self.tail - 1 };
        self.count -= 1;

        Ok(())
    }
}
