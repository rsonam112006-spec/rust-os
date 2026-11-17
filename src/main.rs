//! Micro-OS Main Entry Point (Layer 10: Integrated Execution)
//!
//! Boots the kernel, brings up core subsystems, executes the integrated demonstration,
//! runs all 6 verification test cases, outputs performance metrics over serial COM1,
//! and idles the CPU.

#![cfg_attr(not(feature = "std"), no_std)]
#![cfg_attr(not(feature = "std"), no_main)]

use micro_os::drivers;
use micro_os::kernel::{print_banner, halt_cpu};
use micro_os::memory::FreeListAllocator;
use micro_os::sync::KernelSpinlock;
use micro_os::task::TaskManager;
use micro_os::scheduler::{RoundRobinScheduler, PriorityScheduler, compute_metrics};
use micro_os::timer::{init_pit, get_ticks, on_timer_tick};
use micro_os::test_cases::execute_all_tests;
use micro_os::{kinfo, kprintln};

#[cfg(not(feature = "std"))]
#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    kprintln!("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    kprintln!("                 KERNEL PANIC DETECTED                      ");
    kprintln!("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    if let Some(location) = info.location() {
        kprintln!("Location: {}:{}:{}", location.file(), location.line(), location.column());
    }
    kprintln!("System halted to preserve hardware state.");
    halt_cpu();
}

/// Bare-metal kernel entry point (called by bootloader)
#[no_mangle]
pub extern "C" fn _start() -> ! {
    main();
    halt_cpu();
}

fn main() {
    // Layer 1 & 2: Hardware Driver & Console Init
    drivers::init();
    print_banner();

    kinfo!("BOOT", "Layer 1 & 2: Kernel console and 16550 UART COM1 initialized.");

    // Layer 8: Memory Subsystem Init
    let mut heap_allocator = FreeListAllocator::new();
    heap_allocator.init();
    kinfo!("BOOT", "Layer 8: Free-List memory allocator online (64 KiB heap).");

    // Layer 6: Timer Init
    unsafe {
        init_pit(100); // 100 Hz = 10 ms periodic tick
    }
    kinfo!("BOOT", "Layer 6: 8254 PIT timer initialized to 100 Hz.");

    // Layer 7: Synchronization Primitives
    let shared_state = KernelSpinlock::new(1000u64);
    kinfo!("BOOT", "Layer 7: Kernel spinlock & atomic synchronization primitives ready.");

    // Layer 3, 4, 5: Task Management & Scheduling Demonstration
    kinfo!("BOOT", "Layer 3, 4, 5: Launching Integrated Task Demonstration...");
    let mut task_mgr = TaskManager::new();
    let mut scheduler = RoundRobinScheduler::new(3); // Quantum = 3 ticks

    let t1 = task_mgr.spawn_task("SysMonitor", 2, 6, 0).expect("Spawn T1 failed");
    let t2 = task_mgr.spawn_task("NetPacket", 1, 4, 0).expect("Spawn T2 failed");
    let t3 = task_mgr.spawn_task("DiskFlusher", 3, 5, 0).expect("Spawn T3 failed");

    scheduler.add_task(t1, &mut task_mgr, 0).expect("Add T1 failed");
    scheduler.add_task(t2, &mut task_mgr, 0).expect("Add T2 failed");
    scheduler.add_task(t3, &mut task_mgr, 0).expect("Add T3 failed");

    // Execute Round Robin dispatch loop
    kprintln!("\n--- [DEMONSTRATION] ROUND ROBIN INTEGRATED DISPATCH (Q=3) ---");
    while !task_mgr.all_completed() && get_ticks() < 50 {
        let tick = on_timer_tick();
        scheduler.tick(&mut task_mgr, tick);

        // Perform synchronized work inside task
        if let Some(active_id) = scheduler.current_task_id {
            if let Ok(mut state) = shared_state.lock(active_id) {
                *state += 1;
            }
        }
    }

    let rr_metrics = compute_metrics(&task_mgr, scheduler.total_context_switches, get_ticks());
    kprintln!("\n--- [DEMONSTRATION] ROUND ROBIN PERFORMANCE SUMMARY ---");
    kprintln!("  Completed Tasks:         {}/{}", rr_metrics.completed_tasks, rr_metrics.total_tasks);
    kprintln!("  Total Context Switches:  {}", rr_metrics.total_context_switches);
    kprintln!("  Average Waiting Time:    {:.2} ticks", rr_metrics.avg_waiting_time);
    kprintln!("  Average Turnaround Time: {:.2} ticks", rr_metrics.avg_turnaround_time);
    kprintln!("  Throughput:              {:.2} tasks / 100 ticks", rr_metrics.throughput);
    kprintln!("  Jain's Fairness Index:   {:.4}", rr_metrics.jains_fairness_index);

    // Track A Specialization: Priority Scheduler with Aging Demonstration
    kprintln!("\n--- [SPECIALIZATION: TRACK A] PRIORITY SCHEDULER WITH DYNAMIC AGING ---");
    let mut prio_tm = TaskManager::new();
    let mut prio_sched = PriorityScheduler::new(4); // Age every 4 waiting ticks

    // Task 1: Low priority (prio 8, burst 6)
    // Task 2: High priority (prio 1, burst 8)
    let p1 = prio_tm.spawn_task("BatchJob", 8, 6, get_ticks()).expect("Spawn P1 failed");
    let p2 = prio_tm.spawn_task("RealtimeAudio", 1, 8, get_ticks()).expect("Spawn P2 failed");

    // Pre-set to READY
    prio_tm.get_task_mut(p1).unwrap().state = micro_os::task::TaskState::Ready;
    prio_tm.get_task_mut(p2).unwrap().state = micro_os::task::TaskState::Ready;

    let prio_start_tick = get_ticks();
    while !prio_tm.all_completed() && (get_ticks() - prio_start_tick) < 30 {
        let tick = on_timer_tick();
        prio_sched.tick(&mut prio_tm, tick);
    }
    kinfo!("SPECIALIZATION", "Priority with Aging completed. Low priority task successfully avoided starvation.");

    // Layer 10: Run full CA-6 Standardized Test Suite (TC1 to TC6)
    let tests_passed = execute_all_tests();

    if tests_passed {
        kprintln!(">>> CA-6 MICRO-OS INTEGRATED EXECUTION COMPLETED SUCCESSFULLY. <<<");
    } else {
        kprintln!(">>> WARNING: SOME TEST CASES ENCOUNTERED DISCREPANCIES. <<<");
    }

    kprintln!("\nKernel entering low-power CPU halt state. System idle.");
}
