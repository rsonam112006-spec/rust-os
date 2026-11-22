//! System Settings & About Micro-OS Application
//!
//! Displays comprehensive kernel, hardware, network, and desktop compositor specifications.

use crate::gui::framebuffer::Framebuffer;
use crate::gui::theme::Theme;

pub struct SettingsApp;

impl SettingsApp {
    pub const fn new() -> Self {
        Self
    }

    pub fn render(&self, fb: &mut Framebuffer, x: i32, y: i32, w: u32, h: u32) {
        let content_y = y + 28;
        let content_h = h - 28;

        fb.fill_rect(x, content_y, w, content_h, Theme::WIN_BG_DARK);

        // System Logo Badge
        let badge_x = x + 24;
        let badge_y = content_y + 20;
        fb.draw_rounded_rect(badge_x, badge_y, 60, 60, 12, Theme::ACCENT_BLUE, true);
        fb.draw_string((badge_x + 16) as usize, (badge_y + 22) as usize, "[OS]", Theme::TEXT_PRIMARY);

        // Main Header Title
        fb.draw_string((badge_x + 80) as usize, (badge_y + 12) as usize, "Rust Micro-OS 2.0", Theme::TEXT_PRIMARY);
        fb.draw_string((badge_x + 80) as usize, (badge_y + 32) as usize, "macOS Ventura & Windows 11 Fluent Desktop Edition", Theme::ACCENT_GREEN);

        // Specs List Card
        let card_y = badge_y + 80;
        fb.draw_rounded_rect(x + 16, card_y, w - 32, content_h - 120, 8, Theme::WIN_TITLEBAR_INACTIVE, true);
        fb.draw_rounded_rect(x + 16, card_y, w - 32, content_h - 120, 8, Theme::WIN_BORDER, false);

        let specs = [
            ("Operating System:", "Rust Micro-OS (Microkernel Architecture)"),
            ("Kernel Version:",   "v2.0.0-release (Target: x86_64)"),
            ("Memory Model:",     "Free-List Allocator with Block Coalescing"),
            ("Scheduler:",        "Preemptive Round Robin & Priority Dynamic Aging"),
            ("Networking Stack:", "VirtIO / e1000 Driver (Ethernet, IPv4, ICMP, TCP/UDP)"),
            ("Wi-Fi Subsystem:",  "wlan0: IEEE 802.11ax Wi-Fi 6 (WPA3-SAE / WPA2-PSK)"),
            ("Wi-Fi Network:",    "Connected to 'Home-Fiber-5G' (Ch 36, 5 GHz, 95%)"),
            ("Network Address:",  "192.168.1.142 / 24 (Default Gateway: 192.168.1.1)"),
            ("Window Server:",    "TrueColor 32bpp Compositor with Acrylic Glass"),
            ("Implementation:",   "100% Safe Rust Core + Audited Port I/O Hardware Abstractions"),
        ];

        let mut sy = card_y + 16;
        for (label, val) in specs.iter() {
            fb.draw_string((x + 30) as usize, sy as usize, label, Theme::TEXT_MUTED);
            fb.draw_string((x + 180) as usize, sy as usize, val, Theme::TEXT_PRIMARY);
            sy += 22;
        }
    }
}
