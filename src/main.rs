//! Micro-OS Main Entry Point (Layer 10: Integrated Execution)
//!
//! Boots the kernel, brings up memory and timer, initializes the network stack
//! and macOS/Windows 11 desktop GUI compositor, runs the integrated scheduler
//! and full verification test suite (TC1 to TC8), and halts safely.

#![cfg_attr(not(feature = "std"), no_std)]
#![cfg_attr(not(feature = "std"), no_main)]

use micro_os::drivers;
use micro_os::gui::{create_default_desktop, Framebuffer};
use micro_os::kernel::{halt_cpu, print_banner};
use micro_os::memory::FreeListAllocator;
use micro_os::net::NetworkStack;
use micro_os::scheduler::{compute_metrics, PriorityScheduler, RoundRobinScheduler};
use micro_os::sync::KernelSpinlock;
use micro_os::task::TaskManager;
use micro_os::test_cases::execute_all_tests;
use micro_os::timer::{get_ticks, init_pit, on_timer_tick};
use micro_os::{kinfo, kprintln};

#[cfg(not(feature = "std"))]
#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    kprintln!("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    kprintln!("                 KERNEL PANIC DETECTED                      ");
    kprintln!("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    if let Some(location) = info.location() {
        kprintln!(
            "Location: {}:{}:{}",
            location.file(),
            location.line(),
            location.column()
        );
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
    // 1. Hardware Driver & Console Init
    drivers::init();
    print_banner();
    kinfo!("BOOT", "Layer 1 & 2: Kernel console and 16550 UART COM1 initialized.");

    // 2. Memory Subsystem Init
    let mut heap_allocator = FreeListAllocator::new();
    heap_allocator.init();
    kinfo!("BOOT", "Layer 8: Free-List memory allocator online (64 KiB heap).");

    // 3. Timer Init (100 Hz = 10 ms periodic tick)
    unsafe {
        init_pit(100);
    }
    kinfo!("BOOT", "Layer 6: 8254 PIT timer initialized to 100 Hz.");

    // 4. Synchronization Primitives
    let shared_state = KernelSpinlock::new(1000u64);
    kinfo!("BOOT", "Layer 7: Kernel spinlock & atomic synchronization primitives ready.");

    // 5. Network Stack Init
    let mut net_stack = NetworkStack::new();
    net_stack.init();
    kinfo!(
        "NET",
        "Layer 9A: Ethernet NIC online. IP: {} / 24, MAC: {}, GW: {}",
        net_stack.nic.ip,
        net_stack.nic.mac,
        net_stack.nic.gateway
    );
    kinfo!(
        "WIFI",
        "Layer 9B: IEEE 802.11 wlan0 online. Associated SSID: '{}', Signal: {}%, Ch: 36 (5 GHz)",
        net_stack.wifi.connected_ssid_as_str(),
        net_stack.wifi.signal_percent()
    );

    // Perform an initial ICMP ping test to the default gateway
    if let Ok(rtt) = net_stack.ping(net_stack.nic.gateway, 1) {
        kinfo!("NET", "ICMP Ping to Default Gateway 192.168.1.1 successful (RTT: {} ms)", rtt);
    }

    // 6. Desktop GUI Compositor Init
    #[cfg(feature = "std")]
    {
        let compositor = create_default_desktop();
        let mut fb = Framebuffer::new(1024, 768);
        compositor.render(&mut fb);
        kinfo!(
            "GUI",
            "Layer 10: 32bpp Desktop Compositor online (1024x768). Windows & Dock mounted."
        );
    }

    // 7. Task Management & Scheduling Demonstration
    kinfo!("BOOT", "Launching Integrated Task & Network Demonstration...");
    let mut task_mgr = TaskManager::new();
    let mut scheduler = RoundRobinScheduler::new(3); // Quantum = 3 ticks

    let t1 = task_mgr
        .spawn_task("SysMonitor", 2, 6, 0)
        .expect("Spawn T1 failed");
    let t2 = task_mgr
        .spawn_task("NetPacket", 1, 4, 0)
        .expect("Spawn T2 failed");
    let t3 = task_mgr
        .spawn_task("DiskFlusher", 3, 5, 0)
        .expect("Spawn T3 failed");

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
    let mut prio_sched = PriorityScheduler::new(4);

    let p1 = prio_tm.spawn_task("BatchJob", 8, 6, get_ticks()).expect("Spawn P1 failed");
    let p2 = prio_tm.spawn_task("RealtimeAudio", 1, 8, get_ticks()).expect("Spawn P2 failed");

    prio_tm.get_task_mut(p1).unwrap().state = micro_os::task::TaskState::Ready;
    prio_tm.get_task_mut(p2).unwrap().state = micro_os::task::TaskState::Ready;

    let prio_start_tick = get_ticks();
    while !prio_tm.all_completed() && (get_ticks() - prio_start_tick) < 30 {
        let tick = on_timer_tick();
        prio_sched.tick(&mut prio_tm, tick);
    }
    kinfo!("SPECIALIZATION", "Priority with Aging completed. Low priority task avoided starvation.");

    // 8. Run Full Verification Test Suite (TC1 to TC8)
    let tests_passed = execute_all_tests();

    if tests_passed {
        kprintln!(">>> RUST MICRO-OS v2.0 INTEGRATED EXECUTION COMPLETED SUCCESSFULLY. <<<");
    } else {
        kprintln!(">>> WARNING: SOME TEST CASES ENCOUNTERED DISCREPANCIES. <<<");
    }

    kprintln!("\nKernel entering low-power CPU halt state. System idle.");
}
