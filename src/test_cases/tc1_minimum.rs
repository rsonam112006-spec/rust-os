//! TC1 – Minimum Configuration Test
//!
//! Specification: Exactly two tasks executing under Round Robin scheduling (Q=2).
//! Validates: Task creation, ready queue insertion, quantum expiration preemption, and termination.

use crate::task::TaskManager;
use crate::scheduler::{RoundRobinScheduler, ScheduleEvent};
use crate::timer::reset_ticks;
use crate::kinfo;

pub fn run_tc1() -> bool {
    kinfo!("TEST", "=== STARTING TC1: MINIMUM CONFIGURATION (2 TASKS, Q=2) ===");
    reset_ticks();

    let mut tm = TaskManager::new();
    let mut sched = RoundRobinScheduler::new(2);

    // Spawn 2 tasks
    let t1 = tm.spawn_task("Worker-Alpha", 1, 4, 0).expect("Spawn T1 failed");
    let t2 = tm.spawn_task("Worker-Beta", 1, 4, 0).expect("Spawn T2 failed");

    sched.add_task(t1, &mut tm, 0).expect("Add T1 failed");
    sched.add_task(t2, &mut tm, 0).expect("Add T2 failed");

    let mut current_tick = 0u64;
    let mut preemption_observed = false;

    while !tm.all_completed() && current_tick < 20 {
        current_tick += 1;
        let event = sched.tick(&mut tm, current_tick);

        if let ScheduleEvent::Preempted { .. } = event {
            preemption_observed = true;
        }
    }

    let t1_tcb = tm.get_task(t1).unwrap();
    let t2_tcb = tm.get_task(t2).unwrap();

    let success = t1_tcb.turnaround_time().is_some() 
        && t2_tcb.turnaround_time().is_some() 
        && preemption_observed;

    kinfo!(
        "TEST",
        "=== TC1 FINISHED: {} (T1 Turnaround: {:?}, T2 Turnaround: {:?}, Preemption: {}) ===",
        if success { "PASSED" } else { "FAILED" },
        t1_tcb.turnaround_time(),
        t2_tcb.turnaround_time(),
        preemption_observed
    );

    success
}
