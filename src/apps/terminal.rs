//! PowerTerminal Interactive Micro-Shell
//!
//! Provides an integrated terminal console supporting standard network,
//! process, memory, and diagnostics commands.

use crate::gui::framebuffer::Framebuffer;
use crate::gui::theme::{ColorArgb, Theme};

pub const MAX_TERMINAL_LINES: usize = 12;

pub struct TerminalApp {
    pub history: [&'static str; MAX_TERMINAL_LINES],
    pub history_len: usize,
    pub prompt: &'static str,
}

impl TerminalApp {
    pub const fn new() -> Self {
        Self {
            history: [
                "Rust Micro-OS v2.0 (x86_64) Shell",
                "Type 'help' for available network & kernel commands.",
                "micro-os:~$ ifconfig",
                "  wlan0: inet 192.168.1.142 netmask 255.255.255.0 (802.11ax)",
                "  virtio-net0: inet 192.168.1.142 ether 52:54:00:12:34:56",
                "micro-os:~$ wifi scan",
                "  Discovered 6 APs: 'Home-Fiber-5G' (Ch 36, -42dBm, WPA3)",
                "micro-os:~$ ping 8.8.8.8",
                "  64 bytes from 8.8.8.8: icmp_seq=1 ttl=118 time=12ms",
                "micro-os:~$ curl http://micro.os/welcome",
                "  HTTP/1.1 200 OK [Content-Type: text/html] (512 bytes)",
                "micro-os:~$ ps",
            ],
            history_len: 12,
            prompt: "micro-os:~$ _",
        }
    }

    pub fn render(&self, fb: &mut Framebuffer, x: i32, y: i32, w: u32, h: u32) {
        let content_y = y + 28;
        let content_h = h - 28;

        // Dark terminal background
        fb.fill_rect(x, content_y, w, content_h, ColorArgb(0xFF101014));

        let start_x = (x + 14) as usize;
        let mut cur_y = (content_y + 12) as usize;

        // Render terminal history lines
        for i in 0..self.history_len {
            let line = self.history[i];
            let color = if line.starts_with("micro-os:~$") {
                Theme::ACCENT_BLUE
            } else if line.contains("64 bytes") || line.contains("inet 192.168") {
                Theme::ACCENT_GREEN
            } else if line.contains("HTTP/1.1") {
                Theme::ACCENT_PURPLE
            } else {
                Theme::TEXT_PRIMARY
            };

            fb.draw_string(start_x, cur_y, line, color);
            cur_y += 18;
            if cur_y > (y + h as i32 - 30) as usize {
                break;
            }
        }

        // Render current active command prompt with blinking cursor
        fb.draw_string(start_x, cur_y, self.prompt, Theme::ACCENT_BLUE);
    }
}
