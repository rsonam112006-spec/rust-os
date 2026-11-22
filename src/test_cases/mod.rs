//! Standardized Test Suite (TC1 through TC9)
//!
//! Covers:
//! - Subsystem Verification: TC1 to TC6 (Process scheduling, memory, synchronization, exceptions)
//! - Network Verification: TC7 (ARP, IPv4, ICMP Ping, TCP/UDP sockets, HTTP 1.1)
//! - Desktop GUI Verification: TC8 (32-bit Framebuffer, 2D renderer, window compositor, traffic lights)
//! - Wi-Fi Verification: TC9 (IEEE 802.11 scan, beacon parser, WPA2 handshake, DHCP lease)

pub mod tc1_minimum;
pub mod tc2_multi_task;
pub mod tc3_boundary;
pub mod tc4_stress;
pub mod tc5_failure;
pub mod tc6_repeatability;
pub mod tc7_network;
pub mod tc8_gui;
pub mod tc9_wifi;

pub use tc1_minimum::run_tc1;
pub use tc2_multi_task::run_tc2;
pub use tc3_boundary::run_tc3;
pub use tc4_stress::run_tc4;
pub use tc5_failure::run_tc5;
pub use tc6_repeatability::run_tc6;
pub use tc7_network::run_tc7;
pub use tc8_gui::run_tc8;
pub use tc9_wifi::run_tc9;

use crate::kprintln;

pub fn execute_all_tests() -> bool {
    kprintln!("\n============================================================");
    kprintln!("         RUNNING MICRO-OS STANDARDIZED TEST SUITE (TC1-TC9) ");
    kprintln!("============================================================");

    let t1 = run_tc1();
    let t2 = run_tc2();
    let t3 = run_tc3();
    let t4 = run_tc4();
    let t5 = run_tc5();
    let t6 = run_tc6();
    let t7 = run_tc7();
    let t8 = run_tc8();
    let t9 = run_tc9();

    let all_passed = t1 && t2 && t3 && t4 && t5 && t6 && t7 && t8 && t9;

    kprintln!("\n============================================================");
    kprintln!("                    TEST SUITE SUMMARY                      ");
    kprintln!("============================================================");
    kprintln!("  TC1 - Minimum Configuration (2 Tasks, Q=2):  {}", if t1 { "PASS" } else { "FAIL" });
    kprintln!("  TC2 - Multiple Tasks (5 Tasks, Q=3):         {}", if t2 { "PASS" } else { "FAIL" });
    kprintln!("  TC3 - Boundary Case (Q=1 vs Q=50 Overhead):  {}", if t3 { "PASS" } else { "FAIL" });
    kprintln!("  TC4 - Stress Case (16 Tasks + Churn):        {}", if t4 { "PASS" } else { "FAIL" });
    kprintln!("  TC5 - Controlled Failure & Error Codes:      {}", if t5 { "PASS" } else { "FAIL" });
    kprintln!("  TC6 - Deterministic Repeatability:           {}", if t6 { "PASS" } else { "FAIL" });
    kprintln!("  TC7 - Network Stack (IPv4, ICMP, TCP, HTTP): {}", if t7 { "PASS" } else { "FAIL" });
    kprintln!("  TC8 - Desktop GUI & Window Compositor:       {}", if t8 { "PASS" } else { "FAIL" });
    kprintln!("  TC9 - Wi-Fi 802.11 Scan & WPA2 Handshake:    {}", if t9 { "PASS" } else { "FAIL" });
    kprintln!("------------------------------------------------------------");
    kprintln!("  OVERALL STATUS: {}", if all_passed { "ALL 9 TEST CASES PASSED" } else { "ONE OR MORE TESTS FAILED" });
    kprintln!("============================================================\n");

    all_passed
}
