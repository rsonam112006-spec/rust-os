//! # Rust Micro-OS
//! 
//! An educational Micro-OS designed to make fundamental Operating System mechanisms
//! visible, measurable, and verifiable on x86_64 virtualization platforms such as Oracle VirtualBox.
//!
//! ## Subsystems
//! - **Drivers**: 16550 UART serial driver (`COM1`, port `0x3F8`) and 80x25 VGA text buffer (`0xB8000`).
//! - **Kernel**: Logging framework, diagnostic telemetry, panic handling, and kernel lifecycle.
//! - **Task**: Task Control Block (TCB), execution context, and priority/FIFO ready queue.
//! - **Scheduler**: Preemptive Round Robin, Priority Scheduling with dynamic aging, and metrics engine.
//! - **Timer**: 8254 Programmable Interval Timer (PIT) frequency abstraction and tick dispatcher.
//! - **Sync**: Atomic spinlocks and cooperative mutexes with contention tracking.
//! - **Memory**: Bump allocator and Free-List allocator with coalescing and fragmentation metrics.
//! - **Sys**: Minimal system call dispatching interface (`yield`, `sleep`, `malloc`, `free`, `print`, `exit`).
//! - **Test Cases**: Standardized verification suite (TC1 through TC6).

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(feature = "std")]
extern crate std;

pub mod drivers;
pub mod kernel;
pub mod task;
pub mod scheduler;
pub mod sync;
pub mod memory;
pub mod timer;
pub mod sys;
pub mod test_cases;
