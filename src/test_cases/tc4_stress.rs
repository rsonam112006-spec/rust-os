//! TC4 – Stress Case Test (16 Concurrent Tasks, Spinlock Contention & Memory Churn)
//!
//! Specification: Heavy workload testing task limits, atomic spinlock contention,
//! and repeated dynamic memory allocation/coalescing under pressure.

use crate::task::TaskManager;
use crate::scheduler::RoundRobinScheduler;
use crate::sync::KernelSpinlock;
use crate::memory::FreeListAllocator;
use crate::timer::reset_ticks;
use crate::kinfo;

pub fn run_tc4() -> bool {
    kinfo!("TEST", "=== STARTING TC4: STRESS CASE (16 TASKS, SPINLOCK & HEAP CHURN) ===");
    reset_ticks();

    let mut tm = TaskManager::new();
    let mut sched = RoundRobinScheduler::new(2);
    let mut allocator = FreeListAllocator::new();
    allocator.init();

    let shared_counter = KernelSpinlock::new(0u64);

    // Spawn 16 tasks
    for i in 1..=16 {
        let tid = tm.spawn_task("StressWorker", 1, 3, 0).expect("Spawn stress task failed");
        sched.add_task(tid, &mut tm, 0).expect("Queue stress task failed");
    }

    let mut tick = 0u64;
    while !tm.all_completed() && tick < 200 {
        tick += 1;
        sched.tick(&mut tm, tick);

        // Simulate concurrent task memory allocation and lock contention
        if let Some(active_id) = sched.current_task_id {
            // Memory allocation churn
            if let Some(ptr) = allocator.allocate(64) {
                // Access memory
                unsafe { *ptr = (active_id & 0xFF) as u8 };
                // Free memory
                let _ = allocator.deallocate(ptr);
            }

            // Lock contention
            if let Ok(mut guard) = shared_counter.lock(active_id) {
                *guard += 1;
            }
        }
    }

    let (acquisitions, contentions) = shared_counter.stats();
    let (allocated, free, largest) = allocator.memory_stats();
    let frag = allocator.fragmentation_ratio();

    let success = tm.all_completed() && acquisitions > 0 && frag < 0.1;

    kinfo!(
        "TEST",
        "=== TC4 FINISHED: {} (All 16 Finished, Lock Acquisitions: {}, Contentions: {}, Free Heap: {} B, Frag Ratio: {:.4}) ===",
        if success { "PASSED" } else { "FAILED" },
        acquisitions,
        contentions,
        free,
        frag
    );

    success
}
