//! Clock Page Replacement Algorithm
//!
//! A high-efficiency circular buffer implementation that approximates LRU.
//! Maintains a circular array of physical frames and a rotating clock hand.
//!
//! Operation:
//! 1. On access (Hit): set reference bit for that frame to 1.
//! 2. On fault when full: the clock hand sweeps across frames.
//!    - If reference bit is 1, clear to 0 and advance hand.
//!    - If reference bit is 0, select that frame as the victim, replace with new page,
//!      set reference bit to 1, and advance hand to the next position.

use crate::types::{AccessResult, AlgorithmStats, Page, StepRecord};

pub fn run_clock(reference_string: &[Page], frame_capacity: usize) -> AlgorithmStats {
    assert!(frame_capacity > 0, "Frame capacity must be greater than 0");

    let mut frames: Vec<Option<Page>> = vec![None; frame_capacity];
    let mut ref_bits: Vec<bool> = vec![false; frame_capacity];
    let mut clock_hand: usize = 0;
    let mut history = Vec::with_capacity(reference_string.len());

    let mut hits = 0;
    let mut faults = 0;
    let mut replacements = 0;

    for (step, &page) in reference_string.iter().enumerate() {
        if let Some(pos) = frames.iter().position(|&f| f == Some(page)) {
            // Page Hit: set reference bit
            hits += 1;
            ref_bits[pos] = true;

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
                ref_bits[empty_idx] = true;
                clock_hand = (empty_idx + 1) % frame_capacity;
            } else {
                // Frames full: sweep with clock hand
                replacements += 1;

                loop {
                    if ref_bits[clock_hand] {
                        // Page was used: clear bit and advance hand
                        ref_bits[clock_hand] = false;
                        clock_hand = (clock_hand + 1) % frame_capacity;
                    } else {
                        // Found victim with bit = 0
                        victim_page = frames[clock_hand];
                        frames[clock_hand] = Some(page);
                        ref_bits[clock_hand] = true;
                        clock_hand = (clock_hand + 1) % frame_capacity;
                        break;
                    }
                }
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
        "Clock",
        frame_capacity,
        reference_string.len(),
        hits,
        faults,
        replacements,
        history,
    )
}
