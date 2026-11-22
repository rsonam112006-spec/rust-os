//! First-In, First-Out (FIFO) Page Replacement Algorithm
//!
//! Replaces the page that has been in memory the longest time.
//! Operates using a strict first-in arrival queue.

use std::collections::VecDeque;
use crate::types::{AccessResult, AlgorithmStats, Page, StepRecord};

pub fn run_fifo(reference_string: &[Page], frame_capacity: usize) -> AlgorithmStats {
    assert!(frame_capacity > 0, "Frame capacity must be greater than 0");

    let mut frames: Vec<Option<Page>> = vec![None; frame_capacity];
    let mut arrival_queue: VecDeque<Page> = VecDeque::with_capacity(frame_capacity);
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

            if arrival_queue.len() < frame_capacity {
                // Free frame available: find first None
                for slot in frames.iter_mut() {
                    if slot.is_none() {
                        *slot = Some(page);
                        break;
                    }
                }
                arrival_queue.push_back(page);
            } else {
                // Frames full: evict oldest page at front of queue
                replacements += 1;
                let oldest = arrival_queue.pop_front().expect("Queue cannot be empty");
                victim_page = Some(oldest);

                // Replace oldest in frames
                for slot in frames.iter_mut() {
                    if *slot == Some(oldest) {
                        *slot = Some(page);
                        break;
                    }
                }
                arrival_queue.push_back(page);
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
        "FIFO",
        frame_capacity,
        reference_string.len(),
        hits,
        faults,
        replacements,
        history,
    )
}
