//! Standardized CA-6 Test Suite (TC1 through TC6)

pub mod tc1_minimum;
pub mod tc2_multi_task;
pub mod tc3_boundary;
pub mod tc4_stress;
pub mod tc5_failure;
pub mod tc6_repeatability;

pub use tc1_minimum::run_tc1;
pub use tc2_multi_task::run_tc2;
pub use tc3_boundary::run_tc3;
pub use tc4_stress::run_tc4;
pub use tc5_failure::run_tc5;
pub use tc6_repeatability::run_tc6;

use crate::kprintln;

pub fn execute_all_tests() -> bool {
    kprintln!("\n============================================================");
    kprintln!("         RUNNING CA-6 STANDARDIZED TEST SUITE (TC1-TC6)     ");
    kprintln!("============================================================");

    let t1 = run_tc1();
    let t2 = run_tc2();
    let t3 = run_tc3();
    let t4 = run_tc4();
    let t5 = run_tc5();
    let t6 = run_tc6();

    let all_passed = t1 && t2 && t3 && t4 && t5 && t6;

    kprintln!("\n============================================================");
    kprintln!("                    TEST SUITE SUMMARY                      ");
    kprintln!("============================================================");
    kprintln!("  TC1 - Minimum Configuration (2 Tasks, Q=2):  {}", if t1 { "PASS" } else { "FAIL" });
    kprintln!("  TC2 - Multiple Tasks (5 Tasks, Q=3):         {}", if t2 { "PASS" } else { "FAIL" });
    kprintln!("  TC3 - Boundary Case (Q=1 vs Q=50 Overhead):  {}", if t3 { "PASS" } else { "FAIL" });
    kprintln!("  TC4 - Stress Case (16 Tasks + Churn):        {}", if t4 { "PASS" } else { "FAIL" });
    kprintln!("  TC5 - Controlled Failure & Error Codes:      {}", if t5 { "PASS" } else { "FAIL" });
    kprintln!("  TC6 - Deterministic Repeatability:           {}", if t6 { "PASS" } else { "FAIL" });
    kprintln!("------------------------------------------------------------");
    kprintln!("  OVERALL STATUS: {}", if all_passed { "ALL 6 TEST CASES PASSED" } else { "ONE OR MORE TESTS FAILED" });
    kprintln!("============================================================\n");

    all_passed
}
