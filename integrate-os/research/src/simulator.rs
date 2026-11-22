//! High-Level Page Replacement Simulator and Formatter

use crate::algorithms::{run_clock, run_fifo, run_lru, run_optimal, run_second_chance};
use crate::types::{AccessResult, AlgorithmStats, Page};

pub struct PageReplacementSimulator;

impl PageReplacementSimulator {
    /// Run all 5 algorithms across the given reference string with fixed frame capacity.
    pub fn run_all(reference_string: &[Page], frame_capacity: usize) -> Vec<AlgorithmStats> {
        vec![
            run_fifo(reference_string, frame_capacity),
            run_lru(reference_string, frame_capacity),
            run_optimal(reference_string, frame_capacity),
            run_second_chance(reference_string, frame_capacity),
            run_clock(reference_string, frame_capacity),
        ]
    }

    /// Format step-by-step frame execution history for an algorithm
    pub fn format_execution_table(stats: &AlgorithmStats) -> String {
        let mut out = String::new();
        out.push_str(&format!(
            "\n=== Execution Table: {} (Capacity: {} Frames) ===\n",
            stats.algorithm_name, stats.frame_capacity
        ));

        // Header
        let mut header = format!("{:<6} | {:<6} |", "Step", "Page");
        for f in 0..stats.frame_capacity {
            header.push_str(&format!(" F{:<4} |", f));
        }
        header.push_str(" Result     | Replaced\n");
        out.push_str(&header);
        out.push_str(&"-".repeat(header.len() - 1));
        out.push('\n');

        // Rows
        for rec in &stats.history {
            let mut row = format!("{:<6} | {:<6} |", rec.step, rec.page);
            for f in 0..stats.frame_capacity {
                match rec.frames_after.get(f).and_then(|&val| val) {
                    Some(p) => row.push_str(&format!(" {:<5} |", p)),
                    None => row.push_str(" [ ]   |"),
                }
            }

            match &rec.result {
                AccessResult::Hit => {
                    row.push_str(" HIT        | -");
                }
                AccessResult::Fault { replaced_page } => match replaced_page {
                    Some(victim) => row.push_str(&format!(" FAULT      | Page {}", victim)),
                    None => row.push_str(" FAULT      | (Loaded)"),
                },
            }
            row.push('\n');
            out.push_str(&row);
        }

        out.push_str(&"-".repeat(header.len() - 1));
        out.push_str(&format!(
            "\nSummary: Total: {}, Hits: {} ({:.1}%), Faults: {} ({:.1}%), Replacements: {}\n",
            stats.total_references,
            stats.page_hits,
            stats.hit_ratio,
            stats.page_faults,
            stats.fault_ratio,
            stats.page_replacements
        ));

        out
    }

    /// Format a multi-algorithm comparative table
    pub fn format_comparison_table(results: &[AlgorithmStats]) -> String {
        let mut out = String::new();
        out.push_str("\n+-----------------+--------+------------+------+--------+-------------+--------------+--------------+\n");
        out.push_str("| Algorithm       | Frames | References | Hits | Faults | Hit Ratio % | Fault Ratio% | Replacements |\n");
        out.push_str("+-----------------+--------+------------+------+--------+-------------+--------------+--------------+\n");

        for s in results {
            out.push_str(&format!(
                "| {:<15} | {:<6} | {:<10} | {:<4} | {:<6} | {:>10.2}% | {:>11.2}% | {:<12} |\n",
                s.algorithm_name,
                s.frame_capacity,
                s.total_references,
                s.page_hits,
                s.page_faults,
                s.hit_ratio,
                s.fault_ratio,
                s.page_replacements
            ));
        }
        out.push_str("+-----------------+--------+------------+------+--------+-------------+--------------+--------------+\n");

        // ASCII Fault Comparison Bar Chart
        out.push_str("\n--- Visual Page Fault Comparison (Lower is Better) ---\n");
        let max_faults = results.iter().map(|s| s.page_faults).max().unwrap_or(1);
        for s in results {
            let bar_len = if max_faults > 0 {
                (s.page_faults * 30) / max_faults
            } else {
                0
            };
            let bar = "█".repeat(bar_len);
            out.push_str(&format!("{:<15} [{:>2} faults] {}\n", s.algorithm_name, s.page_faults, bar));
        }

        out
    }
}
