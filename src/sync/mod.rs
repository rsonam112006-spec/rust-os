//! Synchronization Subsystem (Spinlock & Cooperative Mutex)

pub mod spinlock;
pub mod mutex;

pub use spinlock::{KernelSpinlock, SpinlockGuard};
pub use mutex::KernelMutex;
