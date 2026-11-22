//! Least Recently Used (LRU) Page Replacement Algorithm
//!
//! Replaces the page that has not been accessed for the longest period of time.
//! Relies directly on the principle of Temporal Locality: recently accessed
//! pages are very likely to be accessed again in the near future.

use crate::types::{AccessResult, AlgorithmStats, Page, StepRecord};

pub fn run_lru(reference_string: &[Page], frame_capacity: usize) -> AlgorithmStats {
    assert!(frame_capacity > 0, "Frame capacity must be greater than 0");

    let mut frames: Vec<Option<Page>> = vec![None; frame_capacity];
    let mut last_used: Vec<usize> = vec![0; frame_capacity];
    let mut history = Vec::with_capacity(reference_string.len());

    let mut hits = 0;
    let mut faults = 0;
    let mut replacements = 0;

    for (step, &page) in reference_string.iter().enumerate() {
        let current_time = step + 1;

        if let Some(pos) = frames.iter().position(|&f| f == Some(page)) {
            // Page Hit: update recency timestamp for this frame
            hits += 1;
            last_used[pos] = current_time;

            history.push(StepRecord {
                step: current_time,
                page,
                frames_after: frames.clone(),
                result: AccessResult::Hit,
            });
        } else {
            // Page Fault
            faults += 1;
            let mut victim_page = None;

            if let Some(empty_idx) = frames.iter().position(|f| f.is_none()) {
                // Free frame available
                frames[empty_idx] = Some(page);
                last_used[empty_idx] = current_time;
            } else {
                // Frames full: find frame with minimum last_used timestamp (least recently used)
                replacements += 1;
                let lru_idx = last_used
                    .iter()
                    .enumerate()
                    .min_by_key(|&(_, &time)| time)
                    .map(|(idx, _)| idx)
                    .expect("Must have LRU index");

                victim_page = frames[lru_idx];
                frames[lru_idx] = Some(page);
                last_used[lru_idx] = current_time;
            }

            history.push(StepRecord {
                step: current_time,
                page,
                frames_after: frames.clone(),
                result: AccessResult::Fault { replaced_page: victim_page },
            });
        }
    }

    AlgorithmStats::new(
        "LRU",
        frame_capacity,
        reference_string.len(),
        hits,
        faults,
        replacements,
        history,
    )
}
