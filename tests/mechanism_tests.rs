//! CA-6 Level 2: Mechanism Tests (Section 15)

use micro_os::task::TaskManager;
use micro_os::scheduler::RoundRobinScheduler;
use micro_os::memory::FreeListAllocator;
use micro_os::sync::KernelSpinlock;

#[test]
fn test_round_robin_preemption_mechanism() {
    let mut tm = TaskManager::new();
    let mut sched = RoundRobinScheduler::new(2);

    let t1 = tm.spawn_task("T1", 1, 4, 0).unwrap();
    let t2 = tm.spawn_task("T2", 1, 4, 0).unwrap();

    sched.add_task(t1, &mut tm, 0).unwrap();
    sched.add_task(t2, &mut tm, 0).unwrap();

    // Tick 1: T1 dispatched (remaining: 3, quantum_ticks: 1)
    sched.tick(&mut tm, 1);
    assert_eq!(sched.current_task_id, Some(t1));

    // Tick 2: T1 continues (remaining: 2, quantum_ticks: 2 -> Quantum exhausted)
    sched.tick(&mut tm, 2);
    assert_eq!(sched.current_task_id, Some(t1));

    // Tick 3: Preemption occurs! T1 preempted to READY, T2 dispatched to RUNNING
    sched.tick(&mut tm, 3);
    assert_eq!(sched.current_task_id, Some(t2));
}

#[test]
fn test_lock_contention_measurement() {
    let lock = KernelSpinlock::new(0);
    // Task 1 acquires lock
    let _guard = lock.lock(1).unwrap();

    // Stats show 1 acquisition, 0 contention
    let (acq, cont) = lock.stats();
    assert_eq!(acq, 1);
    assert_eq!(cont, 0);
}

#[test]
fn test_memory_fragmentation_metric() {
    let mut alloc = FreeListAllocator::new();
    alloc.init();

    // Allocate 3 blocks
    let p1 = alloc.allocate(100).unwrap();
    let p2 = alloc.allocate(100).unwrap();
    let p3 = alloc.allocate(100).unwrap();

    // Free the middle block only (creates a hole in memory)
    alloc.deallocate(p2).unwrap();

    // Free list now has a non-contiguous hole
    let frag = alloc.fragmentation_ratio();
    assert!(frag >= 0.0);

    // Free remaining blocks to trigger coalescing
    alloc.deallocate(p1).unwrap();
    alloc.deallocate(p3).unwrap();

    // After all freed and coalesced, fragmentation is 0
    assert_eq!(alloc.fragmentation_ratio(), 0.0);
}
