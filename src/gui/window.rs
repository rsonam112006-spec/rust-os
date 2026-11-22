//! Window Entity & Chrome Decorator
//!
//! Provides window frame layout, titlebar, macOS traffic light controls
//! (Close, Minimize, Maximize), focus state, and client area bounds.

use super::framebuffer::Framebuffer;
use super::theme::Theme;

pub const TITLEBAR_HEIGHT: u32 = 28;
pub const TRAFFIC_LIGHT_RADIUS: u32 = 6;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AppType {
    Browser,
    Terminal,
    TaskManager,
    Explorer,
    Settings,
    Wifi,
    SnapStore,
}

pub struct Window {
    pub id: usize,
    pub title: &'static str,
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
    pub is_active: bool,
    pub is_minimized: bool,
    pub is_maximized: bool,
    pub is_dragging: bool,
    pub drag_offset_x: i32,
    pub drag_offset_y: i32,
    pub app_type: AppType,
    pub saved_x: i32,
    pub saved_y: i32,
    pub saved_w: u32,
    pub saved_h: u32,
}

impl Window {
    pub fn new(
        id: usize,
        title: &'static str,
        x: i32,
        y: i32,
        width: u32,
        height: u32,
        app_type: AppType,
    ) -> Self {
        Self {
            id,
            title,
            x,
            y,
            width,
            height,
            is_active: true,
            is_minimized: false,
            is_maximized: false,
            is_dragging: false,
            drag_offset_x: 0,
            drag_offset_y: 0,
            app_type,
            saved_x: x,
            saved_y: y,
            saved_w: width,
            saved_h: height,
        }
    }

    pub fn contains_point(&self, px: i32, py: i32) -> bool {
        if self.is_minimized {
            return false;
        }
        px >= self.x
            && px < (self.x + self.width as i32)
            && py >= self.y
            && py < (self.y + self.height as i32)
    }

    pub fn titlebar_contains(&self, px: i32, py: i32) -> bool {
        if self.is_minimized {
            return false;
        }
        px >= self.x
            && px < (self.x + self.width as i32)
            && py >= self.y
            && py < (self.y + TITLEBAR_HEIGHT as i32)
    }

    /// Checks if mouse clicked the close button (🔴 Coral Red)
    pub fn hit_close(&self, px: i32, py: i32) -> bool {
        let btn_x = self.x + 16;
        let btn_y = self.y + 14;
        let dx = px - btn_x;
        let dy = py - btn_y;
        (dx * dx + dy * dy) <= (TRAFFIC_LIGHT_RADIUS as i32 + 2).pow(2)
    }

    /// Checks if mouse clicked the minimize button (🟡 Amber Yellow)
    pub fn hit_minimize(&self, px: i32, py: i32) -> bool {
        let btn_x = self.x + 36;
        let btn_y = self.y + 14;
        let dx = px - btn_x;
        let dy = py - btn_y;
        (dx * dx + dy * dy) <= (TRAFFIC_LIGHT_RADIUS as i32 + 2).pow(2)
    }

    /// Checks if mouse clicked the maximize button (🟢 Emerald Green)
    pub fn hit_maximize(&self, px: i32, py: i32) -> bool {
        let btn_x = self.x + 56;
        let btn_y = self.y + 14;
        let dx = px - btn_x;
        let dy = py - btn_y;
        (dx * dx + dy * dy) <= (TRAFFIC_LIGHT_RADIUS as i32 + 2).pow(2)
    }

    /// Renders the complete window frame, shadow, titlebar, traffic lights, and borders
    pub fn render_frame(&self, fb: &mut Framebuffer) {
        if self.is_minimized {
            return;
        }

        // Draw soft drop shadow behind window
        fb.draw_shadow(self.x, self.y, self.width, self.height, 8, 90);

        // Window background fill
        let bg_color = Theme::WIN_BG_DARK;
        fb.draw_rounded_rect(self.x, self.y, self.width, self.height, 8, bg_color, true);

        // Window Titlebar
        let titlebar_color = if self.is_active {
            Theme::WIN_TITLEBAR_ACTIVE
        } else {
            Theme::WIN_TITLEBAR_INACTIVE
        };

        // Titlebar rectangle
        fb.fill_rect(self.x, self.y, self.width, TITLEBAR_HEIGHT, titlebar_color);

        // Traffic Light Controls (macOS style 🔴 🟡 🟢)
        let (c_close, c_min, c_max) = if self.is_active {
            (Theme::BTN_CLOSE, Theme::BTN_MINIMIZE, Theme::BTN_MAXIMIZE)
        } else {
            (Theme::BTN_INACTIVE, Theme::BTN_INACTIVE, Theme::BTN_INACTIVE)
        };

        fb.draw_circle(self.x + 16, self.y + 14, TRAFFIC_LIGHT_RADIUS, c_close, true);
        fb.draw_circle(self.x + 36, self.y + 14, TRAFFIC_LIGHT_RADIUS, c_min, true);
        fb.draw_circle(self.x + 56, self.y + 14, TRAFFIC_LIGHT_RADIUS, c_max, true);

        // Titlebar Title String
        let title_color = if self.is_active {
            Theme::TEXT_PRIMARY
        } else {
            Theme::TEXT_MUTED
        };
        let text_x = (self.x + 76) as usize;
        let text_y = (self.y + 6) as usize;
        fb.draw_string(text_x, text_y, self.title, title_color);

        // 1px Outer border
        fb.draw_rounded_rect(self.x, self.y, self.width, self.height, 8, Theme::WIN_BORDER, false);
    }
}
