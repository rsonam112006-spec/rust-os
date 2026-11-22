//! Workload Generators for Locality of Reference Experiments
//!
//! Generates memory reference strings modeling distinct computer program behaviors:
//! 1. Temporal Locality: Repeated references to a compact working set (e.g. inner loop).
//! 2. Spatial Locality: Cluster references to adjacent pages (e.g. iterating a matrix).
//! 3. Sequential Locality: Linear stream scanning through memory (e.g. file streaming).
//! 4. Random Access: Uniform non-local access (e.g. hash tables with bad distribution).
//! 5. Mixed Locality: Realistic application with loops, local variables, and heap allocations.

use crate::types::Page;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WorkloadType {
    Temporal,
    Spatial,
    Sequential,
    Random,
    Mixed,
}

impl WorkloadType {
    pub fn name(&self) -> &'static str {
        match self {
            WorkloadType::Temporal => "Temporal Locality (High Loop Reuse)",
            WorkloadType::Spatial => "Spatial Locality (Clustered Access)",
            WorkloadType::Sequential => "Sequential Locality (Linear Sweep)",
            WorkloadType::Random => "Random Access (Zero Locality)",
            WorkloadType::Mixed => "Mixed Locality (Realistic Program)",
        }
    }
}

pub struct Workload {
    pub workload_type: WorkloadType,
    pub description: &'static str,
    pub references: Vec<Page>,
}

pub struct WorkloadGenerator;

impl WorkloadGenerator {
    /// Experiment 1: Temporal Locality
    /// High-frequency reuse of a compact working set: [1, 2, 3, 1, 2, 3, 1, 2, 3...]
    pub fn temporal(len: usize) -> Workload {
        let loop_pages = [1, 2, 3];
        let mut refs = Vec::with_capacity(len);
        for i in 0..len {
            refs.push(loop_pages[i % loop_pages.len()]);
        }

        Workload {
            workload_type: WorkloadType::Temporal,
            description: "Repeated access to a working set of 3 hot pages modeling a tight compute loop.",
            references: refs,
        }
    }

    /// Experiment 2: Spatial Locality
    /// Accesses adjacent pages in small clusters: [1, 2, 3, 2, 1, 4, 5, 6, 5, 4, 7, 8, 9, 8, 7...]
    pub fn spatial(len: usize) -> Workload {
        let mut refs = Vec::with_capacity(len);
        let mut base = 1;
        while refs.len() < len {
            for &offset in &[0, 1, 2, 1, 0] {
                if refs.len() < len {
                    refs.push(base + offset);
                }
            }
            base += 3;
        }

        Workload {
            workload_type: WorkloadType::Spatial,
            description: "Clustered memory accesses stepping through contiguous address blocks.",
            references: refs,
        }
    }

    /// Experiment 3: Sequential Locality
    /// Strict ascending scan: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10...]
    pub fn sequential(len: usize) -> Workload {
        let refs: Vec<Page> = (1..=len).collect();
        Workload {
            workload_type: WorkloadType::Sequential,
            description: "Strict monotonic linear traversal modeling sequential file I/O or vector streaming.",
            references: refs,
        }
    }

    /// Experiment 4: Random Access
    /// Pseudo-random access without locality across a wide page domain [1..15]
    pub fn random(len: usize, seed: u64) -> Workload {
        let mut refs = Vec::with_capacity(len);
        // Linear congruential pseudo-random generator for determinism
        let mut state = seed;
        for _ in 0..len {
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            let page = ((state >> 33) % 15) as usize + 1;
            refs.push(page);
        }

        Workload {
            workload_type: WorkloadType::Random,
            description: "Uniform pseudo-random access across 15 pages destroying spatial & temporal locality.",
            references: refs,
        }
    }

    /// Experiment 5: Mixed Locality
    /// Standard benchmark: [1, 2, 3, 1, 4, 5, 2, 3, 1, 6, 2, 3, 7, 8, 1, 2, 3, 1, 9, 10]
    pub fn mixed() -> Workload {
        let refs = vec![
            1, 2, 3, 1, 4, 5, 2, 3, 1, 6, 2, 3, 7, 8, 1, 2, 3, 1, 9, 10,
        ];
        Workload {
            workload_type: WorkloadType::Mixed,
            description: "Realistic multi-phase program mixing loop iterations with occasional allocation spikes.",
            references: refs,
        }
    }
}
