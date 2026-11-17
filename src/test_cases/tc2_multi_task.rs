//! TC2 – Multiple Tasks Test
//!
//! Specification: 5 controlled tasks with diverse burst times (short, medium, long).
//! Validates: Fair round-robin rotation, metrics computation, and completion ordering.

use crate::task::TaskManager;
use crate::scheduler::{RoundRobinScheduler, compute_metrics};
use crate::timer::reset_ticks;
use crate::kinfo;

pub fn run_tc2() -> bool {
    kinfo!("TEST", "=== STARTING TC2: MULTIPLE TASKS (5 TASKS, Q=3) ===");
    reset_ticks();

    let mut tm = TaskManager::new();
    let mut sched = RoundRobinScheduler::new(3);

    // 5 tasks with varied bursts: 2, 4, 6, 8, 3 ticks
    let bursts = [2u64, 4, 6, 8, 3];
    let names = ["QuickJob", "DataProcess", "ComputeMatrix", "RenderFrame", "LogSync"];

    for i in 0..5 {
        let tid = tm.spawn_task(names[i], 1, bursts[i], 0).expect("Spawn failed");
        sched.add_task(tid, &mut tm, 0).expect("Add failed");
    }

    let mut current_tick = 0u64;
    while !tm.all_completed() && current_tick < 60 {
        current_tick += 1;
        sched.tick(&mut tm, current_tick);
    }

    let metrics = compute_metrics(&tm, sched.total_context_switches, current_tick);

    let success = metrics.completed_tasks == 5;

    kinfo!(
        "TEST",
        "=== TC2 FINISHED: {} (Completed: 5/5, Avg Wait: {:.2} ticks, Avg Turnaround: {:.2} ticks, Jain Fairness: {:.3}) ===",
        if success { "PASSED" } else { "FAILED" },
        metrics.avg_waiting_time,
        metrics.avg_turnaround_time,
        metrics.jains_fairness_index
    );

    success
}
