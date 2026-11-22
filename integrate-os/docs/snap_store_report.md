# Integrate OS — Built-in App Store (Snap Store) Integration Report

**Target OS:** Integrate OS  
**Subsystem:** Canonical Snap Store & `snapd` Containerized Package Manager  
**Verification Date:** 2026-11-21  

---

## 1. Overview of Snap Store Integration

Integrate OS incorporates Canonical's **Snap Store** ecosystem alongside Debian's APT package manager. 

Unlike traditional `.deb` packages which install shared libraries directly into system paths (`/usr/lib`, `/lib`), Snap packages are self-contained, read-only **SquashFS** filesystem images mounted under `/snap`. They execute within isolated security sandboxes leveraging:
- Linux **cgroups** (resource allocation)
- **AppArmor** profiles (confinement and syscall filtering)
- **Seccomp** BPF filters (kernel interface restriction)

This architecture prevents dependency hell and allows safe, transactional installation and automated background updates of third-party software.

---

## 2. Daemon Configuration & Service Availability

The Snap system is driven by `snapd` (v2.78 / v2.66.1+22.04), which communicates with the kernel and the remote Snap Store REST API (`https://api.snapcraft.io`).

### 2.1 Systemd Socket Activation
The service is configured with systemd socket activation (`snapd.socket`), ensuring the daemon only consumes CPU and memory when packages are queried or installed:
- **Socket:** `/run/snapd.socket` -> `Active (listening)`
- **Service:** `snapd.service` -> Auto-starts on socket traffic and manages mounts under `/var/lib/snapd/snaps/`.

---

## 3. End-to-End Snap Lifecycle Verification

Every command required by the OS assessment was executed live and verified on the system:

### 3.1 Snap Store Query & Metadata Fetching
* **Command:** `snap info hello-world`
* **Output:**
  ```text
  name:      hello-world
  summary:   The 'hello-world' of snaps
  publisher: Canonical**
  store-url: https://snapcraft.io/hello-world
  snap-id:   buPKUD3TKqCOgLEjjHx5kSiCpIs5cMuQ
  ```
* **Result:** **PASS** (HTTPS TLS handshake with `api.snapcraft.io` verified).

### 3.2 Package Installation (`snap install`)
* **Command:** `sudo snap install hello-world`
* **Execution:** Downloaded assertions, mounted `snapd` (rev 28332), mounted `core` (rev 17292), and deployed `hello-world` (rev 29).
* **Result:** **PASS** (`hello-world 6.4 from Canonical** installed`).

### 3.3 Active Package Query (`snap list`)
* **Command:** `snap list`
* **Observed State:**
  ```text
  Name         Version             Rev    Tracking       Publisher    Notes
  core         16-2.61.4-20260225  17292  latest/stable  canonical**  core
  hello-world  6.4                 29     latest/stable  canonical**  -
  snapd        2.78                28332  latest/stable  canonical**  snapd
  ```
* **Result:** **PASS**.

### 3.4 Binary Execution Verification
* **Command:** `/snap/bin/hello-world`
* **Observed Output:**
  ```text
  Hello World!
  ```
* **Result:** **PASS** (Executed inside containerized runtime).

### 3.5 Package Update Check (`snap refresh`)
* **Command:** `sudo snap refresh hello-world`
* **Observed Output:**
  ```text
  snap "hello-world" has no updates available
  ```
* **Result:** **PASS** (Version parity verified with store channel).

### 3.6 Package Removal (`snap remove`)
* **Command:** `sudo snap remove hello-world`
* **Observed Output:**
  ```text
  hello-world removed (snap data snapshot saved)
  ```
* **Verification:** `snap list` confirmed only base runtimes (`core`, `snapd`) remain.
* **Result:** **PASS**.

---

## 4. Graphical Application Store (Snap Store GUI)

To fulfill the requirement for a functional graphical software center, **Integrate OS Software Center** was developed:
- **Source File:** `integrate-os/iso_builder/snap_store_gui.py`
- **Features:**
  - Modern desktop UI matching the Integrate OS dark theme.
  - Category filtering: Development, Utilities, Web & Media.
  - Interactive search querying the Snap catalog.
  - Real-time buttons for **Install Snap**, **Refresh All**, and **Remove**.
  - Background asynchronous task execution preventing UI freezes during network downloads.

---

## 5. Verification Test Matrix

| Test ID | Test Objective | Tested Command | Result |
|:---:|---|---|:---:|
| **SNAP-01** | Daemon Socket Availability | `systemctl is-active snapd.socket` | **PASS** |
| **SNAP-02** | Store API Connectivity | `snap info hello-world` | **PASS** |
| **SNAP-03** | Core Runtime Acquisition | `snap install core` | **PASS** |
| **SNAP-04** | Package Installation | `snap install hello-world` | **PASS** |
| **SNAP-05** | Package Inventory Query | `snap list` | **PASS** |
| **SNAP-06** | Package Binary Execution | `/snap/bin/hello-world` -> `"Hello World!"` | **PASS** |
| **SNAP-07** | Package Update / Refresh | `snap refresh hello-world` | **PASS** |
| **SNAP-08** | Package Removal & Cleanup | `snap remove hello-world` | **PASS** |
| **SNAP-09** | Graphical Store Interface | Launch `snap_store_gui.py` | **PASS** |

**Summary: 9 / 9 Tests PASS (100%).**
