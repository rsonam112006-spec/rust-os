//! Performance Metrics Engine (Section 18 & Section 19)
//!
//! Computes quantitative scheduling metrics including Average Waiting Time,
//! Average Turnaround Time, Throughput, and Jain's Fairness Index.

use crate::task::TaskManager;

#[derive(Debug, Clone, Copy, Default)]
pub struct SchedulerMetrics {
    pub total_tasks: usize,
    pub completed_tasks: usize,
    pub total_burst_ticks: u64,
    pub total_waiting_ticks: u64,
    pub total_turnaround_ticks: u64,
    pub total_context_switches: u64,
    pub total_elapsed_ticks: u64,
    pub avg_waiting_time: f64,
    pub avg_turnaround_time: f64,
    pub throughput: f64, // tasks per 100 ticks
    pub jains_fairness_index: f64,
}

pub fn compute_metrics(task_manager: &TaskManager, total_switches: u64, elapsed_ticks: u64) -> SchedulerMetrics {
    let mut count = 0usize;
    let mut completed = 0usize;
    let mut total_burst = 0u64;
    let mut total_wait = 0u64;
    let mut total_turnaround = 0u64;
    let mut wait_times: [u64; 32] = [0; 32];

    for slot in task_manager.tasks_slice().iter() {
        if let Some(ref tcb) = slot {
            if count < 32 {
                wait_times[count] = tcb.total_waiting_ticks;
            }
            count += 1;
            total_burst += tcb.burst_ticks;
            total_wait += tcb.total_waiting_ticks;

            if let Some(tt) = tcb.turnaround_time() {
                total_turnaround += tt;
                completed += 1;
            }
        }
    }

    let avg_waiting_time = if completed > 0 {
        total_wait as f64 / completed as f64
    } else {
        0.0
    };

    let avg_turnaround_time = if completed > 0 {
        total_turnaround as f64 / completed as f64
    } else {
        0.0
    };

    let throughput = if elapsed_ticks > 0 {
        (completed as f64 / elapsed_ticks as f64) * 100.0
    } else {
        0.0
    };

    // Calculate Jain's Fairness Index over task service ratios
    // J(x) = (sum(x_i))^2 / (n * sum(x_i^2))
    let jains_fairness_index = if completed > 0 {
        let n = completed as f64;
        let mut sum = 0.0;
        let mut sum_sq = 0.0;

        for i in 0..completed {
            let x = (wait_times[i] + 1) as f64; // normalize
            sum += x;
            sum_sq += x * x;
        }

        if sum_sq > 0.0 {
            (sum * sum) / (n * sum_sq)
        } else {
            1.0
        }
    } else {
        1.0
    };

    SchedulerMetrics {
        total_tasks: count,
        completed_tasks: completed,
        total_burst_ticks: total_burst,
        total_waiting_ticks: total_wait,
        total_turnaround_ticks: total_turnaround,
        total_context_switches: total_switches,
        total_elapsed_ticks: elapsed_ticks,
        avg_waiting_time,
        avg_turnaround_time,
        throughput,
        jains_fairness_index,
    }
}
