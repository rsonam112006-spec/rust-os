# Integrate OS — Source Code to Bootable ISO Binary Pipeline

**Assessment Presentation Topic:** Operating System Construction & ISO Generation  
**Target Image:** `integrate-os.iso` (Hybrid BIOS & UEFI 64-bit Bootable Image)  
**Output Size:** 59,119,616 bytes (~56.4 MB)  
**Date:** 2026-11-21  

---

## 1. Master Architecture Flowchart

The diagram below illustrates the exact end-to-end industrial pipeline developed to convert bare source code into a bootable ISO capable of running on virtual machines and physical hardware:

```text
       SOURCE CODE
            │ (Rust no_std, Rust std, Shell scripts, Python)
            ▼
       COMPILATION
            │ (cargo build --release, GCC 11.4)
            ▼
 KERNEL + DRIVERS + APPLICATIONS
            │ (vmlinuz 5.15, iwlwifi, integrate-os research binary)
            ▼
      ROOT FILESYSTEM
            │ (glibc, APT, snapd, /usr/local/bin, /etc, /dev)
            ▼
      GRUB BOOTLOADER
            │ (grub.cfg, i386-pc eltorito, x86_64-efi)
            ▼
   ISO IMAGE GENERATION
            │ (grub-mkrescue, xorriso RockRidge engine)
            ▼
       BOOTABLE ISO
            │ (integrate-os.iso - 56.4 MB Hybrid Image)
            ▼
  VIRTUAL MACHINE TESTING
            │ (Oracle VirtualBox 7.2.22 / QEMU)
            ▼
  PHYSICAL LAPTOP TESTING
              (Boot via USB flash drive on Lenovo Intel i7)
```

---

## 2. Step-by-Step Technical Stage Breakdown

### Step 1: Source Code
* **What it contains:**  
  The raw human-readable source code of all system components:
  - **Research Engine Source:** `integrate-os/research/src/` (Rust algorithms: FIFO, LRU, Optimal, Second Chance, Clock).
  - **Kernel Architecture Models:** `integrate-os/kernel_arch/src/` (64-bit GDT, TSS, IDT, Paging structures).
  - **System Drivers & Scripts:** `network_setup.sh`, `detect_hardware.sh`, `measure_boot.py`, `snap_store_gui.py`.
  - **Bootloader Configurations:** `boot/grub/grub.cfg`.

### Step 2: Compilation
* **Mechanism:**  
  Converting Rust and C source code into machine-executable ELF (Executable and Linkable Format) 64-bit binaries:
  ```bash
  cargo build --release --manifest-path integrate-os/research/Cargo.toml
  ```
* **Output:**  
  Optimized binary `target/release/integrate_os_research` stripped of debugging bloat with Level 3 compiler optimizations (`opt-level = 3`).

### Step 3: Kernel and Modules
* **Mechanism:**  
  Providing the operating system core that controls hardware:
  - **Kernel Binary (`vmlinuz`):** A compressed, self-booting 64-bit Linux kernel binary (`5.15.0-204-generic`) containing CPU schedulers, virtual memory manager, and basic drivers.
  - **Kernel Modules:** Loadable drivers for Wi-Fi (`iwlwifi`), audio (`snd_hda_intel`), and graphics (`i915`).
  - **Initial Ramdisk (`initrd.img`):** A temporary root filesystem loaded into memory by GRUB to provide essential storage and driver modules before the main system mounts.

### Step 4: Root Filesystem (Rootfs)
* **Organization:**  
  Preparing the directory hierarchy compliant with the Linux Filesystem Hierarchy Standard (FHS):
  - `/bin`, `/sbin`: Core system commands (`ip`, `ping`, `sh`).
  - `/usr/local/bin`: Staging location for the compiled `integrate-os` research engine.
  - `/etc`: Configuration files (APT `sources.list`, GRUB config, network rules).
  - `/var/lib/snapd`: Working state directory for containerized Snap Store packages.

### Step 5: Bootloader Integration (GRUB 2)
* **Mechanism:**  
  The bootloader is the first software executed by system firmware (BIOS/UEFI):
  - Integrate OS embeds **GRUB 2** configured via `boot/grub/grub.cfg`.
  - Configures serial console output at 115200 baud for VirtualBox COM1 capture.
  - Presents a graphical splash menu offering Default Mode, Research Console Benchmark Mode, and Safe Graphics Diagnostic Mode.

### Step 6: ISO Filesystem Organization (El Torito Specification)
* **Staging Layout:**  
  The staging tree is assembled in a dedicated build directory:
  ```text
  /tmp/integrate_os_iso_staging/
  ├── boot/
  │   ├── grub/
  │   │   └── grub.cfg
  │   ├── vmlinuz
  │   └── initrd.img
  └── integrate-os/
      ├── bin/
      │   └── integrate-os
      └── scripts/
          ├── detect_hardware.sh
          ├── network_setup.sh
          └── snap_store_gui.py
  ```

### Step 7: ISO Generation (Build Tools)
* **Build Engine:**  
  The final binary image is synthesized using `grub-mkrescue` and `xorriso`:
  ```bash
  grub-mkrescue -o integrate-os.iso /tmp/integrate_os_iso_staging
  ```
* **Output:**  
  Produces a **Hybrid ISO 9660** filesystem with **El Torito extensions**:
  - Contains an MBR (Master Boot Record) with legacy BIOS boot code (`boot_hybrid.img`).
  - Contains an EFI System Partition (`efi.img`) enabling direct native 64-bit UEFI boot.

### Step 8: Virtual Machine Testing (VirtualBox)
* **Validation:**  
  The resulting `integrate-os.iso` is mounted as a virtual optical disc in **Oracle VirtualBox**:
  - Verifies MBR/GRUB handoff.
  - Confirms video resolution and serial console logging.
  - Verifies kernel decompression and memory allocation.

### Step 9: Physical Laptop Testing
* **Procedure:**  
  The ISO can be flashed onto a USB drive (via Rufus or `dd`):
  ```bash
  sudo dd if=integrate-os.iso of=/dev/sdX bs=4M status=progress oflag=sync
  ```
  Booted directly on the physical Lenovo laptop by selecting the USB boot drive in the UEFI Boot Menu (F12 key).

---

## 3. ISO Binary Verification Audit

The generated `integrate-os.iso` was audited using `xorriso` and `file`:

```text
Boot record  : El Torito , MBR protective-msdos-label grub2-mbr GPT APM
Volume ID    : 'ISOIMAGE'
Size         : 59,119,616 bytes (56.4 MB)
Sectors      : 28,867 sectors at LBA 0 (2048 bytes/sector)
BIOS Entry   : -b '/boot/grub/i386-pc/eltorito.img' -no-emul-boot
UEFI Entry   : -eltorito-alt-boot -e '/efi.img' -no-emul-boot
```

**Verification Status: VALID HYBRID BOOTABLE ISO GENERATED (100% PASS).**
