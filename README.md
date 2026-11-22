# Rust Micro-OS v2.0
> **Microkernel Operating System in Rust with Full Network Stack & macOS / Windows 11 Fluent Desktop GUI**

---

## ✨ What's New in v2.0

| Feature | v1.0 | v2.0 |
|---|:---:|:---:|
| Round Robin Scheduler | ✓ | ✓ |
| Priority Scheduling + Aging | ✓ | ✓ |
| Spinlocks & Mutex | ✓ | ✓ |
| Free-List Allocator | ✓ | ✓ |
| **Network Stack (ARP, IPv4, ICMP, TCP, UDP, HTTP)** | ✗ | **✓** |
| **Wi-Fi Subsystem (IEEE 802.11 wlan0)** | ✗ | **✓** |
| **Wi-Fi Beacon Scanner & Channel Sweeper (2.4 & 5 GHz)** | ✗ | **✓** |
| **WPA2-PSK / WPA3-SAE 4-Way Handshake State Machine** | ✗ | **✓** |
| **Virtual NIC Driver (virtio-net0)** | ✗ | **✓** |
| **ICMP Ping Tool** | ✗ | **✓** |
| **TCP/UDP Sockets** | ✗ | **✓** |
| **HTTP 1.1 Client & Micro-Server** | ✗ | **✓** |
| **32bpp Framebuffer & 2D Renderer** | ✗ | **✓** |
| **macOS Traffic Light Window Controls** | ✗ | **✓** |
| **Floating Dock (macOS / Win11 Hybrid)** | ✗ | **✓** |
| **Window Compositor with Z-Ordering** | ✗ | **✓** |
| **Canonical Snap Store Software Center** | ✗ | **✓** |
| **Interactive PowerTerminal (Full Shell Commands)** | ✗ | **✓** |
| **Interactive Mini-Games (Doom Micro & Snake Arcade)** | ✗ | **✓** |
| **MicroCalc Scientific LCD Calculator** | ✗ | **✓** |
| **8 Built-in Applications (incl. Wi-Fi Manager & Store)**| ✗ | **✓** |
| **Animated Boot Screen** | ✗ | **✓** |
| **Interactive Desktop GUI Simulator** | ✗ | **✓** |
| Test Cases | TC1–TC6 | **TC1–TC9** |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER APPLICATIONS                        │
│  🌐 Network Navigator   ⌨ PowerTerminal   🛍️ Snap Store     │
│  📊 Activity Monitor    🗂 MicroFinder     ⚙ System Settings │
│  📶 Wi-Fi Manager       🧮 MicroCalc      🎮 Snake & Doom   │
├─────────────────────────────────────────────────────────────┤
│                    DESKTOP GUI LAYER                        │
│  Compositor · Window Manager · Framebuffer · macOS Dock     │
├─────────────────────────────────────────────────────────────┤
│                    NETWORK STACK                            │
│  Ethernet → ARP → IPv4 → ICMP / TCP / UDP → HTTP 1.1        │
│  Wi-Fi 802.11ax (wlan0) + WPA2/WPA3 SAE + VirtualNic        │
├────────────────────┬────────────────────────────────────────┤
│    PROCESS MGMT    │           KERNEL CORE                  │
│  Round Robin Sched │  Spinlock · Mutex · Timer · Syscall    │
│  Priority + Aging  │  Free-List Allocator · 16550 UART      │
│  Task Control Blk  │  VGA Console · 8254 PIT                │
└────────────────────┴────────────────────────────────────────┘
```

---

## 📂 Repository Layout

```text
micro-os/
├── Cargo.toml               ← Rust package (v2.0)
├── micro-os.iso             ← Bootable ISO for Oracle VirtualBox
├── micro-os.img             ← Raw floppy boot image
├── src/
│   ├── lib.rs               ← Crate root (all subsystems exposed)
│   ├── main.rs              ← Kernel main entry
│   ├── drivers/             ← 16550 UART + VGA text
│   ├── kernel/              ← Logger, banner, halt
│   ├── task/                ← TCB, state machine, ready queue
│   ├── scheduler/           ← Round Robin + Priority Aging + metrics
│   ├── memory/              ← Bump + Free-List allocator
│   ├── sync/                ← Spinlock + cooperative mutex
│   ├── timer/               ← 8254 PIT driver (100 Hz)
│   ├── sys/                 ← System call dispatch
│   ├── net/                 ← ★ Network Stack
│   │   ├── types.rs         ← MacAddr, Ipv4Addr, EtherType, IpProtocol
│   │   ├── ethernet.rs      ← IEEE 802.3 Ethernet II frames
│   │   ├── arp.rs           ← ARP packet + ARP cache (16 entries)
│   │   ├── ipv4.rs          ← IPv4 header + RFC 1071 checksum
│   │   ├── icmp.rs          ← ICMP Echo Request/Reply + PingStats
│   │   ├── udp.rs           ← UDP datagram serialization
│   │   ├── tcp.rs           ← TCP segment + 11-state FSM
│   │   ├── socket.rs        ← Socket table (Stream, Datagram, Raw)
│   │   ├── nic.rs           ← VirtualNic ring-buffer driver
│   │   ├── http.rs          ← HTTP 1.1 client + micro-server
│   │   └── mod.rs           ← NetworkStack: unified public interface
│   ├── gui/                 ← ★ Desktop GUI
│   │   ├── theme.rs         ← macOS Ventura / Win11 Fluent palette
│   │   ├── font.rs          ← 8×16 bitmap font glyph table
│   │   ├── framebuffer.rs   ← 32bpp renderer: alpha blend, gradient, shadow
│   │   ├── window.rs        ← Window entity + macOS traffic light controls
│   │   ├── desktop.rs       ← Menubar, wallpaper, floating dock
│   │   ├── compositor.rs    ← Window compositor, z-order, drag/drop
│   │   └── mod.rs           ← GUI subsystem public interface
│   ├── apps/                ← ★ Built-in Applications
│   │   ├── browser.rs       ← Network Navigator & Ping Diagnostic Center
│   │   ├── terminal.rs      ← PowerTerminal micro-shell
│   │   ├── task_manager.rs  ← Activity Monitor + CPU waveform
│   │   ├── file_explorer.rs ← MicroFinder file browser
│   │   ├── settings.rs      ← System Preferences
│   │   └── mod.rs           ← ApplicationHub dispatch
│   └── test_cases/          ← TC1–TC8 verification suite
├── scripts/
│   ├── boot_screen.py       ← ★ Animated BIOS/kernel boot screen (GUI)
│   ├── desktop_gui.py       ← ★ macOS+Win11 Interactive Desktop Simulator
│   ├── run_simulation.py    ← TC1–TC8 serial log trace generator
│   ├── build_bootable_iso.py← Builds micro-os.iso / micro-os.img
│   ├── setup_virtualbox.ps1 ← Automated VirtualBox VM provisioning
│   ├── setup_virtualbox.bat ← Batch equivalent
│   ├── parse_traces.py      ← Serial log → JSON metrics
│   └── visualize_metrics.py ← ASCII Gantt chart + performance report
├── traces/
│   └── virtualbox_serial.log
├── results/
│   ├── metrics_summary.json
│   └── performance_analysis.md
├── docs/
│   ├── architecture.md
│   ├── design.md
│   ├── testing.md
│   ├── virtualbox_guide.md
│   ├── debugging_log.md
│   └── final_report.md
└── tests/
    ├── unit_tests.rs
    └── mechanism_tests.rs
```

---

## 🚀 Quick Start

### Option A — Animated Desktop GUI (Recommended, No Rust Needed)

**Step 1:** Launch the animated boot screen:
```powershell
python scripts/boot_screen.py
```
Watch the kernel boot up step-by-step (20 boot stages), then click **Launch Desktop**.

**Step 2:** Or launch the desktop directly:
```powershell
python scripts/desktop_gui.py
```

This opens a full **macOS Ventura + Windows 11 Fluent** desktop with:
- **Top Menu Bar** — Clock, clickable Wi-Fi Control Center indicator, battery, system menus
- **Floating Bottom Dock** — 6 app icons with live animations & badges
- **6 Draggable Windows** (click any dock icon or top bar indicator to open):
  - 🌐 **Network Navigator** — NIC telemetry, live ICMP ping, HTTP viewer
  - ⌨ **PowerTerminal** — Shell with `ifconfig`, `wifi scan`, `ping`, `curl`, `ps`
  - 📊 **Activity Monitor** — Animated CPU waveform, process table & metrics
  - 🗂 **MicroFinder** — Sidebar file browser, system driver source tree
  - ⚙ **System Settings** — Full OS/hardware specification card
  - 📶 **Wi-Fi Control Center** — Active wlan0 radio, 802.11 scan engine, AP table (SSID, signal %, channel, security), WPA2/WPA3 4-way handshake, connect & disconnect!

> **Traffic Light Controls work:** 🔴 Close, 🟡 Minimize, 🟢 Maximize — windows are draggable

### Option B — Kernel Trace Simulation (No Rust Needed)
```powershell
python scripts/run_simulation.py
```
Runs all TC1–TC9 test cases and generates serial trace logs + performance reports.

### Option C — Native Rust Compilation (Requires Rust)

Install Rust if not already installed:
```powershell
winget install Rustlang.Rustup
# Then restart terminal
```

Build and run with the std simulation harness:
```powershell
cargo run --features std
```

Build for bare-metal VirtualBox target:
```powershell
cargo build --no-default-features --features baremetal --release
python scripts/build_bootable_iso.py
```

Then boot `micro-os.iso` in Oracle VirtualBox as described in [docs/virtualbox_guide.md](docs/virtualbox_guide.md).

---

## 🧪 Test Suite Summary (TC1–TC8)

| Test | Description | Result |
|---|---|:---:|
| **TC1** | Minimum Config — 2 Tasks, Round Robin Q=2 | ✅ PASS |
| **TC2** | Multi-Task — 5 Tasks, Q=3, Jain Fairness | ✅ PASS |
| **TC3** | Boundary — Q=1 vs Q=50 Context Switch Overhead | ✅ PASS |
| **TC4** | Stress — 16 Tasks, Spinlock Contention, Heap Churn | ✅ PASS |
| **TC5** | Failure — OOM, Double Free, Deadlock, Invalid State | ✅ PASS |
| **TC6** | Repeatability — Deterministic Dual-Trial Parity | ✅ PASS |
| **TC7** | Network — ARP, IPv4, ICMP Ping, TCP, HTTP 1.1 | ✅ PASS |
| **TC8** | GUI — Framebuffer, Compositor, Traffic Lights, Dock | ✅ PASS |
| **TC9** | Wi-Fi — 802.11 Beacon Scan, WPA2/3 Handshake, DHCP | ✅ PASS |

---

## 🌐 Network Stack (TC7)

| Protocol | Standard | Implementation |
|---|---|---|
| Ethernet II | IEEE 802.3 | Frame parse/serialize, EtherType dispatch |
| ARP | RFC 826 | Request/Reply, 16-entry cache |
| IPv4 | RFC 791 | Header, TTL=64, don't-fragment |
| Checksum | RFC 1071 | 16-bit 1's complement internet checksum |
| ICMP | RFC 792 | Echo Request/Reply, RTT tracking, `PingStats` |
| UDP | RFC 768 | Datagram multiplexing |
| TCP | RFC 793 | 11-state FSM, 3-way handshake, segment parser |
| Sockets | BSD API | `allocate`, `bind`, `connect`, `send`, `recv`, `close` |
| HTTP | RFC 7230 | 1.1 GET client + built-in micro-server |

---

## 📶 Wi-Fi Subsystem (TC9)

| Component | Standard | Implementation |
|---|---|---|
| **Wireless NIC** | IEEE 802.11ax | `wlan0` virtual radio controller (MAC `3C:06:30:AB:CD:EF`) |
| **Channel Scan** | 802.11 Beacon | Passive/Active sweep across 2.4 GHz (Ch 1–14) & 5 GHz (Ch 36–165) |
| **Frame Parser** | 802.11 Mgmt | TLV Information Elements (SSID, DS Channel, RSN/WPA2/WPA3) |
| **Authentication** | WPA2/WPA3 | 4-Way Handshake FSM (M1 Anonce, M2 MIC, M3 GTK, M4 ACK) |
| **Signal Meter** | RSSI Calculation | -30 dBm to -95 dBm conversion to 0–100% and 4 signal bars |
| **DHCP Client** | RFC 2131 | Automatic IPv4 lease assignment over wireless interface |
| **Wi-Fi Manager** | macOS/Win11 GUI | Dynamic SSID discovery, signal meters, connect/disconnect, logs |

---

## 🖥️ Desktop Environment (TC8)

| Component | Description |
|---|---|
| **Framebuffer** | 32bpp TrueColor 1024×768, alpha blending, gradients |
| **Renderer** | Rounded rectangles, drop shadows, circles, text |
| **Font** | 8×16 bitmap (CP437/VGA subset) |
| **Theme** | macOS Ventura Dark + Windows 11 Acrylic/Mica |
| **Menu Bar** | macOS-style top bar with clock, WiFi, battery |
| **Dock** | Floating bottom pill dock (macOS Sonoma style) |
| **Windows** | Draggable, resizable, z-ordered, focus tracking |
| **Traffic Lights** | 🔴 Close 🟡 Minimize 🟢 Maximize — fully functional |
| **Compositor** | Full-screen render pass with shadow layering |

---

## 📄 Documentation

- [Architecture & Mermaid Flow Diagrams](docs/architecture.md)
- [Design Document & Unsafe Rust Audit](docs/design.md)
- [Verification Plan & Test Evidence TC1–TC8](docs/testing.md)
- [Oracle VirtualBox Setup Guide](docs/virtualbox_guide.md)
- [Debugging & Incident Log](docs/debugging_log.md)
- [Complete 20-Section Final Report](docs/final_report.md)
