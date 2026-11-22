//! macOS & Windows 11 Desktop Environment Decorator
//!
//! Renders the top translucent menu bar, system clock, network indicators,
//! abstract gradient wallpaper, and the floating bottom application dock.

use super::framebuffer::Framebuffer;
use super::theme::Theme;
use super::window::AppType;

pub const MENUBAR_HEIGHT: u32 = 26;
pub const DOCK_HEIGHT: u32 = 56;
pub const DOCK_WIDTH: u32 = 488;
pub const DOCK_ITEM_SIZE: u32 = 44;

pub struct Desktop {
    pub current_time_str: &'static str,
    pub ip_display_str: &'static str,
    pub wifi_ssid_str: &'static str,
}

impl Desktop {
    pub const fn new() -> Self {
        Self {
            current_time_str: "11:20 AM",
            ip_display_str: "192.168.1.142",
            wifi_ssid_str: "WiFi: Home-Fiber-5G",
        }
    }

    /// Renders the wallpaper gradient, top menu bar, and bottom dock
    pub fn render(&self, fb: &mut Framebuffer) {
        let w = fb.width as u32;
        let h = fb.height as u32;

        // 1. Desktop Wallpaper (Flow gradient from deep midnight navy to velvet purple)
        fb.draw_gradient_v(0, 0, w, h / 2, Theme::WALLPAPER_TOP, Theme::WALLPAPER_MID);
        fb.draw_gradient_v(
            0,
            (h / 2) as i32,
            w,
            h - h / 2,
            Theme::WALLPAPER_MID,
            Theme::WALLPAPER_BOTTOM,
        );

        // 2. Top Menu Bar (macOS frosted acrylic glass header)
        fb.fill_rect(0, 0, w, MENUBAR_HEIGHT, Theme::MENUBAR_BG);
        fb.fill_rect(0, MENUBAR_HEIGHT as i32 - 1, w, 1, Theme::WIN_BORDER);

        // Apple / Micro-OS Logo & Menus
        fb.draw_string(14, 5, "[#] Micro-OS", Theme::TEXT_PRIMARY);
        fb.draw_string(130, 5, "File   Edit   View   Network   Window   Help", Theme::TEXT_MUTED);

        // Top-Right System Indicators (macOS style WiFi / Battery / Clock)
        let status_x = (w - 380) as usize;
        fb.draw_string(status_x, 5, self.wifi_ssid_str, Theme::ACCENT_CYAN);
        fb.draw_string(status_x + 160, 5, self.ip_display_str, Theme::ACCENT_GREEN);
        fb.draw_string(status_x + 265, 5, "100%", Theme::TEXT_PRIMARY);
        fb.draw_string(status_x + 305, 5, self.current_time_str, Theme::TEXT_PRIMARY);

        // 3. Floating Bottom Dock (macOS / Windows 11 hybrid centered dock)
        let dock_x = ((w - DOCK_WIDTH) / 2) as i32;
        let dock_y = (h - DOCK_HEIGHT - 12) as i32;

        // Dock drop shadow
        fb.draw_shadow(dock_x, dock_y, DOCK_WIDTH, DOCK_HEIGHT, 10, 110);

        // Dock background (Frosted translucent rounded pill)
        fb.draw_rounded_rect(dock_x, dock_y, DOCK_WIDTH, DOCK_HEIGHT, 16, Theme::DOCK_BG, true);
        fb.draw_rounded_rect(dock_x, dock_y, DOCK_WIDTH, DOCK_HEIGHT, 16, Theme::DOCK_BORDER, false);

        // Dock Icons
        // 7 apps: Browser, Terminal, TaskManager, Explorer, Settings, Wifi, SnapStore
        let icons = [
            (AppType::Browser, "[WEB]", Theme::ACCENT_BLUE),
            (AppType::Terminal, "[TERM]", Theme::TEXT_PRIMARY),
            (AppType::TaskManager, "[PERF]", Theme::ACCENT_GREEN),
            (AppType::Explorer, "[FIND]", Theme::ACCENT_PURPLE),
            (AppType::Settings, "[CONF]", Theme::TEXT_MUTED),
            (AppType::Wifi, "[WIFI]", Theme::ACCENT_CYAN),
            (AppType::SnapStore, "[SNAP]", Theme::ACCENT_AMBER),
        ];

        let start_x = dock_x + 20;
        let item_spacing = 64;

        for (idx, (_app, label, col)) in icons.iter().enumerate() {
            let item_x = start_x + (idx as i32 * item_spacing);
            let item_y = dock_y + 8;

            // Icon square container
            fb.draw_rounded_rect(item_x, item_y, DOCK_ITEM_SIZE, DOCK_ITEM_SIZE, 8, *col, true);

            // Icon inner text
            let text_x = (item_x + 6) as usize;
            let text_y = (item_y + 14) as usize;
            fb.draw_string(text_x, text_y, label, Theme::WIN_BG_DARK);

            // Active running dot indicator beneath icon
            fb.draw_circle(item_x + (DOCK_ITEM_SIZE as i32 / 2), dock_y + DOCK_HEIGHT as i32 - 4, 2, Theme::DOCK_ACTIVE_DOT, true);
        }
    }

    /// Hit-tests which dock icon was clicked
    pub fn hit_dock_icon(&self, w: u32, h: u32, px: i32, py: i32) -> Option<AppType> {
        let dock_x = ((w - DOCK_WIDTH) / 2) as i32;
        let dock_y = (h - DOCK_HEIGHT - 12) as i32;

        if px < dock_x || px >= (dock_x + DOCK_WIDTH as i32) || py < dock_y || py >= (dock_y + DOCK_HEIGHT as i32) {
            return None;
        }

        let start_x = dock_x + 20;
        let item_spacing = 64;

        let apps = [
            AppType::Browser,
            AppType::Terminal,
            AppType::TaskManager,
            AppType::Explorer,
            AppType::Settings,
            AppType::Wifi,
            AppType::SnapStore,
        ];

        for (idx, app) in apps.iter().enumerate() {
            let item_x = start_x + (idx as i32 * item_spacing);
            if px >= item_x && px < (item_x + DOCK_ITEM_SIZE as i32) {
                return Some(*app);
            }
        }

        None
    }
}
