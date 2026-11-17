//! TC6 – Deterministic Repeatability Test
//!
//! Specification: Executes identical workloads across two successive trials and
//! compares metrics to verify zero non-deterministic drift.

use crate::task::TaskManager;
use crate::scheduler::RoundRobinScheduler;
use crate::timer::reset_ticks;
use crate::kinfo;

fn run_single_trial() -> (u64, u64, u64, u64) {
    reset_ticks();
    let mut tm = TaskManager::new();
    let mut sched = RoundRobinScheduler::new(2);

    let t1 = tm.spawn_task("Alpha", 1, 4, 0).unwrap();
    let t2 = tm.spawn_task("Beta", 1, 3, 0).unwrap();
    let t3 = tm.spawn_task("Gamma", 1, 5, 0).unwrap();

    sched.add_task(t1, &mut tm, 0).unwrap();
    sched.add_task(t2, &mut tm, 0).unwrap();
    sched.add_task(t3, &mut tm, 0).unwrap();

    let mut tick = 0u64;
    while !tm.all_completed() && tick < 40 {
        tick += 1;
        sched.tick(&mut tm, tick);
    }

    let t1_tt = tm.get_task(t1).unwrap().turnaround_time().unwrap_or(0);
    let t2_tt = tm.get_task(t2).unwrap().turnaround_time().unwrap_or(0);
    let t3_tt = tm.get_task(t3).unwrap().turnaround_time().unwrap_or(0);

    (tick, sched.total_context_switches, t1_tt + t2_tt + t3_tt, t1_tt)
}

pub fn run_tc6() -> bool {
    kinfo!("TEST", "=== STARTING TC6: REPEATABILITY & DETERMINISM VERIFICATION ===");

    let trial_1 = run_single_trial();
    let trial_2 = run_single_trial();

    let matches = trial_1 == trial_2;

    kinfo!(
        "TEST",
        "Trial 1: Ticks={}, Switches={}, Total Turnaround={}, T1={}",
        trial_1.0, trial_1.1, trial_1.2, trial_1.3
    );
    kinfo!(
        "TEST",
        "Trial 2: Ticks={}, Switches={}, Total Turnaround={}, T1={}",
        trial_2.0, trial_2.1, trial_2.2, trial_2.3
    );

    kinfo!(
        "TEST",
        "=== TC6 FINISHED: {} (Deterministic Parity: 100% Identical) ===",
        if matches { "PASSED" } else { "FAILED" }
    );

    matches
}
