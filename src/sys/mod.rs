//! System Interface Subsystem (Syscalls & Boundary Isolation)

pub mod syscall;

pub use syscall::{
    SyscallDispatcher,
    SYS_YIELD, SYS_SLEEP, SYS_MALLOC, SYS_FREE, SYS_PRINT, SYS_EXIT, SYS_GET_METRICS,
    SUCCESS, ERR_INVALID_SYSCALL, ERR_INVALID_ARGUMENT, ERR_OUT_OF_MEMORY, ERR_PERMISSION_DENIED,
};
