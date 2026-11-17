# CA-6: Rust Micro-OS Engineering Project
> **Operating Systems Course | Flagship Continuous Assessment – 15 Marks**  
> *Target Architecture: x86_64 Virtual Machine on Oracle VirtualBox (No QEMU)*

---

## 1. Executive Summary

This repository contains the complete implementation, verification harness, and technical documentation for **CA-6 – Rust Micro-OS**, the flagship engineering assessment of the Operating Systems course.

The project demonstrates:
> **OS Concept → Design → Rust Abstraction → Hardware Interaction → Kernel Mechanism → Observable Behaviour**

Rather than relying on QEMU, the Micro-OS specifically targets **Oracle VirtualBox**, utilizing virtualized 16550 UART serial output (`COM1` at `0x3F8`) redirected to a host trace file (`traces/virtualbox_serial.log`), an 80x25 VGA text console (`0xB8000`), an 8254 Programmable Interval Timer (100 Hz PIT), atomic spinlocks with contention/deadlock detection, a coalescing free-list allocator, and a preemptive Round Robin scheduler augmented with **Track A: Priority Scheduling with Dynamic Aging**.

---

## 2. Repository Layout

```text
micro-os/
├── README.md                          # Quick start and project overview
├── Cargo.toml                         # Rust package definition and configuration
├── .gitignore                         # Build and virtual disk exclusion rules
├── micro-os.iso                       # Bootable ISO image for Oracle VirtualBox
├── micro-os.img                       # Raw bootable disk image
├── docs/
│   ├── architecture.md                # System architecture & Mermaid flow diagrams
│   ├── design.md                      # Subsystem design & Unsafe Rust audit
│   ├── testing.md                     # Verification plan & TC1-TC6 test evidence
│   ├── virtualbox_guide.md            # Detailed VirtualBox setup & troubleshooting
│   ├── debugging_log.md               # Engineering incident & debugging log
│   └── final_report.md                # Complete 20-section final technical report
├── src/
│   ├── lib.rs                         # Crate entry point exposing all modules
│   ├── main.rs                        # Kernel main entry & Layer 10 demonstration
│   ├── drivers/                       # 16550 UART COM1 & VGA text drivers
│   ├── kernel/                        # Structured logger, banner, and halt
│   ├── task/                          # TCB, execution context, and circular ready queue
│   ├── scheduler/                     # Round Robin, Priority Aging, and metrics
│   ├── memory/                        # Bitmap frame, bump, and free-list allocators
│   ├── sync/                          # Atomic spinlock & cooperative mutex
│   ├── timer/                         # 8254 PIT timer driver (100 Hz tick)
│   ├── sys/                           # System call dispatch interface (Layer 9)
│   └── test_cases/                    # Standardized TC1 through TC6 verification
├── tests/
│   ├── unit_tests.rs                  # Level 1: Unit-level data structure tests
│   └── mechanism_tests.rs             # Level 2: OS mechanism verification tests
├── scripts/
│   ├── setup_virtualbox.ps1           # Automated VirtualBox VM setup & launch (PowerShell)
│   ├── setup_virtualbox.bat           # Automated VirtualBox VM setup & launch (Batch)
│   ├── build_bootable_iso.py          # Builds micro-os.iso and micro-os.img
│   ├── run_simulation.py              # End-to-end simulation & test runner
│   ├── parse_traces.py                # Serial log trace parser -> JSON
│   └── visualize_metrics.py           # Timeline ASCII Gantt chart & report generator
├── traces/
│   └── virtualbox_serial.log          # Serial trace logs captured from VirtualBox COM1
└── results/
    ├── metrics_summary.json           # Extracted quantitative OS metrics
    └── performance_analysis.md        # Formatted performance analysis & comparison
```

---

## 3. Quick Start Guide

### Step 1: Automated Oracle VirtualBox Launch
To create, configure, and boot the Micro-OS inside Oracle VirtualBox with COM1 serial logging:
- **PowerShell:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/setup_virtualbox.ps1
  ```
- **Windows Batch (Command Prompt):**
  ```cmd
  scripts\setup_virtualbox.bat
  ```

### Step 2: Running End-to-End Test Suite & Analysis Pipeline
To execute all 6 verification test cases, parse the trace log, and generate performance reports:
```bash
python scripts/run_simulation.py
```

### Step 3: Inspecting Performance Data
- View the ASCII Gantt execution timeline and Linux comparison:
  [results/performance_analysis.md](results/performance_analysis.md)
- View structured JSON metrics:
  [results/metrics_summary.json](results/metrics_summary.json)

---

## 4. Verification Summary (TC1 to TC6)

| Test ID | Test Case | Target Subsystem | Result |
|---|---|---|:---:|
| **TC1** | Minimum Configuration | 2 Tasks under Round Robin ($Q=2$) | **PASSED** |
| **TC2** | Multiple Tasks | 5 Tasks, Heterogeneous Bursts ($Q=3$) | **PASSED** |
| **TC3** | Boundary Case | Quantum Overhead Analysis ($Q=1$ vs $Q=50$) | **PASSED** |
| **TC4** | Stress Case | 16 Tasks, Spinlock Contention, Heap Churn | **PASSED** |
| **TC5** | Controlled Failure | OOM, Double Free, Deadlock, Invalid State | **PASSED** |
| **TC6** | Repeatability | Deterministic Dual-Trial Parity Check | **PASSED** |

---

## 5. Technical Documentation Index

- [Architecture Document & Mermaid Flow](docs/architecture.md)
- [Design Document & Unsafe Rust Audit](docs/design.md)
- [Verification Plan & Test Results](docs/testing.md)
- [Oracle VirtualBox Configuration Guide](docs/virtualbox_guide.md)
- [Debugging & Incident Resolution Log](docs/debugging_log.md)
- [Complete 20-Section Final Technical Report](docs/final_report.md)
