# Integrate OS — Page Replacement Research Engine Report

**Academic Subject:** Operating Systems & Memory Management  
**Research Topic:** Page Replacement Under Locality of Reference  
**Implementation Language:** Pure Rust (`integrate-os/research`)  
**Verification Date:** 2026-11-21  

---

## 1. Mathematical Definitions & Performance Metrics

When a process references a virtual memory page that is not currently mapped into physical memory (RAM), the CPU Memory Management Unit (MMU) triggers a **Page Fault Exception** (Vector 14). If all available physical frames are occupied, the operating system must invoke a **Page Replacement Policy** to evict an existing victim page.

Performance is quantified by the following exact formulas:

$$\text{Page Fault Ratio} = \left( \frac{\text{Page Faults}}{\text{Total References}} \right) \times 100\%$$

$$\text{Page Hit Ratio} = \left( \frac{\text{Page Hits}}{\text{Total References}} \right) \times 100\%$$

$$\text{Page Fault Ratio} + \text{Page Hit Ratio} = 100\%$$

---

## 2. Implemented Page Replacement Algorithms

### 2.1 FIFO (First-In, First-Out)
- **Concept:** Evicts the page that arrived in physical memory earliest, regardless of how frequently or recently it was accessed.
- **Data Structure:** First-in queue (`std::collections::VecDeque`).
- **Limitation:** Does not exploit temporal locality. Suffer from **Belady's Anomaly** (increasing frame capacity can paradoxically increase page faults).

### 2.2 LRU (Least Recently Used)
- **Concept:** Evicts the page that has not been referenced for the longest duration of time.
- **Locality Relationship:** Leverages **Temporal Locality** (if a page was used recently, it will likely be used again soon).
- **Implementation:** Monotonic logical timestamp tracking per physical frame.

### 2.3 Optimal Page Replacement (Belady's MIN)
- **Concept:** Replaces the page whose next memory reference is farthest in the future (or will never be used again).
- **Role:** Theoretical performance benchmark. Provably yields the absolute minimum possible number of page faults for a fixed frame allocation.
- **Feasibility:** Cannot be implemented in a general real-time kernel because the OS cannot foresee future instruction streams, but serves as the ideal standard of comparison.

### 2.4 Second Chance Algorithm
- **Concept:** Practical enhancement to FIFO using hardware reference bits.
- **Mechanics:** When inspecting candidates at the head of the arrival queue:
  - If $\text{reference\_bit} = 1$: Clear bit to $0$ and move page to the tail of the queue ("second chance" granted).
  - If $\text{reference\_bit} = 0$: Evict page immediately as the victim.

### 2.5 Clock Algorithm
- **Concept:** High-performance circular buffer implementation approximating LRU with $O(1)$ amortized overhead.
- **Mechanics:** Uses a rotating clock hand sweeping over physical frames. If reference bit is $1$, it resets to $0$ and the hand advances; if $0$, that frame is replaced, the bit is set to $1$, and the hand steps to the next slot.

---

## 3. Standard Textbook Benchmark Results (3 Frames)

**Reference String:** `[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]` (20 References)

### 3.1 Step-by-Step Frame Execution Table (LRU)
```text
Step   | Page   | F0    | F1    | F2    | Result     | Replaced
---------------------------------------------------------------
1      | 7      | 7     | [ ]   | [ ]   | FAULT      | (Loaded)
2      | 0      | 7     | 0     | [ ]   | FAULT      | (Loaded)
3      | 1      | 7     | 0     | 1     | FAULT      | (Loaded)
4      | 2      | 2     | 0     | 1     | FAULT      | Page 7
5      | 0      | 2     | 0     | 1     | HIT        | -
6      | 3      | 2     | 0     | 3     | FAULT      | Page 1
7      | 0      | 2     | 0     | 3     | HIT        | -
8      | 4      | 4     | 0     | 3     | FAULT      | Page 2
9      | 2      | 4     | 0     | 2     | FAULT      | Page 3
10     | 3      | 4     | 3     | 2     | FAULT      | Page 0
11     | 0      | 0     | 3     | 2     | FAULT      | Page 4
12     | 3      | 0     | 3     | 2     | HIT        | -
13     | 2      | 0     | 3     | 2     | HIT        | -
14     | 1      | 1     | 3     | 2     | FAULT      | Page 0
15     | 2      | 1     | 3     | 2     | HIT        | -
16     | 0      | 1     | 0     | 2     | FAULT      | Page 3
17     | 1      | 1     | 0     | 2     | HIT        | -
18     | 7      | 1     | 0     | 7     | FAULT      | Page 2
19     | 0      | 1     | 0     | 7     | HIT        | -
20     | 1      | 1     | 0     | 7     | HIT        | -
---------------------------------------------------------------
Summary: Total: 20, Hits: 8 (40.0%), Faults: 12 (60.0%), Replacements: 9
```

### 3.2 Five-Algorithm Performance Comparison Table

| Algorithm | Frame Capacity | Memory References | Page Hits | Page Faults | Page Hit Ratio | Page Fault Ratio | Page Replacements |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Optimal (MIN)** | 3 | 20 | **11** | **9** | **55.00%** | **45.00%** | **6** |
| **Second Chance** | 3 | 20 | 9 | 11 | 45.00% | 55.00% | 8 |
| **LRU** | 3 | 20 | 8 | 12 | 40.00% | 60.00% | 9 |
| **Clock** | 3 | 20 | 6 | 14 | 30.00% | 70.00% | 11 |
| **FIFO** | 3 | 20 | 5 | 15 | 25.00% | 75.00% | 12 |

---

## 4. Belady's Anomaly Audit

**Workload:** `[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]` (12 References)

| Algorithm | Frame Capacity | Page Faults | Fault Ratio | Anomaly Behavior |
|---|:---:|:---:|:---:|---|
| **FIFO** | 3 Frames | 9 | 75.0% | Normal baseline |
| **FIFO** | **4 Frames** | **10** | **83.3%** | **Belady's Anomaly Triggered (+1 Fault despite +33% Memory!)** |
| **LRU** | 3 Frames | 10 | 83.3% | Normal |
| **LRU** | 4 Frames | 8 | 66.7% | Strictly Decreasing (Stack Algorithm - Anomaly Immune) |

### Theoretical Insight: Why LRU is Immune to Belady's Anomaly
LRU belongs to the mathematical class of **Stack Algorithms**. For any stack algorithm, the set of pages resident in memory with $n$ frames is always a strict subset of the pages resident with $n+1$ frames:
$$M(n, t) \subseteq M(n+1, t)$$
FIFO is **not** a stack algorithm; its replacement decision depends on arrival sequence rather than access recency, allowing its working set to drift and incur more faults as capacity grows.

---

## 5. Verification Test Matrix

| Test ID | Test Objective | Target Condition | Result |
|:---:|---|---|:---:|
| **PAGE-01** | FIFO Textbook Accuracy | 15 Faults / 5 Hits on 20-ref textbook trace | **PASS** |
| **PAGE-02** | LRU Temporal Exploitation | 12 Faults / 8 Hits on 20-ref textbook trace | **PASS** |
| **PAGE-03** | Optimal Theoretical Limit | 9 Faults / 11 Hits on 20-ref textbook trace | **PASS** |
| **PAGE-04** | Belady's Anomaly Verification | FIFO Faults(4 Frames) > FIFO Faults(3 Frames) | **PASS** |
| **PAGE-05** | Second Chance Mechanism | Reference bit clearing & second chance re-queue | **PASS** |
| **PAGE-06** | Clock Circular Hand Pointer | Correct cyclic frame replacement & bit sweep | **PASS** |
| **PAGE-07** | Step Record Consistency | $\text{Hits} + \text{Faults} = \text{Total References}$ | **PASS** |

**Summary: 7 / 7 Tests PASS (100%).**
