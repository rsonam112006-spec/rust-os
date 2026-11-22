//! Automated Locality of Reference Experiment Suite
//!
//! Evaluates FIFO, LRU, Optimal, Second Chance, and Clock across:
//! - 5 Locality Workloads (Temporal, Spatial, Sequential, Random, Mixed)
//! - 3 Frame Capacities (3, 4, 5 Frames)
//! Totaling 75 experimental evaluations.

use crate::simulator::PageReplacementSimulator;
use crate::types::AlgorithmStats;
use crate::workloads::{Workload, WorkloadGenerator};

pub struct ExperimentRun {
    pub workload: Workload,
    pub frame_capacity: usize,
    pub results: Vec<AlgorithmStats>,
}

pub struct LocalityExperimentSuite;

impl LocalityExperimentSuite {
    /// Execute all 75 locality experiments
    pub fn run_all() -> Vec<ExperimentRun> {
        let workloads = vec![
            WorkloadGenerator::temporal(20),
            WorkloadGenerator::spatial(20),
            WorkloadGenerator::sequential(20),
            WorkloadGenerator::random(20, 42),
            WorkloadGenerator::mixed(),
        ];

        let frame_counts = [3, 4, 5];
        let mut runs = Vec::with_capacity(workloads.len() * frame_counts.len());

        for workload in workloads {
            for &frames in &frame_counts {
                let results = PageReplacementSimulator::run_all(&workload.references, frames);
                runs.push(ExperimentRun {
                    workload: Workload {
                        workload_type: workload.workload_type,
                        description: workload.description,
                        references: workload.references.clone(),
                    },
                    frame_capacity: frames,
                    results,
                });
            }
        }

        runs
    }

    /// Format summary of an experiment run into an ASCII comparison table
    pub fn format_run(run: &ExperimentRun) -> String {
        let mut out = String::new();
        out.push_str(&format!(
            "\n>>> Workload: {} (Capacity: {} Frames) <<<\n",
            run.workload.workload_type.name(),
            run.frame_capacity
        ));
        out.push_str(&format!("    Pattern: {:?}\n", run.workload.references));
        out.push_str(&PageReplacementSimulator::format_comparison_table(&run.results));
        out
    }
}
