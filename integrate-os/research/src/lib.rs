//! # Integrate OS — Page Replacement Research Engine
//!
//! Evaluates page replacement algorithms under locality of reference:
//! - FIFO (First-In First-Out)
//! - LRU (Least Recently Used)
//! - Optimal (Belady's MIN)
//! - Second Chance
//! - Clock (Approximation of LRU)

pub mod algorithms;
pub mod experiments;
pub mod simulator;
pub mod types;
pub mod workloads;

pub use algorithms::*;
pub use experiments::{ExperimentRun, LocalityExperimentSuite};
pub use simulator::PageReplacementSimulator;
pub use types::*;
pub use workloads::{Workload, WorkloadGenerator, WorkloadType};

#[cfg(test)]
mod tests {
    use super::*;

    const TEXTBOOK_STRING: [Page; 20] = [
        7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1,
    ];

    #[test]
    fn test_fifo_textbook() {
        let stats = run_fifo(&TEXTBOOK_STRING, 3);
        assert_eq!(stats.page_faults, 15);
        assert_eq!(stats.page_hits, 5);
        assert_eq!(stats.hit_ratio + stats.fault_ratio, 100.0);
    }

    #[test]
    fn test_lru_textbook() {
        let stats = run_lru(&TEXTBOOK_STRING, 3);
        assert_eq!(stats.page_faults, 12);
        assert_eq!(stats.page_hits, 8);
    }

    #[test]
    fn test_optimal_textbook() {
        let stats = run_optimal(&TEXTBOOK_STRING, 3);
        assert_eq!(stats.page_faults, 9);
        assert_eq!(stats.page_hits, 11);
    }

    #[test]
    fn test_belady_anomaly_fifo() {
        let anomaly_refs = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5];
        let stats_3_frames = run_fifo(&anomaly_refs, 3);
        let stats_4_frames = run_fifo(&anomaly_refs, 4);

        assert_eq!(stats_3_frames.page_faults, 9);
        assert_eq!(stats_4_frames.page_faults, 10);
        assert!(stats_4_frames.page_faults > stats_3_frames.page_faults);
    }

    #[test]
    fn test_clock_and_second_chance() {
        let clock_stats = run_clock(&TEXTBOOK_STRING, 3);
        let second_chance_stats = run_second_chance(&TEXTBOOK_STRING, 3);
        assert!(clock_stats.page_faults <= 15);
        assert!(second_chance_stats.page_faults <= 15);
    }

    #[test]
    fn test_locality_workloads_generated() {
        let temporal = WorkloadGenerator::temporal(20);
        assert_eq!(temporal.references.len(), 20);

        let spatial = WorkloadGenerator::spatial(20);
        assert_eq!(spatial.references.len(), 20);

        let sequential = WorkloadGenerator::sequential(20);
        assert_eq!(sequential.references.len(), 20);

        let random = WorkloadGenerator::random(20, 100);
        assert_eq!(random.references.len(), 20);

        let mixed = WorkloadGenerator::mixed();
        assert_eq!(mixed.references.len(), 20);
    }

    #[test]
    fn test_temporal_locality_yields_high_hits() {
        let temporal = WorkloadGenerator::temporal(20);
        let lru_stats = run_lru(&temporal.references, 3);
        // Working set size is 3 pages, frame capacity is 3 frames:
        // After 3 initial compulsory faults, EVERY subsequent access MUST be a hit (17 hits / 3 faults = 85% hit ratio!)
        assert_eq!(lru_stats.page_faults, 3);
        assert_eq!(lru_stats.page_hits, 17);
        assert_eq!(lru_stats.hit_ratio, 85.0);
    }

    #[test]
    fn test_sequential_locality_yields_zero_hits_when_exceeding_capacity() {
        let sequential = WorkloadGenerator::sequential(20);
        let lru_stats = run_lru(&sequential.references, 3);
        // In a purely monotonic stream with unique pages, NO page is ever revisited:
        // Exactly 20 faults, 0 hits (0% hit ratio!)
        assert_eq!(lru_stats.page_faults, 20);
        assert_eq!(lru_stats.page_hits, 0);
        assert_eq!(lru_stats.hit_ratio, 0.0);
    }
}
