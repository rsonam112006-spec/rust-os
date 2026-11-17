//! Task Control Block (TCB) and Execution Context Representation
//!
//! Encapsulates all state, execution registers, scheduling metrics, and stack resources
//! required to represent an isolated kernel task.

pub const STACK_SIZE: usize = 4096;
pub const STACK_CANARY: u64 = 0xDEADBEEFCAFE0001;

pub type TaskId = u32;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BlockReason {
    Lock(u32),
    Sleep(u64), // Target wake-up tick
    Io,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskState {
    Ready,
    Running,
    Blocked(BlockReason),
    Terminated,
}

impl TaskState {
    pub const fn as_str(&self) -> &'static str {
        match self {
            TaskState::Ready => "READY",
            TaskState::Running => "RUNNING",
            TaskState::Blocked(_) => "BLOCKED",
            TaskState::Terminated => "TERMINATED",
        }
    }
}

/// Execution register context for low-level task switching (x86_64 ABI)
#[derive(Debug, Clone, Copy)]
#[repr(C)]
pub struct ExecutionContext {
    pub rsp: u64,
    pub rbp: u64,
    pub rip: u64,
    pub rbx: u64,
    pub r12: u64,
    pub r13: u64,
    pub r14: u64,
    pub r15: u64,
    pub rflags: u64,
}

impl ExecutionContext {
    pub const fn empty() -> Self {
        Self {
            rsp: 0,
            rbp: 0,
            rip: 0,
            rbx: 0,
            r12: 0,
            r13: 0,
            r14: 0,
            r15: 0,
            rflags: 0x202, // IF (Interrupt Flag) enabled
        }
    }
}

/// The core Task Control Block (TCB)
pub struct TaskControlBlock {
    pub id: TaskId,
    pub name: [u8; 16],
    pub name_len: usize,
    pub state: TaskState,
    pub static_priority: u8,
    pub dynamic_priority: u8,
    pub arrival_tick: u64,
    pub burst_ticks: u64,
    pub remaining_ticks: u64,
    pub start_tick: Option<u64>,
    pub completion_tick: Option<u64>,
    pub total_waiting_ticks: u64,
    pub last_ready_tick: u64,
    pub context_switches: u64,
    pub context: ExecutionContext,
    pub stack_canary_top: u64,
    pub stack: [u8; STACK_SIZE],
}

impl TaskControlBlock {
    pub fn new(id: TaskId, name_str: &str, priority: u8, burst_ticks: u64, arrival_tick: u64) -> Self {
        let mut name = [0u8; 16];
        let bytes = name_str.as_bytes();
        let len = bytes.len().min(16);
        name[..len].copy_from_slice(&bytes[..len]);

        let mut tcb = Self {
            id,
            name,
            name_len: len,
            state: TaskState::Ready,
            static_priority: priority,
            dynamic_priority: priority,
            arrival_tick,
            burst_ticks,
            remaining_ticks: burst_ticks,
            start_tick: None,
            completion_tick: None,
            total_waiting_ticks: 0,
            last_ready_tick: arrival_tick,
            context_switches: 0,
            context: ExecutionContext::empty(),
            stack_canary_top: STACK_CANARY,
            stack: [0u8; STACK_SIZE],
        };

        // Top of stack calculation (stacks grow downwards in x86_64)
        let stack_top = tcb.stack.as_ptr() as u64 + STACK_SIZE as u64;
        tcb.context.rsp = stack_top;
        tcb.context.rbp = stack_top;

        tcb
    }

    pub fn name_as_str(&self) -> &str {
        core::str::from_utf8(&self.name[..self.name_len]).unwrap_or("unknown")
    }

    /// Enforces strict OS task state transitions.
    ///
    /// Valid transitions:
    /// - Ready -> Running
    /// - Running -> Ready (preemption)
    /// - Running -> Blocked (I/O, Sleep, Lock wait)
    /// - Blocked -> Ready (resource acquired / timer wake-up)
    /// - Running -> Terminated (task finished execution)
    pub fn transition_to(&mut self, next: TaskState, current_tick: u64) -> Result<(), &'static str> {
        match (self.state, next) {
            (TaskState::Ready, TaskState::Running) => {
                if self.start_tick.is_none() {
                    self.start_tick = Some(current_tick);
                }
                // Accumulate waiting time spent in ready queue
                if current_tick >= self.last_ready_tick {
                    self.total_waiting_ticks += current_tick - self.last_ready_tick;
                }
                self.state = next;
                Ok(())
            }
            (TaskState::Running, TaskState::Ready) => {
                self.last_ready_tick = current_tick;
                self.state = next;
                Ok(())
            }
            (TaskState::Running, TaskState::Blocked(_)) => {
                self.state = next;
                Ok(())
            }
            (TaskState::Blocked(_), TaskState::Ready) => {
                self.last_ready_tick = current_tick;
                self.state = next;
                Ok(())
            }
            (TaskState::Running, TaskState::Terminated) => {
                self.completion_tick = Some(current_tick);
                self.state = next;
                Ok(())
            }
            // Explicitly invalid transitions
            (TaskState::Terminated, _) => Err("Cannot transition from TERMINATED state"),
            (TaskState::Ready, TaskState::Blocked(_)) => Err("Ready task cannot block directly without running"),
            (TaskState::Blocked(_), TaskState::Running) => Err("Blocked task must return to Ready queue before running"),
            _ => Err("Invalid task state transition"),
        }
    }

    /// Validates stack integrity using the canary value
    pub fn check_stack_canary(&self) -> bool {
        self.stack_canary_top == STACK_CANARY
    }

    /// Calculates Turnaround Time: Completion Tick - Arrival Tick
    pub fn turnaround_time(&self) -> Option<u64> {
        self.completion_tick.map(|c| c.saturating_sub(self.arrival_tick))
    }
}
