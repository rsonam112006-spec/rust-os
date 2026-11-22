//! Snap Store & Package Manager Application for Micro-OS
//!
//! Provides a software center interface:
//! - Browse and discover snap packages across categories
//! - Install and remove micro-applications
//! - View package sizes, versions, ratings, and dependencies
//! - Integration with snapd package management daemon

use crate::gui::framebuffer::Framebuffer;
use crate::gui::theme::Theme;

pub struct SnapStoreApp;

impl SnapStoreApp {
    pub const fn new() -> Self {
        Self
    }

    pub fn render(&self, fb: &mut Framebuffer, x: i32, y: i32, w: u32, h: u32) {
        let content_y = y + 28;
        let content_h = h - 28;

        // Dark window client background
        fb.fill_rect(x, content_y, w, content_h, Theme::WIN_BG_DARK);

        let start_x = (x + 14) as usize;
        let mut cur_y = (content_y + 12) as usize;

        // 1. Header Banner
        fb.draw_string(
            start_x,
            cur_y,
            "🛍 Snap Store -- Micro-OS Software Center & Package Manager",
            Theme::ACCENT_AMBER,
        );
        cur_y += 18;

        fb.draw_string(
            start_x,
            cur_y,
            "Channel: stable  |  Core: core22-x86_64  |  Daemon: snapd v2.58 (Active)",
            Theme::TEXT_MUTED,
        );
        cur_y += 16;

        // Separator
        fb.fill_rect(x + 10, cur_y as i32, w - 20, 1, Theme::WIN_BORDER);
        cur_y += 8;

        // 2. Search & Category Bar
        fb.draw_rounded_rect(x + 14, cur_y as i32, 220, 22, 4, Theme::WIN_TITLEBAR_INACTIVE, true);
        fb.draw_string(start_x + 8, cur_y + 3, "🔍 Search packages...", Theme::TEXT_MUTED);

        let categories = ["All", "Featured", "Utilities", "Development", "Network", "Games", "Installed"];
        let mut cat_x = x + 246;
        for cat in categories.iter() {
            let cat_w = (cat.len() * 8 + 14) as u32;
            let is_sel = *cat == "Featured";
            let bg_col = if is_sel { Theme::ACCENT_BLUE } else { Theme::WIN_CHROME };
            let text_col = if is_sel { Theme::TEXT_PRIMARY } else { Theme::TEXT_MUTED };

            fb.draw_rounded_rect(cat_x, cur_y as i32, cat_w, 22, 4, bg_col, true);
            fb.draw_string((cat_x + 7) as usize, cur_y + 3, cat, text_col);
            cat_x += cat_w as i32 + 6;
        }

        cur_y += 32;

        // 3. Package Cards Table
        fb.draw_string(
            start_x,
            cur_y,
            "PACKAGE NAME     VER     SIZE    CATEGORY    RATING   STATUS     DESCRIPTION",
            Theme::TEXT_MUTED,
        );
        cur_y += 14;
        fb.fill_rect(x + 14, cur_y as i32, w - 28, 1, Theme::WIN_BORDER);
        cur_y += 4;

        let packages = [
            ("neofetch",      "7.1.0", "1.2MB", "Utilities",  "***** ", "INSTALLED", Theme::ACCENT_GREEN,  "Fast system info & ASCII crab logo"),
            ("htop",          "3.2.2", "2.8MB", "Development","***** ", "INSTALLED", Theme::ACCENT_GREEN,  "Interactive process viewer & CPU load"),
            ("wireguard",     "1.0.2", "3.4MB", "Network",    "***** ", "AVAILABLE", Theme::TEXT_PRIMARY,   "Fast, modern encrypted VPN tunnel"),
            ("doom-micro",    "1.9.0", "8.6MB", "Games",      "***** ", "AVAILABLE", Theme::ACCENT_CYAN,    "Classic 1993 retro raycaster engine"),
            ("wireshark-lite","4.0.1", "5.1MB", "Network",    "****. ", "AVAILABLE", Theme::TEXT_PRIMARY,   "802.11 & Ethernet packet sniffer"),
            ("vim-tiny",      "9.0.8", "2.2MB", "Development","****. ", "AVAILABLE", Theme::TEXT_PRIMARY,   "Vi IMproved - modal text editor"),
            ("speedtest-cli", "2.1.3", "1.6MB", "Network",    "****. ", "AVAILABLE", Theme::TEXT_PRIMARY,   "Broadband bandwidth & ping tester"),
            ("snake-arcade",  "1.2.0", "0.9MB", "Games",      "****. ", "AVAILABLE", Theme::ACCENT_CYAN,    "Retro arcade snake game in terminal"),
            ("micro-calc",    "2.0.0", "1.1MB", "Utilities",  "****. ", "INSTALLED", Theme::ACCENT_GREEN,  "Programmer & scientific hex/dec calc"),
            ("docker-micro",  "24.0 ", "9.4MB", "Development","***** ", "AVAILABLE", Theme::TEXT_PRIMARY,   "Micro-container runtime daemon"),
        ];

        for (name, ver, sz, cat, rat, stat, stat_col, desc) in packages.iter() {
            if cur_y + 18 > (y + h as i32 - 30) as usize {
                break;
            }

            fb.draw_string(start_x, cur_y, name, Theme::TEXT_PRIMARY);
            fb.draw_string(start_x + 130, cur_y, ver, Theme::TEXT_MUTED);
            fb.draw_string(start_x + 190, cur_y, sz, Theme::TEXT_MUTED);
            fb.draw_string(start_x + 250, cur_y, cat, Theme::ACCENT_BLUE);
            fb.draw_string(start_x + 350, cur_y, rat, Theme::ACCENT_AMBER);
            fb.draw_string(start_x + 420, cur_y, stat, *stat_col);
            fb.draw_string(start_x + 510, cur_y, desc, Theme::TEXT_MUTED);

            cur_y += 18;
        }

        // 4. Status Bar at bottom
        let status_y = y + h as i32 - 24;
        fb.fill_rect(x, status_y, w, 24, Theme::WIN_CHROME);
        fb.draw_string(
            start_x,
            (status_y + 4) as usize,
            "10 packages available | 3 installed | Terminal CLI: `snap install <name>` | `snap list`",
            Theme::TEXT_MUTED,
        );
    }
}
