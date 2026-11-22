//! Integrate OS — Interactive Page Replacement Research Console
//! Main Research Topic: Page Replacement Under Locality of Reference

use integrate_os_research::{LocalityExperimentSuite, Page, PageReplacementSimulator};
use std::env;

fn main() {
    println!("================================================================================");
    println!("            INTEGRATE OS — PAGE REPLACEMENT RESEARCH ENGINE                     ");
    println!("        Research Focus: Page Replacement Under Locality of Reference            ");
    println!("================================================================================");

    let args: Vec<String> = env::args().collect();

    if args.iter().any(|a| a == "--experiments" || a == "-e" || a == "--all") {
        println!("\n[*] Executing Full Locality of Reference Experiment Suite (75 Benchmark Runs)...");
        let runs = LocalityExperimentSuite::run_all();

        for run in &runs {
            println!("{}", LocalityExperimentSuite::format_run(run));
        }

        println!("\n================================================================================");
        println!("             LOCALITY RESEARCH SUITE SUMMARY & INSIGHTS                         ");
        println!("================================================================================");
        println!("1. Temporal Locality: High page reuse enables LRU and Clock to achieve 85%+ hit ratios.");
        println!("2. Spatial Locality: Clustered page accesses maintain high hit rates when cluster size <= frames.");
        println!("3. Sequential Locality: Streaming through linear pages causes 100% compulsory faults (thrashing).");
        println!("4. Random Access: No working set stability; all algorithms degrade toward uniform miss rates.");
        println!("5. Mixed Locality: Approximates real OS workloads; Optimal sets upper bound, LRU/Clock track closely.");
        println!("================================================================================\n");
        return;
    }

    // Default demonstration: Textbook standard reference string
    let textbook_refs: Vec<Page> = vec![
        7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1,
    ];

    let frames = if args.len() > 1 && !args[1].starts_with('-') {
        args[1].parse::<usize>().unwrap_or(3)
    } else {
        3
    };

    println!("\n[*] Workload: Standard Reference String (20 References, {} Frames)", frames);
    println!("    Reference String: {:?}", textbook_refs);

    // 1. Run all 5 algorithms
    let results = PageReplacementSimulator::run_all(&textbook_refs, frames);

    // 2. Display detailed execution table for LRU (shows recency mechanics)
    println!("{}", PageReplacementSimulator::format_execution_table(&results[1]));

    // 3. Display summary comparison table across all 5 algorithms
    println!("\n[*] Comparative Performance Across All Implemented Algorithms:");
    println!("{}", PageReplacementSimulator::format_comparison_table(&results));

    // 4. Belady's Anomaly Demonstration
    println!("\n================================================================================");
    println!("                  SPECIAL EXPERIMENT: BELADY'S ANOMALY AUDIT                    ");
    println!("================================================================================");
    println!("Testing FIFO anomaly with trace: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]");
    let anomaly_refs = vec![1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5];

    let fifo_3 = integrate_os_research::run_fifo(&anomaly_refs, 3);
    let fifo_4 = integrate_os_research::run_fifo(&anomaly_refs, 4);

    println!("  -> Frame Capacity = 3 Frames: {} Page Faults ({:.1}% Fault Ratio)", fifo_3.page_faults, fifo_3.fault_ratio);
    println!("  -> Frame Capacity = 4 Frames: {} Page Faults ({:.1}% Fault Ratio)", fifo_4.page_faults, fifo_4.fault_ratio);

    if fifo_4.page_faults > fifo_3.page_faults {
        println!("  [!] BELADY'S ANOMALY CONFIRMED: Increasing memory frames from 3 to 4 caused");
        println!("      page faults to INCREASE from {} to {} under the FIFO policy!", fifo_3.page_faults, fifo_4.page_faults);
    }

    println!("\n[+] Integrate OS Page Replacement Engine execution completed successfully.");
    println!("    (Tip: Run with '--experiments' to view all 75 locality comparison runs!)\n");
}
