//! Window Compositor & Desktop Event Dispatcher
//!
//! Manages z-ordered window stacking, mouse events, window drag/drop,
//! traffic light button actions, and full screen composition.

use super::desktop::Desktop;
use super::framebuffer::Framebuffer;
use super::theme::ColorArgb;
use super::window::Window;

pub const MAX_WINDOWS: usize = 8;

pub struct Compositor {
    pub desktop: Desktop,
    pub windows: [Option<Window>; MAX_WINDOWS],
    pub mouse_x: i32,
    pub mouse_y: i32,
    pub active_window_idx: Option<usize>,
    pub dragging_idx: Option<usize>,
}

impl Compositor {
    pub const fn new() -> Self {
        const NONE_WIN: Option<Window> = None;
        Self {
            desktop: Desktop::new(),
            windows: [NONE_WIN; MAX_WINDOWS],
            mouse_x: 200,
            mouse_y: 200,
            active_window_idx: None,
            dragging_idx: None,
        }
    }

    pub fn add_window(&mut self, win: Window) -> Result<usize, &'static str> {
        for (i, slot) in self.windows.iter_mut().enumerate() {
            if slot.is_none() {
                *slot = Some(win);
                self.focus_window(i);
                return Ok(i);
            }
        }
        Err("Window table full")
    }

    pub fn focus_window(&mut self, idx: usize) {
        if idx >= MAX_WINDOWS || self.windows[idx].is_none() {
            return;
        }

        // Set all windows inactive
        for slot in self.windows.iter_mut() {
            if let Some(w) = slot {
                w.is_active = false;
            }
        }

        // Activate target window
        if let Some(w) = &mut self.windows[idx] {
            w.is_active = true;
            w.is_minimized = false;
        }
        self.active_window_idx = Some(idx);
    }

    pub fn close_window(&mut self, idx: usize) {
        if idx < MAX_WINDOWS {
            self.windows[idx] = None;
            if self.active_window_idx == Some(idx) {
                self.active_window_idx = None;
            }
        }
    }

    pub fn on_mouse_down(&mut self, px: i32, py: i32) {
        let (screen_w, screen_h) = (1024u32, 768u32);

        // 1. Check dock click
        if let Some(app) = self.desktop.hit_dock_icon(screen_w, screen_h, px, py) {
            // Check if window already exists for this app
            for i in 0..MAX_WINDOWS {
                if let Some(w) = &self.windows[i] {
                    if w.app_type == app {
                        self.focus_window(i);
                        return;
                    }
                }
            }
            return;
        }

        // 2. Check window hit from top to bottom (active window checked first)
        let mut hit_idx = None;
        for i in (0..MAX_WINDOWS).rev() {
            if let Some(w) = &self.windows[i] {
                if w.contains_point(px, py) {
                    hit_idx = Some(i);
                    break;
                }
            }
        }

        if let Some(idx) = hit_idx {
            self.focus_window(idx);
            if let Some(w) = &mut self.windows[idx] {
                if w.hit_close(px, py) {
                    self.close_window(idx);
                    return;
                }
                if w.hit_minimize(px, py) {
                    w.is_minimized = true;
                    return;
                }
                if w.hit_maximize(px, py) {
                    if w.is_maximized {
                        w.x = w.saved_x;
                        w.y = w.saved_y;
                        w.width = w.saved_w;
                        w.height = w.saved_h;
                        w.is_maximized = false;
                    } else {
                        w.saved_x = w.x;
                        w.saved_y = w.y;
                        w.saved_w = w.width;
                        w.saved_h = w.height;
                        w.x = 0;
                        w.y = 26; // Below top menu bar
                        w.width = screen_w;
                        w.height = screen_h - 26 - 68; // Above dock
                        w.is_maximized = true;
                    }
                    return;
                }
                if w.titlebar_contains(px, py) {
                    w.is_dragging = true;
                    w.drag_offset_x = px - w.x;
                    w.drag_offset_y = py - w.y;
                    self.dragging_idx = Some(idx);
                }
            }
        }
    }

    pub fn on_mouse_move(&mut self, px: i32, py: i32) {
        self.mouse_x = px;
        self.mouse_y = py;

        if let Some(idx) = self.dragging_idx {
            if let Some(w) = &mut self.windows[idx] {
                if w.is_dragging {
                    w.x = px - w.drag_offset_x;
                    w.y = py - w.drag_offset_y;
                }
            }
        }
    }

    pub fn on_mouse_up(&mut self, _px: i32, _py: i32) {
        if let Some(idx) = self.dragging_idx {
            if let Some(w) = &mut self.windows[idx] {
                w.is_dragging = false;
            }
            self.dragging_idx = None;
        }
    }

    /// Renders mouse pointer cursor (macOS/Windows style sleek pointer)
    pub fn draw_cursor(&self, fb: &mut Framebuffer) {
        let cx = self.mouse_x;
        let cy = self.mouse_y;

        // Draw cursor pointer arrow shape
        let cursor_shape = [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11),
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
            (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
            (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
            (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
            (5, 5), (5, 6), (5, 8), (5, 9), (5, 10),
            (6, 6), (6, 9), (6, 10), (6, 11),
            (7, 11), (7, 12),
        ];

        let cursor_fg = ColorArgb::rgb(0xFF, 0xFF, 0xFF);
        let cursor_outline = ColorArgb::rgb(0x10, 0x10, 0x14);

        // Draw dark border around cursor
        for (dx, dy) in cursor_shape.iter() {
            fb.blend_pixel((cx + dx + 1) as usize, (cy + dy + 1) as usize, cursor_outline);
        }
        // Draw white core
        for (dx, dy) in cursor_shape.iter() {
            fb.blend_pixel((cx + dx) as usize, (cy + dy) as usize, cursor_fg);
        }
    }

    /// Full screen composition pass
    pub fn render(&self, fb: &mut Framebuffer) {
        // 1. Render desktop background, top menu bar, and dock
        self.desktop.render(fb);

        // 2. Render all non-active windows first
        for slot in self.windows.iter() {
            if let Some(w) = slot {
                if !w.is_active && !w.is_minimized {
                    w.render_frame(fb);
                }
            }
        }

        // 3. Render active window on top
        if let Some(idx) = self.active_window_idx {
            if let Some(w) = &self.windows[idx] {
                if !w.is_minimized {
                    w.render_frame(fb);
                }
            }
        }

        // 4. Render mouse cursor on top of everything
        self.draw_cursor(fb);
    }
}
