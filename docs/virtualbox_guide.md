# Oracle VirtualBox Deployment & Execution Guide for Rust Micro-OS

This document details how to configure, boot, and trace the **Rust Micro-OS** in **Oracle VirtualBox** without relying on QEMU.

---

## 1. Why Oracle VirtualBox (Replacing QEMU)

The CA-6 project specification permits running on virtualized hardware. Oracle VirtualBox was chosen as the primary hypervisor to:
1. Provide a true hypervisor environment representative of bare-metal x86_64 PC hardware.
2. Emulate standard legacy PC peripherals:
   - **8254 Programmable Interval Timer (PIT)** at I/O ports `0x40` and `0x43`.
   - **16550A UART Serial COM1** at I/O port `0x3F8` (IRQ 4).
   - **VGA Text Framebuffer** at physical address `0xB8000`.
3. Enable direct serial log redirection to a host file via VirtualBox's native **Raw File** serial port mode, producing trace logs (`traces/virtualbox_serial.log`) for the Python analysis engine.

---

## 2. Automated One-Click Provisioning

We provide automated setup scripts in PowerShell and Windows Command Prompt:

### Option A: PowerShell Script (`scripts/setup_virtualbox.ps1`)
Open PowerShell as Administrator or standard user in the project directory:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_virtualbox.ps1
```

### Option B: Windows Batch Script (`scripts/setup_virtualbox.bat`)
Double-click `scripts/setup_virtualbox.bat` in Windows File Explorer or execute from CMD:
```cmd
scripts\setup_virtualbox.bat
```

The script automatically:
1. Locates `VBoxManage.exe` on your system.
2. Unregisters and cleans up any existing `RustMicroOS` VM.
3. Creates a new 64-bit VM named `RustMicroOS`.
4. Allocates 256 MB RAM and 1 CPU.
5. Enables ACPI and I/O APIC.
6. Configures COM1 serial output directly to `traces/virtualbox_serial.log`.
7. Attaches the bootable image `micro-os.iso`.
8. Starts the VM in GUI mode.

---

## 3. Manual Step-by-Step GUI Configuration

If you prefer configuring VirtualBox through the graphical user interface:

### Step 1: Create the Virtual Machine
1. Open **Oracle VirtualBox Manager**.
2. Click **Machine -> New** (or press `Ctrl+N`).
3. Set the following parameters:
   - **Name:** `RustMicroOS`
   - **Type:** `Other`
   - **Version:** `Other/Unknown (64-bit)`
4. Set **Base Memory** to **256 MB**.
5. Set **Processors** to **1 CPU**.
6. Select **Do not add a virtual hard disk** (the OS boots directly from ISO/floppy).
7. Click **Finish**.

### Step 2: Configure System Settings
1. Select `RustMicroOS` and click **Settings -> System**.
2. On the **Motherboard** tab:
   - Check **Enable I/O APIC**.
   - Check **Enable ACPI**.
   - Boot Order: Check **Optical** (move to the top), uncheck Floppy and Hard Disk.

### Step 3: Attach Boot Media
1. Go to **Settings -> Storage**.
2. Under **Storage Devices**, select the optical drive (or add an IDE Controller if missing).
3. Click the disk icon on the right side and choose **Choose a disk file...**.
4. Select `micro-os.iso` located in the root of the project directory.

### Step 4: Configure Serial Port COM1 (Critical for Trace Logging)
1. Go to **Settings -> Serial Ports**.
2. Select **Port 1**.
3. Check **Enable Serial Port**.
4. Set **Port Number:** `COM1` (I/O Port: `0x3F8`, IRQ: `4`).
5. Set **Port Mode:** `Raw File`.
6. Set **Path/Address:** Enter the absolute path to your trace log, e.g.:
   `C:\Users\Lenovo\OneDrive\Desktop\os\traces\virtualbox_serial.log`
7. Click **OK**.

### Step 5: Start the Virtual Machine
1. Click **Start** (Green arrow icon) in VirtualBox.
2. The VM will boot from `micro-os.iso`.
3. The VirtualBox display window will render the VGA console output.
4. All detailed kernel diagnostics and scheduler telemetry will stream into `traces/virtualbox_serial.log`.

---

## 4. Trace Analysis Pipeline

Once the VirtualBox execution finishes, run the Python analysis pipeline:

### Step 1: Parse Serial Log
```bash
python scripts/parse_traces.py traces/virtualbox_serial.log results/metrics_summary.json
```
Extracts all timestamps, preemptions, context switches, task completions, and produces `results/metrics_summary.json`.

### Step 2: Generate Timeline & Performance Report
```bash
python scripts/visualize_metrics.py results/metrics_summary.json results/performance_analysis.md
```
Generates an ASCII Gantt chart and markdown report with scheduling metrics and Linux comparative analysis.

---

## 5. VirtualBox Troubleshooting

| Issue | Root Cause | Solution |
|---|---|---|
| `VBoxManage.exe not found` | VirtualBox installation path not in system PATH | Run installer from `C:\Program Files\Oracle\VirtualBox\` or install VirtualBox from official website. |
| `Cannot open file traces/virtualbox_serial.log` | File is locked by another program or permissions issue | Ensure previous VM instance is stopped: `VBoxManage controlvm RustMicroOS poweroff`. |
| `VT-x/AMD-V is not available` | Hardware virtualization disabled in BIOS or Hyper-V conflict | Enable Intel VT-x or AMD SVM in BIOS/UEFI. Disable Windows Hyper-V if running nested. |
| `FATAL: No bootable medium found` | ISO not properly attached to VirtualBox optical drive | Verify `micro-os.iso` exists. Re-run `python scripts/build_bootable_iso.py` and attach to IDE controller. |
