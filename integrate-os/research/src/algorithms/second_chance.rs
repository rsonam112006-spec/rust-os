//! Second Chance Page Replacement Algorithm
//!
//! A practical approximation that enhances FIFO using reference bits.
//! When a page is accessed, its reference bit is set to 1.
//! During page replacement, candidates with reference bit = 1 are given a "second chance":
//! their reference bit is cleared to 0 and they are appended to the rear of the queue.
//! The first candidate encountered with reference bit = 0 is selected as the victim.

use std::collections::VecDeque;
use crate::types::{AccessResult, AlgorithmStats, Page, StepRecord};

#[derive(Debug, Clone)]
struct PageEntry {
    page: Page,
    reference_bit: bool,
}

pub fn run_second_chance(reference_string: &[Page], frame_capacity: usize) -> AlgorithmStats {
    assert!(frame_capacity > 0, "Frame capacity must be greater than 0");

    let mut frames: Vec<Option<Page>> = vec![None; frame_capacity];
    let mut queue: VecDeque<PageEntry> = VecDeque::with_capacity(frame_capacity);
    let mut history = Vec::with_capacity(reference_string.len());

    let mut hits = 0;
    let mut faults = 0;
    let mut replacements = 0;

    for (step, &page) in reference_string.iter().enumerate() {
        if frames.iter().any(|&f| f == Some(page)) {
            // Page Hit: set reference bit to 1 (give second chance)
            hits += 1;
            for entry in queue.iter_mut() {
                if entry.page == page {
                    entry.reference_bit = true;
                    break;
                }
            }

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

            if queue.len() < frame_capacity {
                // Free frame available
                for slot in frames.iter_mut() {
                    if slot.is_none() {
                        *slot = Some(page);
                        break;
                    }
                }
                queue.push_back(PageEntry {
                    page,
                    reference_bit: false,
                });
            } else {
                // Frames full: inspect head of queue
                replacements += 1;

                while let Some(mut head) = queue.pop_front() {
                    if head.reference_bit {
                        // Second chance granted: clear bit and move to back
                        head.reference_bit = false;
                        queue.push_back(head);
                    } else {
                        // Found victim with reference bit = 0
                        victim_page = Some(head.page);
                        break;
                    }
                }

                let victim = victim_page.expect("Must find a victim page");
                for slot in frames.iter_mut() {
                    if *slot == Some(victim) {
                        *slot = Some(page);
                        break;
                    }
                }

                queue.push_back(PageEntry {
                    page,
                    reference_bit: false,
                });
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
        "Second Chance",
        frame_capacity,
        reference_string.len(),
        hits,
        faults,
        replacements,
        history,
    )
}
