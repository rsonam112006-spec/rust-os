//! TC5 – Controlled Failure & Negative Testing
//!
//! Specification: Evaluates kernel resilience by deliberately invoking invalid operations:
//! 1. Out-of-memory (OOM) allocation request
//! 2. Double-free pointer rejection
//! 3. Reentrant spinlock deadlock detection
//! 4. Invalid task state machine transition
//! 5. Ready queue overflow boundary rejection

use crate::task::{ReadyQueue, TaskControlBlock, TaskState};
use crate::sync::KernelSpinlock;
use crate::memory::{FreeListAllocator, HEAP_BUFFER_SIZE};
use crate::kinfo;

pub fn run_tc5() -> bool {
    kinfo!("TEST", "=== STARTING TC5: CONTROLLED FAILURE & EXCEPTION HANDLING ===");

    let mut all_passed = true;

    // Failure Test 1: Out-of-Memory (Requesting 128 KiB from 64 KiB heap)
    let mut allocator = FreeListAllocator::new();
    allocator.init();
    let oom_res = allocator.allocate(HEAP_BUFFER_SIZE * 2);
    let oom_passed = oom_res.is_none();
    kinfo!("TEST", "  TC5.1 - Out of Memory Rejection: {}", if oom_passed { "PASSED" } else { "FAILED" });
    all_passed &= oom_passed;

    // Failure Test 2: Double Free Detection
    let ptr = allocator.allocate(32).expect("Alloc failed");
    let free_1 = allocator.deallocate(ptr);
    let free_2 = allocator.deallocate(ptr); // Double free
    let double_free_passed = free_1.is_ok() && free_2.is_err();
    kinfo!("TEST", "  TC5.2 - Double Free Rejection: {}", if double_free_passed { "PASSED" } else { "FAILED" });
    all_passed &= double_free_passed;

    // Failure Test 3: Deadlock / Reentrant Lock Detection
    let lock = KernelSpinlock::new(42);
    let guard1 = lock.lock(100);
    let guard2 = lock.lock(100); // Same task attempting reentrant lock
    let deadlock_passed = guard1.is_ok() && guard2.is_err();
    kinfo!("TEST", "  TC5.3 - Deadlock Detection on Reentrancy: {}", if deadlock_passed { "PASSED" } else { "FAILED" });
    all_passed &= deadlock_passed;

    // Failure Test 4: Invalid Task State Transition (Terminated -> Running)
    let mut tcb = TaskControlBlock::new(1, "TestTask", 1, 5, 0);
    let _ = tcb.transition_to(TaskState::Running, 1);
    let _ = tcb.transition_to(TaskState::Terminated, 2);
    let invalid_trans = tcb.transition_to(TaskState::Running, 3);
    let state_passed = invalid_trans.is_err();
    kinfo!("TEST", "  TC5.4 - Invalid Task State Transition Rejection: {}", if state_passed { "PASSED" } else { "FAILED" });
    all_passed &= state_passed;

    // Failure Test 5: Ready Queue Overflow
    let mut q = ReadyQueue::new();
    for i in 1..=q.capacity() {
        let _ = q.enqueue(i as u32);
    }
    let overflow_res = q.enqueue(999);
    let overflow_passed = overflow_res.is_err();
    kinfo!("TEST", "  TC5.5 - Ready Queue Overflow Guard: {}", if overflow_passed { "PASSED" } else { "FAILED" });
    all_passed &= overflow_passed;

    kinfo!(
        "TEST",
        "=== TC5 FINISHED: {} (All 5 Boundary/Failure Protections Verified) ===",
        if all_passed { "PASSED" } else { "FAILED" }
    );

    all_passed
}
