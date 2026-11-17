//! CA-6 Level 1: Unit-Level Tests (Section 15)

use micro_os::task::{ReadyQueue, TaskControlBlock, TaskState};
use micro_os::sync::KernelSpinlock;
use micro_os::memory::FreeListAllocator;

#[test]
fn test_ready_queue_fifo_order() {
    let mut q = ReadyQueue::new();
    assert!(q.is_empty());

    assert!(q.enqueue(10).is_ok());
    assert!(q.enqueue(20).is_ok());
    assert!(q.enqueue(30).is_ok());
    assert_eq!(q.len(), 3);

    assert_eq!(q.dequeue(), Some(10));
    assert_eq!(q.dequeue(), Some(20));
    assert_eq!(q.dequeue(), Some(30));
    assert_eq!(q.dequeue(), None);
    assert!(q.is_empty());
}

#[test]
fn test_task_state_machine_valid() {
    let mut tcb = TaskControlBlock::new(1, "TestTask", 1, 10, 0);
    assert_eq!(tcb.state, TaskState::Ready);

    assert!(tcb.transition_to(TaskState::Running, 1).is_ok());
    assert_eq!(tcb.state, TaskState::Running);

    assert!(tcb.transition_to(TaskState::Ready, 5).is_ok());
    assert_eq!(tcb.state, TaskState::Ready);

    assert!(tcb.transition_to(TaskState::Running, 6).is_ok());
    assert!(tcb.transition_to(TaskState::Terminated, 10).is_ok());
    assert_eq!(tcb.state, TaskState::Terminated);
    assert_eq!(tcb.turnaround_time(), Some(10));
}

#[test]
fn test_spinlock_mutual_exclusion() {
    let lock = KernelSpinlock::new(100);
    {
        let mut guard = lock.lock(1).expect("Failed to lock");
        *guard += 50;
    }
    assert!(!lock.is_locked());
    {
        let guard = lock.lock(2).expect("Failed to lock again");
        assert_eq!(*guard, 150);
    }
}

#[test]
fn test_free_list_allocation_and_coalescing() {
    let mut allocator = FreeListAllocator::new();
    allocator.init();

    let p1 = allocator.allocate(64).expect("Alloc 1 failed");
    let p2 = allocator.allocate(128).expect("Alloc 2 failed");

    assert!(allocator.deallocate(p1).is_ok());
    assert!(allocator.deallocate(p2).is_ok());

    // After coalescing adjacent blocks, fragmentation should be 0.0
    assert_eq!(allocator.fragmentation_ratio(), 0.0);
}
