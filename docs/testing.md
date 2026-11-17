# CA-6 Micro-OS Verification and Test Plan

## 1. Multi-Level Testing Strategy (Section 15)

The Micro-OS undergoes three progressive tiers of validation:

```text
Level 1: Unit-Level Tests (Data Structures & Memory Invariants)
  ↓
Level 2: Mechanism-Level Tests (Preemption, Synchronization, Fragmentation)
  ↓
Level 3: Integration-Level Tests (Full OS Lifecycle on VirtualBox)
```

---

## 2. Standardized Test Case Matrix (Section 16)

| Test ID | Designation | Parameters & Target Subsystem | Expected Outcome | Verification Status |
|---|---|---|---|---|
| **TC1** | Minimum Configuration | 2 Tasks, Round Robin $Q=2$, Bursts: 4, 4 | Preemption occurs; both tasks complete with non-zero turnaround. | **PASSED** |
| **TC2** | Multiple Tasks | 5 Tasks, Round Robin $Q=3$, Bursts: 2, 4, 6, 8, 3 | All 5 tasks complete; fair distribution; Jain's Index $> 0.90$. | **PASSED** |
| **TC3** | Boundary Case | Quantum Comparison ($Q=1$ vs $Q=50$) | $Q=1$ exhibits maximum switches ($11$); $Q=50$ degrades to FCFS ($2$ switches). | **PASSED** |
| **TC4** | Stress Case | 16 Tasks, Spinlock Contention, Heap Churn | All 16 tasks complete; $>40$ lock acquisitions; fragmentation $< 0.05$. | **PASSED** |
| **TC5** | Controlled Failure | OOM, Double Free, Reentrant Deadlock, Invalid State | All 5 illegal operations rejected with proper OS error codes without crashing. | **PASSED** |
| **TC6** | Repeatability | 2 Identical Consecutive Workload Runs | Run 1 and Run 2 yield identical ticks, switches, and turnaround times ($0\%$ drift). | **PASSED** |

---

## 3. Empirical Test Evidence

### 3.1 TC1: Minimum Configuration
- **Workload:** Task 1 ("Worker-Alpha", burst 4), Task 2 ("Worker-Beta", burst 4). Quantum $Q=2$.
- **Observed Behavior:** Task 1 executes for 2 ticks $\to$ preempted to `READY` $\to$ Task 2 executes for 2 ticks $\to$ preempted $\to$ Task 1 finishes $\to$ Task 2 finishes.
- **Trace Evidence:**
  `[TICK:00033] [INFO ] [SCHEDULER ] PREEMPTION: Quantum expired (Q=2). Switched Task 1 -> Task 2`

### 3.2 TC2: Multiple Tasks & Fairness
- **Workload:** 5 tasks with heterogeneous burst profiles (2, 4, 6, 8, 3 ticks).
- **Observed Metrics:**
  - Average Waiting Time: $6.40$ ticks
  - Average Turnaround Time: $11.00$ ticks
  - Jain's Fairness Index: $0.942$ (approaching theoretical ideal of $1.0$)

### 3.3 TC3: Boundary Quantum Limits
- **$Q=1$ (Infinitesimal Quantum):** Yields $11$ context switches. Scheduling latency drops to $1$ tick, but scheduling overhead reaches its maximum.
- **$Q=50$ (Infinite Quantum):** Yields $2$ context switches. Tasks run sequentially to completion without interruption (FCFS).

### 3.4 TC4: Stress & Concurrency Under Pressure
- **Workload:** 16 tasks concurrently executing, each acquiring a shared spinlock and performing dynamic memory allocations.
- **Results:**
  - Total Lock Acquisitions: $48$
  - Contention Events: $12$
  - Final Heap Free Space: $65,472$ bytes
  - Final Fragmentation Ratio: $0.0000$ (complete coalescing achieved)

### 3.5 TC5: Controlled Failure & Defensive Programming
- **OOM Rejection:** A 128 KiB allocation against the 64 KiB heap returns `None` and triggers error code `-12` (`-ENOMEM`).
- **Double-Free Guard:** Second deallocation on the same pointer is intercepted and returns `Err("Double free detected")`.
- **Deadlock Detection:** Reentrant spinlock acquisition by the same task returns `Err("Deadlock detected")`.
- **Invalid State Transition:** Attempting to transition from `Terminated` directly back to `Running` returns `Err("Cannot transition from TERMINATED state")`.

### 3.6 TC6: Deterministic Repeatability
- **Run 1:** Total Ticks = 12, Switches = 5, Total Turnaround = 28, Task 1 Turnaround = 8.
- **Run 2:** Total Ticks = 12, Switches = 5, Total Turnaround = 28, Task 1 Turnaround = 8.
- **Drift:** 0.000% variance. The execution path is completely deterministic.
