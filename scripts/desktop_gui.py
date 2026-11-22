#!/usr/bin/env python3
"""
Rust Micro-OS v2.0 — Interactive Desktop GUI Simulator
Renders a macOS Ventura / Windows 11 Fluent hybrid desktop environment using Tkinter.

Features:
  • Gradient wallpaper (Deep Navy → Purple flow)
  • Translucent frosted top menu bar with system time, WiFi, battery
  • Floating bottom dock with 5 app icons (Browser, Terminal, TaskMgr, Finder, Settings)
  • Draggable, resizable windows with:
      - macOS traffic-light controls (🔴🟡🟢) with real close/minimize/maximize
      - Window shadows and rounded corner aesthetic
      - 5 fully functional app panels rendered inside each window
  • Network Navigator: live ping animation, NIC stats, HTTP document viewer
  • PowerTerminal: scrollable terminal with live kernel log stream
  • Activity Monitor: animated CPU waveform bar chart + process table
  • MicroFinder: sidebar file browser
  • System Settings: OS info card with specs
  • Animated network activity dots on the menu bar
  • Clock ticking every second in real-time
"""

import tkinter as tk
from tkinter import ttk, font
import threading
import time
import math
import random
from datetime import datetime

# ─── Color Palette (Windows 11 Light / Mica — Exact Match to User Laptop) ────
WALLPAPER_TOP    = "#E8ECEF"
WALLPAPER_MID    = "#EDF1F5"
WALLPAPER_BOT    = "#E2E7ED"
TASKBAR_BG       = "#F3F3F3"
TASKBAR_BORDER   = "#E0E0E0"
WIN_CHROME       = "#F3F3F3"
WIN_INACTIVE     = "#EBEBEB"
WIN_BORDER       = "#D5D5D5"
WIN_CONTENT_BG   = "#FFFFFF"
TEXT_PRIMARY     = "#1E1E1E"
TEXT_MUTED       = "#616161"
ACCENT_BLUE      = "#0078D4"
ACCENT_CYAN      = "#00A4EF"
ACCENT_GREEN     = "#107C41"
ACCENT_AMBER     = "#D83B01"
ACCENT_PURPLE    = "#8764B8"
WIN11_HOVER      = "#E5E5E5"
WIN11_CLOSE_HOVER= "#E81123"
SELECTION_BG     = "#CCE8FF"
BTN_CLOSE        = "#FF5F57"
BTN_MINIMIZE     = "#FFBD2E"
BTN_MAXIMIZE     = "#28C941"
BTN_INACTIVE     = "#B0B0B0"
MENUBAR_BG       = "#F3F3F3"
MENUBAR_TEXT     = "#1E1E1E"
DOCK_BG          = "#F3F3F3"
DOCK_BORDER      = "#E0E0E0"

class MicroOS(tk.Tk):
    """Root window hosting the entire Micro-OS desktop."""

    def __init__(self):
        super().__init__()
        self.title("Rust Micro-OS v2.0 — Windows 11 Fluent Desktop")
        self.geometry("1280x800")
        self.minsize(1024, 680)
        self.configure(bg="#E8ECEF")
        self.resizable(True, True)

        self.windows_list = []     # Active window widgets
        self.active_window = None
        self._drag_data = {}

        # Wi-Fi Subsystem State
        self.wifi_power = True
        self.wifi_connected = True
        self.wifi_ssid = "Jain_Student"
        self.wifi_ip = "192.168.1.142"
        self.wifi_signal = 92
        self.wifi_channel = "44"
        self.wifi_band = "5 GHz"
        self.wifi_bssid = "84:23:88:95:3d:ec"
        self.wifi_security = "Open / None"

        # Shell & System State
        self.boot_time = datetime.now()
        self.cwd = "/home/macha"
        self.cmd_history = []
        self.cmd_history_idx = 0

        # Snap Store Catalog
        self.snap_packages = {
            "neofetch": {
                "name": "neofetch",
                "version": "7.1.0",
                "category": "Utilities",
                "rating": "★★★★★ 4.9",
                "size": "1.2 MB",
                "summary": "Fast CLI system information tool with ASCII crab logo",
                "developer": "dylanaraps • stable",
                "icon": "🦀",
                "installed": True,
            },
            "htop": {
                "name": "htop",
                "version": "3.2.2",
                "category": "Development",
                "rating": "★★★★★ 4.8",
                "size": "2.8 MB",
                "summary": "Interactive real-time process viewer and system load monitor",
                "developer": "hishamhm • stable",
                "icon": "📊",
                "installed": True,
            },
            "wireguard": {
                "name": "wireguard",
                "version": "1.0.2",
                "category": "Networking",
                "rating": "★★★★★ 4.9",
                "size": "3.4 MB",
                "summary": "Fast, modern, secure cryptographic VPN & tunnel manager",
                "developer": "zx2c4 • stable",
                "icon": "🛡️",
                "installed": False,
            },
            "doom-micro": {
                "name": "doom-micro",
                "version": "1.9.0",
                "category": "Games & Fun",
                "rating": "★★★★★ 5.0",
                "size": "8.6 MB",
                "summary": "Classic 1993 retro raycaster game engine for Micro-OS",
                "developer": "idSoftware • stable",
                "icon": "👾",
                "installed": False,
            },
            "wireshark-lite": {
                "name": "wireshark-lite",
                "version": "4.0.1",
                "category": "Networking",
                "rating": "★★★★☆ 4.6",
                "size": "5.1 MB",
                "summary": "Lightweight 802.11 Wi-Fi & Ethernet packet capture analyzer",
                "developer": "combs • candidate",
                "icon": "🦈",
                "installed": False,
            },
            "vim-tiny": {
                "name": "vim-tiny",
                "version": "9.0.8",
                "category": "Development",
                "rating": "★★★★☆ 4.7",
                "size": "2.2 MB",
                "summary": "Vi IMproved - compact modal text editor with syntax color",
                "developer": "brammoolenaar • stable",
                "icon": "📝",
                "installed": False,
            },
            "speedtest-cli": {
                "name": "speedtest-cli",
                "version": "2.1.3",
                "category": "Networking",
                "rating": "★★★★☆ 4.5",
                "size": "1.6 MB",
                "summary": "Command line internet bandwidth, latency, and jitter tester",
                "developer": "sivel • stable",
                "icon": "🚀",
                "installed": False,
            },
            "snake-arcade": {
                "name": "snake-arcade",
                "version": "1.2.0",
                "category": "Games & Fun",
                "rating": "★★★★☆ 4.4",
                "size": "0.9 MB",
                "summary": "Retro arcade snake game with high scores and glowing colors",
                "developer": "retrodev • stable",
                "icon": "🐍",
                "installed": False,
            },
            "micro-calc": {
                "name": "micro-calc",
                "version": "2.0.0",
                "category": "Utilities",
                "rating": "★★★★☆ 4.6",
                "size": "1.1 MB",
                "summary": "Scientific and programmer calculator (Hex, Dec, Bin, Math)",
                "developer": "os-dev • stable",
                "icon": "🧮",
                "installed": True,
            },
            "docker-micro": {
                "name": "docker-micro",
                "version": "24.0.7",
                "category": "Development",
                "rating": "★★★★★ 4.8",
                "size": "9.4 MB",
                "summary": "Microkernel container daemon and lightweight OCI runner",
                "developer": "docker • edge",
                "icon": "🐳",
                "installed": False,
            },
            "rust-analyzer": {
                "name": "rust-analyzer",
                "version": "1.75.0",
                "category": "Development",
                "rating": "★★★★★ 5.0",
                "size": "12.8 MB",
                "summary": "Rust language server, LSP protocol compiler diagnostics",
                "developer": "rust-lang • stable",
                "icon": "⚙️",
                "installed": False,
            },
            "spotify-lite": {
                "name": "spotify-lite",
                "version": "1.0.4",
                "category": "Utilities",
                "rating": "★★★★☆ 4.5",
                "size": "4.2 MB",
                "summary": "Lo-fi synthwave ambient audio player and streamer",
                "developer": "music-dev • stable",
                "icon": "🎵",
                "installed": False,
            },
        }

        # Virtual File System (VFS)
        self.vfs = {
            "/": ["bin", "etc", "home", "system", "var"],
            "/bin": ["sh", "echo", "cat", "ls", "ps", "kill", "ping", "wifi", "curl", "neofetch", "snap", "calc", "clear", "uname", "whoami", "date", "uptime", "free"],
            "/etc": ["os-release", "resolv.conf", "hosts", "hostname", "wifi.conf"],
            "/home": ["macha", "guest"],
            "/home/macha": ["welcome.txt", "notes.md", "todo.list"],
            "/home/guest": ["readme.txt"],
            "/system": ["kernel.bin", "drivers"],
            "/system/drivers": ["virtio_net.sys", "wlan_80211ax.sys", "vga_fb.sys", "pit_timer.sys", "uart16550.sys"],
            "/var": ["log", "snap"],
            "/var/log": ["boot.log", "wifi.log", "kernel.log"],
            "/var/snap": []
        }
        self.vfs_files = {
            "/etc/os-release": "NAME=\"Rust Micro-OS\"\nVERSION=\"2.0.0\"\nID=micro-os\nPRETTY_NAME=\"Rust Micro-OS 2.0 (x86_64 Fluent Desktop)\"\nHOME_URL=\"https://github.com/micro-os/rust-micro-os\"",
            "/etc/resolv.conf": "nameserver 8.8.8.8\nnameserver 1.1.1.1",
            "/etc/hosts": "127.0.0.1   localhost micro-os\n192.168.1.142 micro-os-x86\n192.168.1.1   router.gateway",
            "/etc/hostname": "micro-os-x86",
            "/etc/wifi.conf": "interface=wlan0\nssid=\"Home-Fiber-5G\"\nproto=WPA3-SAE\nkey_mgmt=WPA-PSK\npairwise=CCMP",
            "/home/macha/welcome.txt": "Welcome to your custom Micro-OS, Macha!\nBuilt with 100% Rust microkernel, macOS & Windows 11 Fluent UI, Wi-Fi 802.11ax scanner, and full Snap Store.",
            "/home/macha/notes.md": "# Quick Notes\n- Microkernel round robin & priority aging running smoothly.\n- Wi-Fi wlan0 associated with Home-Fiber-5G.\n- Snap store active with 12 packages available.",
            "/home/macha/todo.list": "[x] Build Microkernel in Rust\n[x] Implement macOS/Win11 GUI & Dock\n[x] Add 802.11 Wi-Fi Scanner & 4-Way Handshake\n[x] Add Snap Store\n[x] Make all terminal commands work",
            "/home/guest/readme.txt": "Guest access is read-only. Run 'whoami' to verify permissions.",
            "/var/log/boot.log": "[BOOT] CPU self-test OK\n[BOOT] Memory 64KiB heap initialized\n[BOOT] PIT 100Hz online\n[NET] virtio-net0 online 192.168.1.142\n[WIFI] wlan0 802.11ax associated\n[GUI] 32bpp compositor mounted",
            "/var/log/wifi.log": "[WIFI] Scanning channels 1..165\n[WIFI] Found 6 APs\n[WPA2] 4-way handshake completed\n[DHCP] Lease 192.168.1.142 ack",
            "/var/log/kernel.log": "[KERNEL] Scheduler: 6 tasks dispatched\n[KERNEL] Zero crashes. 9/9 verification tests passed."
        }

        # Windows 11 State
        self.start_menu_visible = False
        self.start_menu = None
        self.wifi_flyout_visible = False
        self.wifi_flyout = None

        # Build layers (Windows 11 Fluent Desktop)
        self._build_wallpaper()
        self._build_taskbar()
        self._build_start_menu()
        self._build_wifi_flyout()

        # Open default windows
        self.after(100, self._open_terminal)
        self.after(400, self._open_snap_store)
        self.after(700, self._open_wifi_manager)

        # Start clock & telemetry
        self._tick_clock()

    def _resolve_path(self, path):
        """Resolves absolute, relative (~, .., .) virtual filesystem paths."""
        if not path or path in (".", ""):
            return self.cwd
        if path == "~":
            return "/home/macha"
        if path.startswith("~/"):
            path = "/home/macha/" + path[2:]
        elif not path.startswith("/"):
            path = self.cwd.rstrip("/") + "/" + path
        
        # Normalize double slashes and resolve . and ..
        parts = [p for p in path.split("/") if p and p != "."]
        stack = []
        for p in parts:
            if p == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(p)
        return "/" + "/".join(stack)

    def scan_device_wifi(self):
        """Scans the physical host Windows Wi-Fi adapter for real available networks."""
        discovered = []
        host_ssid = "Jain_Student"
        host_signal = 92
        host_band = "5 GHz"
        host_channel = "44"
        host_bssid = "84:23:88:95:3d:ec"
        host_sec = "Open / None"

        # 1. Query active host connection via netsh
        try:
            import subprocess
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                stderr=subprocess.STDOUT, text=True, timeout=3
            )
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("SSID") and not line.startswith("BSSID"):
                    val = line.split(":", 1)[1].strip()
                    if val:
                        host_ssid = val
                elif line.startswith("Signal"):
                    val = line.split(":", 1)[1].strip().replace("%", "")
                    if val.isdigit():
                        host_signal = int(val)
                elif line.startswith("Band"):
                    host_band = line.split(":", 1)[1].strip()
                elif line.startswith("Channel") and "Utilization" not in line:
                    ch = line.split(":", 1)[1].strip()
                    if ch.isdigit():
                        host_channel = ch
                elif line.startswith("Authentication"):
                    host_sec = line.split(":", 1)[1].strip()
                elif line.startswith("AP BSSID"):
                    host_bssid = line.split(":", 1)[1].strip()
        except Exception:
            pass

        if host_ssid:
            self.wifi_ssid = host_ssid
            self.wifi_signal = host_signal
            self.wifi_band = host_band
            self.wifi_channel = host_channel
            self.wifi_security = host_sec
            self.wifi_bssid = host_bssid
            self.wifi_connected = True
            discovered.append({
                "signal_icon": "📶 4b",
                "ssid": host_ssid,
                "security": host_sec,
                "channel": host_channel,
                "band": host_band,
                "signal": f"{host_signal}%",
                "status": "Connected",
                "tag": "connected",
                "bssid": host_bssid
            })

        # 2. Query all visible networks via netsh
        try:
            import subprocess
            net_out = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                stderr=subprocess.STDOUT, text=True, timeout=3
            )
            curr = {}
            for line in net_out.splitlines():
                line = line.strip()
                if line.startswith("SSID "):
                    if curr and curr.get("ssid") and curr["ssid"] != host_ssid:
                        discovered.append(curr)
                    s_name = line.split(":", 1)[1].strip()
                    curr = {
                        "signal_icon": "📶 3b",
                        "ssid": s_name,
                        "security": "Open",
                        "channel": "6",
                        "band": "2.4 GHz",
                        "signal": "75%",
                        "status": "Available",
                        "tag": "available",
                        "bssid": "Auto"
                    }
                elif line.startswith("Authentication"):
                    curr["security"] = line.split(":", 1)[1].strip()
                elif line.startswith("Signal"):
                    sig_val = line.split(":", 1)[1].strip()
                    curr["signal"] = sig_val
                    int_sig = int(sig_val.replace("%", "")) if sig_val.replace("%", "").isdigit() else 70
                    curr["signal_icon"] = "📶 4b" if int_sig >= 80 else ("📶 3b" if int_sig >= 60 else "📶 2b")
                elif line.startswith("Band"):
                    curr["band"] = line.split(":", 1)[1].strip()
                elif line.startswith("Channel") and "Utilization" not in line:
                    ch_val = line.split(":", 1)[1].strip()
                    if ch_val.isdigit():
                        curr["channel"] = ch_val
            if curr and curr.get("ssid") and curr["ssid"] != host_ssid:
                discovered.append(curr)
        except Exception:
            pass

        # Also merge known campus / hotspot APs so list is rich and realistic
        sample_extras = [
            {"signal_icon": "📶 4b", "ssid": "Jain_Faculty",   "security": "WPA2-Enterprise", "channel": "36", "band": "5 GHz",   "signal": "88%", "status": "Available", "tag": "available", "bssid": "84:23:88:95:3d:ed"},
            {"signal_icon": "📶 3b", "ssid": "eduroam",        "security": "802.1X WPA3",     "channel": "40", "band": "5 GHz",   "signal": "76%", "status": "Available", "tag": "available", "bssid": "84:23:88:95:3d:ee"},
            {"signal_icon": "📶 3b", "ssid": "Jain_Guest",      "security": "Open / None",     "channel": "11", "band": "2.4 GHz", "signal": "68%", "status": "Available", "tag": "available", "bssid": "84:23:88:95:3d:ef"},
            {"signal_icon": "📶 2b", "ssid": "AndroidHotspot",  "security": "WPA2-Personal",  "channel": "6",  "band": "2.4 GHz", "signal": "58%", "status": "Available", "tag": "available", "bssid": "52:54:00:12:88:99"},
            {"signal_icon": "📶 2b", "ssid": "iPhone-Hotspot",  "security": "WPA2-Personal",  "channel": "149", "band": "5 GHz",   "signal": "45%", "status": "Available", "tag": "available", "bssid": "66:55:44:33:22:11"},
        ]
        for item in sample_extras:
            if not any(d["ssid"] == item["ssid"] for d in discovered):
                discovered.append(item)

        return discovered

    # ─── Wallpaper ────────────────────────────────────────────────────────────

    def _build_wallpaper(self):
        self.wallpaper = tk.Canvas(self, highlightthickness=0, bd=0, bg="#E8ECEF")
        self.wallpaper.place(x=0, y=0, relwidth=1, relheight=1)
        self.wallpaper.bind("<Configure>", self._redraw_wallpaper)
        self._redraw_wallpaper(None)

    def _redraw_wallpaper(self, _event):
        self.wallpaper.delete("all")
        w = self.winfo_width() or 1280
        h = self.winfo_height() or 800
        steps = 100
        # Smooth Windows 11 light silver/mica gradient
        for i in range(steps):
            t = i / steps
            r = int(232 + (237 - 232) * t)
            g = int(236 + (241 - 236) * t)
            b = int(239 + (245 - 239) * t)
            y0 = int(i * h / steps)
            y1 = int((i + 1) * h / steps) + 1
            self.wallpaper.create_rectangle(0, y0, w, y1,
                fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

        # Central delicate Windows 11 Bloom petals in azure blues
        cx, cy = w // 2, h // 2 - 20
        petals = [
            (260, "#0078D4", "gray25"),
            (210, "#2B88D8", "gray25"),
            (160, "#00A4EF", "gray50"),
            (110, "#60CDFF", "gray50"),
            (60,  "#A4D8FD", ""),
        ]
        for r_val, color, stip in petals:
            self.wallpaper.create_oval(
                cx - r_val, cy - int(r_val * 0.72), cx + r_val, cy + int(r_val * 0.72),
                fill=color, outline="", stipple=stip
            )

    # ─── Windows 11 Light Taskbar ────────────────────────────────────────────

    def _build_taskbar(self):
        self.taskbar = tk.Frame(self, bg="#F3F3F3", height=48,
                                highlightbackground="#E0E0E0", highlightthickness=1)
        self.taskbar.place(x=0, y=self.winfo_height() - 48, relwidth=1, height=48)
        self.taskbar.lift()
        self.bind("<Configure>", self._reposition_taskbar)

        # ── Left: Weather Widget (Exact match to user's laptop photo!) ────────
        weather_frame = tk.Frame(self.taskbar, bg="#F3F3F3", cursor="hand2")
        weather_frame.pack(side=tk.LEFT, padx=12, pady=4)
        tk.Label(weather_frame, text="☀️", bg="#F3F3F3", font=("Segoe UI Emoji", 14)).pack(side=tk.LEFT, padx=(0, 6))
        w_sub = tk.Frame(weather_frame, bg="#F3F3F3")
        w_sub.pack(side=tk.LEFT)
        tk.Label(w_sub, text="24°C", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(w_sub, text="Sunny", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 8)).pack(anchor="w")

        # ── Center: Windows 11 Start, Search, and Centered App Icons ──────────
        self.center_taskbar = tk.Frame(self.taskbar, bg="#F3F3F3")
        self.center_taskbar.place(relx=0.5, rely=0.5, anchor="center")

        # 🪟 Windows 11 Blue Start Button
        self.start_btn = tk.Label(self.center_taskbar, text="🪟", bg="#F3F3F3", fg="#0078D4",
                                  font=("Segoe UI Emoji", 16), width=3, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=2)
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.configure(bg="#E5E5E5"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.configure(bg="#F3F3F3"))
        self.start_btn.bind("<Button-1>", lambda e: self._toggle_start_menu())

        # 🔍 Search Bar Pill (Clean white capsule with subtle border)
        search_box = tk.Frame(self.center_taskbar, bg="#FFFFFF", cursor="hand2", padx=10, pady=4,
                              highlightbackground="#D5D5D5", highlightthickness=1)
        search_box.pack(side=tk.LEFT, padx=4)
        tk.Label(search_box, text="🔍", bg="#FFFFFF", fg="#606060", font=("Segoe UI Emoji", 10)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(search_box, text="Search", bg="#FFFFFF", fg="#424242", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 16))
        search_box.bind("<Button-1>", lambda e: self._toggle_start_menu())

        # Centered App Icons:
        TASKBAR_APPS = [
            ("⌨", "Terminal",   self._open_terminal),
            ("🌊", "Browser",    self._open_browser),
            ("📁", "Explorer",   self._open_finder),
            ("📊", "TaskMgr",    self._open_taskmanager),
            ("🛍️", "Snap Store", self._open_snap_store),
            ("🧮", "Calc",       self._open_calculator),
            ("⚙️", "Settings",   self._open_settings),
            ("🎮", "Snake",      self._open_snake_game),
            ("👾", "Doom",       self._open_doom_viewer),
        ]

        self.taskbar_widgets = {}
        for icon, name, cmd in TASKBAR_APPS:
            col = tk.Frame(self.center_taskbar, bg="#F3F3F3", cursor="hand2", padx=4, pady=2)
            col.pack(side=tk.LEFT, padx=1)

            lbl = tk.Label(col, text=icon, bg="#F3F3F3", fg="#1E1E1E",
                           font=("Segoe UI Emoji", 16), width=2, height=1)
            lbl.pack(pady=(2, 0))

            indicator = tk.Frame(col, bg="#0078D4", height=3, width=14)
            indicator.pack(pady=(2, 1))

            def make_handler(c=cmd, col_f=col, l=lbl):
                def _enter(e): col_f.configure(bg="#E5E5E5"); l.configure(bg="#E5E5E5")
                def _leave(e): col_f.configure(bg="#F3F3F3"); l.configure(bg="#F3F3F3")
                def _click(e): c()
                col_f.bind("<Enter>", _enter)
                col_f.bind("<Leave>", _leave)
                col_f.bind("<Button-1>", _click)
                l.bind("<Button-1>", _click)
            make_handler()
            self.taskbar_widgets[name] = {"col": col, "ind": indicator}

        # ── Right: System Tray & Notification Area ────────────────────────────
        tray = tk.Frame(self.taskbar, bg="#F3F3F3")
        tray.pack(side=tk.RIGHT, padx=6)

        tk.Label(tray, text="⌃", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=3)

        # Language: ENG over IN (Matching user's laptop photo!)
        lang_box = tk.Frame(tray, bg="#F3F3F3", padx=2)
        lang_box.pack(side=tk.LEFT, padx=3)
        tk.Label(lang_box, text="ENG", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI", 8, "bold")).pack(anchor="center")
        tk.Label(lang_box, text="IN", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 7)).pack(anchor="center")

        # Quick Settings Cluster (Wi-Fi + Volume + Battery)
        qs_cluster = tk.Frame(tray, bg="#F3F3F3", cursor="hand2", padx=6, pady=4,
                              highlightbackground="#E0E0E0", highlightthickness=0)
        qs_cluster.pack(side=tk.LEFT, padx=3)
        self.tray_wifi_icon = tk.Label(qs_cluster, text="📶", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11))
        self.tray_wifi_icon.pack(side=tk.LEFT, padx=2)
        tk.Label(qs_cluster, text="🔊", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=2)
        tk.Label(qs_cluster, text="🔋", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=2)

        def _qs_enter(e):
            qs_cluster.configure(bg="#E5E5E5")
            for ch in qs_cluster.winfo_children(): ch.configure(bg="#E5E5E5")
        def _qs_leave(e):
            qs_cluster.configure(bg="#F3F3F3")
            for ch in qs_cluster.winfo_children(): ch.configure(bg="#F3F3F3")

        qs_cluster.bind("<Enter>", _qs_enter)
        qs_cluster.bind("<Leave>", _qs_leave)
        qs_cluster.bind("<Button-1>", lambda e: self._toggle_wifi_flyout())
        for ch in qs_cluster.winfo_children():
            ch.bind("<Button-1>", lambda e: self._toggle_wifi_flyout())

        # Two-line Digital Clock & Date
        clock_box = tk.Frame(tray, bg="#F3F3F3", padx=6)
        clock_box.pack(side=tk.LEFT, padx=2)
        self.clock_time_lbl = tk.Label(clock_box, text="15:48", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI", 9))
        self.clock_time_lbl.pack(anchor="e")
        self.clock_date_lbl = tk.Label(clock_box, text="21-11-2026", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 8))
        self.clock_date_lbl.pack(anchor="e")

        # Notification Bell
        tk.Label(tray, text="🔔", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=4)

        # Show Desktop Strip on far right
        show_dt = tk.Frame(tray, bg="#D5D5D5", width=2, height=32, cursor="hand2")
        show_dt.pack(side=tk.LEFT, padx=(4, 0))
        show_dt.bind("<Button-1>", lambda e: [w.place_forget() for w in self.windows_list])

    def _reposition_taskbar(self, _event=None):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        if hasattr(self, "taskbar"):
            self.taskbar.place(x=0, y=h - 48, relwidth=1, height=48)
            self.taskbar.lift()

    def _tick_clock(self):
        now = datetime.now()
        t_str = now.strftime("%H:%M")
        d_str = now.strftime("%d-%m-%Y")
        if hasattr(self, "clock_time_lbl"):
            self.clock_time_lbl.configure(text=t_str)
        if hasattr(self, "clock_date_lbl"):
            self.clock_date_lbl.configure(text=d_str)
        self.after(1000, self._tick_clock)

    # ─── Windows 11 Light Start Menu ─────────────────────────────────────────

    def _build_start_menu(self):
        self.start_menu = tk.Frame(self, bg="#FBFBFB",
                                   highlightbackground="#D0D0D0", highlightthickness=1)
        self.start_menu_w = 560
        self.start_menu_h = 520

        # Top Search Box
        s_box = tk.Frame(self.start_menu, bg="#FFFFFF", padx=10, pady=8,
                         highlightbackground="#D5D5D5", highlightthickness=1)
        s_box.pack(fill=tk.X, padx=20, pady=(20, 14))
        tk.Label(s_box, text="🔍", bg="#FFFFFF", fg="#606060", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(s_box, text="Type here to search", bg="#FFFFFF", fg="#888888", font=("Segoe UI", 10)).pack(side=tk.LEFT)

        # "Pinned" Header
        p_hdr = tk.Frame(self.start_menu, bg="#FBFBFB")
        p_hdr.pack(fill=tk.X, padx=24, pady=(4, 8))
        tk.Label(p_hdr, text="Pinned", bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        all_btn = tk.Label(p_hdr, text="All apps >", bg="#FBFBFB", fg="#0078D4", font=("Segoe UI", 9), cursor="hand2")
        all_btn.pack(side=tk.RIGHT)

        # Pinned Apps 3x3 Grid
        grid_frame = tk.Frame(self.start_menu, bg="#FBFBFB")
        grid_frame.pack(fill=tk.BOTH, padx=20, pady=4)

        PINNED = [
            ("⌨", "Terminal",      self._open_terminal),
            ("🌊", "Edge Browser",  self._open_browser),
            ("📁", "File Explorer", self._open_finder),
            ("📊", "Task Manager",  self._open_taskmanager),
            ("🛍️", "Snap Store",    self._open_snap_store),
            ("🧮", "Calculator",    self._open_calculator),
            ("⚙️", "Settings",      self._open_settings),
            ("🎮", "Snake Arcade",  self._open_snake_game),
            ("👾", "Doom Micro",    self._open_doom_viewer),
        ]

        for i, (icon, name, cmd) in enumerate(PINNED):
            r = i // 3
            c = i % 3
            item = tk.Frame(grid_frame, bg="#FBFBFB", cursor="hand2", padx=8, pady=8)
            item.grid(row=r, column=c, padx=6, pady=4, sticky="nsew")

            ico_lbl = tk.Label(item, text=icon, bg="#FBFBFB", font=("Segoe UI Emoji", 20))
            ico_lbl.pack()
            txt_lbl = tk.Label(item, text=name, bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 9))
            txt_lbl.pack(pady=(2, 0))

            def make_pinned_click(c=cmd, f=item, l1=ico_lbl, l2=txt_lbl):
                def _e(ev): [w.configure(bg="#EAEAEA") for w in (f, l1, l2)]
                def _l(ev): [w.configure(bg="#FBFBFB") for w in (f, l1, l2)]
                def _c(ev): self._toggle_start_menu(); c()
                for w in (f, l1, l2):
                    w.bind("<Enter>", _e)
                    w.bind("<Leave>", _l)
                    w.bind("<Button-1>", _c)
            make_pinned_click()
            grid_frame.columnconfigure(c, weight=1)

        # "Recommended" Header
        r_hdr = tk.Frame(self.start_menu, bg="#FBFBFB")
        r_hdr.pack(fill=tk.X, padx=24, pady=(16, 6))
        tk.Label(r_hdr, text="Recommended", bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        rec_box = tk.Frame(self.start_menu, bg="#FBFBFB")
        rec_box.pack(fill=tk.X, padx=20, pady=2)

        RECS = [
            ("📄", "welcome.txt", "Modified 2h ago"),
            ("📄", "notes.md", "Modified 3h ago"),
        ]
        for ico, title, desc in RECS:
            rf = tk.Frame(rec_box, bg="#FBFBFB", padx=6, pady=4, cursor="hand2")
            rf.pack(fill=tk.X, pady=1)
            tk.Label(rf, text=ico, bg="#FBFBFB", font=("Segoe UI Emoji", 12)).pack(side=tk.LEFT, padx=(0, 8))
            sub = tk.Frame(rf, bg="#FBFBFB")
            sub.pack(side=tk.LEFT)
            tk.Label(sub, text=title, bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(sub, text=desc, bg="#FBFBFB", fg="#616161", font=("Segoe UI", 8)).pack(anchor="w")

        # Bottom Profile Bar
        prof_bar = tk.Frame(self.start_menu, bg="#EFEFEF", height=50)
        prof_bar.pack(side=tk.BOTTOM, fill=tk.X)
        prof_bar.pack_propagate(False)

        user_box = tk.Frame(prof_bar, bg="#EFEFEF", padx=14, pady=6)
        user_box.pack(side=tk.LEFT)
        tk.Label(user_box, text="👤", bg="#EFEFEF", font=("Segoe UI Emoji", 14)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(user_box, text="macha", bg="#EFEFEF", fg="#1E1E1E", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        power_btn = tk.Label(prof_bar, text="⏻", bg="#EFEFEF", fg="#1E1E1E", font=("Segoe UI", 14), cursor="hand2", padx=16)
        power_btn.pack(side=tk.RIGHT)
        power_btn.bind("<Button-1>", lambda e: self.destroy())

    def _toggle_start_menu(self):
        if not hasattr(self, "start_menu"):
            return
        if self.start_menu_visible:
            self.start_menu.place_forget()
            self.start_menu_visible = False
        else:
            if getattr(self, "wifi_flyout_visible", False):
                self._toggle_wifi_flyout()
            sw = self.winfo_width()
            sh = self.winfo_height()
            mx = (sw - self.start_menu_w) // 2
            my = sh - 48 - self.start_menu_h - 10
            self.start_menu.place(x=mx, y=my, width=self.start_menu_w, height=self.start_menu_h)
            self.start_menu.lift()
            self.start_menu_visible = True

    # ─── Windows 11 Wi-Fi Quick Settings Flyout (Exact Replica) ──────────────

    def _build_wifi_flyout(self):
        self.wifi_flyout = tk.Frame(self, bg="#FBFBFB",
                                    highlightbackground="#D0D0D0", highlightthickness=1)
        self.wifi_flyout_w = 380
        self.wifi_flyout_h = 500

        # Header: "Wi-Fi" + [ ● ON ] toggle pill
        top = tk.Frame(self.wifi_flyout, bg="#FBFBFB", height=44)
        top.pack(fill=tk.X, padx=16, pady=(14, 6))
        tk.Label(top, text="Wi-Fi", bg="#FBFBFB", fg="#1E1E1E",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        self.fly_power_btn = tk.Button(top, text="●  ON", bg="#0078D4", fg="#FFFFFF",
                                       font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=2,
                                       cursor="hand2", bd=0)
        self.fly_power_btn.pack(side=tk.RIGHT)

        def toggle_wifi_power():
            self.wifi_power = not self.wifi_power
            if self.wifi_power:
                self.fly_power_btn.configure(text="●  ON", bg="#0078D4", fg="#FFFFFF")
                self.wifi_connected = True
            else:
                self.fly_power_btn.configure(text="○  OFF", bg="#E0E0E0", fg="#606060")
                self.wifi_connected = False
            self._refresh_wifi_flyout()

        self.fly_power_btn.configure(command=toggle_wifi_power)

        # Connected Card (Pure White with Subtle Border)
        self.fly_conn_card = tk.Frame(self.wifi_flyout, bg="#FFFFFF", padx=12, pady=10,
                                      highlightbackground="#E2E2E2", highlightthickness=1)
        self.fly_conn_card.pack(fill=tk.X, padx=14, pady=6)

        c_top = tk.Frame(self.fly_conn_card, bg="#FFFFFF")
        c_top.pack(fill=tk.X)
        self.fly_conn_icon = tk.Label(c_top, text="📶", bg="#FFFFFF", fg="#0078D4", font=("Segoe UI Emoji", 14))
        self.fly_conn_icon.pack(side=tk.LEFT, padx=(0, 8))
        self.fly_conn_ssid = tk.Label(c_top, text=self.wifi_ssid, bg="#FFFFFF", fg="#1E1E1E",
                                      font=("Segoe UI", 11, "bold"))
        self.fly_conn_ssid.pack(side=tk.LEFT)

        self.fly_conn_sub = tk.Label(self.fly_conn_card,
                                     text=f"Connected, open  •  {self.wifi_band} (Ch {self.wifi_channel})  •  {self.wifi_signal}%",
                                     bg="#FFFFFF", fg="#107C41", font=("Segoe UI", 9))
        self.fly_conn_sub.pack(anchor="w", padx=26, pady=(2, 6))

        c_bottom = tk.Frame(self.fly_conn_card, bg="#FFFFFF")
        c_bottom.pack(fill=tk.X)
        tk.Label(c_bottom, text="Intel(R) Wi-Fi 6 AX203", bg="#FFFFFF", fg="#888888", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        self.fly_disc_btn = tk.Button(c_bottom, text="Disconnect", bg="#F4F4F4", fg="#C42B1C",
                                      font=("Segoe UI", 9), relief="flat", padx=12, pady=2, cursor="hand2", bd=1)
        self.fly_disc_btn.pack(side=tk.RIGHT)

        def _do_disconnect():
            if self.wifi_connected:
                self.wifi_connected = False
                self.fly_conn_sub.configure(text="Disconnected", fg="#C42B1C")
                self.fly_disc_btn.configure(text="Connect", fg="#0078D4")
            else:
                self.wifi_connected = True
                self.fly_conn_sub.configure(text=f"Connected, open  •  {self.wifi_band} (Ch {self.wifi_channel})  •  {self.wifi_signal}%", fg="#107C41")
                self.fly_disc_btn.configure(text="Disconnect", fg="#C42B1C")
            self._refresh_wifi_flyout()

        self.fly_disc_btn.configure(command=_do_disconnect)

        # "Available networks" Header
        tk.Label(self.wifi_flyout, text="Available networks", bg="#FBFBFB", fg="#616161",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(10, 4))

        # Scrollable networks frame
        canvas = tk.Canvas(self.wifi_flyout, bg="#FBFBFB", highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.wifi_flyout, orient="vertical", command=canvas.yview)
        self.fly_net_list = tk.Frame(canvas, bg="#FBFBFB")

        self.fly_net_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        c_win = canvas.create_window((0, 0), window=self.fly_net_list, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(c_win, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0), pady=(0, 42))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 14), pady=(0, 42))

        # Bottom Bar: Scan & More Settings
        b_bar = tk.Frame(self.wifi_flyout, bg="#EFEFEF", height=38)
        b_bar.pack(side=tk.BOTTOM, fill=tk.X)
        b_bar.pack_propagate(False)

        scan_btn = tk.Button(b_bar, text="🔄  Scan for networks", bg="#EFEFEF", fg="#0078D4",
                             font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2",
                             command=self._refresh_wifi_flyout)
        scan_btn.pack(side=tk.LEFT, padx=14, pady=6)

        adv_btn = tk.Label(b_bar, text="More Wi-Fi settings", bg="#EFEFEF", fg="#616161",
                           font=("Segoe UI", 9), cursor="hand2")
        adv_btn.pack(side=tk.RIGHT, padx=14, pady=6)
        adv_btn.bind("<Button-1>", lambda e: (self._toggle_wifi_flyout(), self._open_wifi_manager()))

    def _refresh_wifi_flyout(self):
        for widget in self.fly_net_list.winfo_children():
            widget.destroy()

        networks = self.scan_device_wifi()
        for net in networks:
            is_curr = (net["ssid"] == self.wifi_ssid and self.wifi_connected)
            row = tk.Frame(self.fly_net_list, bg="#FFFFFF", padx=10, pady=7, cursor="hand2",
                           highlightbackground="#EAEAEA", highlightthickness=1)
            row.pack(fill=tk.X, pady=2)

            ico = tk.Label(row, text=net.get("signal_icon", "📶"), bg="#FFFFFF", font=("Segoe UI Emoji", 12))
            ico.pack(side=tk.LEFT, padx=(0, 8))

            name_lbl = tk.Label(row, text=net["ssid"], bg="#FFFFFF",
                                fg="#107C41" if is_curr else "#1E1E1E",
                                font=("Segoe UI", 10, "bold" if is_curr else "normal"))
            name_lbl.pack(side=tk.LEFT)

            stat_txt = "Connected" if is_curr else f"{net.get('signal', '80%')} • {net.get('band', '5 GHz')}"
            stat_lbl = tk.Label(row, text=stat_txt, bg="#FFFFFF", fg="#616161", font=("Segoe UI", 8))
            stat_lbl.pack(side=tk.RIGHT)

            def make_row_click(s_name=net["ssid"], sec=net.get("security", "Open"), row_f=row, n_lbl=name_lbl, st_lbl=stat_lbl, i_lbl=ico):
                def _enter(ev):
                    for w in (row_f, n_lbl, st_lbl, i_lbl): w.configure(bg="#F0F4F9")
                def _leave(ev):
                    for w in (row_f, n_lbl, st_lbl, i_lbl): w.configure(bg="#FFFFFF")
                def _click(ev):
                    self.wifi_ssid = s_name
                    self.wifi_security = sec
                    self.wifi_connected = True
                    self.fly_conn_ssid.configure(text=s_name)
                    self.fly_conn_sub.configure(text=f"Connected, secured ({sec})", fg="#107C41")
                    self._refresh_wifi_flyout()
                row_f.bind("<Enter>", _enter)
                row_f.bind("<Leave>", _leave)
                row_f.bind("<Button-1>", _click)
                for w in (n_lbl, st_lbl, i_lbl):
                    w.bind("<Enter>", _enter)
                    w.bind("<Leave>", _leave)
                    w.bind("<Button-1>", _click)
            make_row_click()

    def _toggle_wifi_flyout(self):
        if not hasattr(self, "wifi_flyout"):
            return
        if self.wifi_flyout_visible:
            self.wifi_flyout.place_forget()
            self.wifi_flyout_visible = False
        else:
            if getattr(self, "start_menu_visible", False):
                self._toggle_start_menu()
            sw = self.winfo_width()
            sh = self.winfo_height()
            mx = sw - self.wifi_flyout_w - 12
            my = sh - 48 - self.wifi_flyout_h - 10
            self.wifi_flyout.place(x=mx, y=my, width=self.wifi_flyout_w, height=self.wifi_flyout_h)
            self.wifi_flyout.lift()
            self.wifi_flyout_visible = True
            self._refresh_wifi_flyout()

    # ─── Windows 11 Window Factory ───────────────────────────────────────────

    def _make_window(self, title, width, height, offset_x=80, offset_y=60):
        # Creates a floating, draggable Windows 11 Fluent Light window frame.
        stagger = len(self.windows_list) * 28
        wx = offset_x + stagger
        wy = offset_y + stagger

        win = tk.Frame(self, bg="#F3F3F3", bd=0,
                       highlightbackground="#D5D5D5", highlightthickness=1)
        win.place(x=wx, y=wy, width=width, height=height)
        win.lift()
        self.windows_list.append(win)
        self.active_window = win

        # ── Windows 11 Titlebar ─────────────────────────────────────────────
        tbar = tk.Frame(win, bg="#F3F3F3", height=34)
        tbar.pack(fill=tk.X)
        tbar.pack_propagate(False)

        # Title & App Icon on LEFT
        title_box = tk.Frame(tbar, bg="#F3F3F3")
        title_box.pack(side=tk.LEFT, padx=12)

        win.title_lbl = tk.Label(title_box, text=title, bg="#F3F3F3", fg="#1E1E1E",
                                 font=("Segoe UI", 10, "bold"))
        win.title_lbl.pack(side=tk.LEFT)

        # Windows 11 Caption Buttons on RIGHT: [ ─ ] [ □ ] [ ✕ ]
        controls_frame = tk.Frame(tbar, bg="#F3F3F3")
        controls_frame.pack(side=tk.RIGHT)

        def make_caption_btn(sym, hover_bg, hover_fg, cmd):
            lbl = tk.Label(controls_frame, text=sym, bg="#F3F3F3", fg="#404040",
                           font=("Segoe UI", 10), width=4, height=1, cursor="hand2")
            lbl.pack(side=tk.LEFT)
            lbl.bind("<Enter>", lambda e: lbl.configure(bg=hover_bg, fg=hover_fg))
            lbl.bind("<Leave>", lambda e: lbl.configure(bg="#F3F3F3", fg="#404040"))
            lbl.bind("<Button-1>", lambda e: cmd())
            return lbl

        # Minimize
        make_caption_btn("─", "#E5E5E5", "#000000", lambda: win.place_forget())
        # Maximize
        make_caption_btn("□", "#E5E5E5", "#000000", lambda: self._toggle_maximize(win))
        # Close (Windows 11 red hover)
        make_caption_btn("✕", "#E81123", "#FFFFFF", lambda: self._close_window(win))

        # ── Content Frame ─────────────────────────────────────────────────
        content = tk.Frame(win, bg="#FFFFFF")
        content.pack(fill=tk.BOTH, expand=True)

        # ── Drag logic ───────────────────────────────────────────────────
        def start_drag(e):
            self.active_window = win
            win.lift()
            self._drag_data = {"x": e.x, "y": e.y}

        def do_drag(e):
            info = win.place_info()
            nx = int(info["x"]) + (e.x - self._drag_data["x"])
            ny = int(info["y"]) + (e.y - self._drag_data["y"])
            ny = max(0, ny)
            win.place(x=nx, y=ny)

        tbar.bind("<Button-1>", start_drag)
        tbar.bind("<B1-Motion>", do_drag)
        win.title_lbl.bind("<Button-1>", start_drag)
        win.title_lbl.bind("<B1-Motion>", do_drag)

        return win, content

    def _close_window(self, win):
        if win in self.windows_list:
            win.destroy()
            self.windows_list.remove(win)

    _maximized_state = {}

    def _toggle_maximize(self, win):
        if win in self._maximized_state:
            prev = self._maximized_state.pop(win)
            win.place(x=prev["x"], y=prev["y"],
                      width=prev["w"], height=prev["h"])
        else:
            info = win.place_info()
            self._maximized_state[win] = {
                "x": int(info["x"]), "y": int(info["y"]),
                "w": int(info["width"]), "h": int(info["height"])
            }
            win.place(x=0, y=0, width=self.winfo_width(),
                      height=self.winfo_height() - 48)

    # ─── App 1: Network Navigator (Browser) ───────────────────────────────────

    def _open_browser(self):
        win, content = self._make_window(
            "🌐  Network Navigator — Rust Micro-OS",
            900, 580, offset_x=70, offset_y=50)

        # URL/toolbar row
        toolbar = tk.Frame(content, bg=WIN_CHROME, height=42)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="  ←  →  ↺ ", bg=WIN_CHROME,
                 fg=TEXT_MUTED, font=("SF Pro Display", 13)).pack(side=tk.LEFT, padx=4)

        url_var = tk.StringVar(value="http://micro.os/welcome")
        url_bar = tk.Entry(toolbar, textvariable=url_var, bg="#2A2D3A",
                           fg=ACCENT_BLUE, font=("SF Pro Mono", 11),
                           relief="flat", bd=4, insertbackground=TEXT_PRIMARY)
        url_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)

        ping_btn = tk.Label(toolbar, text="  Ping  ", bg=ACCENT_BLUE, fg=TEXT_PRIMARY,
                            font=("SF Pro Display", 11, "bold"), cursor="hand2",
                            padx=8, pady=3)
        ping_btn.pack(side=tk.RIGHT, padx=8, pady=6)

        # NIC telemetry card
        nic_frame = tk.Frame(content, bg=WIN_CHROME, bd=0,
                             highlightbackground=WIN_BORDER, highlightthickness=1)
        nic_frame.pack(fill=tk.X, padx=12, pady=6)

        nic_lines = [
            ("ADAPTER:", "virtio-net0  (Ethernet)  10 Gbps", TEXT_PRIMARY),
            ("IPv4 / Mask:", "192.168.1.142 / 24   GW: 192.168.1.1   DNS: 8.8.8.8", ACCENT_GREEN),
            ("MAC:", "52:54:00:12:34:56   LINK: ONLINE (Full Duplex)", TEXT_MUTED),
        ]
        for label, val, col in nic_lines:
            row = tk.Frame(nic_frame, bg=WIN_CHROME)
            row.pack(fill=tk.X, padx=12, pady=2)
            tk.Label(row, text=label, bg=WIN_CHROME, fg=TEXT_MUTED,
                     font=("SF Pro Mono", 10), width=14, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=val, bg=WIN_CHROME, fg=col,
                     font=("SF Pro Mono", 10)).pack(side=tk.LEFT)

        # Ping output log
        ping_frame = tk.Frame(content, bg=WIN_CHROME,
                              highlightbackground=WIN_BORDER, highlightthickness=1)
        ping_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        ping_title = tk.Label(ping_frame, text="  ICMP Echo / Ping Diagnostic Console",
                              bg=WIN_CHROME, fg=TEXT_MUTED,
                              font=("SF Pro Display", 10), anchor="w")
        ping_title.pack(fill=tk.X, padx=4, pady=4)

        ping_log = tk.Text(ping_frame, bg="#101014", fg=ACCENT_GREEN,
                           font=("SF Pro Mono", 10), relief="flat", bd=6,
                           state="disabled", cursor="arrow", wrap="word")
        ping_log.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Seed log with initial content
        def append_ping(msg, color=ACCENT_GREEN):
            ping_log.configure(state="normal")
            ping_log.insert(tk.END, msg + "\n")
            ping_log.see(tk.END)
            ping_log.configure(state="disabled")

        append_ping("PING 8.8.8.8 (Google DNS) — Rust Micro-OS Network Stack")
        append_ping("------------------------------------------------------------")
        self._do_ping(append_ping)

        def on_ping_click(_e):
            target = url_var.get().split("//")[-1].split("/")[0]
            append_ping(f"\nPING {target} — New Request Initiated")
            self._do_ping(append_ping)

        ping_btn.bind("<Button-1>", on_ping_click)

        # HTTP document viewer at bottom
        http_frame = tk.Frame(content, bg=WIN_CHROME,
                              highlightbackground=WIN_BORDER, highlightthickness=1)
        http_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        tk.Label(http_frame, text="  HTTP 1.1 / Document Viewer",
                 bg=WIN_CHROME, fg=TEXT_MUTED,
                 font=("SF Pro Display", 10), anchor="w").pack(fill=tk.X, padx=4)
        tk.Label(http_frame,
                 text="  ● 200 OK  |  Content-Type: text/html  |  Welcome to Rust Micro-OS v2.0  "
                      "|  TCP/IP Socket ✓  |  virtio-net0 ✓  |  0 Errors",
                 bg=WIN_CHROME, fg=ACCENT_GREEN,
                 font=("SF Pro Mono", 10), anchor="w").pack(fill=tk.X, padx=4, pady=4)

    def _do_ping(self, append_fn):
        """Simulates asynchronous ICMP echo RTTs."""
        seq = [0]
        def _one():
            rtt = round(random.uniform(9.8, 15.4), 2)
            seq[0] += 1
            append_fn(f"  64 bytes from 8.8.8.8: icmp_seq={seq[0]} ttl=118 time={rtt} ms")
            if seq[0] < 4:
                self.after(600, _one)
            else:
                loss = 0
                append_fn(f"  --- 4 packets tx, 4 rx, {loss}% loss, avg={rtt} ms")
        _one()

    # ─── App 2: PowerTerminal (Interactive Micro-Shell) ──────────────────────

    def _open_terminal(self):
        win, content = self._make_window(
            f"⌨  PowerTerminal — micro-os:{self.cwd}$",
            840, 540, offset_x=160, offset_y=100)

        # Main terminal frame (Windows Terminal Fluent Dark Console)
        term_frame = tk.Frame(content, bg="#1E1E1E")
        term_frame.pack(fill=tk.BOTH, expand=True)

        term_text = tk.Text(term_frame, bg="#1E1E1E", fg="#E0E0E0",
                            font=("Consolas", 10), relief="flat", bd=10,
                            insertbackground="#60CDFF", wrap="char",
                            selectbackground="#264F78")
        term_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(term_frame, command=term_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        term_text.configure(yscrollcommand=scrollbar.set)

        # Tag styles
        term_text.tag_configure("prompt",  foreground="#60CDFF")
        term_text.tag_configure("output",  foreground="#E0E0E0")
        term_text.tag_configure("error",   foreground="#F14C4C")
        term_text.tag_configure("ok",      foreground="#73C991")
        term_text.tag_configure("muted",   foreground="#8A8A8A")
        term_text.tag_configure("purple",  foreground="#C586C0")
        term_text.tag_configure("amber",   foreground="#DCDCAA")
        term_text.tag_configure("cyan",    foreground="#4EC9B0")
        term_text.tag_configure("bold",    foreground="#FFFFFF", font=("Consolas", 10, "bold"))

        def w(text, tag="output"):
            term_text.insert(tk.END, text, tag)
            term_text.see(tk.END)

        # Initial Boot Banner
        w("🦀 Rust Micro-OS v2.0 (Windows 11 Light / Fluent Edition) PowerTerminal\n", "amber")
        w("Kernel: microkernel-rr-prio v2.0.0  |  Shell: micro-sh 2.0  |  User: macha (uid=1000)\n", "muted")
        w("Type 'help' for manual, 'wifi scan' for host APs, 'snap list' for software.\n\n", "muted")

        # Bottom interactive prompt bar
        prompt_bar = tk.Frame(content, bg="#252526", height=34,
                              highlightbackground="#3C3C3C", highlightthickness=1)
        prompt_bar.pack(side=tk.BOTTOM, fill=tk.X)
        prompt_bar.pack_propagate(False)

        prompt_lbl = tk.Label(prompt_bar, text=f"micro-os:{self.cwd}$", bg="#252526",
                              fg="#60CDFF", font=("Consolas", 10, "bold"), padx=8)
        prompt_lbl.pack(side=tk.LEFT)

        cmd_entry = tk.Entry(prompt_bar, bg="#252526", fg="#FFFFFF",
                             font=("Consolas", 10), relief="flat", bd=2,
                             insertbackground="#60CDFF")
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), pady=4)
        cmd_entry.focus_set()

        term_text.bind("<Button-1>", lambda e: cmd_entry.focus_set())
        content.bind("<Button-1>", lambda e: cmd_entry.focus_set(), add="+")
        prompt_bar.bind("<Button-1>", lambda e: cmd_entry.focus_set(), add="+")
        win.bind("<Button-1>", lambda e: cmd_entry.focus_set(), add="+")

        # History cursor
        hist_cursor = [len(self.cmd_history)]

        def hist_prev(event):
            if not self.cmd_history:
                return "break"
            if hist_cursor[0] > 0:
                hist_cursor[0] -= 1
            cmd_entry.delete(0, tk.END)
            cmd_entry.insert(0, self.cmd_history[hist_cursor[0]])
            return "break"

        def hist_next(event):
            if not self.cmd_history:
                return "break"
            if hist_cursor[0] < len(self.cmd_history) - 1:
                hist_cursor[0] += 1
                cmd_entry.delete(0, tk.END)
                cmd_entry.insert(0, self.cmd_history[hist_cursor[0]])
            else:
                hist_cursor[0] = len(self.cmd_history)
                cmd_entry.delete(0, tk.END)
            return "break"

        cmd_entry.bind("<Up>", hist_prev)
        cmd_entry.bind("<Down>", hist_next)

        # Tab auto-completion
        COMMAND_LIST = [
            "help", "clear", "cls", "echo", "pwd", "cd", "ls", "dir", "cat", "touch",
            "mkdir", "rm", "neofetch", "fastfetch", "uname", "whoami", "hostname",
            "uptime", "date", "ps", "top", "htop", "free", "meminfo", "kill",
            "ifconfig", "ip", "route", "ping", "curl", "wget", "wifi", "snap",
            "calc", "history", "store", "doom", "snake", "reboot", "shutdown"
        ]

        def handle_tab(event):
            curr = cmd_entry.get()
            parts = curr.split()
            if not parts:
                return "break"
            prefix = parts[-1]
            matches = [c for c in COMMAND_LIST if c.startswith(prefix)]
            if len(matches) == 1:
                parts[-1] = matches[0]
                cmd_entry.delete(0, tk.END)
                cmd_entry.insert(0, " ".join(parts) + " ")
            elif len(matches) > 1:
                w(f"\nSuggestions: {'  '.join(matches)}\n", "cyan")
                w(f"micro-os:{self.cwd}$ {curr}", "prompt")
            return "break"

        cmd_entry.bind("<Tab>", handle_tab)

        # Command Dispatcher
        def execute_cmd(event=None):
            raw = cmd_entry.get().strip()
            cmd_entry.delete(0, tk.END)

            if not raw:
                w(f"micro-os:{self.cwd}$ \n", "prompt")
                return

            self.cmd_history.append(raw)
            hist_cursor[0] = len(self.cmd_history)
            w(f"micro-os:{self.cwd}$ {raw}\n", "prompt")

            parts = raw.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ("help", "?"):
                sub_help = args[0].lower().strip("-") if args else ""
                if sub_help in ("wifi", "wlan", "network", "net"):
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("COMMAND: wifi - Physical Wi-Fi Adapter & Wireless Management\n", "cyan")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("USAGE:\n", "amber")
                    w("  wifi status                 Show current Wi-Fi connection, SSID, signal %, IP\n", "output")
                    w("  wifi scan                   Sweep 2.4/5GHz channels and list real host APs\n", "output")
                    w("  wifi connect <SSID> [pass]  Associate and handshake with wireless network\n", "output")
                    w("  wifi disconnect             Disconnect from active Wi-Fi and release DHCP lease\n", "output")
                    w("  wifi gui / netmgr           Open the graphical Wi-Fi & Network Manager window\n", "output")
                    w("\nEXAMPLES:\n", "amber")
                    w("  wifi scan                   # Discover Jain_Student, Jain_Faculty, eduroam...\n", "output")
                    w("  wifi connect Jain_Student   # Connect to Jain_Student network\n", "output")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                elif sub_help in ("ls", "dir", "list"):
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("COMMAND: ls / dir - Directory Listing\n", "cyan")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("USAGE:\n", "amber")
                    w("  ls                          List files in current directory\n", "output")
                    w("  ls -l                       Long format (permissions, owner, size, date)\n", "output")
                    w("  ls -a                       Include hidden / dot entries (. and ..)\n", "output")
                    w("  ls -la / ls -lh             Combined long listing with all entries\n", "output")
                    w("  ls <dir>                    List contents of specified folder (e.g. ls /system)\n", "output")
                    w("  dir [/w] [/a]               Windows-style directory listing\n", "output")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                elif sub_help in ("snap", "store", "pkg"):
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("COMMAND: snap - Snap Store Package Manager CLI\n", "cyan")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("USAGE:\n", "amber")
                    w("  snap list                   List installed snap packages\n", "output")
                    w("  snap search <term>          Search software catalog for apps\n", "output")
                    w("  snap install <pkg>          Download, verify SHA256, and install a package\n", "output")
                    w("  snap remove <pkg>           Uninstall a snap package\n", "output")
                    w("  snap info <pkg>             Display detailed package metadata and developer\n", "output")
                    w("  store                       Launch Graphical Snap Store Software Center\n", "output")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                elif sub_help in ("fs", "file", "files"):
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("COMMAND GROUP: File System & Directory Operations\n", "cyan")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                    w("  ls [-l|-a] / dir            List directory contents\n", "output")
                    w("  cd <dir>                    Change directory (~, .., /, or relative paths)\n", "output")
                    w("  pwd                         Print current working directory path\n", "output")
                    w("  cat <file> / type <file>    Print text file contents to screen\n", "output")
                    w("  cp <src> <dest> / copy      Copy file to destination\n", "output")
                    w("  mv <src> <dest> / move      Move or rename file\n", "output")
                    w("  touch <file>                Create new empty file\n", "output")
                    w("  mkdir <dir> / md <dir>      Create new folder\n", "output")
                    w("  rm <file> / del <file>      Delete file or folder\n", "output")
                    w("  grep <pat> [file] / find    Search pattern in virtual files\n", "output")
                    w("  df / diskfree               Display disk storage and mount points\n", "output")
                    w("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "muted")
                else:
                    w("================================================================================\n", "muted")
                    w("                     RUST MICRO-OS v2.0 COMPLETE COMMAND MANUAL                 \n", "amber")
                    w("================================================================================\n\n", "muted")
                    w("📁 FILE SYSTEM & DIRECTORY OPERATIONS:\n", "cyan")
                    w("  ls [-l|-a]          List files and directories in current working folder\n", "output")
                    w("  dir                 Windows-style directory listing\n", "output")
                    w("  cd <dir>            Change directory (supports ~, .., /, or relative paths)\n", "output")
                    w("  pwd                 Print absolute path of current working directory\n", "output")
                    w("  cat <file>          Print contents of a text file (e.g. cat welcome.txt)\n", "output")
                    w("  type <file>         Windows-style print file contents (alias for cat)\n", "output")
                    w("  cp <src> <dest>     Copy file to new destination path (alias: copy)\n", "output")
                    w("  mv <src> <dest>     Move or rename file (aliases: move, ren, rename)\n", "output")
                    w("  touch <file>        Create a new empty file in current folder\n", "output")
                    w("  mkdir <dir>         Create a new directory in virtual filesystem (alias: md)\n", "output")
                    w("  rm <file>           Delete a file from virtual filesystem (aliases: del, erase)\n", "output")
                    w("  grep <pat> [file]   Search pattern in files or across filesystem (alias: find)\n", "output")
                    w("  df / diskfree       Display filesystem storage partitions and mount points\n", "output")
                    w("  echo [text]         Display text or inspect environment vars ($USER, $IP, $WIFI)\n", "output")
                    w("\n📊 SYSTEM DIAGNOSTICS & TELEMETRY:\n", "cyan")
                    w("  neofetch / fastfetch Display ASCII Rust crab logo and hardware/kernel specs\n", "output")
                    w("  uname [-a]          Print kernel architecture, version, and OS name\n", "output")
                    w("  ver / version       Windows-style display OS version and build number\n", "output")
                    w("  whoami              Print active logged-in user (macha)\n", "output")
                    w("  hostname            Print computer network hostname (micro-os-x86)\n", "output")
                    w("  uptime              Show system running time and scheduling load average\n", "output")
                    w("  date / time         Show current system date, time, and timezone\n", "output")
                    w("  sysinfo / systeminfo Display complete OS hardware, kernel & network summary\n", "output")
                    w("  dmesg               Display kernel boot ring buffer and hardware detection log\n", "output")
                    w("\n⚡ PROCESS & MEMORY CONTROL:\n", "cyan")
                    w("  ps [aux] / tasklist List active processes, PIDs, priority, state, and memory\n", "output")
                    w("  top / htop          Real-time interactive process viewer\n", "output")
                    w("  free / meminfo      Display memory allocation stats (Free-List 64 KiB heap)\n", "output")
                    w("  kill <pid>          Terminate a process by PID (alias: taskkill)\n", "output")
                    w("\n🌐 NETWORK & PHYSICAL WI-FI CONTROL:\n", "cyan")
                    w("  wifi status         Show current Wi-Fi connection, SSID, signal %, band, IP\n", "output")
                    w("  wifi scan           Sweep 2.4/5GHz channels and list real networks from device\n", "output")
                    w("  wifi connect <ssid> Connect to a wireless network and obtain DHCP lease\n", "output")
                    w("  wifi disconnect     Disconnect from active Wi-Fi and release DHCP IP lease\n", "output")
                    w("  wifi gui / netmgr   Open the graphical Wi-Fi & Network Manager window\n", "output")
                    w("  ipconfig            Windows-style IP configuration for Wi-Fi and Ethernet\n", "output")
                    w("  ifconfig / ip addr  List all network interfaces (virtio-net0, wlan0, lo0)\n", "output")
                    w("  route               Show IPv4 routing table and default gateway\n", "output")
                    w("  ping <ip|host>      Send ICMP echo requests and calculate round-trip latency\n", "output")
                    w("  curl <url> / wget   Perform HTTP GET request and display server response\n", "output")
                    w("  netstat             Show active TCP/UDP sockets and open network ports\n", "output")
                    w("\n🛍️ PACKAGE MANAGEMENT (SNAP STORE):\n", "cyan")
                    w("  snap list           List all installed snap packages on the system\n", "output")
                    w("  snap search <term>  Search software catalog for apps (utilities, games, dev)\n", "output")
                    w("  snap install <pkg>  Download, verify SHA256, and install a snap package\n", "output")
                    w("  snap remove <pkg>   Uninstall a snap package\n", "output")
                    w("  snap info <pkg>     Display detailed package metadata, developer, and rating\n", "output")
                    w("\n🪟 WINDOWS APPS & GAMES:\n", "cyan")
                    w("  browser / web       Open MicroBrowser with live web navigation\n", "output")
                    w("  store / snap-store  Open the Graphical Snap Store Software Center\n", "output")
                    w("  calc [expr]         Evaluate mathematical expression or launch MicroCalc GUI\n", "output")
                    w("  files / explorer    Open the graphical File Explorer\n", "output")
                    w("  taskmgr / monitor   Open the graphical Task Manager / Activity Monitor\n", "output")
                    w("  settings            Open System Settings & Kernel Specifications\n", "output")
                    w("  snake               Launch the playable retro Snake Arcade game\n", "output")
                    w("  doom                Launch the 3D Raycaster Dungeon Engine (1993)\n", "output")
                    w("\n⚙️ SHELL CONTROLS:\n", "cyan")
                    w("  help [cmd] / ?      Display this complete manual or specific command usage\n", "output")
                    w("  clear / cls         Clear the terminal screen buffer\n", "output")
                    w("  history             Display executed command history\n", "output")
                    w("  reboot              Reboot the operating system\n", "output")
                    w("  shutdown / exit     Power off or close terminal session (alias: quit)\n", "output")
                    w("================================================================================\n", "muted")

            elif cmd in ("clear", "cls"):
                term_text.delete("1.0", tk.END)

            elif cmd == "echo":
                expanded = []
                for a in args:
                    clean_a = a.strip('"\'')
                    if clean_a == "$USER":
                        expanded.append("macha")
                    elif clean_a == "$HOME":
                        expanded.append("/home/macha")
                    elif clean_a == "$IP":
                        expanded.append(self.wifi_ip if self.wifi_connected else "0.0.0.0")
                    elif clean_a == "$WIFI":
                        expanded.append(self.wifi_ssid if self.wifi_connected else "Disconnected")
                    elif clean_a == "$OS":
                        expanded.append("Rust Micro-OS 2.0 (x86_64)")
                    elif clean_a == "$SHELL":
                        expanded.append("/bin/sh (micro-sh)")
                    else:
                        expanded.append(clean_a)
                w(" ".join(expanded) + "\n", "output")

            elif cmd == "pwd":
                w(f"{self.cwd}\n", "output")

            elif cmd == "cd":
                req = args[0] if args else "~"
                new_path = self._resolve_path(req)

                if new_path in self.vfs:
                    self.cwd = new_path
                    prompt_lbl.configure(text=f"micro-os:{self.cwd}$")
                    if hasattr(win, "title_lbl"):
                        win.title_lbl.configure(text=f"⌨  PowerTerminal — micro-os:{self.cwd}$")
                else:
                    w(f"cd: no such file or directory: {req}\n", "error")

            elif cmd in ("ls", "dir"):
                flags = []
                targets = []
                for a in args:
                    if a.startswith("-") or (cmd == "dir" and a.startswith("/")):
                        flags.append(a.lower())
                    else:
                        targets.append(a)

                show_long = any("l" in f for f in flags) or (cmd == "dir" and "/w" not in flags)
                show_all = any("a" in f for f in flags) or (cmd == "dir" and "/a" in flags)

                req = targets[0] if targets else "."
                target = self._resolve_path(req)

                if target in self.vfs:
                    items = list(self.vfs[target])
                    if show_all:
                        items = [".", ".."] + items

                    if not items:
                        w("(empty directory)\n", "muted")
                    elif cmd == "dir":
                        w(f" Volume in drive C is Rust Micro-OS\n Volume Serial Number is 2026-1121\n\n Directory of C:{target.replace('/', chr(92))}\n\n", "muted")
                        files_cnt = 0
                        dirs_cnt = 0
                        total_bytes = 0
                        for it in items:
                            subpath = (target.rstrip("/") + "/" + it).rstrip("/")
                            if subpath in self.vfs or it in (".", ".."):
                                dirs_cnt += 1
                                w(f"21-11-2026  15:40    <DIR>          {it}\n", "ok")
                            else:
                                files_cnt += 1
                                sz = len(self.vfs_files.get(subpath, ""))
                                total_bytes += sz
                                w(f"21-11-2026  15:40              {sz:>5} {it}\n", "output")
                        w(f"               {files_cnt} File(s)          {total_bytes:>7} bytes\n", "muted")
                        w(f"               {dirs_cnt} Dir(s)       47,104,000 bytes free\n", "muted")
                    elif show_long:
                        total_k = sum(len(self.vfs_files.get((target.rstrip('/') + '/' + it).rstrip('/'), '')) for it in items) // 1024 + 1
                        w(f"total {total_k * 4}\n", "muted")
                        for it in items:
                            subpath = (target.rstrip("/") + "/" + it).rstrip("/")
                            is_dir = (subpath in self.vfs or it in (".", ".."))
                            perm = "drwxr-xr-x" if is_dir else "-rw-r--r--"
                            sz = 4096 if is_dir else len(self.vfs_files.get(subpath, "128"))
                            tag = "ok" if is_dir else "output"
                            icon = "📁" if is_dir else "📄"
                            w(f"{perm}  2 macha macha  {sz:>5} Nov 21 15:40 {icon} {it}\n", tag)
                    else:
                        formatted = []
                        for it in items:
                            subpath = (target.rstrip("/") + "/" + it).rstrip("/")
                            if subpath in self.vfs or it in (".", ".."):
                                formatted.append(f"📁 {it}/")
                            elif it.endswith(".sys") or it.endswith(".bin"):
                                formatted.append(f"🔧 {it}")
                            else:
                                formatted.append(f"📄 {it}")
                        w("  ".join(formatted) + "\n", "output")

                elif target in self.vfs_files:
                    it = target.rsplit("/", 1)[1]
                    sz = len(self.vfs_files.get(target, ""))
                    if show_long:
                        w(f"-rw-r--r--  1 macha macha  {sz:>5} Nov 21 15:40 📄 {it}\n", "output")
                    else:
                        w(f"📄 {it}\n", "output")
                else:
                    w(f"{cmd}: cannot access '{req}': No such file or directory\n", "error")

            elif cmd in ("cat", "type"):
                flags = [a for a in args if a.startswith("-")]
                targets = [a for a in args if not a.startswith("-")]
                if not targets:
                    w(f"{cmd}: missing file operand\n", "error")
                else:
                    req = targets[0]
                    target = self._resolve_path(req)
                    if target in self.vfs_files:
                        lines = self.vfs_files[target].splitlines()
                        if any("n" in f for f in flags):
                            for idx, line in enumerate(lines, 1):
                                w(f"  {idx:>3}  {line}\n", "output")
                        else:
                            w(self.vfs_files[target] + "\n", "output")
                    elif target in self.vfs:
                        w(f"{cmd}: {req}: Is a directory\n", "error")
                    else:
                        w(f"{cmd}: {req}: No such file or directory\n", "error")

            elif cmd in ("cp", "copy"):
                clean_args = [a for a in args if not a.startswith("-")]
                if len(clean_args) < 2:
                    w(f"{cmd}: missing destination file operand. Usage: {cmd} <src> <dest>\n", "error")
                else:
                    src = self._resolve_path(clean_args[0])
                    dest = self._resolve_path(clean_args[1])
                    if src in self.vfs_files:
                        content = self.vfs_files[src]
                        dest_parent = dest.rsplit("/", 1)[0] or "/"
                        dest_base = dest.rsplit("/", 1)[1]
                        if dest_parent in self.vfs:
                            if dest_base not in self.vfs[dest_parent]:
                                self.vfs[dest_parent].append(dest_base)
                            self.vfs_files[dest] = content
                            w(f"Copied '{clean_args[0]}' -> '{clean_args[1]}'\n", "ok")
                        else:
                            w(f"{cmd}: target directory does not exist: '{dest_parent}'\n", "error")
                    else:
                        w(f"{cmd}: cannot stat '{clean_args[0]}': No such file\n", "error")

            elif cmd in ("mv", "move", "ren", "rename"):
                clean_args = [a for a in args if not a.startswith("-")]
                if len(clean_args) < 2:
                    w(f"{cmd}: missing destination operand. Usage: {cmd} <src> <dest>\n", "error")
                else:
                    src = self._resolve_path(clean_args[0])
                    dest = self._resolve_path(clean_args[1])
                    if src in self.vfs_files:
                        content = self.vfs_files.pop(src)
                        src_parent = src.rsplit("/", 1)[0] or "/"
                        src_base = src.rsplit("/", 1)[1]
                        if src_parent in self.vfs and src_base in self.vfs[src_parent]:
                            self.vfs[src_parent].remove(src_base)
                        dest_parent = dest.rsplit("/", 1)[0] or "/"
                        dest_base = dest.rsplit("/", 1)[1]
                        if dest_parent in self.vfs:
                            if dest_base not in self.vfs[dest_parent]:
                                self.vfs[dest_parent].append(dest_base)
                            self.vfs_files[dest] = content
                            w(f"Moved '{clean_args[0]}' -> '{clean_args[1]}'\n", "ok")
                        else:
                            w(f"{cmd}: target directory does not exist: '{dest_parent}'\n", "error")
                    else:
                        w(f"{cmd}: cannot stat '{clean_args[0]}': No such file\n", "error")

            elif cmd == "touch":
                clean_args = [a for a in args if not a.startswith("-")]
                if not clean_args:
                    w("touch: missing file operand\n", "error")
                else:
                    fname = clean_args[0]
                    target = self._resolve_path(fname)
                    parent = target.rsplit("/", 1)[0] or "/"
                    base = target.rsplit("/", 1)[1]
                    if parent in self.vfs:
                        if base not in self.vfs[parent]:
                            self.vfs[parent].append(base)
                        self.vfs_files[target] = f"# Created on {datetime.now()}"
                        w(f"Created file: {target}\n", "ok")
                    else:
                        w(f"touch: cannot touch '{fname}': No such directory\n", "error")

            elif cmd in ("mkdir", "md"):
                clean_args = [a for a in args if not a.startswith("-")]
                if not clean_args:
                    w(f"{cmd}: missing operand\n", "error")
                else:
                    dname = clean_args[0]
                    target = self._resolve_path(dname)
                    parent = target.rsplit("/", 1)[0] or "/"
                    base = target.rsplit("/", 1)[1]
                    if parent in self.vfs:
                        if base not in self.vfs[parent]:
                            self.vfs[parent].append(base)
                        self.vfs[target] = []
                        w(f"Created directory: {target}\n", "ok")
                    else:
                        w(f"{cmd}: cannot create directory '{dname}': No such file or directory\n", "error")

            elif cmd in ("rm", "del", "erase"):
                clean_args = [a for a in args if not a.startswith("-")]
                if not clean_args:
                    w(f"{cmd}: missing operand\n", "error")
                else:
                    fname = clean_args[0]
                    target = self._resolve_path(fname)
                    parent = target.rsplit("/", 1)[0] or "/"
                    base = target.rsplit("/", 1)[1]
                    if target in self.vfs_files:
                        del self.vfs_files[target]
                        if parent in self.vfs and base in self.vfs[parent]:
                            self.vfs[parent].remove(base)
                        w(f"Removed '{fname}'\n", "muted")
                    elif target in self.vfs:
                        del self.vfs[target]
                        if parent in self.vfs and base in self.vfs[parent]:
                            self.vfs[parent].remove(base)
                        w(f"Removed directory '{fname}'\n", "muted")
                    else:
                        w(f"{cmd}: cannot remove '{fname}': No such file or directory\n", "error")

            elif cmd in ("grep", "find"):
                flags = [a for a in args if a.startswith("-")]
                targets = [a for a in args if not a.startswith("-")]
                if not targets:
                    w(f"{cmd}: usage: {cmd} <pattern> [file]\n", "error")
                elif len(targets) == 1:
                    pat = targets[0].lower()
                    found = False
                    for path, content in self.vfs_files.items():
                        for line_no, line in enumerate(content.splitlines(), 1):
                            if pat in line.lower():
                                w(f"{path}:{line_no}: {line}\n", "ok")
                                found = True
                    if not found:
                        w(f"No matches found for '{pat}' in virtual filesystem.\n", "muted")
                else:
                    pat = targets[0].lower()
                    req = targets[1]
                    target = self._resolve_path(req)
                    if target in self.vfs_files:
                        content = self.vfs_files[target]
                        found = False
                        for line_no, line in enumerate(content.splitlines(), 1):
                            if pat in line.lower():
                                w(f"{req}:{line_no}: {line}\n", "ok")
                                found = True
                        if not found:
                            w(f"Pattern '{pat}' not found in {req}\n", "muted")
                    else:
                        w(f"{cmd}: {req}: No such file\n", "error")

            elif cmd in ("df", "diskfree"):
                w("Filesystem     Type      Size  Used Avail Use% Mounted on\n", "muted")
                w("/dev/sda1      ext4       64M   18M   46M  28% /\n", "ok")
                w("devtmpfs       devtmpfs  4.0M     0  4.0M   0% /dev\n", "muted")
                w("tmpfs          tmpfs     8.0M  512K  7.5M   6% /run\n", "muted")
                w("/dev/loop0     squashfs  4.2M  4.2M     0 100% /snap/core22\n", "muted")
                w("/dev/loop1     squashfs  8.2M  8.2M     0 100% /snap/doom\n", "muted")

            elif cmd in ("neofetch", "fastfetch"):
                elapsed = datetime.now() - self.boot_time
                mins = max(1, elapsed.seconds // 60)
                installed_count = sum(1 for p in self.snap_packages.values() if p.get("installed"))
                wifi_desc = f"{self.wifi_ssid} (Ch {self.wifi_channel}, {self.wifi_signal}%)" if self.wifi_connected else "Disconnected"

                lines = [
                    ("        _      _        ", "amber", f"macha@micro-os-x86\n", "bold"),
                    ("      (o \\-=-/ o)       ", "amber", "------------------\n", "muted"),
                    ("       (  \\ /  )        ", "amber", f"OS:        Rust Micro-OS v2.0 (x86_64)\n", "ok"),
                    ("      __\\  v  /__       ", "amber", f"Host:      VirtualBox 7.0 / QEMU KVM\n", "output"),
                    ("     (____/ \\____)      ", "amber", f"Kernel:    microkernel-rr-prio 2.0.0\n", "output"),
                    ("       / /   \\ \\        ", "amber", f"Uptime:    {mins} mins\n", "output"),
                    ("      /_/     \\_\\       ", "amber", f"Packages:  {installed_count} (snap), 6 (builtin)\n", "output"),
                    ("                        ", "output", f"Shell:     micro-sh 2.0.0\n", "output"),
                    ("                        ", "output", f"DE / WM:   Windows 11 Fluent Dark Mica\n", "output"),
                    ("                        ", "output", f"Network:   virtio-net0 (192.168.1.142)\n", "cyan"),
                    ("                        ", "output", f"Wi-Fi:     {wifi_desc}\n", "ok" if self.wifi_connected else "muted"),
                    ("                        ", "output", f"CPU:       virtio-vCPU x4 @ 3.40 GHz\n", "output"),
                    ("                        ", "output", f"Memory:    18.4 KiB / 64.0 KiB (Free-List)\n\n", "purple"),
                ]
                for prefix, ptag, text_l, ttag in lines:
                    w(prefix, ptag)
                    w(text_l, ttag)

            elif cmd in ("uname", "ver", "version"):
                if "-a" in args:
                    w("RustMicroOS micro-os-x86 2.0.0-release #1 SMP Sat Nov 20 2026 x86_64 Windows 11 Fluent Edition\n", "ok")
                elif "-r" in args:
                    w("2.0.0-release\n", "ok")
                elif "-m" in args:
                    w("x86_64\n", "ok")
                else:
                    w("RustMicroOS 2.0.0 (x86_64) [Version 10.0.22631.3007]\n", "ok")

            elif cmd == "whoami":
                w("macha (uid=1000 gid=1000 groups=1000(macha),4(adm),27(sudo))\n", "ok")

            elif cmd == "hostname":
                w("micro-os-x86\n", "ok")

            elif cmd == "uptime":
                elapsed = datetime.now() - self.boot_time
                mins = elapsed.seconds // 60
                secs = elapsed.seconds % 60
                w(f" {datetime.now().strftime('%H:%M:%S')} up {mins} min {secs} sec, 1 user, load average: 0.08, 0.05, 0.02\n", "ok")

            elif cmd in ("date", "time"):
                w(f"{datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')}\n", "ok")

            elif cmd in ("sysinfo", "systeminfo"):
                elapsed = datetime.now() - self.boot_time
                w("================================================================================\n", "muted")
                w("                      MICRO-OS SYSTEM INFORMATION SUMMARY                       \n", "amber")
                w("================================================================================\n", "muted")
                w("OS Name:                   Rust Micro-OS v2.0 (x86_64 Windows 11 Fluent Edition)\n", "ok")
                w("OS Version:                2.0.0-release Build 20261120\n", "output")
                w("OS Manufacturer:           Custom Kernel Project (Rust + x86_64 Bare-Metal)\n", "output")
                w("System Hostname:           micro-os-x86\n", "output")
                w("System Architecture:       x86_64-unknown-none (64-bit protected mode)\n", "output")
                w("Processor(s):              1 Processor(s) Installed [virtio-vCPU x4 Cores @ 3.4 GHz]\n", "output")
                w(f"System Uptime:             {elapsed.seconds // 60} minutes, {elapsed.seconds % 60} seconds\n", "output")
                w("Total Physical Memory:     64.0 KiB\n", "output")
                w("Available Physical Memory: 45.6 KiB (Coalescing Free-List Allocator)\n", "output")
                w("Virtual Memory In Use:     18.4 KiB (0% fragmentation ratio)\n", "output")
                w("Wi-Fi Adapter:             Intel(R) Wi-Fi 6 AX203 (MAC: 90:10:57:c0:0b:7a)\n", "cyan")
                w(f"Wi-Fi Network:             {self.wifi_ssid} ({self.wifi_signal}% Signal, {self.wifi_band}, Ch {self.wifi_channel})\n", "ok" if self.wifi_connected else "muted")
                w("Ethernet Adapter:          virtio-net0 (MAC: 52:54:00:12:34:56, 192.168.1.142)\n", "cyan")
                w("Desktop Compositor:        Windows 11 Fluent Dark Mica Compositor\n", "output")
                w("Installed Snap Packages:   6 packages (neofetch, htop, doom, snake, calc, snap-store)\n", "output")
                w("================================================================================\n", "muted")

            elif cmd == "dmesg":
                w("[    0.000000] Linux/Rust Micro-OS v2.0.0-release (root@build-server) #1 SMP Sat Nov 20 2026\n", "muted")
                w("[    0.000008] Command line: BOOT_IMAGE=/boot/vmlinuz-rust root=/dev/sda1 ro quiet\n", "muted")
                w("[    0.000045] BIOS-e820: [mem 0x0000000000000000-0x000000000000ffff] usable\n", "muted")
                w("[    0.000120] Free-List Allocator: 65536 bytes managed heap initialized\n", "ok")
                w("[    0.001402] PCI: Probing PCI hardware (bus 00)\n", "muted")
                w("[    0.002810] pci 0000:00:03.0: virtio-net device detected (IRQ 11)\n", "cyan")
                w("[    0.003150] virtio-net0: link up, 10Gbps full duplex, MAC: 52:54:00:12:34:56\n", "ok")
                w("[    0.004920] pci 0000:00:04.0: Intel(R) Wi-Fi 6 AX203 wireless controller (IRQ 12)\n", "cyan")
                w(f"[    0.007800] wlan0: Authenticating with AP '{self.wifi_ssid}' (BSSID: {self.wifi_bssid})\n", "muted")
                w(f"[    0.009400] wlan0: Associated with {self.wifi_ssid} on channel {self.wifi_channel} ({self.wifi_band})\n", "ok")
                w(f"[    0.010210] DHCP: Assigned IPv4 lease {self.wifi_ip}/24 to wlan0\n", "ok")
                w("[    0.012500] systemd[1]: Started Windows 11 Fluent Desktop Compositor.\n", "ok")
                w("[    0.014200] micro-os: System initialization complete.\n", "ok")

            elif cmd in ("ps", "ps aux", "tasklist"):
                w("USER       PID  %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n", "muted")
                w("root         1   4.2  2.1   4200   512 ?        Ss   09:30   0:02 [kernel] idle/init\n", "ok")
                w("root         2   8.4  3.8   6800  1024 ?        S    09:30   0:05 [net] virtio-net0\n", "ok")
                w("root         3   3.1  1.4   2100   256 ?        S    09:30   0:01 [disk] flusher_thread\n", "ok")
                w("macha        4  14.2  8.6  12400  2048 tty0     R    09:31   0:08 [gui] compositor\n", "ok")
                w("root         5   2.0  1.8   3200   512 ?        S    09:31   0:01 [wifi] wlan0_daemon\n", "ok")
                w("root         6   1.2  2.4   4800   768 ?        S    09:31   0:01 [snap] snapd_service\n", "ok")
                w("macha        7   0.8  1.1   1800   256 tty0     R+   09:32   0:00 /bin/sh (powerterminal)\n", "ok")

            elif cmd in ("top", "htop"):
                w("Tasks: 7 total, 2 running, 5 sleeping, 0 stopped, 0 zombie\n", "cyan")
                w("%Cpu(s):  6.2 us,  2.1 sy,  0.0 ni, 91.7 id,  0.0 wa,  0.0 hi\n", "muted")
                w("MiB Mem :     64.0 total,     18.4 used,     45.6 free\n", "muted")
                w("  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n", "muted")
                w("    4 macha     20   0   12400   2048    512 R  14.2   8.6   0:08.42 compositor\n", "ok")
                w("    2 root      20   0    6800   1024    256 S   8.4   3.8   0:05.12 virtio-net\n", "ok")
                w("    5 root      20   0    3200    512    128 S   2.0   1.8   0:01.20 wlan0_svc\n", "ok")
                w("    6 root      20   0    4800    768    256 S   1.2   2.4   0:01.05 snapd\n", "ok")
                w("(Press any command to continue)\n", "muted")

            elif cmd in ("kill", "taskkill"):
                clean_args = [a for a in args if not a.startswith("-")]
                if not clean_args:
                    w(f"{cmd}: usage: {cmd} <pid>\n", "error")
                else:
                    target_pid = clean_args[0].replace("/pid", "").replace("/PID", "").strip()
                    w(f"Signal SIGTERM sent to process {target_pid}. Process terminated.\n", "muted")

            elif cmd in ("free", "meminfo"):
                w("               total        used        free      shared  buff/cache   available\n", "muted")
                w("Mem:           64KiB       18KiB       46KiB        4KiB        8KiB       42KiB\n", "ok")
                w("Swap:             0B          0B          0B\n", "muted")
                w("Heap Allocator: Free-List Coalescing Allocator (0% fragmentation ratio)\n", "cyan")

            elif cmd in ("ifconfig", "ipconfig", "ip", "ip a", "ip addr"):
                if cmd == "ipconfig":
                    w("Windows / Micro-OS IP Configuration\n\n", "cyan")
                    w("Wireless LAN adapter Wi-Fi (wlan0):\n", "cyan")
                    if self.wifi_connected:
                        w("   Connection-specific DNS Suffix  . : localdomain\n", "muted")
                        w(f"   IPv4 Address. . . . . . . . . . . : {self.wifi_ip}\n", "ok")
                        w("   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n", "muted")
                        w("   Default Gateway . . . . . . . . . : 192.168.1.1\n", "ok")
                        w(f"   Physical Address (MAC). . . . . . : 90-10-57-C0-0B-7A\n", "muted")
                        w(f"   SSID. . . . . . . . . . . . . . . : {self.wifi_ssid} ({self.wifi_signal}% Signal, {self.wifi_band}, Ch {self.wifi_channel})\n\n", "ok")
                    else:
                        w("   Media State . . . . . . . . . . . : Media disconnected\n\n", "amber")
                    w("Ethernet adapter virtio-net0:\n", "cyan")
                    w("   Connection-specific DNS Suffix  . : localdomain\n", "muted")
                    w("   IPv4 Address. . . . . . . . . . . : 192.168.1.142\n", "ok")
                    w("   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n", "muted")
                    w("   Default Gateway . . . . . . . . . : 192.168.1.1\n", "ok")
                    w("   Physical Address (MAC). . . . . . : 52-54-00-12-34-56\n\n", "muted")
                else:
                    w("virtio-net0: flags=8863<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> mtu 1500\n", "cyan")
                    w("        inet 192.168.1.142  netmask 255.255.255.0  broadcast 192.168.1.255\n", "ok")
                    w("        ether 52:54:00:12:34:56  txqueuelen 1000  (Ethernet 10Gbps)\n", "muted")
                    w("        RX packets 1428  bytes 2048000 (2.0 MB)  RX errors 0\n", "muted")
                    w("        TX packets 1392  bytes 1920000 (1.9 MB)  TX errors 0\n\n", "muted")

                    w("wlan0: flags=8863<UP,BROADCAST,RUNNING,MULTICAST> mtu 1500\n", "cyan")
                    if self.wifi_connected:
                        w(f"        inet {self.wifi_ip}  netmask 255.255.255.0  broadcast 192.168.1.255\n", "ok")
                        w(f"        ether 90:10:57:C0:0B:7A  txqueuelen 1000  (Intel Wi-Fi 6 AX203)\n", "muted")
                        w(f"        status: connected to '{self.wifi_ssid}' (BSSID: {self.wifi_bssid})\n", "ok")
                        w(f"        channel: {self.wifi_channel} ({self.wifi_band})  signal: {self.wifi_signal}% (-38 dBm)\n", "purple")
                    else:
                        w("        ether 90:10:57:C0:0B:7A  txqueuelen 1000  (Intel Wi-Fi 6 AX203)\n", "muted")
                        w("        status: disconnected (radio idle)\n", "amber")

                    w("\nlo0: flags=8049<UP,LOOPBACK,RUNNING> mtu 65536\n", "muted")
                    w("        inet 127.0.0.1  netmask 255.0.0.0\n", "muted")

            elif cmd == "route":
                w("Kernel IP routing table\n", "muted")
                w("Destination     Gateway         Genmask         Flags Metric Ref    Use Iface\n", "muted")
                w("0.0.0.0         192.168.1.1     0.0.0.0         UG    100    0        0 wlan0\n", "ok")
                w("192.168.1.0     0.0.0.0         255.255.255.0   U     100    0        0 virtio-net0\n", "ok")

            elif cmd == "netstat":
                w("Active Internet connections (servers and established)\n", "muted")
                w("Proto Recv-Q Send-Q Local Address           Foreign Address         State\n", "muted")
                w("tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN (sshd)\n", "ok")
                w("tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN (micro-httpd)\n", "ok")
                w("tcp        0      0 127.0.0.1:6000          0.0.0.0:*               LISTEN (compositor)\n", "ok")
                w(f"tcp        0      0 {self.wifi_ip}:49210    142.250.190.46:443      ESTABLISHED (browser)\n", "cyan")
                w("udp        0      0 0.0.0.0:68              0.0.0.0:*               (dhclient/wlan0)\n", "ok")
                w("udp        0      0 0.0.0.0:5353            0.0.0.0:*               (mdns/avahi)\n", "muted")

            elif cmd == "ping":
                clean_args = [a for a in args if not a.startswith("-") and not a.isdigit()]
                if not clean_args:
                    w("ping: usage: ping <hostname/ip> [-c count]\n", "error")
                else:
                    target = clean_args[0]
                    w(f"PING {target} (8.8.8.8): 56 data bytes\n", "muted")
                    for seq in range(1, 5):
                        rtt = round(random.uniform(9.4, 14.8), 2)
                        w(f"64 bytes from {target}: icmp_seq={seq} ttl=118 time={rtt} ms\n", "ok")
                    w(f"--- {target} ping statistics ---\n4 packets transmitted, 4 received, 0% packet loss, avg 11.2ms\n", "muted")

            elif cmd == "wifi":
                sub = args[0].lower() if args else "status"
                if sub == "status":
                    if self.wifi_connected:
                        w(f"wlan0: CONNECTED\n  SSID:     {self.wifi_ssid}\n  IPv4:     {self.wifi_ip}\n  Gateway:  192.168.1.1\n  Signal:   {self.wifi_signal}% (-38 dBm, 4 bars)\n  Channel:  {self.wifi_channel} ({self.wifi_band})\n  Security: {self.wifi_security}\n  BSSID:    {self.wifi_bssid}\n", "ok")
                    else:
                        w("wlan0: DISCONNECTED (Radio active, not associated)\n", "amber")

                elif sub == "scan":
                    w("Scanning physical host Wi-Fi adapter (Intel Wi-Fi 6 AX203)...\n", "cyan")
                    w("STATUS     SIGNAL  SSID                   CH   BAND     SECURITY         BSSID\n", "muted")
                    w("─────────  ──────  ─────────────────────  ───  ───────  ───────────────  ─────────────────\n", "muted")
                    discovered = self.scan_device_wifi()
                    for net in discovered:
                        st = net.get("status", "Available")
                        sig = net.get("signal", "80%")
                        s = net.get("ssid", "Unknown")
                        ch = net.get("channel", "1")
                        b = net.get("band", "2.4 GHz")
                        sec = net.get("security", "Open")
                        bssid = net.get("bssid", "Auto")
                        color = "ok" if st == "Connected" else "output"
                        w(f"{st:<9}  {sig:<6}  {s:<21}  {ch:<3}  {b:<7}  {sec:<15}  {bssid}\n", color)
                    w(f"\nDiscovered {len(discovered)} access points on host device.\n", "muted")

                elif sub == "connect":
                    clean_con = [a.strip('"\'') for a in args[1:] if not a.startswith("-")]
                    if not clean_con:
                        w("wifi connect: usage: wifi connect <SSID> [password]\n", "error")
                    else:
                        target_ssid = clean_con[0]
                        w(f"[wlan0] Associating with '{target_ssid}'...\n", "cyan")
                        w("  [1/4] Anonce received from Access Point\n", "muted")
                        w("  [2/4] Snonce + MIC HMAC-SHA256 verified\n", "muted")
                        w("  [3/4] GTK installed & PTK verified\n", "muted")
                        w("  [4/4] 4-Way Handshake Successful!\n", "ok")
                        w("  [DHCP] Requesting IP configuration... Assigned 192.168.1.142\n", "ok")
                        w(f"✓ CONNECTED to '{target_ssid}'! Interface wlan0 active.\n", "ok")
                        self.wifi_connected = True
                        self.wifi_ssid = target_ssid
                        if hasattr(self, "_refresh_wifi_flyout"):
                            self._refresh_wifi_flyout()

                elif sub == "disconnect":
                    w("[wlan0] Sending 802.11 Deauthentication frame...\n", "amber")
                    w("[DHCP] Released IPv4 lease 192.168.1.142\n", "muted")
                    w("✓ Disconnected from Wi-Fi. Interface wlan0 idle.\n", "amber")
                    self.wifi_connected = False
                    if hasattr(self, "_refresh_wifi_flyout"):
                        self._refresh_wifi_flyout()

                elif sub in ("gui", "manager", "netmgr", "open"):
                    self._open_wifi_manager()
                    w("Opened Graphical Wi-Fi & Network Manager.\n", "ok")

                else:
                    w(f"wifi: unknown subcommand '{sub}'. Use: status, scan, connect, disconnect, gui\n", "error")

            elif cmd in ("curl", "wget"):
                clean_url = [a for a in args if not a.startswith("-")]
                if not clean_url:
                    w(f"{cmd}: usage: {cmd} <url>\n", "error")
                else:
                    url = clean_url[0]
                    w(f"Connecting to {url}...\n", "cyan")
                    w("HTTP/1.1 200 OK\n", "ok")
                    w("Server: MicroOS-Httpd/2.0 (x86_64 Rust)\n", "muted")
                    w("Content-Type: application/json\n", "muted")
                    w("Transfer-Encoding: chunked\n\n", "muted")
                    w(f'{{"status": "success", "os": "Rust Micro-OS", "ip": "{self.wifi_ip}", "wifi": "{self.wifi_ssid}", "message": "Hello from Micro-OS HTTP Engine!"}}\n', "purple")

            elif cmd == "calc":
                if not args:
                    self._open_calculator()
                    w("Opened MicroCalc graphical calculator.\n", "ok")
                else:
                    expr = " ".join(args)
                    try:
                        allowed = set("0123456789+-*/%(). xabcdefABCDEF")
                        if all(c in allowed for c in expr):
                            res = eval(expr, {"__builtins__": None}, {})
                            w(f"= {res}\n", "ok")
                        else:
                            w("calc: invalid character in expression\n", "error")
                    except Exception as ex:
                        w(f"calc error: {ex}\n", "error")

            elif cmd == "snap":
                sub = args[0].lower() if args else "help"
                if sub == "help":
                    w("Snap Store Package Manager CLI:\n", "cyan")
                    w("  snap list           List installed snap packages\n", "output")
                    w("  snap search <term>  Search software catalog\n", "output")
                    w("  snap install <pkg>  Download & install a snap package\n", "output")
                    w("  snap remove <pkg>   Uninstall a snap package\n", "output")
                    w("  snap info <pkg>     Display detailed package metadata\n", "output")
                    w("  store               Open graphical Snap Store\n", "output")

                elif sub == "list":
                    w(f"{'Name':<16} {'Version':<10} {'Rev':<5} {'Tracking':<10} {'Publisher':<14} {'Notes'}\n", "muted")
                    w(f"{'core22':<16} {'2.0.0':<10} {'1':<5} {'latest':<10} {'micro-os':<14} {'base'}\n", "ok")
                    w(f"{'virtio-net':<16} {'1.4.2':<10} {'8':<5} {'stable':<10} {'kernel':<14} {'driver'}\n", "ok")
                    w(f"{'wlan-driver':<16} {'2.1.0':<10} {'4':<5} {'stable':<10} {'kernel':<14} {'driver'}\n", "ok")
                    for pname, pdata in self.snap_packages.items():
                        if pdata.get("installed"):
                            pub = pdata.get("developer", "dev").split(" • ")[0]
                            w(f"{pname:<16} {pdata['version']:<10} {'14':<5} {'stable':<10} {pub:<14} {'app'}\n", "ok")

                elif sub == "search":
                    query = args[1].lower() if len(args) > 1 else ""
                    w(f"{'Name':<16} {'Version':<10} {'Publisher':<16} {'Summary'}\n", "muted")
                    found = 0
                    for pname, pdata in self.snap_packages.items():
                        if not query or query in pname.lower() or query in pdata["summary"].lower() or query in pdata["category"].lower():
                            pub = pdata.get("developer", "dev").split(" • ")[0]
                            w(f"{pname:<16} {pdata['version']:<10} {pub:<16} {pdata['summary']}\n", "output")
                            found += 1
                    w(f"\nDiscovered {found} snap packages matching '{query}'.\n", "muted")

                elif sub == "install":
                    clean_pkgs = [a for a in args[1:] if not a.startswith("-")]
                    if not clean_pkgs:
                        w("snap install: missing package name. Usage: snap install <pkg>\n", "error")
                    else:
                        pkg = clean_pkgs[0].lower()
                        if pkg in self.snap_packages:
                            if self.snap_packages[pkg].get("installed"):
                                w(f"snap \"{pkg}\" is already installed.\n", "muted")
                            else:
                                pdata = self.snap_packages[pkg]
                                w(f"Fetching snap \"{pkg}\" ({pdata['size']})...\n", "cyan")
                                w(f"[snapd] Verifying cryptographic SHA256 assertion for {pkg}...\n", "muted")
                                w(f"[snapd] Mounting squashfs filesystem image to /snap/{pkg}/current...\n", "muted")
                                self.snap_packages[pkg]["installed"] = True
                                w(f"✓ {pkg} {pdata['version']} from {pdata['developer']} installed!\n", "ok")
                                w(f"Run '{pkg}' in terminal or open from Snap Store / Taskbar.\n", "amber")
                        else:
                            w(f"error: snap \"{pkg}\" not found in stable channel. Use 'snap search <term>'.\n", "error")

                elif sub == "remove":
                    clean_pkgs = [a for a in args[1:] if not a.startswith("-")]
                    if not clean_pkgs:
                        w("snap remove: missing package name. Usage: snap remove <pkg>\n", "error")
                    else:
                        pkg = clean_pkgs[0].lower()
                        if pkg in self.snap_packages and self.snap_packages[pkg].get("installed"):
                            self.snap_packages[pkg]["installed"] = False
                            w(f"[snapd] Unmounted /snap/{pkg}...\n", "muted")
                            w(f"✓ {pkg} removed successfully.\n", "ok")
                        else:
                            w(f"error: snap \"{pkg}\" is not currently installed.\n", "error")

                elif sub == "info":
                    clean_pkgs = [a for a in args[1:] if not a.startswith("-")]
                    if not clean_pkgs:
                        w("snap info: missing package name. Usage: snap info <pkg>\n", "error")
                    else:
                        pkg = clean_pkgs[0].lower()
                        if pkg in self.snap_packages:
                            p = self.snap_packages[pkg]
                            w(f"name:      {p['name']}\n", "cyan")
                            w(f"summary:   {p['summary']}\n", "output")
                            w(f"publisher: {p['developer']}\n", "output")
                            w(f"version:   {p['version']}\n", "output")
                            w(f"installed: {'yes' if p['installed'] else 'no'}\n", "ok" if p['installed'] else "muted")
                            w(f"rating:    {p['rating']}\n", "amber")
                            w(f"size:      {p['size']}\n", "output")
                            w(f"channels:  stable (latest: {p['version']})\n", "muted")
                        else:
                            w(f"error: snap \"{pkg}\" not found.\n", "error")
                else:
                    w(f"snap: unknown command '{sub}'. Use: list, search, install, remove, info\n", "error")

            elif cmd == "history":
                for idx, h in enumerate(self.cmd_history, 1):
                    w(f"  {idx:>3}  {h}\n", "output")

            elif cmd in ("browser", "web"):
                self._open_browser()
                w("Opened MicroBrowser.\n", "ok")

            elif cmd in ("files", "explorer"):
                self._open_finder()
                w("Opened File Explorer.\n", "ok")

            elif cmd in ("taskmgr", "monitor"):
                self._open_taskmanager()
                w("Opened Task Manager.\n", "ok")

            elif cmd == "settings":
                self._open_settings()
                w("Opened System Settings.\n", "ok")

            elif cmd in ("store", "snap-store", "appstore"):
                self._open_snap_store()
                w("Opened Snap Store Software Center.\n", "ok")

            elif cmd == "doom":
                self._open_doom_viewer()
                w("Launching Doom Micro (1993 Raycaster Engine)...\n", "cyan")

            elif cmd == "snake":
                self._open_snake_game()
                w("Launching Snake Arcade mini-game...\n", "ok")

            elif cmd in ("exit", "quit"):
                w("Terminal session terminated.\n", "amber")
                win.destroy()

            elif cmd in ("reboot", "shutdown"):
                w("Broadcast message from macha@micro-os-x86:\n", "amber")
                w("The system is going down for maintenance NOW!\n", "amber")
                w("[TICK] Syncing filesystems... OK\n", "muted")
                w("[TICK] Stopping snapd daemon... OK\n", "muted")
                w("[TICK] Bringing down wlan0 interface... OK\n", "muted")
                w("[TICK] Kernel halted. Power off.\n", "error")

            else:
                w(f"micro-sh: command not found: '{cmd}'. Type 'help' for available commands.\n", "error")
        cmd_entry.bind("<Return>", execute_cmd)

    # ─── App 3: Activity Monitor ──────────────────────────────────────────────

    def _open_taskmanager(self):
        win, content = self._make_window(
            "📊  Activity Monitor — Rust Micro-OS",
            720, 500, offset_x=130, offset_y=90)

        # CPU Graph
        graph_frame = tk.Frame(content, bg=WIN_CHROME,
                               highlightbackground=WIN_BORDER, highlightthickness=1)
        graph_frame.pack(fill=tk.X, padx=12, pady=(10, 4))
        tk.Label(graph_frame, text="  CPU UTILIZATION — virtio-vCPU (x4 cores virtualized)",
                 bg=WIN_CHROME, fg=TEXT_MUTED, font=("SF Pro Display", 10),
                 anchor="w").pack(fill=tk.X, padx=6, pady=4)

        graph_canvas = tk.Canvas(graph_frame, bg="#101014", height=80, highlightthickness=0)
        graph_canvas.pack(fill=tk.X, padx=6, pady=4)

        self._cpu_history = [random.randint(10, 70) for _ in range(80)]

        def redraw_graph():
            graph_canvas.delete("all")
            w = graph_canvas.winfo_width() or 680
            n = len(self._cpu_history)
            bar_w = max(1, w // n)
            for i, v in enumerate(self._cpu_history):
                x0 = i * bar_w
                h_bar = int(v * 60 / 100)
                # Color: green → amber → red based on usage
                if v < 40:
                    col = ACCENT_GREEN
                elif v < 70:
                    col = ACCENT_AMBER
                else:
                    col = BTN_CLOSE
                graph_canvas.create_rectangle(x0, 70 - h_bar, x0 + bar_w - 1, 70,
                                              fill=col, outline="")
            graph_canvas.create_line(0, 70, w, 70, fill=WIN_BORDER, width=1)
            graph_canvas.after(400, lambda: (
                self._cpu_history.append(max(5, min(95, self._cpu_history[-1] + random.randint(-15, 15)))),
                self._cpu_history.pop(0),
                redraw_graph()
            ))

        graph_canvas.after(100, redraw_graph)

        # Process Table
        tbl_frame = tk.Frame(content, bg=WIN_CHROME)
        tbl_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        columns = ("PID", "Name", "Priority", "State", "CPU%", "Memory", "Burst")
        tree = ttk.Treeview(tbl_frame, columns=columns, show="headings",
                            style="Custom.Treeview", height=10)
        tree.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=WIN_CONTENT_BG, foreground=TEXT_PRIMARY,
                         fieldbackground=WIN_CONTENT_BG, rowheight=24,
                         font=("SF Pro Mono", 10))
        style.configure("Custom.Treeview.Heading",
                         background=WIN_CHROME, foreground=TEXT_MUTED,
                         font=("SF Pro Display", 10, "bold"))
        style.map("Custom.Treeview", background=[("selected", SELECTION_BG)])

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=90, anchor="center")

        processes = [
            ("1", "SysMonitor",  "2", "RUNNING",  "12%",  "4.2 KB", "6"),
            ("2", "NetPacket",   "1", "READY",    "8%",   "6.8 KB", "4"),
            ("3", "DiskFlusher", "3", "READY",    "4%",   "2.1 KB", "5"),
            ("4", "Compositor",  "1", "READY",    "14%",  "12.4 KB","8"),
            ("5", "AudioServer", "2", "BLOCKED",  "0%",   "1.8 KB", "3"),
            ("6", "BatchJob",    "8", "READY",    "2%",   "0.9 KB", "12"),
            ("7", "RealtimeAud","1",  "RUNNING",  "18%",  "3.2 KB", "8"),
            ("8", "DrvPoll",    "4",  "READY",    "1%",   "0.5 KB", "2"),
        ]

        for row in processes:
            tag = "run" if row[3] == "RUNNING" else ("blocked" if row[3] == "BLOCKED" else "")
            tree.insert("", tk.END, values=row, tags=(tag,))

        tree.tag_configure("run", foreground=ACCENT_GREEN)
        tree.tag_configure("blocked", foreground=TEXT_MUTED)

        # Memory telemetry bar at bottom
        mem_frame = tk.Frame(content, bg=WIN_CHROME,
                             highlightbackground=WIN_BORDER, highlightthickness=1)
        mem_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
        mem_canvas = tk.Canvas(mem_frame, bg=WIN_CHROME, height=24, highlightthickness=0)
        mem_canvas.pack(fill=tk.X, padx=8, pady=6)

        def draw_mem_bar():
            mem_canvas.delete("all")
            w = mem_canvas.winfo_width() or 680
            used_pct = 0.42
            mem_canvas.create_rectangle(0, 4, w, 18, fill="#222530", outline=WIN_BORDER)
            mem_canvas.create_rectangle(0, 4, int(w * used_pct), 18, fill=ACCENT_BLUE, outline="")
            mem_canvas.create_text(w // 2, 11, text=f"Heap Used: 42% (27 KB / 64 KB)",
                                   fill=TEXT_PRIMARY, font=("SF Pro Mono", 9))
            mem_canvas.after(2000, draw_mem_bar)

        mem_canvas.after(100, draw_mem_bar)

    # ─── App 4: MicroFinder ───────────────────────────────────────────────────

    def _open_finder(self):
        win, content = self._make_window(
            "🗂  MicroFinder — /system/drivers/net",
            700, 480, offset_x=160, offset_y=110)

        # Breadcrumb bar
        breadcrumb = tk.Frame(content, bg=WIN_CHROME, height=32)
        breadcrumb.pack(fill=tk.X)
        breadcrumb.pack_propagate(False)
        tk.Label(breadcrumb, text="  Computer  ›  OS (C:)  ›  system  ›  drivers  ›  net",
                 bg=WIN_CHROME, fg=TEXT_MUTED, font=("SF Pro Display", 10),
                 anchor="w").pack(fill=tk.X, padx=10, pady=6)
        tk.Frame(content, bg=WIN_BORDER, height=1).pack(fill=tk.X)

        body = tk.Frame(content, bg=WIN_CONTENT_BG)
        body.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg="#16171F", width=150)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Frame(body, bg=WIN_BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        SIDEBAR_ITEMS = [
            ("FAVORITES", None, TEXT_MUTED),
            ("  Desktop",    "🖥", TEXT_PRIMARY),
            ("  Documents",  "📄", TEXT_PRIMARY),
            ("  Downloads",  "⬇", TEXT_PRIMARY),
            ("  Network",    "🌐", TEXT_PRIMARY),
            ("LOCATIONS", None, TEXT_MUTED),
            ("  Hard Disk",  "💾", TEXT_PRIMARY),
            ("  VirtualBox", "📦", TEXT_PRIMARY),
        ]
        for text, icon, col in SIDEBAR_ITEMS:
            label = f"{icon}  {text}" if icon else text
            lbl = tk.Label(sidebar, text=label, bg="#16171F", fg=col,
                           font=("SF Pro Display", 10 if icon else 9),
                           anchor="w", padx=10, pady=3)
            lbl.pack(fill=tk.X)

        # Main file grid
        main_area = tk.Frame(body, bg=WIN_CONTENT_BG)
        main_area.pack(fill=tk.BOTH, expand=True)

        columns = ("Name", "Kind", "Size", "Modified")
        tree = ttk.Treeview(main_area, columns=columns, show="headings",
                            style="Custom.Treeview", height=16)
        tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        for col in columns:
            tree.heading(col, text=col)
        tree.column("Name", width=240)
        tree.column("Kind", width=100)
        tree.column("Size", width=80)
        tree.column("Modified", width=120)

        files = [
            ("📁 ..  (parent directory)",  "Folder",  "—",      "17 Nov 2026"),
            ("📁 virtio_net",              "Folder",  "—",      "17 Nov 2026"),
            ("📁 e1000",                   "Folder",  "—",      "17 Nov 2026"),
            ("📄 tcp_ip.sys",              "Driver",  "48 KB",  "17 Nov 2026"),
            ("📄 icmp_echo.sys",           "Driver",  "12 KB",  "17 Nov 2026"),
            ("📄 udp.sys",                 "Driver",  "8 KB",   "17 Nov 2026"),
            ("📄 arp_cache.sys",           "Driver",  "4 KB",   "17 Nov 2026"),
            ("📄 socket.sys",              "Driver",  "32 KB",  "17 Nov 2026"),
            ("📄 http_client.sys",         "Driver",  "20 KB",  "17 Nov 2026"),
            ("🔧 config.ini",              "Config",  "2 KB",   "17 Nov 2026"),
        ]

        for row in files:
            tag = "folder" if row[1] == "Folder" else "file"
            tree.insert("", tk.END, values=row, tags=(tag,))

        tree.tag_configure("folder", foreground=ACCENT_BLUE)
        tree.tag_configure("file",   foreground=TEXT_PRIMARY)

        # Status bar
        status_bar = tk.Frame(content, bg=WIN_CHROME, height=24)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(status_bar, text="  10 items  |  virtio-net0 driver source tree  |  Read-Only",
                 bg=WIN_CHROME, fg=TEXT_MUTED,
                 font=("SF Pro Display", 9), anchor="w").pack(fill=tk.X, padx=8)

    # ─── App 5: System Settings ───────────────────────────────────────────────

    def _open_settings(self):
        win, content = self._make_window(
            "⚙  System Preferences — Rust Micro-OS",
            680, 520, offset_x=100, offset_y=80)

        # Header card
        header = tk.Frame(content, bg=WIN_CHROME, height=90,
                          highlightbackground=WIN_BORDER, highlightthickness=1)
        header.pack(fill=tk.X, padx=12, pady=12)
        header.pack_propagate(False)

        logo_frame = tk.Frame(header, bg=ACCENT_BLUE, width=70, height=70)
        logo_frame.pack(side=tk.LEFT, padx=16, pady=10)
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="🦀", font=("SF Pro Display", 28),
                 bg=ACCENT_BLUE).pack(expand=True)

        info_frame = tk.Frame(header, bg=WIN_CHROME)
        info_frame.pack(side=tk.LEFT, padx=8, pady=10)
        tk.Label(info_frame, text="Rust Micro-OS  v2.0.0", bg=WIN_CHROME,
                 fg=TEXT_PRIMARY, font=("SF Pro Display", 15, "bold")).pack(anchor="w")
        tk.Label(info_frame, text="macOS Ventura + Windows 11 Fluent Desktop Environment",
                 bg=WIN_CHROME, fg=ACCENT_GREEN,
                 font=("SF Pro Display", 10)).pack(anchor="w")
        tk.Label(info_frame, text="100% Rust  •  Zero C dependencies  •  VirtualBox x86_64",
                 bg=WIN_CHROME, fg=TEXT_MUTED,
                 font=("SF Pro Display", 9)).pack(anchor="w")

        # Specs list
        specs_frame = tk.Frame(content, bg=WIN_CHROME,
                               highlightbackground=WIN_BORDER, highlightthickness=1)
        specs_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        SPECS = [
            ("Kernel Architecture",  "Microkernel x86_64 (Bare-Metal + VirtualBox)"),
            ("Scheduler",            "Preemptive Round Robin (Q=3) + Priority Aging"),
            ("Memory Allocator",     "Free-List Coalescing Allocator (64 KiB Heap)"),
            ("Synchronization",      "Atomic Spinlocks + Cooperative Mutex (Deadlock Detection)"),
            ("Ethernet Interface",   "virtio-net0  |  MAC: 52:54:00:12:34:56  |  10 Gbps"),
            ("Wi-Fi Interface",      "wlan0: IEEE 802.11ax Wi-Fi 6  |  MAC: 3C:06:30:AB:CD:EF"),
            ("Wi-Fi Network",        "Connected to 'Home-Fiber-5G' (Channel 36, 5 GHz, 95% Signal)"),
            ("IPv4 Address",         "192.168.1.142 / 24   GW: 192.168.1.1   DNS: 8.8.8.8"),
            ("Protocol Stack",       "Ethernet II → ARP → IPv4 → ICMP / TCP / UDP → HTTP 1.1 + WPA2/3"),
            ("Display",              "32-bit TrueColor 1024×768 Framebuffer (Acrylic Glass)"),
            ("Window Manager",       "Floating Compositor  |  macOS Traffic Lights  |  Drag & Drop"),
            ("System Call Table",    "yield, sleep, malloc, free, print, exit, socket, ping, wifi"),
            ("Test Coverage",        "TC1–TC9: Scheduler, Memory, Sync, Net, GUI, Wi-Fi (9/9 PASS ✓)"),
            ("Rust Edition",         "2021  |  no_std bare-metal + std simulation harness"),
        ]

        for label, val in SPECS:
            row = tk.Frame(specs_frame, bg=WIN_CHROME)
            row.pack(fill=tk.X)
            tk.Frame(row, bg=WIN_BORDER, height=1).pack(fill=tk.X)
            inner = tk.Frame(row, bg=WIN_CHROME)
            inner.pack(fill=tk.X, padx=12, pady=4)
            tk.Label(inner, text=label, bg=WIN_CHROME, fg=TEXT_MUTED,
                     font=("SF Pro Display", 10), width=22, anchor="w").pack(side=tk.LEFT)
            tk.Label(inner, text=val, bg=WIN_CHROME, fg=TEXT_PRIMARY,
                     font=("SF Pro Mono", 10)).pack(side=tk.LEFT)

    # ─── App 6: Wi-Fi Settings & Scanner ─────────────────────────────────────

    def _open_wifi_manager(self):
        win, content = self._make_window(
            "📶  Wi-Fi Control Center & Scanner — wlan0 (802.11ax)",
            840, 600, offset_x=120, offset_y=60)

        # ── 1. Top Control Strip (Power Toggle & Quick Scan)
        top_bar = tk.Frame(content, bg=WIN_CHROME, height=48,
                           highlightbackground=WIN_BORDER, highlightthickness=1)
        top_bar.pack(fill=tk.X, padx=12, pady=(10, 6))
        top_bar.pack_propagate(False)

        tk.Label(top_bar, text="Wi-Fi Radio (wlan0):", bg=WIN_CHROME,
                 fg=TEXT_PRIMARY, font=("SF Pro Display", 11, "bold")).pack(side=tk.LEFT, padx=(14, 8))

        power_btn = tk.Button(top_bar, text="● ON", bg="#1C4B27", fg=ACCENT_GREEN,
                              activebackground="#256B37", activeforeground=TEXT_PRIMARY,
                              font=("SF Pro Display", 10, "bold"), relief="flat", padx=12, pady=2,
                              cursor="hand2")
        power_btn.pack(side=tk.LEFT, padx=4)

        scan_status_lbl = tk.Label(top_bar, text="● Radio Active (2.4 & 5 GHz)", bg=WIN_CHROME,
                                   fg=ACCENT_GREEN, font=("SF Pro Display", 10))
        scan_status_lbl.pack(side=tk.LEFT, padx=14)

        scan_btn = tk.Button(top_bar, text="🔍  Scan Wi-Fi Networks", bg=ACCENT_BLUE, fg=TEXT_PRIMARY,
                             activebackground="#0066CC", activeforeground=TEXT_PRIMARY,
                             font=("SF Pro Display", 10, "bold"), relief="flat", padx=14, pady=3,
                             cursor="hand2")
        scan_btn.pack(side=tk.RIGHT, padx=12)

        # ── 2. Active Connection Status Card (macOS / Win11 Fluent Card)
        card = tk.Frame(content, bg=WIN_CHROME,
                        highlightbackground=WIN_BORDER, highlightthickness=1)
        card.pack(fill=tk.X, padx=12, pady=6)

        card_top = tk.Frame(card, bg=WIN_CHROME)
        card_top.pack(fill=tk.X, padx=14, pady=(10, 4))

        status_icon = tk.Label(card_top, text="📶", font=("SF Pro Display", 22), bg=WIN_CHROME)
        status_icon.pack(side=tk.LEFT, padx=(0, 10))

        status_info = tk.Frame(card_top, bg=WIN_CHROME)
        status_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ssid_title = tk.Label(status_info, text=f"{self.wifi_ssid}",
                              bg=WIN_CHROME, fg=TEXT_PRIMARY,
                              font=("SF Pro Display", 13, "bold"), anchor="w")
        ssid_title.pack(fill=tk.X)

        conn_sub = tk.Label(status_info,
                            text=f"Connected, open ({self.wifi_security})  •  Internet Access  •  BSSID: 84:23:88:95:3d:ec",
                            bg=WIN_CHROME, fg=ACCENT_GREEN,
                            font=("SF Pro Display", 10), anchor="w")
        conn_sub.pack(fill=tk.X)

        disc_btn = tk.Button(card_top, text="Disconnect", bg="#F4F4F4", fg="#C42B1C",
                             activebackground="#E5E5E5", activeforeground="#C42B1C",
                             font=("SF Pro Display", 10, "bold"), relief="flat", padx=12, pady=4,
                             cursor="hand2", bd=1)
        disc_btn.pack(side=tk.RIGHT, padx=6)

        # IP Details Grid
        details_grid = tk.Frame(card, bg=WIN_CHROME)
        details_grid.pack(fill=tk.X, padx=14, pady=(4, 10))
        tk.Frame(card, bg=WIN_BORDER, height=1).pack(fill=tk.X, padx=14, pady=(0, 8))

        detail_lbl_widgets = {}
        detail_fields = [
            ("IPv4 Address:", f"{self.wifi_ip} / 24"),
            ("Default Gateway:", "192.168.1.1"),
            ("Physical Adapter (MAC):", "90:10:57:C0:0B:7A (Intel AX203)"),
            ("Band & Channel:", f"{self.wifi_band}  •  Channel {self.wifi_channel}"),
            ("Signal Strength:", f"{self.wifi_signal}% (-38 dBm)  •  4 Bars"),
            ("Link Speed / Standard:", "780 Mbps  •  Wi-Fi 6 (802.11ax)"),
        ]

        for idx, (k, v) in enumerate(detail_fields):
            row = idx // 2
            col = (idx % 2) * 2
            tk.Label(details_grid, text=k, bg=WIN_CHROME, fg=TEXT_MUTED,
                     font=("SF Pro Display", 9), anchor="w").grid(row=row, column=col, sticky="w", padx=(0, 6), pady=2)
            val_lbl = tk.Label(details_grid, text=v, bg=WIN_CHROME, fg=TEXT_PRIMARY,
                               font=("SF Pro Mono", 9), anchor="w")
            val_lbl.grid(row=row, column=col+1, sticky="w", padx=(0, 20), pady=2)
            detail_lbl_widgets[k] = val_lbl

        # ── 3. Scanned 802.11 Access Points Table
        table_frame = tk.Frame(content, bg=WIN_CHROME,
                               highlightbackground=WIN_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        table_header = tk.Frame(table_frame, bg=WIN_CHROME, height=28)
        table_header.pack(fill=tk.X, padx=10, pady=(6, 2))
        tk.Label(table_header, text="Discovered 802.11 Wireless Access Points (Beacon Scan):",
                 bg=WIN_CHROME, fg=TEXT_PRIMARY, font=("SF Pro Display", 10, "bold")).pack(side=tk.LEFT)

        columns = ("Signal", "SSID", "Security", "Channel", "Band", "Signal %", "Status")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                            style="Custom.Treeview", height=5)
        tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tree.heading("Signal", text="Signal")
        tree.heading("SSID", text="Network Name (SSID)")
        tree.heading("Security", text="Security")
        tree.heading("Channel", text="Ch")
        tree.heading("Band", text="Band")
        tree.heading("Signal %", text="Signal %")
        tree.heading("Status", text="Status")

        tree.column("Signal", width=55, anchor="center")
        tree.column("SSID", width=220)
        tree.column("Security", width=130)
        tree.column("Channel", width=40, anchor="center")
        tree.column("Band", width=70, anchor="center")
        tree.column("Signal %", width=80, anchor="center")
        tree.column("Status", width=90, anchor="center")

        tree.tag_configure("connected", foreground=ACCENT_GREEN)
        tree.tag_configure("available", foreground=TEXT_PRIMARY)

        # ── 4. Connection & Authentication Control Strip
        action_bar = tk.Frame(content, bg=WIN_CHROME, height=44,
                              highlightbackground=WIN_BORDER, highlightthickness=1)
        action_bar.pack(fill=tk.X, padx=12, pady=4)

        tk.Label(action_bar, text="Selected AP:", bg=WIN_CHROME, fg=TEXT_MUTED,
                 font=("SF Pro Display", 10)).pack(side=tk.LEFT, padx=(10, 4))
        selected_ssid_var = tk.StringVar(value="Home-Fiber-5G")
        selected_lbl = tk.Label(action_bar, textvariable=selected_ssid_var, bg=WIN_CHROME,
                                fg=ACCENT_BLUE, font=("SF Pro Display", 10, "bold"), width=20, anchor="w")
        selected_lbl.pack(side=tk.LEFT, padx=4)

        tk.Label(action_bar, text="Password:", bg=WIN_CHROME, fg=TEXT_MUTED,
                 font=("SF Pro Display", 10)).pack(side=tk.LEFT, padx=(10, 4))
        pass_var = tk.StringVar(value="SecretWiFiPass123")
        pass_entry = tk.Entry(action_bar, textvariable=pass_var, show="•", bg="#2A2D3A",
                              fg=TEXT_PRIMARY, font=("SF Pro Mono", 10), width=18, relief="flat", bd=3)
        pass_entry.pack(side=tk.LEFT, padx=4)

        connect_btn = tk.Button(action_bar, text="  Connect  ", bg=ACCENT_GREEN, fg="#000000",
                                activebackground="#40E060", activeforeground="#000000",
                                font=("SF Pro Display", 10, "bold"), relief="flat", padx=12, pady=3,
                                cursor="hand2")
        connect_btn.pack(side=tk.RIGHT, padx=10)

        # ── 5. 4-Way Handshake & Diagnostics Output Log
        log_frame = tk.Frame(content, bg=WIN_CHROME, height=90,
                             highlightbackground=WIN_BORDER, highlightthickness=1)
        log_frame.pack(fill=tk.X, padx=12, pady=(4, 10))
        log_frame.pack_propagate(False)

        log_text = tk.Text(log_frame, bg="#101014", fg=ACCENT_GREEN,
                           font=("SF Pro Mono", 9), relief="flat", bd=4,
                           state="disabled", cursor="arrow", wrap="word")
        log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        def log_msg(msg, color=ACCENT_GREEN):
            log_text.configure(state="normal")
            log_text.insert(tk.END, msg + "\n")
            log_text.see(tk.END)
            log_text.configure(state="disabled")

        log_msg("[wlan0] 802.11ax Radio operational. Associated with 'Home-Fiber-5G' (IP: 192.168.1.142)")
        log_msg("[WPA3] SAE Handshake complete. Pairwise Transient Key active (AES-CCMP-128)")

        # Populate Scanned Networks from Physical Device
        discovered_nets = self.scan_device_wifi()
        sample_networks = []
        for n in discovered_nets:
            sample_networks.append((
                n.get("signal_icon", "📶 4b"),
                n.get("ssid", "Unknown"),
                n.get("security", "Open"),
                n.get("channel", "1"),
                n.get("band", "5 GHz"),
                n.get("signal", "80%"),
                n.get("status", "Available"),
                n.get("tag", "available")
            ))

        def refresh_table(networks):
            tree.delete(*tree.get_children())
            for row in networks:
                tree.insert("", tk.END, values=row[:7], tags=(row[7],))

        refresh_table(sample_networks)

        def on_select_network(event):
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                vals = item["values"]
                if vals:
                    ssid = vals[1]
                    selected_ssid_var.set(ssid)
                    if vals[2] == "Open / None":
                        pass_var.set("")
                        pass_entry.configure(state="disabled")
                    else:
                        pass_entry.configure(state="normal")
                        if not pass_var.get():
                            pass_var.set("SecretWiFiPass123")

        tree.bind("<<TreeviewSelect>>", on_select_network)

        # ── Wi-Fi Scan Handler
        def perform_scan():
            if not self.wifi_power:
                log_msg("[ERROR] Cannot scan: Wi-Fi radio is turned OFF", "#FF5F57")
                return

            scan_btn.configure(state="disabled", text="Scanning...")
            scan_status_lbl.configure(text="Scanning host adapter (Intel Wi-Fi 6 AX203)...", fg=ACCENT_AMBER)
            log_msg("[SCAN] wlan0 sweeping 2.4 GHz (Channels 1–14) and 5 GHz (Channels 36–165)...", ACCENT_BLUE)

            def finish_scan():
                scan_btn.configure(state="normal", text="🔄  Scan Wi-Fi Networks")
                fresh_nets = self.scan_device_wifi()
                updated = []
                for n in fresh_nets:
                    is_curr = (n["ssid"] == self.wifi_ssid and self.wifi_connected)
                    stat = "Connected" if is_curr else "Available"
                    tag = "connected" if is_curr else "available"
                    updated.append((
                        n.get("signal_icon", "📶 4b"),
                        n["ssid"],
                        n.get("security", "Open"),
                        n.get("channel", "1"),
                        n.get("band", "5 GHz"),
                        n.get("signal", "80%"),
                        stat,
                        tag
                    ))
                scan_status_lbl.configure(text=f"Scan complete: {len(updated)} Access Points found", fg=ACCENT_GREEN)
                log_msg(f"[SCAN] Discovered {len(updated)} access points on host device: {', '.join(n['ssid'] for n in fresh_nets[:4])}")
                refresh_table(updated)

            win.after(800, finish_scan)

        scan_btn.configure(command=perform_scan)

        # ── Wi-Fi Connect Handler
        def perform_connect():
            if not self.wifi_power:
                log_msg("[ERROR] Cannot connect: Wi-Fi radio is turned OFF", "#FF5F57")
                return

            target_ssid = selected_ssid_var.get()
            pwd = pass_var.get()

            # Find network info
            target_info = next((n for n in sample_networks if n[1] == target_ssid), None)
            if not target_info:
                return

            is_open = (target_info[2] == "Open / None")
            if not is_open and len(pwd) < 8:
                log_msg(f"[AUTH ERROR] WPA passphrase must be >= 8 characters (given {len(pwd)})", "#FF5F57")
                return

            connect_btn.configure(state="disabled", text="Connecting...")
            log_msg(f"[AUTH] Initiating 802.11 Association with SSID '{target_ssid}'...", ACCENT_BLUE)

            def step1():
                log_msg(f"  [1/4] Association Request accepted by BSSID. Capability: 802.11ax, Channel: {target_info[3]}")
                win.after(200, step2)

            def step2():
                if not is_open:
                    log_msg("  [2/4] WPA2-PSK 4-Way Handshake: EAPOL-Key M1 received (Anonce generated by AP)")
                    log_msg("  [3/4] EAPOL-Key M2 sent (Snonce + HMAC-SHA256 MIC computed with PMK)")
                    win.after(200, step3)
                else:
                    win.after(100, step3)

            def step3():
                if not is_open:
                    log_msg("  [4/4] EAPOL-Key M3 received (GTK installed) • EAPOL-Key M4 ACK sent")
                    log_msg("  [WPA2] 4-Way Handshake Successful! Pairwise Transient Key active.")
                win.after(200, step4)

            def step4():
                log_msg("  [DHCP] Broadcasting DHCP Discover over wlan0...")
                log_msg("  [DHCP] DHCP Offer received from 192.168.1.1: Assigned IP 192.168.1.142")
                log_msg(f"✓ CONNECTED to '{target_ssid}'! Internet access established.")

                self.wifi_connected = True
                self.wifi_ssid = target_ssid
                self.wifi_channel = int(target_info[3])
                self.wifi_band = target_info[4]
                self.wifi_signal = int(target_info[5].replace("%", ""))
                self.wifi_security = target_info[2]

                # Update UI
                ssid_title.configure(text=f"{self.wifi_ssid}")
                conn_sub.configure(text=f"Connected, secured ({self.wifi_security})  •  Internet Access", fg=ACCENT_GREEN)
                status_icon.configure(text="📶", fg=TEXT_PRIMARY)
                disc_btn.configure(state="normal")
                connect_btn.configure(state="normal", text="  Connect  ")

                detail_lbl_widgets["Band & Channel:"].configure(text=f"{self.wifi_band}  •  Channel {self.wifi_channel}")
                detail_lbl_widgets["Signal Strength:"].configure(text=f"{self.wifi_signal}%  •  4 Bars")

                perform_scan()

            win.after(200, step1)

        connect_btn.configure(command=perform_connect)

        # ── Wi-Fi Disconnect Handler
        def perform_disconnect():
            if not self.wifi_connected:
                return
            log_msg(f"[DEAUTH] Sending 802.11 Deauthentication frame to '{self.wifi_ssid}'", "#FFD60A")
            log_msg("[DHCP] Releasing IPv4 lease 192.168.1.142 on wlan0")
            log_msg("[wlan0] Disconnected from Wi-Fi. Interface state: IDLE", "#FFD60A")

            self.wifi_connected = False
            ssid_title.configure(text="Not Connected")
            conn_sub.configure(text="Wi-Fi radio active  •  No active network connection", fg=ACCENT_AMBER)
            status_icon.configure(text="○", fg=TEXT_MUTED)
            disc_btn.configure(state="disabled")

            detail_lbl_widgets["IPv4 Address:"].configure(text="0.0.0.0 (Unspecified)")
            detail_lbl_widgets["Band & Channel:"].configure(text="Idle")
            detail_lbl_widgets["Signal Strength:"].configure(text="0% (Disconnected)")

            perform_scan()

        disc_btn.configure(command=perform_disconnect)

        # ── Power Toggle Handler
        def toggle_power():
            self.wifi_power = not self.wifi_power
            if self.wifi_power:
                power_btn.configure(text="● ON", bg="#1C4B27", fg=ACCENT_GREEN)
                scan_status_lbl.configure(text="● Radio Active (2.4 & 5 GHz)", fg=ACCENT_GREEN)
                log_msg("[wlan0] 802.11 Wireless Radio powered ON")
                perform_connect()
            else:
                power_btn.configure(text="○ OFF", bg="#3A2020", fg="#FF6B6B")
                scan_status_lbl.configure(text="○ Radio Powered Off", fg=TEXT_MUTED)
                perform_disconnect()
                log_msg("[wlan0] 802.11 Wireless Radio powered OFF", "#FF5F57")

        power_btn.configure(command=toggle_power)

    # ─── Snap Store Application Window ──────────────────────────────────────

    def _open_snap_store(self):
        win, content = self._make_window(
            "🛍️  Snap Store — Software Center (v2.60.2)",
            820, 560, offset_x=120, offset_y=70)

        # Header bar: Search and Category Pills
        top_bar = tk.Frame(content, bg=WIN_CHROME, height=54,
                           highlightbackground=WIN_BORDER, highlightthickness=1)
        top_bar.pack(fill=tk.X, padx=12, pady=(10, 6))
        top_bar.pack_propagate(False)

        # Search icon + Entry
        search_box = tk.Frame(top_bar, bg="#2A2D3A", padx=8, pady=4)
        search_box.pack(side=tk.LEFT, padx=10, pady=8)
        tk.Label(search_box, text="🔍", bg="#2A2D3A", fg=TEXT_MUTED,
                 font=("SF Pro Display", 11)).pack(side=tk.LEFT, padx=(0, 4))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_box, textvariable=search_var, bg="#2A2D3A",
                                fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                font=("SF Pro Display", 10), width=22, relief="flat", bd=0)
        search_entry.pack(side=tk.LEFT)

        # Category buttons
        cat_frame = tk.Frame(top_bar, bg=WIN_CHROME)
        cat_frame.pack(side=tk.RIGHT, padx=10, pady=8)

        current_category = tk.StringVar(value="All")
        cat_buttons = {}

        # Scrollable / Canvas package grid
        main_canvas = tk.Canvas(content, bg="#181920", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#181920")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        canvas_win = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(event):
            main_canvas.itemconfig(canvas_win, width=event.width)

        main_canvas.bind("<Configure>", _on_canvas_configure)
        main_canvas.configure(yscrollcommand=scrollbar.set)

        status_bar = tk.Frame(content, bg=WIN_CHROME, height=28)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=(0, 4))
        status_lbl = tk.Label(status_bar, text="Ready", bg=WIN_CHROME, fg=TEXT_MUTED, font=("SF Pro Display", 9))
        status_lbl.pack(side=tk.LEFT, padx=4)

        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0), pady=(0, 6))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 12), pady=(0, 6))

        def render_packages():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            query = search_var.get().strip().lower()
            cat = current_category.get()

            # Filter
            filtered = []
            for pkg_id, pkg in self.snap_packages.items():
                if cat == "Installed" and not pkg.get("installed"):
                    continue
                if cat not in ("All", "Installed") and pkg.get("category") != cat:
                    continue
                if query and (query not in pkg_id and query not in pkg["name"].lower() and query not in pkg["summary"].lower()):
                    continue
                filtered.append((pkg_id, pkg))

            total_installed = sum(1 for p in self.snap_packages.values() if p.get("installed"))
            status_lbl.configure(text=f"Showing {len(filtered)} packages  •  {total_installed} installed on system  •  Canonical Snap Store (stable channel)")

            # Render 2-column grid of cards
            for idx, (pkg_id, pkg) in enumerate(filtered):
                row = idx // 2
                col = idx % 2

                card = tk.Frame(scrollable_frame, bg="#20222B",
                                highlightbackground="#2E3240", highlightthickness=1)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

                top_row = tk.Frame(card, bg="#20222B")
                top_row.pack(fill=tk.X, padx=10, pady=(10, 4))

                icon_lbl = tk.Label(top_row, text=pkg.get("icon", "📦"),
                                    font=("SF Pro Display", 22), bg="#20222B")
                icon_lbl.pack(side=tk.LEFT, padx=(0, 8))

                title_col = tk.Frame(top_row, bg="#20222B")
                title_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

                tk.Label(title_col, text=pkg["name"], bg="#20222B", fg=TEXT_PRIMARY,
                         font=("SF Pro Display", 11, "bold"), anchor="w").pack(fill=tk.X)
                tk.Label(title_col, text=f"{pkg['developer']}  •  v{pkg['version']}  •  {pkg['size']}",
                         bg="#20222B", fg=TEXT_MUTED, font=("SF Pro Display", 8), anchor="w").pack(fill=tk.X)

                tk.Label(top_row, text=pkg.get("rating", "★★★★☆"), bg="#20222B",
                         fg=ACCENT_AMBER, font=("SF Pro Display", 9)).pack(side=tk.RIGHT)

                tk.Label(card, text=pkg["summary"], bg="#20222B", fg="#C0C2D0",
                         font=("SF Pro Display", 9), anchor="w", justify=tk.LEFT, wraplength=340).pack(fill=tk.X, padx=10, pady=(0, 8))

                act_row = tk.Frame(card, bg="#20222B")
                act_row.pack(fill=tk.X, padx=10, pady=(0, 10))

                is_inst = pkg.get("installed", False)

                def make_install_handler(p_id=pkg_id):
                    def _h():
                        self.snap_packages[p_id]["installed"] = True
                        status_lbl.configure(text=f"✓ Successfully installed snap '{p_id}' from Canonical Store", fg=ACCENT_GREEN)
                        render_packages()
                    return _h

                def make_remove_handler(p_id=pkg_id):
                    def _h():
                        self.snap_packages[p_id]["installed"] = False
                        status_lbl.configure(text=f"Removed snap '{p_id}'", fg=ACCENT_AMBER)
                        render_packages()
                    return _h

                def make_launch_handler(p_id=pkg_id):
                    def _h():
                        if p_id == "micro-calc":
                            self._open_calculator()
                        elif p_id == "snake-arcade":
                            self._open_snake_game()
                        elif p_id == "doom-micro":
                            self._open_doom_viewer()
                        elif p_id in ("htop", "neofetch"):
                            self._open_terminal()
                        else:
                            status_lbl.configure(text=f"Launched '{p_id}' background process.", fg=ACCENT_GREEN)
                    return _h

                if is_inst:
                    inst_badge = tk.Label(act_row, text="✓ Installed", bg="#1C3827", fg=ACCENT_GREEN,
                                          font=("SF Pro Display", 9, "bold"), padx=8, pady=3)
                    inst_badge.pack(side=tk.LEFT)

                    launch_btn = tk.Button(act_row, text="Launch", bg="#2F3342", fg=TEXT_PRIMARY,
                                           activebackground=ACCENT_BLUE, activeforeground="#FFFFFF",
                                           font=("SF Pro Display", 9), relief="flat", padx=10, pady=2,
                                           cursor="hand2", command=make_launch_handler())
                    launch_btn.pack(side=tk.LEFT, padx=6)

                    rm_btn = tk.Button(act_row, text="Remove", bg="#3B2323", fg="#FF7B7B",
                                       activebackground="#502A2A", activeforeground="#FFA0A0",
                                       font=("SF Pro Display", 9), relief="flat", padx=8, pady=2,
                                       cursor="hand2", command=make_remove_handler())
                    rm_btn.pack(side=tk.RIGHT)
                else:
                    inst_btn = tk.Button(act_row, text="⬇  Install", bg="#E95420", fg="#FFFFFF",
                                         activebackground="#FF6F3D", activeforeground="#FFFFFF",
                                         font=("SF Pro Display", 9, "bold"), relief="flat", padx=14, pady=3,
                                         cursor="hand2", command=make_install_handler())
                    inst_btn.pack(side=tk.RIGHT)

            scrollable_frame.columnconfigure(0, weight=1)
            scrollable_frame.columnconfigure(1, weight=1)

        def set_cat(cat_name):
            current_category.set(cat_name)
            for name, btn in cat_buttons.items():
                if name == cat_name:
                    btn.configure(bg="#E95420", fg="#FFFFFF")
                else:
                    btn.configure(bg="#2A2D3A", fg=TEXT_MUTED)
            render_packages()

        CATEGORIES = ["All", "Utilities", "Development", "Networking", "Games & Fun", "Installed"]
        for cat in CATEGORIES:
            btn = tk.Button(cat_frame, text=cat, bg="#E95420" if cat == "All" else "#2A2D3A",
                            fg="#FFFFFF" if cat == "All" else TEXT_MUTED,
                            font=("SF Pro Display", 9, "bold" if cat == "All" else "normal"),
                            relief="flat", padx=8, pady=2, cursor="hand2",
                            command=lambda c=cat: set_cat(c))
            btn.pack(side=tk.LEFT, padx=3)
            cat_buttons[cat] = btn

        search_var.trace_add("write", lambda *args: render_packages())
        render_packages()

    # ─── Calculator Application Window ──────────────────────────────────────

    def _open_calculator(self):
        win, content = self._make_window(
            "🧮  Calculator — MicroCalc",
            320, 420, offset_x=320, offset_y=140)

        calc_frame = tk.Frame(content, bg="#1E1E24")
        calc_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        display_var = tk.StringVar(value="0")
        sub_var = tk.StringVar(value="")

        # LCD Display card
        disp_box = tk.Frame(calc_frame, bg="#141418", highlightbackground=WIN_BORDER, highlightthickness=1)
        disp_box.pack(fill=tk.X, padx=4, pady=(4, 10))

        tk.Label(disp_box, textvariable=sub_var, bg="#141418", fg=TEXT_MUTED,
                 font=("SF Pro Mono", 10), anchor="e").pack(fill=tk.X, padx=8, pady=(4, 0))
        tk.Label(disp_box, textvariable=display_var, bg="#141418", fg=TEXT_PRIMARY,
                 font=("SF Pro Mono", 24, "bold"), anchor="e").pack(fill=tk.X, padx=8, pady=(0, 6))

        # Button matrix
        BTN_GRID = [
            ("C", "#4A4D58", "#FFFFFF"), ("±", "#4A4D58", "#FFFFFF"), ("%", "#4A4D58", "#FFFFFF"), ("÷", "#FF9F0A", "#FFFFFF"),
            ("7", "#2D3039", "#FFFFFF"), ("8", "#2D3039", "#FFFFFF"), ("9", "#2D3039", "#FFFFFF"), ("×", "#FF9F0A", "#FFFFFF"),
            ("4", "#2D3039", "#FFFFFF"), ("5", "#2D3039", "#FFFFFF"), ("6", "#2D3039", "#FFFFFF"), ("-", "#FF9F0A", "#FFFFFF"),
            ("1", "#2D3039", "#FFFFFF"), ("2", "#2D3039", "#FFFFFF"), ("3", "#2D3039", "#FFFFFF"), ("+", "#FF9F0A", "#FFFFFF"),
            ("0", "#2D3039", "#FFFFFF"), (".", "#2D3039", "#FFFFFF"), ("DEL", "#3D404A", "#FFFFFF"), ("=", "#FF9F0A", "#FFFFFF"),
        ]

        def on_calc_btn(char):
            cur = display_var.get()
            if char == "C":
                display_var.set("0")
                sub_var.set("")
            elif char == "DEL":
                if len(cur) > 1 and cur != "Error":
                    display_var.set(cur[:-1])
                else:
                    display_var.set("0")
            elif char == "±":
                if cur.startswith("-"):
                    display_var.set(cur[1:])
                elif cur != "0":
                    display_var.set("-" + cur)
            elif char == "%":
                try:
                    val = float(cur) / 100.0
                    display_var.set(f"{val:.4g}")
                except Exception:
                    display_var.set("Error")
            elif char in ("+", "-", "×", "÷"):
                sub_var.set(f"{cur} {char}")
                display_var.set("0")
            elif char == "=":
                expr = sub_var.get()
                if expr:
                    full_expr = expr + " " + cur
                    try:
                        safe_expr = full_expr.replace("×", "*").replace("÷", "/")
                        import ast, operator
                        operators = {ast.Add: operator.add, ast.Sub: operator.sub,
                                     ast.Mult: operator.mul, ast.Div: operator.truediv}
                        def eval_expr(node):
                            if isinstance(node, ast.Constant):
                                return node.value
                            elif isinstance(node, ast.BinOp):
                                return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
                                return -eval_expr(node.operand)
                            raise ValueError("Invalid expression")
                        res = eval_expr(ast.parse(safe_expr, mode='eval').body)
                        if isinstance(res, float) and res.is_integer():
                            res = int(res)
                        display_var.set(str(res))
                        sub_var.set(full_expr + " =")
                    except Exception:
                        display_var.set("Error")
                        sub_var.set("")
            else:
                if cur in ("0", "Error"):
                    display_var.set(char if char != "." else "0.")
                else:
                    if char == "." and "." in cur:
                        return
                    display_var.set(cur + char)

        btn_container = tk.Frame(calc_frame, bg="#1E1E24")
        btn_container.pack(fill=tk.BOTH, expand=True)

        for i, (text, bg_c, fg_c) in enumerate(BTN_GRID):
            r = i // 4
            c = i % 4
            b = tk.Button(btn_container, text=text, bg=bg_c, fg=fg_c,
                          activebackground="#5A5D6B", activeforeground="#FFFFFF",
                          font=("SF Pro Display", 13, "bold"), relief="flat", bd=0, cursor="hand2",
                          command=lambda ch=text: on_calc_btn(ch))
            b.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            btn_container.rowconfigure(r, weight=1)
            btn_container.columnconfigure(c, weight=1)

    # ─── Snake Arcade Application Window ────────────────────────────────────

    def _open_snake_game(self):
        win, content = self._make_window(
            "🐍  Snake Arcade — Retro Micro-Game",
            460, 520, offset_x=260, offset_y=90)

        header = tk.Frame(content, bg=WIN_CHROME, height=36)
        header.pack(fill=tk.X, padx=8, pady=4)

        score_var = tk.StringVar(value="Score: 0")
        high_score_var = tk.StringVar(value="Best: 0")
        speed_var = tk.StringVar(value="Speed: 1x")

        tk.Label(header, textvariable=score_var, bg=WIN_CHROME, fg=ACCENT_GREEN,
                 font=("SF Pro Display", 11, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Label(header, textvariable=high_score_var, bg=WIN_CHROME, fg=ACCENT_AMBER,
                 font=("SF Pro Display", 11, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Label(header, textvariable=speed_var, bg=WIN_CHROME, fg=TEXT_MUTED,
                 font=("SF Pro Display", 10)).pack(side=tk.LEFT, padx=10)

        canvas_w, canvas_h = 420, 380
        cell_size = 20
        grid_w = canvas_w // cell_size
        grid_h = canvas_h // cell_size

        canvas = tk.Canvas(content, bg="#0E1015", width=canvas_w, height=canvas_h,
                           highlightbackground=WIN_BORDER, highlightthickness=1)
        canvas.pack(padx=8, pady=4)

        footer = tk.Frame(content, bg=WIN_CHROME)
        footer.pack(fill=tk.X, padx=8, pady=(2, 6))
        tk.Label(footer, text="Controls: Arrow Keys or W/A/S/D  •  Space: Pause / Restart",
                 bg=WIN_CHROME, fg=TEXT_MUTED, font=("SF Pro Display", 9)).pack(side=tk.LEFT, padx=8)

        import random
        snake = [(grid_w // 2, grid_h // 2), (grid_w // 2 - 1, grid_h // 2), (grid_w // 2 - 2, grid_h // 2)]
        direction = [1, 0]
        next_direction = [1, 0]
        food = [grid_w // 2 + 5, grid_h // 2]
        score = [0]
        high_score = [0]
        game_running = [True]
        game_paused = [False]

        def spawn_food():
            while True:
                fx = random.randint(1, grid_w - 2)
                fy = random.randint(1, grid_h - 2)
                if (fx, fy) not in snake:
                    food[0], food[1] = fx, fy
                    break

        def draw():
            canvas.delete("all")
            for gx in range(0, canvas_w, cell_size):
                for gy in range(0, canvas_h, cell_size):
                    canvas.create_rectangle(gx, gy, gx+1, gy+1, fill="#1A1C24", outline="")

            fx, fy = food[0] * cell_size, food[1] * cell_size
            canvas.create_oval(fx + 2, fy + 2, fx + cell_size - 2, fy + cell_size - 2,
                              fill="#FF453A", outline="#FF6961")
            canvas.create_text(fx + cell_size // 2, fy + cell_size // 2, text="🍎", font=("SF Pro Display", 10))

            for idx, (sx, sy) in enumerate(snake):
                px, py = sx * cell_size, sy * cell_size
                color = "#30D158" if idx == 0 else "#248A3D"
                canvas.create_rectangle(px + 1, py + 1, px + cell_size - 1, py + cell_size - 1,
                                       fill=color, outline="#1C5E2C")
                if idx == 0:
                    canvas.create_oval(px + 6, py + 6, px + 10, py + 10, fill="#FFFFFF", outline="")

            if not game_running[0]:
                canvas.create_rectangle(40, 140, canvas_w - 40, 240, fill="#1B1D26", outline=WIN_BORDER)
                canvas.create_text(canvas_w // 2, 175, text="GAME OVER", fill="#FF453A",
                                   font=("SF Pro Display", 20, "bold"))
                canvas.create_text(canvas_w // 2, 210, text="Press Space or Enter to Play Again",
                                   fill=TEXT_PRIMARY, font=("SF Pro Display", 11))

        def game_step():
            if not game_running[0] or game_paused[0]:
                return

            direction[0], direction[1] = next_direction[0], next_direction[1]
            hx = (snake[0][0] + direction[0]) % grid_w
            hy = (snake[0][1] + direction[1]) % grid_h

            if (hx, hy) in snake[:-1]:
                game_running[0] = False
                draw()
                return

            snake.insert(0, (hx, hy))

            if hx == food[0] and hy == food[1]:
                score[0] += 10
                if score[0] > high_score[0]:
                    high_score[0] = score[0]
                score_var.set(f"Score: {score[0]}")
                high_score_var.set(f"Best: {high_score[0]}")
                spawn_food()
            else:
                snake.pop()

            draw()
            delay = max(50, 110 - (score[0] // 50) * 8)
            speed_var.set(f"Speed: {1 + score[0] // 50}x")
            win.after(delay, game_step)

        def on_key(event):
            k = event.keysym.lower()
            if k in ("up", "w") and direction != [0, 1]:
                next_direction[0], next_direction[1] = 0, -1
            elif k in ("down", "s") and direction != [0, -1]:
                next_direction[0], next_direction[1] = 0, 1
            elif k in ("left", "a") and direction != [1, 0]:
                next_direction[0], next_direction[1] = -1, 0
            elif k in ("right", "d") and direction != [-1, 0]:
                next_direction[0], next_direction[1] = 1, 0
            elif k in ("space", "return"):
                if not game_running[0]:
                    snake.clear()
                    snake.extend([(grid_w // 2, grid_h // 2), (grid_w // 2 - 1, grid_h // 2), (grid_w // 2 - 2, grid_h // 2)])
                    direction[0], direction[1] = 1, 0
                    next_direction[0], next_direction[1] = 1, 0
                    score[0] = 0
                    score_var.set("Score: 0")
                    game_running[0] = True
                    spawn_food()
                    game_step()
                else:
                    game_paused[0] = not game_paused[0]
                    if not game_paused[0]:
                        game_step()

        win.bind("<KeyPress>", on_key)
        canvas.focus_set()
        draw()
        game_step()

    # ─── Doom Micro Raycaster Application Window ────────────────────────────

    def _open_doom_viewer(self):
        win, content = self._make_window(
            "👾  Doom Micro — 3D Raycaster Engine (1993)",
            540, 440, offset_x=290, offset_y=110)

        header = tk.Frame(content, bg=WIN_CHROME, height=34)
        header.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(header, text="E1M1: Hangar  •  FPS: 60  •  Engine: Raycasting 32bpp",
                 bg=WIN_CHROME, fg=ACCENT_AMBER, font=("SF Pro Display", 10, "bold")).pack(side=tk.LEFT, padx=10)
        ammo_lbl = tk.Label(header, text="AMMO: 50   HEALTH: 100%   ARMOR: 50%",
                            bg=WIN_CHROME, fg=ACCENT_GREEN, font=("SF Pro Mono", 10, "bold"))
        ammo_lbl.pack(side=tk.RIGHT, padx=10)

        cv_w, cv_h = 520, 320
        canvas = tk.Canvas(content, bg="#000000", width=cv_w, height=cv_h,
                           highlightbackground=WIN_BORDER, highlightthickness=1)
        canvas.pack(padx=8, pady=4)

        import math
        player_x = [3.5]
        player_y = [3.5]
        player_angle = [0.0]

        MAP = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 2, 1],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 3, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 2, 0, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 2, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]

        def render_scene():
            canvas.delete("all")
            canvas.create_rectangle(0, 0, cv_w, cv_h // 2, fill="#1E232B", outline="")
            canvas.create_rectangle(0, cv_h // 2, cv_w, cv_h, fill="#2F251E", outline="")

            fov = math.pi / 3
            num_rays = 65
            ray_step = cv_w / num_rays

            for r in range(num_rays):
                ray_angle = player_angle[0] - fov / 2 + (r / num_rays) * fov
                cos_a = math.cos(ray_angle)
                sin_a = math.sin(ray_angle)

                dist = 0.05
                hit_wall = False
                wall_type = 1
                while dist < 12.0 and not hit_wall:
                    dist += 0.05
                    check_x = int(player_x[0] + cos_a * dist)
                    check_y = int(player_y[0] + sin_a * dist)
                    if 0 <= check_x < 8 and 0 <= check_y < 8:
                        if MAP[check_y][check_x] > 0:
                            hit_wall = True
                            wall_type = MAP[check_y][check_x]

                corr_dist = dist * math.cos(ray_angle - player_angle[0])
                wall_h = min(cv_h, int(cv_h / (corr_dist + 0.001)))

                y0 = (cv_h - wall_h) // 2
                y1 = y0 + wall_h

                intensity = max(30, int(255 - corr_dist * 22))
                if wall_type == 1:
                    color = f"#{intensity:02x}{int(intensity*0.4):02x}{int(intensity*0.2):02x}"
                elif wall_type == 2:
                    color = f"#{int(intensity*0.2):02x}{int(intensity*0.5):02x}{intensity:02x}"
                else:
                    color = f"#{int(intensity*0.6):02x}{int(intensity*0.6):02x}{int(intensity*0.1):02x}"

                canvas.create_rectangle(r * ray_step, y0, (r + 1) * ray_step + 1, y1,
                                       fill=color, outline=color)

            # Minimap in top-right corner
            mm_size = 10
            for my in range(8):
                for mx in range(8):
                    mc = "#555566" if MAP[my][mx] > 0 else "#222228"
                    canvas.create_rectangle(cv_w - 90 + mx * mm_size, 10 + my * mm_size,
                                           cv_w - 90 + (mx + 1) * mm_size, 10 + (my + 1) * mm_size,
                                           fill=mc, outline="")
            pmx = cv_w - 90 + int(player_x[0] * mm_size)
            pmy = 10 + int(player_y[0] * mm_size)
            canvas.create_oval(pmx - 2, pmy - 2, pmx + 2, pmy + 2, fill="#FFCC00", outline="")

            # Center Crosshair
            canvas.create_line(cv_w // 2 - 8, cv_h // 2, cv_w // 2 + 8, cv_h // 2, fill="#00FF66", width=2)
            canvas.create_line(cv_w // 2, cv_h // 2 - 8, cv_w // 2, cv_h // 2 + 8, fill="#00FF66", width=2)

            # Gun HUD sprite
            canvas.create_text(cv_w // 2, cv_h - 35, text="🔫", font=("Segoe UI Emoji", 42))

        def on_doom_key(event):
            k = event.keysym.lower()
            move_speed = 0.2
            rot_speed = 0.15

            new_x = player_x[0]
            new_y = player_y[0]

            if k in ("w", "up"):
                new_x += math.cos(player_angle[0]) * move_speed
                new_y += math.sin(player_angle[0]) * move_speed
            elif k in ("s", "down"):
                new_x -= math.cos(player_angle[0]) * move_speed
                new_y -= math.sin(player_angle[0]) * move_speed
            elif k in ("a", "left"):
                player_angle[0] -= rot_speed
            elif k in ("d", "right"):
                player_angle[0] += rot_speed

            if 0 <= int(new_x) < 8 and 0 <= int(new_y) < 8 and MAP[int(new_y)][int(new_x)] == 0:
                player_x[0] = new_x
                player_y[0] = new_y

            render_scene()

        win.bind("<KeyPress>", on_doom_key)
        canvas.focus_set()
        render_scene()


def main():
    try:
        app = MicroOS()
        app.mainloop()
    except Exception as e:
        import traceback
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
