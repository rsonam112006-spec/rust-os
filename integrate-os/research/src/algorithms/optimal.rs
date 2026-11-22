//! Optimal (Belady's MIN) Page Replacement Algorithm
//!
//! Replaces the page that will not be accessed for the longest period of time in the future.
//! Operates with omniscient future reference lookahead.
//! Serves as the theoretical performance ceiling (lowest possible page faults for fixed frames).

use crate::types::{AccessResult, AlgorithmStats, Page, StepRecord};

pub fn run_optimal(reference_string: &[Page], frame_capacity: usize) -> AlgorithmStats {
    assert!(frame_capacity > 0, "Frame capacity must be greater than 0");

    let mut frames: Vec<Option<Page>> = vec![None; frame_capacity];
    let mut history = Vec::with_capacity(reference_string.len());

    let mut hits = 0;
    let mut faults = 0;
    let mut replacements = 0;

    for (step, &page) in reference_string.iter().enumerate() {
        if frames.iter().any(|&f| f == Some(page)) {
            // Page Hit
            hits += 1;
            history.push(StepRecord {
                step: step + 1,
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
            } else {
                // Frames full: Look ahead in reference_string[step + 1..]
                replacements += 1;
                let future_refs = &reference_string[step + 1..];

                let mut farthest_distance = 0;
                let mut victim_idx = 0;

                for (idx, loaded_page_opt) in frames.iter().enumerate() {
                    let loaded_page = loaded_page_opt.expect("Frame must contain page");

                    // Find first occurrence in future
                    match future_refs.iter().position(|&p| p == loaded_page) {
                        Some(dist) => {
                            if dist > farthest_distance {
                                farthest_distance = dist;
                                victim_idx = idx;
                            }
                        }
                        None => {
                            // Loaded page is NEVER used again in the future: best possible victim
                            victim_idx = idx;
                            break;
                        }
                    }
                }

                victim_page = frames[victim_idx];
                frames[victim_idx] = Some(page);
            }

            history.push(StepRecord {
                step: step + 1,
                page,
                frames_after: frames.clone(),
                result: AccessResult::Fault { replaced_page: victim_page },
            });
        }
    }

    AlgorithmStats::new(
        "Optimal (MIN)",
        frame_capacity,
        reference_string.len(),
        hits,
        faults,
        replacements,
        history,
    )
}
