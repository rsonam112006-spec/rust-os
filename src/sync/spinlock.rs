//! Kernel Spinlock with Contention Telemetry and Deadlock Detection
//!
//! Provides mutual exclusion using atomic test-and-set operations with acquire-release
//! memory ordering and automatic RAII guard cleanup.

use core::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use core::cell::UnsafeCell;
use core::ops::{Deref, DerefMut};

pub struct KernelSpinlock<T> {
    lock: AtomicBool,
    owner_task: AtomicU32,
    acquisition_count: AtomicU64,
    contention_count: AtomicU64,
    data: UnsafeCell<T>,
}

unsafe impl<T: Send> Sync for KernelSpinlock<T> {}
unsafe impl<T: Send> Send for KernelSpinlock<T> {}

impl<T> KernelSpinlock<T> {
    pub const fn new(data: T) -> Self {
        Self {
            lock: AtomicBool::new(false),
            owner_task: AtomicU32::new(0),
            acquisition_count: AtomicU64::new(0),
            contention_count: AtomicU64::new(0),
            data: UnsafeCell::new(data),
        }
    }

    /// Attempts to acquire the lock. If already held by the same task, returns Err to prevent deadlock.
    pub fn lock(&self, task_id: u32) -> Result<SpinlockGuard<T>, &'static str> {
        // Reentrancy / Deadlock detection check
        if self.lock.load(Ordering::Relaxed) && self.owner_task.load(Ordering::Relaxed) == task_id {
            return Err("Deadlock detected: Task reentrantly attempted to acquire already-held spinlock");
        }

        let mut spun = false;
        while self.lock.compare_exchange_weak(false, true, Ordering::Acquire, Ordering::Relaxed).is_err() {
            if !spun {
                self.contention_count.fetch_add(1, Ordering::Relaxed);
                spun = true;
            }
            core::hint::spin_loop();
        }

        self.owner_task.store(task_id, Ordering::Relaxed);
        self.acquisition_count.fetch_add(1, Ordering::Relaxed);

        Ok(SpinlockGuard {
            lock: self,
        })
    }

    pub fn is_locked(&self) -> bool {
        self.lock.load(Ordering::Relaxed)
    }

    pub fn stats(&self) -> (u64, u64) {
        (
            self.acquisition_count.load(Ordering::Relaxed),
            self.contention_count.load(Ordering::Relaxed)
        )
    }
}

pub struct SpinlockGuard<'a, T> {
    lock: &'a KernelSpinlock<T>,
}

impl<'a, T> Deref for SpinlockGuard<'a, T> {
    type Target = T;
    fn deref(&self) -> &Self::Target {
        unsafe { &*self.lock.data.get() }
    }
}

impl<'a, T> DerefMut for SpinlockGuard<'a, T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        unsafe { &mut *self.lock.data.get() }
    }
}

impl<'a, T> Drop for SpinlockGuard<'a, T> {
    fn drop(&mut self) {
        self.lock.owner_task.store(0, Ordering::Relaxed);
        self.lock.lock.store(false, Ordering::Release);
    }
}
