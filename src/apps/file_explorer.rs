//! MicroFinder / File Explorer Application
//!
//! Visual file system browser featuring sidebar navigation, directory paths,
//! and folder/file listings.

use crate::gui::framebuffer::Framebuffer;
use crate::gui::theme::Theme;

pub struct FileExplorerApp {
    pub current_path: &'static str,
}

impl FileExplorerApp {
    pub const fn new() -> Self {
        Self {
            current_path: "/system/drivers/net",
        }
    }

    pub fn render(&self, fb: &mut Framebuffer, x: i32, y: i32, w: u32, h: u32) {
        let content_y = y + 28;
        let content_h = h - 28;

        fb.fill_rect(x, content_y, w, content_h, Theme::WIN_BG_DARK);

        // Path / Breadcrumb Bar
        let bar_h = 30;
        fb.fill_rect(x, content_y, w, bar_h, Theme::WIN_TITLEBAR_INACTIVE);
        fb.fill_rect(x, content_y + bar_h as i32 - 1, w, 1, Theme::WIN_BORDER);
        fb.draw_string((x + 14) as usize, (content_y + 8) as usize, "Path: [ Computer > OS (C:) > system > drivers > net ]", Theme::TEXT_PRIMARY);

        // Left Sidebar (Finder style)
        let sidebar_w = 130;
        let main_x = x + sidebar_w as i32;
        let main_w = w - sidebar_w;
        let view_y = content_y + bar_h as i32;
        let view_h = content_h - bar_h;

        fb.fill_rect(x, view_y, sidebar_w, view_h, Theme::WIN_TITLEBAR_ACTIVE);
        fb.fill_rect(main_x - 1, view_y, 1, view_h, Theme::WIN_BORDER);

        // Sidebar items
        let sidebar_items = [
            "FAVORITES",
            "  * Desktop",
            "  * Documents",
            "  * Downloads",
            "LOCATIONS",
            "  - Hard Disk",
            "  - Network",
        ];
        let mut sy = view_y + 10;
        for item in sidebar_items.iter() {
            let col = if item.starts_with(" ") {
                Theme::TEXT_PRIMARY
            } else {
                Theme::TEXT_MUTED
            };
            fb.draw_string((x + 10) as usize, sy as usize, item, col);
            sy += 20;
        }

        // Main File Grid
        let files = [
            ("[DIR]  .. (parent)", "<DIR>", "17-Nov-2026"),
            ("[DIR]  virtio_net",   "<DIR>", "17-Nov-2026"),
            ("[DIR]  e1000",        "<DIR>", "17-Nov-2026"),
            ("[FILE] tcp_ip.sys",   "48 KB", "17-Nov-2026"),
            ("[FILE] icmp_echo.sys","12 KB", "17-Nov-2026"),
            ("[FILE] socket.sys",   "32 KB", "17-Nov-2026"),
            ("[FILE] config.ini",   "2 KB",  "17-Nov-2026"),
        ];

        let mut fy = view_y + 14;
        fb.draw_string((main_x + 14) as usize, fy as usize, "NAME                   SIZE     MODIFIED", Theme::TEXT_MUTED);
        fy += 22;

        for (name, size, date) in files.iter() {
            let is_dir = name.starts_with("[DIR]");
            let name_col = if is_dir { Theme::ACCENT_BLUE } else { Theme::TEXT_PRIMARY };
            fb.draw_string((main_x + 14) as usize, fy as usize, name, name_col);
            fb.draw_string((main_x + 180) as usize, fy as usize, size, Theme::TEXT_MUTED);
            fb.draw_string((main_x + 250) as usize, fy as usize, date, Theme::TEXT_MUTED);
            fy += 20;
        }
    }
}
