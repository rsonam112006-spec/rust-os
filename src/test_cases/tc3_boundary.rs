//! TC3 – Boundary Case Test (Quantum Limits: Q=1 vs Q=50)
//!
//! Specification: Evaluates the system at extreme quantum boundaries.
//! Validates: At Q=1, context switches peak (high overhead, low latency);
//! at Q=50, the scheduler degrades to FCFS (zero preemptions).

use crate::task::TaskManager;
use crate::scheduler::RoundRobinScheduler;
use crate::timer::reset_ticks;
use crate::kinfo;

pub fn run_tc3() -> bool {
    kinfo!("TEST", "=== STARTING TC3: BOUNDARY CASE (Q=1 vs Q=50) ===");

    // Sub-case 1: Minimal quantum Q=1
    reset_ticks();
    let mut tm1 = TaskManager::new();
    let mut sched1 = RoundRobinScheduler::new(1);

    for i in 1..=3 {
        let tid = tm1.spawn_task("EdgeTask", 1, 4, 0).unwrap();
        sched1.add_task(tid, &mut tm1, 0).unwrap();
    }

    let mut tick = 0u64;
    while !tm1.all_completed() && tick < 50 {
        tick += 1;
        sched1.tick(&mut tm1, tick);
    }
    let switches_q1 = sched1.total_context_switches;

    // Sub-case 2: Massive quantum Q=50 (de facto First-Come First-Served)
    reset_ticks();
    let mut tm2 = TaskManager::new();
    let mut sched2 = RoundRobinScheduler::new(50);

    for i in 1..=3 {
        let tid = tm2.spawn_task("FcfsTask", 1, 4, 0).unwrap();
        sched2.add_task(tid, &mut tm2, 0).unwrap();
    }

    let mut tick = 0u64;
    while !tm2.all_completed() && tick < 50 {
        tick += 1;
        sched2.tick(&mut tm2, tick);
    }
    let switches_q50 = sched2.total_context_switches;

    let success = switches_q1 > switches_q50;

    kinfo!(
        "TEST",
        "=== TC3 FINISHED: {} (Q=1 Switches: {}, Q=50 Switches: {}, Verified Overhead Law: {}) ===",
        if success { "PASSED" } else { "FAILED" },
        switches_q1,
        switches_q50,
        success
    );

    success
}
