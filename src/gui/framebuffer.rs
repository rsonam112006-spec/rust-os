//! Linear Framebuffer & 2D Software Rendering Engine
//!
//! Provides accelerated software graphics primitives, alpha blending, gradients,
//! rounded rectangles, window shadows, and text rasterization.

use super::font::{get_glyph, FONT_WIDTH};
use super::theme::ColorArgb;

#[cfg(feature = "std")]
use std::vec::Vec;

pub const FB_DEFAULT_WIDTH: usize = 1024;
pub const FB_DEFAULT_HEIGHT: usize = 768;

pub struct Framebuffer {
    pub width: usize,
    pub height: usize,
    pub pitch: usize, // bytes per row (width * 4)
    #[cfg(feature = "std")]
    pub buffer: Vec<u32>,
    #[cfg(not(feature = "std"))]
    pub buffer_ptr: *mut u32,
}

impl Framebuffer {
    #[cfg(feature = "std")]
    pub fn new(width: usize, height: usize) -> Self {
        let size = width * height;
        Self {
            width,
            height,
            pitch: width * 4,
            buffer: vec![0u32; size],
        }
    }

    #[cfg(not(feature = "std"))]
    pub unsafe fn from_raw(width: usize, height: usize, ptr: *mut u32) -> Self {
        Self {
            width,
            height,
            pitch: width * 4,
            buffer_ptr: ptr,
        }
    }

    #[inline]
    pub fn put_pixel(&mut self, x: usize, y: usize, color: ColorArgb) {
        if x < self.width && y < self.height {
            #[cfg(feature = "std")]
            {
                self.buffer[y * self.width + x] = color.0;
            }
            #[cfg(not(feature = "std"))]
            unsafe {
                *self.buffer_ptr.add(y * self.width + x) = color.0;
            }
        }
    }

    #[inline]
    pub fn get_pixel(&self, x: usize, y: usize) -> ColorArgb {
        if x < self.width && y < self.height {
            #[cfg(feature = "std")]
            {
                ColorArgb(self.buffer[y * self.width + x])
            }
            #[cfg(not(feature = "std"))]
            unsafe {
                ColorArgb(*self.buffer_ptr.add(y * self.width + x))
            }
        } else {
            ColorArgb(0)
        }
    }

    #[inline]
    pub fn blend_pixel(&mut self, x: usize, y: usize, color: ColorArgb) {
        let a = color.a();
        if a == 255 {
            self.put_pixel(x, y, color);
        } else if a > 0 && x < self.width && y < self.height {
            let bg = self.get_pixel(x, y);
            let inv_a = 255 - a as u32;
            let a_u32 = a as u32;

            let r = ((color.r() as u32 * a_u32 + bg.r() as u32 * inv_a) / 255) as u8;
            let g = ((color.g() as u32 * a_u32 + bg.g() as u32 * inv_a) / 255) as u8;
            let b = ((color.b() as u32 * a_u32 + bg.b() as u32 * inv_a) / 255) as u8;

            self.put_pixel(x, y, ColorArgb::rgb(r, g, b));
        }
    }

    pub fn clear(&mut self, color: ColorArgb) {
        #[cfg(feature = "std")]
        {
            self.buffer.fill(color.0);
        }
        #[cfg(not(feature = "std"))]
        {
            for y in 0..self.height {
                for x in 0..self.width {
                    self.put_pixel(x, y, color);
                }
            }
        }
    }

    pub fn fill_rect(&mut self, x: i32, y: i32, w: u32, h: u32, color: ColorArgb) {
        let x_start = x.max(0) as usize;
        let y_start = y.max(0) as usize;
        let x_end = ((x + w as i32).max(0) as usize).min(self.width);
        let y_end = ((y + h as i32).max(0) as usize).min(self.height);

        for py in y_start..y_end {
            for px in x_start..x_end {
                self.blend_pixel(px, py, color);
            }
        }
    }

    pub fn draw_rect(&mut self, x: i32, y: i32, w: u32, h: u32, color: ColorArgb) {
        if w == 0 || h == 0 {
            return;
        }
        self.fill_rect(x, y, w, 1, color);
        self.fill_rect(x, y + h as i32 - 1, w, 1, color);
        self.fill_rect(x, y, 1, h, color);
        self.fill_rect(x + w as i32 - 1, y, 1, h, color);
    }

    pub fn draw_rounded_rect(
        &mut self,
        x: i32,
        y: i32,
        w: u32,
        h: u32,
        radius: u32,
        color: ColorArgb,
        fill: bool,
    ) {
        if fill {
            let r = radius as i32;
            let wi = w as i32;
            let hi = h as i32;

            // Middle horizontal rectangle
            self.fill_rect(x + r, y, (w - 2 * radius).max(1), h, color);
            // Left & Right side vertical strips
            self.fill_rect(x, y + r, radius, (h - 2 * radius).max(1), color);
            self.fill_rect(x + wi - r, y + r, radius, (h - 2 * radius).max(1), color);

            // Four corner circles
            self.draw_circle(x + r, y + r, radius, color, true);
            self.draw_circle(x + wi - r - 1, y + r, radius, color, true);
            self.draw_circle(x + r, y + hi - r - 1, radius, color, true);
            self.draw_circle(x + wi - r - 1, y + hi - r - 1, radius, color, true);
        } else {
            self.draw_rect(x, y, w, h, color);
        }
    }

    pub fn draw_gradient_v(
        &mut self,
        x: i32,
        y: i32,
        w: u32,
        h: u32,
        c_top: ColorArgb,
        c_bot: ColorArgb,
    ) {
        if h == 0 {
            return;
        }
        for i in 0..h {
            let t = i as f32 / h as f32;
            let r = (c_top.r() as f32 * (1.0 - t) + c_bot.r() as f32 * t) as u8;
            let g = (c_top.g() as f32 * (1.0 - t) + c_bot.g() as f32 * t) as u8;
            let b = (c_top.b() as f32 * (1.0 - t) + c_bot.b() as f32 * t) as u8;
            self.fill_rect(x, y + i as i32, w, 1, ColorArgb::rgb(r, g, b));
        }
    }

    pub fn draw_circle(&mut self, cx: i32, cy: i32, radius: u32, color: ColorArgb, fill: bool) {
        let r = radius as i32;
        let r2 = r * r;

        if fill {
            for dy in -r..=r {
                for dx in -r..=r {
                    if dx * dx + dy * dy <= r2 {
                        let px = cx + dx;
                        let py = cy + dy;
                        if px >= 0 && py >= 0 {
                            self.blend_pixel(px as usize, py as usize, color);
                        }
                    }
                }
            }
        } else {
            let mut x = 0;
            let mut y = r;
            let mut d = 3 - 2 * r;
            while y >= x {
                let pts = [
                    (cx + x, cy + y),
                    (cx - x, cy + y),
                    (cx + x, cy - y),
                    (cx - x, cy - y),
                    (cx + y, cy + x),
                    (cx - y, cy + x),
                    (cx + y, cy - x),
                    (cx - y, cy - x),
                ];
                for (px, py) in pts {
                    if px >= 0 && py >= 0 {
                        self.blend_pixel(px as usize, py as usize, color);
                    }
                }
                x += 1;
                if d > 0 {
                    y -= 1;
                    d += 4 * (x - y) + 10;
                } else {
                    d += 4 * x + 6;
                }
            }
        }
    }

    /// Renders realistic floating window drop shadows
    pub fn draw_shadow(&mut self, x: i32, y: i32, w: u32, h: u32, spread: i32, base_alpha: u8) {
        for s in 1..=spread {
            let alpha = (base_alpha as i32 * (spread - s + 1) / (spread * 2)) as u8;
            let shadow_color = ColorArgb::new(alpha, 0, 0, 0);
            self.draw_rect(
                x - s,
                y - s + 4,
                w + (s as u32 * 2),
                h + (s as u32 * 2),
                shadow_color,
            );
        }
    }

    pub fn draw_char(&mut self, x: usize, y: usize, c: char, fg: ColorArgb) {
        if let Some(glyph) = get_glyph(c) {
            for (row, byte) in glyph.iter().enumerate() {
                for col in 0..8 {
                    if (byte & (0x80 >> col)) != 0 {
                        self.blend_pixel(x + col, y + row, fg);
                    }
                }
            }
        }
    }

    pub fn draw_string(&mut self, x: usize, y: usize, text: &str, fg: ColorArgb) {
        let mut cur_x = x;
        for c in text.chars() {
            if c == '\n' {
                cur_x = x;
            } else {
                self.draw_char(cur_x, y, c, fg);
                cur_x += FONT_WIDTH;
            }
        }
    }
}
