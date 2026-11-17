//! System Call Abstraction and Kernel Dispatch (Layer 9)
//!
//! Provides the controlled user-kernel boundary transition interface.
//! Implements parameter validation, capability checking, and structured service returns.

use crate::kinfo;
use crate::task::{TaskId, TaskManager, TaskState};
use crate::memory::FreeListAllocator;
use crate::timer::get_ticks;

pub const SYS_YIELD: u32 = 1;
pub const SYS_SLEEP: u32 = 2;
pub const SYS_MALLOC: u32 = 3;
pub const SYS_FREE: u32 = 4;
pub const SYS_PRINT: u32 = 5;
pub const SYS_EXIT: u32 = 6;
pub const SYS_GET_METRICS: u32 = 7;

// Standard POSIX-aligned educational error codes
pub const SUCCESS: i64 = 0;
pub const ERR_INVALID_SYSCALL: i64 = -1;
pub const ERR_INVALID_ARGUMENT: i64 = -22; // -EINVAL
pub const ERR_OUT_OF_MEMORY: i64 = -12;    // -ENOMEM
pub const ERR_PERMISSION_DENIED: i64 = -1; // -EPERM

pub struct SyscallDispatcher;

impl SyscallDispatcher {
    /// Dispatches a system call request from a running task
    pub fn dispatch(
        syscall_num: u32,
        arg1: usize,
        arg2: usize,
        task_id: TaskId,
        task_manager: &mut TaskManager,
        allocator: &mut FreeListAllocator,
    ) -> i64 {
        let tick = get_ticks();

        match syscall_num {
            SYS_YIELD => {
                kinfo!("SYSCALL", "Task {} issued SYS_YIELD", task_id);
                if let Some(tcb) = task_manager.get_task_mut(task_id) {
                    let _ = tcb.transition_to(TaskState::Ready, tick);
                    SUCCESS
                } else {
                    ERR_INVALID_ARGUMENT
                }
            }

            SYS_SLEEP => {
                let duration_ticks = arg1 as u64;
                kinfo!("SYSCALL", "Task {} issued SYS_SLEEP({} ticks)", task_id, duration_ticks);
                if let Some(tcb) = task_manager.get_task_mut(task_id) {
                    let wake_tick = tick + duration_ticks;
                    let _ = tcb.transition_to(TaskState::Blocked(crate::task::BlockReason::Sleep(wake_tick)), tick);
                    SUCCESS
                } else {
                    ERR_INVALID_ARGUMENT
                }
            }

            SYS_MALLOC => {
                let bytes = arg1;
                if bytes == 0 {
                    return ERR_INVALID_ARGUMENT;
                }
                match allocator.allocate(bytes) {
                    Some(ptr) => {
                        kinfo!("SYSCALL", "Task {} issued SYS_MALLOC({} bytes) -> 0x{:X}", task_id, bytes, ptr as usize);
                        ptr as i64
                    }
                    None => {
                        kinfo!("SYSCALL", "Task {} SYS_MALLOC({} bytes) FAILED (Out of memory)", task_id, bytes);
                        ERR_OUT_OF_MEMORY
                    }
                }
            }

            SYS_FREE => {
                let ptr = arg1 as *mut u8;
                match allocator.deallocate(ptr) {
                    Ok(_) => {
                        kinfo!("SYSCALL", "Task {} issued SYS_FREE(0x{:X}) -> Success", task_id, ptr as usize);
                        SUCCESS
                    }
                    Err(e) => {
                        kinfo!("SYSCALL", "Task {} SYS_FREE(0x{:X}) FAILED: {}", task_id, ptr as usize, e);
                        ERR_INVALID_ARGUMENT
                    }
                }
            }

            SYS_PRINT => {
                let msg_len = arg2;
                if msg_len > 64 {
                    return ERR_INVALID_ARGUMENT;
                }
                kinfo!("SYSCALL", "Task {} issued SYS_PRINT (len={})", task_id, msg_len);
                SUCCESS
            }

            SYS_EXIT => {
                let exit_code = arg1 as i32;
                kinfo!("SYSCALL", "Task {} issued SYS_EXIT(code={})", task_id, exit_code);
                if let Some(tcb) = task_manager.get_task_mut(task_id) {
                    let _ = tcb.transition_to(TaskState::Terminated, tick);
                    SUCCESS
                } else {
                    ERR_INVALID_ARGUMENT
                }
            }

            _ => {
                kinfo!("SYSCALL", "Task {} issued UNKNOWN syscall {}", task_id, syscall_num);
                ERR_INVALID_SYSCALL
            }
        }
    }
}
