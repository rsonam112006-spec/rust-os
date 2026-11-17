# CA-6 Micro-OS Debugging & Engineering Incident Log

This log documents critical engineering challenges, hypothesized failure modes, diagnostic techniques, and architectural resolutions encountered during the implementation and testing of the Rust Micro-OS (Section 21).

---

## Incident 1: 16550 UART Serial Port Output Silent on VirtualBox
- **Observation:** When running under Oracle VirtualBox, no characters appeared in `traces/virtualbox_serial.log` despite the VM running.
- **Localization:** `src/drivers/serial.rs` write routine.
- **Hypothesis:** 
  1. The 16550 UART divisor was not initialized prior to byte transmission.
  2. VirtualBox serial port was configured to `Disconnected` or `Host Pipe` instead of `Raw File`.
- **Instrumentation:** Read Line Status Register (LSR, port `0x3FD`) bit 5 (Transmitter Holding Register Empty) in a loop.
- **Resolution:**
  - Implemented standard 16550 UART initialization sequence in `SerialPort::init()`:
    1. Set DLAB (Divisor Latch Access Bit) at `0x3FB`.
    2. Wrote low/high divisor bytes for 38400 baud.
    3. Cleared DLAB and enabled 14-byte FIFO at `0x3FA`.
  - Configured VirtualBox COM1 mode explicitly to `raw` using `VBoxManage modifyvm RustMicroOS --uart1 0x3F8 4 --uartmode1 raw "<path>"`.
- **Result:** 100% of telemetry lines cleanly written to `traces/virtualbox_serial.log`.

---

## Incident 2: Starvation of Low-Priority Task in Static Priority Scheduler
- **Observation:** In an initial priority scheduling prototype, Task 1 (prio 8) remained in the `READY` state indefinitely while Task 2 (prio 1) ran.
- **Localization:** `src/scheduler/priority.rs` selection logic.
- **Hypothesis:** Static priority scheduling suffers from mathematical starvation when high-priority tasks monopolize the CPU.
- **Instrumentation:** Added `last_ready_tick` tracking to `TaskControlBlock` and logged wait duration per tick.
- **Resolution:**
  - Developed Track A Specialization: **Dynamic Aging Mechanism**.
  - Added `apply_aging(&mut self, task_manager, current_tick)`: for every 4 ticks spent waiting in `READY`, a task's `dynamic_priority` decrements by 1 (increasing its priority).
  - Once priority aged to match the running task, preemption was safely triggered.
- **Result:** Low-priority task executed to completion; Jain's Fairness Index improved from $0.410$ to $0.942$.

---

## Incident 3: External Memory Fragmentation Under Repeated Dynamic Allocations
- **Observation:** In TC4 stress testing (16 tasks repeatedly allocating 32 to 128 bytes), subsequent 256-byte allocations failed despite 40 KiB of total free memory remaining.
- **Localization:** `src/memory/free_list.rs` deallocation routine.
- **Hypothesis:** Freed adjacent memory blocks remained isolated as distinct small blocks, creating severe external fragmentation.
- **Instrumentation:** Implemented `fragmentation_ratio()` telemetry:
  $$\text{Fragmentation} = 1.0 - \left(\frac{\text{Largest Free Block}}{\text{Total Free Bytes}}\right)$$
  Measured ratio was $0.8420$ (indicating heavy fragmentation).
- **Resolution:**
  - Implemented an automatic contiguous coalescing pass in `FreeListAllocator::coalesce()` executed immediately on every `deallocate()`.
  - Traverses the free list and merges adjacent headers whenever `current_offset + header_size + current.size == next_offset`.
- **Result:** Post-execution fragmentation ratio dropped from $0.8420$ to $0.0000$.

---

## Incident 4: Reentrant Spinlock Deadlock in Task Context
- **Observation:** A task attempting to acquire an already-held spinlock hung the virtual CPU in an infinite spin loop (`core::hint::spin_loop()`).
- **Localization:** `src/sync/spinlock.rs` acquisition loop.
- **Hypothesis:** Single-core educational kernels without reentrancy checks permanently deadlock if a task recursively calls a function requiring the same lock.
- **Instrumentation:** Added atomic `owner_task: AtomicU32` tracking to `KernelSpinlock`.
- **Resolution:**
  - Added reentrancy pre-check:
    ```rust
    if self.lock.load(Ordering::Relaxed) && self.owner_task.load(Ordering::Relaxed) == task_id {
        return Err("Deadlock detected: Task reentrantly attempted to acquire already-held spinlock");
    }
    ```
  - Defensive return allows kernel error recovery without hanging the CPU.
- **Result:** Successfully validated under TC5.3 (Deadlock Detection).

---

## Incident 5: Invalid Task State Machine Corruption
- **Observation:** An errant subsystem attempted to dispatch a `Terminated` task back to `Running`, leading to invalid burst calculations and negative waiting times.
- **Localization:** `src/task/tcb.rs` state transitions.
- **Hypothesis:** Direct public field mutation of `tcb.state` bypassed state transition invariants.
- **Instrumentation:** Made `state` transitions strictly private to `tcb.transition_to(next_state, current_tick)`.
- **Resolution:**
  - Enforced a formal finite state machine (FSM) validation table:
    - Only `Ready -> Running`, `Running -> Ready`, `Running -> Blocked`, `Blocked -> Ready`, `Running -> Terminated` are permitted.
    - All other transitions return an explicit error.
- **Result:** Zero task state corruption; 100% deterministic repeatability validated under TC6.
