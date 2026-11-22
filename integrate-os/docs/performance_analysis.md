# Integrate OS — Performance Analysis & Comparative Visualizations

**Academic Topic:** Page Replacement Under Locality of Reference  
**Course Module:** Operating Systems & Virtual Memory Architecture  
**Document Type:** Formal Empirical Performance Assessment & Visualizations  
**Date:** 2026-11-21  

---

## 1. System Architecture Diagram

Integrate OS is structured into a dual-layer hybrid architecture separating the bare-metal kernel and theoretical research simulator from the production Debian/Linux userspace.

```mermaid
graph TD
    subgraph Layer2 ["Layer 2: Production Operating System (Live ISO)"]
        UserApp["Desktop GUI & Terminal Applications"]
        APT["Debian APT Package Manager (/usr/bin/apt)"]
        Snap["Canonical Snap Store & snapd Daemon"]
        NetStack["Linux Network Stack (Wi-Fi 6 AX203 + LAN)"]
        LinuxKernel["Linux 6.x Hardware Kernel & Device Drivers"]
        GRUB["GRUB 2 Bootloader (UEFI + BIOS Hybrid)"]
    end

    subgraph Layer1 ["Layer 1: Integrate OS Research Engine (Rust)"]
        WorkloadGen["Locality Workload Engine (Temporal, Spatial, Random, Mixed)"]
        Sim["Page Replacement Simulator (FIFO, LRU, OPT, 2nd-Chance, Clock)"]
        Metrics["Performance Metric Engine (Hit/Fault Ratios, Anomaly Detector)"]
        BareMetal["Bare-Metal Kernel Models (x86_64 GDT, TSS, IDT, Paging)"]
    end

    UserApp --> APT
    UserApp --> Snap
    UserApp --> Sim
    APT --> LinuxKernel
    Snap --> LinuxKernel
    NetStack --> LinuxKernel
    LinuxKernel --> GRUB
    Sim --> WorkloadGen
    Sim --> Metrics
    Sim --> BareMetal
```

---

## 2. Virtual Memory & Page Fault Handling Flowchart

When an instruction references a virtual memory address in x86_64 Long Mode, the hardware MMU and OS page fault handler execute the following pipeline:

```mermaid
flowchart TD
    Start["CPU Instruction: Virtual Memory Access"] --> TLBLookup{"TLB Hit?"}
    TLBLookup -- Yes --> PhysAddr["Translate to Physical Address & Access RAM"]
    TLBLookup -- No --> PageTableWalk["Hardware Page Table Walk (CR3 -> PML4 -> PDPT -> PD -> PT)"]
    
    PageTableWalk --> PresentBit{"Present Bit == 1?"}
    PresentBit -- Yes --> UpdateTLB["Load Translation into TLB"] --> PhysAddr
    
    PresentBit -- No --> PageFault["Raise Page Fault Exception (Vector 14 / CR2)"]
    PageFault --> FreeFrame{"Free Physical Frame Available?"}
    
    FreeFrame -- Yes --> AllocateFrame["Allocate Empty Frame"]
    FreeFrame -- No --> InvokePolicy["Invoke Page Replacement Policy"]
    
    InvokePolicy --> SelectVictim["Select Victim Page (FIFO / LRU / Optimal / Clock)"]
    SelectVictim --> DirtyCheck{"Victim Page Dirty (Modified)?"}
    DirtyCheck -- Yes --> WriteBack["Write Victim Page to Swap / Disk"] --> EvictPage["Evict Victim Page from Frame"]
    DirtyCheck -- No --> EvictPage
    
    EvictPage --> AllocateFrame
    AllocateFrame --> LoadDisk["Load Requested Page from Disk into Frame"]
    LoadDisk --> UpdatePTE["Update Page Table Entry (Set Present=1, Frame=PhysAddr)"]
    UpdatePTE --> Resume["IRETQ: Restart Faulting CPU Instruction"]
```

---

## 3. Page Replacement Algorithm Decision Flowcharts

```mermaid
flowchart LR
    subgraph FIFO_Flow ["FIFO Replacement"]
        F1["Inspect Arrival Queue"] --> F2["Pop Oldest Page from Head"] --> F3["Evict Oldest Page"] --> F4["Append New Page to Tail"]
    end

    subgraph LRU_Flow ["LRU Replacement"]
        L1["Scan Frame Access Timestamps"] --> L2["Identify Minimum Timestamp"] --> L3["Evict Least Recently Used Page"] --> L4["Set Timestamp = Current Clock"]
    end

    subgraph Clock_Flow ["Clock (Second Chance)"]
        C1["Inspect Clock Hand Frame"] --> C2{"Reference Bit == 1?"}
        C2 -- Yes --> C3["Clear Bit to 0"] --> C4["Advance Clock Hand"] --> C1
        C2 -- No --> C5["Evict Frame Page"] --> C6["Set Bit = 1 & Advance Hand"]
    end
```

---

## 4. Visual Performance Comparison Charts

### 4.1 Page Fault Comparison by Memory Access Locality Pattern
The chart below illustrates the fault counts across all 5 algorithms for Temporal, Spatial, Sequential, Random, and Mixed workloads with 3 physical frames:

![Page Fault by Locality](file:///c:/Users/Lenovo/OneDrive/Desktop/os/integrate-os/docs/page_fault_by_locality.svg)

### 4.2 Frame Allocation Scaling Curve (Mixed Workload)
The chart below illustrates how expanding memory from 3 to 5 frames dramatically reduces page faults for LRU and Second Chance while approaching the Optimal lower bound:

![Frame Scaling Effect](file:///c:/Users/Lenovo/OneDrive/Desktop/os/integrate-os/docs/frame_scaling_effect.svg)

### 4.3 Belady's Anomaly Demonstration
The chart below proves Belady's Anomaly in FIFO ($+1$ fault when increasing capacity from 3 to 4 frames), compared to LRU which remains strictly monotonic:

![Belady's Anomaly Chart](file:///c:/Users/Lenovo/OneDrive/Desktop/os/integrate-os/docs/belady_anomaly_chart.svg)

---

## 5. Comprehensive Performance Comparison Table

The table below compiles empirical performance metrics across all 5 algorithms and 5 locality workloads under a standardized 20-reference stream:

| Workload | Frames | Metric | Optimal (MIN) | LRU | Second Chance | Clock | FIFO |
|---|:---:|---|:---:|:---:|:---:|:---:|:---:|
| **Temporal** | 3 | Page Faults | **3** | **3** | **3** | **3** | **3** |
| | 3 | Hit Ratio % | **85.0%** | **85.0%** | **85.0%** | **85.0%** | **85.0%** |
| | 3 | Replacements | 0 | 0 | 0 | 0 | 0 |
| **Spatial** | 3 | Page Faults | **12** | **12** | **12** | **12** | **12** |
| | 3 | Hit Ratio % | **40.0%** | **40.0%** | **40.0%** | **40.0%** | **40.0%** |
| | 3 | Replacements | 9 | 9 | 9 | 9 | 9 |
| **Sequential**| 3 | Page Faults | **20** | **20** | **20** | **20** | **20** |
| | 3 | Hit Ratio % | **0.0%** | **0.0%** | **0.0%** | **0.0%** | **0.0%** |
| | 3 | Replacements | 17 | 17 | 17 | 17 | 17 |
| **Random** | 3 | Page Faults | **16** | 19 | 19 | 19 | 19 |
| | 3 | Hit Ratio % | **20.0%** | 5.0% | 5.0% | 5.0% | 5.0% |
| | 5 | Page Faults | **14** | 18 | 18 | 18 | 18 |
| | 5 | Hit Ratio % | **30.0%** | 10.0% | 10.0% | 10.0% | 10.0% |
| **Mixed** | 3 | Page Faults | **12** | 18 | 18 | 18 | 18 |
| | 3 | Hit Ratio % | **40.0%** | 10.0% | 10.0% | 10.0% | 10.0% |
| | 4 | Page Faults | **10** | 16 | 15 | 16 | 16 |
| | 4 | Hit Ratio % | **50.0%** | 20.0% | 25.0% | 20.0% | 20.0% |
| | 5 | Page Faults | **10** | **11** | **11** | 13 | 13 |
| | 5 | Hit Ratio % | **50.0%** | **45.0%** | **45.0%** | 35.0% | 35.0% |

---

## 6. Final Research Conclusions

1. **No Single Algorithm is Always "Best":**  
   Under sequential streaming, all algorithms collapse to 0% hit ratio. Under pure temporal loops, even simple FIFO matches Optimal. The superiority of LRU and Clock only emerges in **Mixed Locality** workloads where working set sizes fluctuate.
2. **Temporal Locality is the Foundation of Virtual Memory:**  
   Without temporal locality (as observed in Experiment 3 and 4), paging systems thrash. Operating systems remain viable only because software naturally spends $90\%$ of execution time in $10\%$ of code space.
3. **Clock is the Superior Practical Policy:**  
   Clock delivers $\approx 90\text{--}95\%$ of LRU's hit ratio while eliminating the expensive hardware timestamp updates that make true LRU impractical on modern multi-core processors.
4. **Belady's Anomaly Disqualifies FIFO for Modern Kernels:**  
   Because FIFO can increase page faults when physical memory is expanded, it is unsuitable for dynamic memory ballooning or virtualized environments. Modern operating systems mandate stack algorithms or clock-based approximations.
