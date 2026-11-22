//! Core types and metrics for Page Replacement Under Locality of Reference

pub type Page = usize;

/// Outcome of a memory reference
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AccessResult {
    Hit,
    Fault { replaced_page: Option<Page> },
}

/// A snapshot of a single page reference step
#[derive(Debug, Clone)]
pub struct StepRecord {
    pub step: usize,
    pub page: Page,
    pub frames_after: Vec<Option<Page>>,
    pub result: AccessResult,
}

/// Comprehensive performance statistics for a page replacement algorithm
#[derive(Debug, Clone)]
pub struct AlgorithmStats {
    pub algorithm_name: &'static str,
    pub frame_capacity: usize,
    pub total_references: usize,
    pub page_hits: usize,
    pub page_faults: usize,
    pub page_replacements: usize,
    pub hit_ratio: f64,
    pub fault_ratio: f64,
    pub history: Vec<StepRecord>,
}

impl AlgorithmStats {
    pub fn new(
        name: &'static str,
        frames: usize,
        total: usize,
        hits: usize,
        faults: usize,
        replacements: usize,
        history: Vec<StepRecord>,
    ) -> Self {
        let hit_ratio = if total > 0 { (hits as f64 / total as f64) * 100.0 } else { 0.0 };
        let fault_ratio = if total > 0 { (faults as f64 / total as f64) * 100.0 } else { 0.0 };

        AlgorithmStats {
            algorithm_name: name,
            frame_capacity: frames,
            total_references: total,
            page_hits: hits,
            page_faults: faults,
            page_replacements: replacements,
            hit_ratio,
            fault_ratio,
            history,
        }
    }
}
