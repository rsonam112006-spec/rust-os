#!/usr/bin/env python3
"""
Rust Micro-OS v2.0 — Animated Boot Screen
Displays a full-screen boot animation before launching the desktop GUI.
"""

import tkinter as tk
import subprocess
import sys
import os
import time
from datetime import datetime

WALLPAPER_TOP = "#0A1931"
WALLPAPER_BOT = "#6E2594"
ACCENT_BLUE   = "#0A84FF"
ACCENT_GREEN  = "#30D158"
TEXT_PRIMARY  = "#F5F5F7"
TEXT_MUTED    = "#8A8EA0"
AMBER         = "#FFD60A"
RED           = "#FF5F57"

BOOT_STEPS = [
    ("BIOS",      "POST: Self-test OK — All 4 vCPUs online"),
    ("MBR",       "MBR boot sector loaded at 0x7C00 — signature AA55 OK"),
    ("BOOTLOADER","Stage 2 bootloader: loading kernel ELF from sector 2"),
    ("KERNEL",    "Kernel mapped to 0xFFFFFFFF80000000 (Higher Half)"),
    ("UART",      "16550 UART COM1 (0x3F8) initialized — 115200 baud"),
    ("VGA",       "VGA console 80×25 at 0xB8000 (Color text mode)"),
    ("MEMORY",    "Free-List allocator online — 64 KiB heap at 0x00100000"),
    ("PIT",       "8254 PIT configured to 100 Hz (10 ms resolution)"),
    ("SPINLOCK",  "Atomic spinlock primitives initialized — contention tracking ON"),
    ("SCHEDULER", "Preemptive Round Robin scheduler — Q=3 ticks"),
    ("PRIO",      "Priority Aging: threshold=4, starvation prevention ON"),
    ("SYSCALL",   "System call dispatcher: yield, sleep, malloc, free, print, exit"),
    ("NET",       "virtio-net0 MAC: 52:54:00:12:34:56  IPv4: 192.168.1.142/24"),
    ("ARP",       "ARP cache seeded — Gateway & DNS resolved"),
    ("TCP/IP",    "TCP/IPv4/ICMP/UDP protocol stack ready"),
    ("HTTP",      "HTTP 1.1 engine initialized — micro-web server listening"),
    ("FRAMEBUF",  "32bpp TrueColor Framebuffer 1024×768 — Compositor active"),
    ("WIFI",      "wlan0 802.11ax controller ready — MAC: 3C:06:30:AB:CD:EF"),
    ("WIFI-SCAN", "802.11 scan: 6 APs discovered — associated with 'Home-Fiber-5G'"),
    ("WPA-DHCP",  "WPA3/WPA2-PSK 4-Way Handshake OK — DHCP lease 192.168.1.142 active"),
    ("DESKTOP",   "macOS & Windows 11 Fluent Desktop Environment launching..."),
    ("TESTS",     "TC1–TC9 self-test suite: ALL 9 PASSED ✓"),
    ("DONE",      ">>> Rust Micro-OS v2.0 — System Ready <<<"),
]


class BootScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rust Micro-OS v2.0 — Boot")
        self.geometry("900x620")
        self.configure(bg="#0A0B10")
        self.resizable(False, False)

        self._build_ui()
        self._step = 0
        self.after(200, self._tick)

    def _build_ui(self):
        # Header logo
        logo = tk.Frame(self, bg="#0A0B10")
        logo.pack(pady=(40, 10))

        tk.Label(logo, text="🦀", font=("Segoe UI Emoji", 52),
                 bg="#0A0B10").pack()
        tk.Label(logo, text="Rust Micro-OS", font=("Segoe UI", 28, "bold"),
                 fg=TEXT_PRIMARY, bg="#0A0B10").pack()
        tk.Label(logo, text="v2.0.0 — macOS & Windows 11 Fluent Desktop  •  x86_64 Microkernel",
                 font=("Segoe UI", 11), fg=TEXT_MUTED, bg="#0A0B10").pack(pady=4)

        # Separator
        tk.Frame(self, bg="#222530", height=1).pack(fill=tk.X, padx=60, pady=10)

        # Boot log text box
        log_outer = tk.Frame(self, bg="#0D0E13", bd=0,
                             highlightbackground="#2A2D3A", highlightthickness=1)
        log_outer.pack(fill=tk.X, padx=60, pady=4)

        self.log_text = tk.Text(log_outer, bg="#0D0E13", fg=ACCENT_GREEN,
                                font=("Courier New", 10), height=12,
                                relief="flat", bd=6, state="disabled",
                                wrap="word", cursor="arrow")
        self.log_text.pack(fill=tk.X)
        self.log_text.tag_configure("ok",     foreground=ACCENT_GREEN)
        self.log_text.tag_configure("info",   foreground="#8A8EA0")
        self.log_text.tag_configure("done",   foreground=AMBER)
        self.log_text.tag_configure("passed", foreground=ACCENT_GREEN)
        self.log_text.tag_configure("label",  foreground=ACCENT_BLUE)

        # Progress bar
        self.prog_frame = tk.Frame(self, bg="#0A0B10")
        self.prog_frame.pack(fill=tk.X, padx=60, pady=10)

        self.prog_canvas = tk.Canvas(self.prog_frame, bg="#222530",
                                     height=10, highlightthickness=0)
        self.prog_canvas.pack(fill=tk.X)

        self.status_label = tk.Label(self, text="Starting up...",
                                     bg="#0A0B10", fg=TEXT_MUTED,
                                     font=("Segoe UI", 10))
        self.status_label.pack(pady=4)

        # Launch button (hidden until boot completes)
        self.launch_btn = tk.Button(
            self, text="  Launch Desktop  ",
            bg=ACCENT_BLUE, fg=TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=20, pady=8,
            cursor="hand2", activebackground="#0060CC",
            command=self._launch_desktop
        )

    def _tick(self):
        if self._step >= len(BOOT_STEPS):
            self._finish()
            return

        subsys, msg = BOOT_STEPS[self._step]
        pct = (self._step + 1) / len(BOOT_STEPS)

        # Append to log
        self.log_text.configure(state="normal")
        tag = "done" if subsys in ("DONE", "TESTS") else "ok"
        self.log_text.insert(tk.END, f"  [ ", "info")
        self.log_text.insert(tk.END, f"{subsys:^10}", "label")
        self.log_text.insert(tk.END, f" ]  {msg}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

        # Progress bar
        w = self.prog_canvas.winfo_width() or 780
        fill_w = int(w * pct)
        self.prog_canvas.delete("all")
        self.prog_canvas.create_rectangle(0, 0, fill_w, 10, fill=ACCENT_BLUE, outline="")
        pct_str = f"{int(pct * 100)}%"
        self.status_label.configure(text=f"Initializing {subsys}... {pct_str}")

        self._step += 1
        # Faster at end
        delay = 80 if self._step > 16 else 160
        self.after(delay, self._tick)

    def _finish(self):
        self.prog_canvas.delete("all")
        w = self.prog_canvas.winfo_width() or 780
        self.prog_canvas.create_rectangle(0, 0, w, 10, fill=ACCENT_GREEN, outline="")
        self.status_label.configure(text="✓  All systems operational — Ready to launch",
                                    fg=ACCENT_GREEN)
        self.launch_btn.pack(pady=12)

    def _launch_desktop(self):
        self.destroy()
        desktop_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_gui.py")
        subprocess.Popen([sys.executable, desktop_script])


if __name__ == "__main__":
    app = BootScreen()
    app.mainloop()
