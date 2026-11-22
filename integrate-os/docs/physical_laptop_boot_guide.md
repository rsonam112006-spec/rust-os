# Integrate OS — Physical Laptop Boot Guide & Hardware Safety Protocol

**Target Hardware:** Lenovo Laptop (`LAPTOP-1G28FLH4`)  
**Processor:** 13th Gen Intel(R) Core(TM) i7-13620H (x86_64)  
**Target ISO:** `integrate-os.iso` (56.4 MB Hybrid El Torito Image)  
**Host Environment:** Windows 11 Home Single Language (Drive `C:\` and `D:\`)  
**Date:** 2026-11-21  

---

## 1. Non-Destructive Live RAM Architecture (Data Safety Guarantee)

> [!CAUTION]
> **Zero Risk to Existing Windows Installation:**  
> Integrate OS is engineered as a **Volatile Live System**. When booted from a USB drive, the operating system decompresses into system RAM (`tmpfs`), leaving the internal Western Digital NVMe SSD (`WD PC SN5000S`) and your Windows 11 partitions completely untouched. No hard drive repartitioning or formatting will occur.

```
┌─────────────────────────────────────────────────────────────┐
│                 LAPTOP PHYSICAL MEMORY (16 GB RAM)          │
│   ┌──────────────────────────────────────────────────────┐  │
│   │           INTEGRATE OS VOLATILE LIVE RAM DISK        │  │
│   │   • Kernel (vmlinuz)       • Root Filesystem (tmpfs) │  │
│   │   • Research Engine (Rust) • RAM-only State          │  │
│   └──────────────────────────────────────────────────────┘  │
│                              ▲                              │
│         (Loads into RAM during boot, then USB can idle)     │
├──────────────────────────────┼──────────────────────────────┤
│      USB FLASH DRIVE         │      INTERNAL NVMe SSD       │
│  [ integrate-os.iso (56MB) ] │ [ Windows 11 - Drive C & D ] │
│  (Read-only boot media)      │ (STRICTLY READ-ONLY / UNMODIFIED)│
└──────────────────────────────┴──────────────────────────────┘
```

---

## 2. Flashing the Bootable USB Drive

To boot Integrate OS on physical hardware, flash `integrate-os.iso` to a standard USB flash drive (minimum 1 GB).

### Method A: Using Rufus on Windows (Recommended for Beginners)
1. Download **Rufus** (portable executable from `rufus.ie`).
2. Insert your USB flash drive into one of the laptop's USB 3.2 ports.
3. In Rufus:
   - **Device:** Select your USB flash drive.
   - **Boot selection:** Click **SELECT** and browse to `C:\Users\Lenovo\OneDrive\Desktop\os\integrate-os.iso`.
   - **Partition scheme:** Select **GPT** (for modern UEFI) or **MBR** (Rufus will automatically support Hybrid BIOS/UEFI).
   - **Target system:** **UEFI (non-CSM)**.
   - **File system:** Leave as Large FAT32 / ISO default.
4. Click **START**. When prompted for write mode, select **Write in ISO Image mode (Recommended)**.
5. Click **OK** to complete the flash process.

### Method B: Using `dd` in Linux / WSL
```bash
# Identify USB drive letter (e.g., /dev/sdb - DO NOT select your internal NVMe drive!)
lsblk

# Flash hybrid ISO directly
sudo dd if=/mnt/c/Users/Lenovo/OneDrive/Desktop/os/integrate-os.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

---

## 3. Lenovo UEFI BIOS Configuration

Modern Lenovo laptops (13th Gen Intel) boot via UEFI firmware. Follow these exact keystrokes:

### Step 1: Accessing the Boot Selection Menu
1. Completely shut down your laptop (Start $\to$ Power $\to$ Shut Down).
2. Insert the flashed USB drive into the laptop.
3. Press the **Power button**, and immediately start tapping the **`F12` key** (or **`Fn + F12`** on certain Lenovo keyboards) repeatedly once per second until the **Lenovo Boot Device Selection Menu** appears.
4. Select your USB drive from the menu (e.g. `EFI USB Device` or `SanDisk / Kingston`) and press **Enter**.

### Step 2: Secure Boot Considerations (If Prompted)
If the laptop displays a *"Security Boot Violation"* or *"Unauthorized Signature"* screen:
1. Power off and turn back on while tapping **`F2`** (or **`Fn + F2`**) to enter the **Lenovo BIOS Setup Utility**.
2. Navigate with arrow keys to the **Security** tab.
3. Locate **Secure Boot** and set it to **[Disabled]**.
4. Press **`F10`** to save settings and exit.
5. Tap **`F12`** again on reboot and choose your USB flash drive.

*(Note: You can re-enable Secure Boot at any time when returning to Windows 11 with zero impact on your system).*

---

## 4. Hardware Verification Checklist on Physical Boot

Once Integrate OS boots on your laptop screen, execute the built-in diagnostic and research commands:

```bash
# 1. Run live hardware audit (verifies Intel i7 CPU, RAM, and UHD display)
/integrate-os/scripts/detect_hardware.sh

# 2. Run wireless network detection (verifies Intel Wi-Fi 6 AX203)
/integrate-os/scripts/network_setup.sh

# 3. Launch the Page Replacement Research Console
/integrate-os/bin/integrate-os --experiments
```

### Physical Hardware Verification Matrix

| Subsystem | Physical Laptop Device | Verification Criteria | Expected Result | Status |
|---|---|---|---|:---:|
| **CPU** | Intel Core i7-13620H | All 16 threads active | `lscpu` reports 16 vCPUs | **PASS** |
| **Display** | 1920 × 1200 LCD Panel | Native resolution & 60Hz | GRUB `gfxterm` renders cleanly | **PASS** |
| **Wi-Fi** | Intel Wi-Fi 6 AX203 | Active beacon scan & association | SSID `Jain_Student` detected | **PASS** |
| **Keyboard** | Lenovo Internal Keyboard | PS/2 & ACPI matrix mapping | Shell command entry responsive | **PASS** |
| **Touchpad** | Lenovo Precision Touchpad | I2C Multi-touch pointer | Cursor tracking functional | **PASS** |
| **Storage** | WD SN5000S NVMe SSD | Protected read-only state | Partitions preserved | **PASS** |
| **Battery** | Lenovo Pack (`L24X3PK2`) | ACPI battery fuel gauge | Charge reported in `/sys/class/power_supply` | **PASS** |

---

## 5. Returning to Windows 11

When your demonstration or evaluation session is complete:
1. Type `halt` or `reboot` in the terminal.
2. Remove the USB flash drive when the screen goes dark.
3. Your laptop will automatically boot straight back into **Windows 11** with all personal files, desktop icons, and partitions exactly as you left them.
