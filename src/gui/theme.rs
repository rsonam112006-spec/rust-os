//! macOS & Windows 11 Fluent Theme Palette & Aesthetics
//!
//! Defines color constants, glass/acrylic translucency styling,
//! and macOS traffic light window controls.

#[derive(Debug, Clone, Copy)]
pub struct ColorArgb(pub u32);

impl ColorArgb {
    pub const fn new(a: u8, r: u8, g: u8, b: u8) -> Self {
        ColorArgb(((a as u32) << 24) | ((r as u32) << 16) | ((g as u32) << 8) | (b as u32))
    }

    pub const fn rgb(r: u8, g: u8, b: u8) -> Self {
        Self::new(255, r, g, b)
    }

    pub fn a(&self) -> u8 {
        ((self.0 >> 24) & 0xFF) as u8
    }

    pub fn r(&self) -> u8 {
        ((self.0 >> 16) & 0xFF) as u8
    }

    pub fn g(&self) -> u8 {
        ((self.0 >> 8) & 0xFF) as u8
    }

    pub fn b(&self) -> u8 {
        (self.0 & 0xFF) as u8
    }
}

pub struct Theme;

impl Theme {
    // macOS traffic light window buttons
    pub const BTN_CLOSE: ColorArgb = ColorArgb::rgb(0xFF, 0x5F, 0x56);      // Coral Red
    pub const BTN_MINIMIZE: ColorArgb = ColorArgb::rgb(0xFF, 0xBD, 0x2E);   // Amber Yellow
    pub const BTN_MAXIMIZE: ColorArgb = ColorArgb::rgb(0x27, 0xC9, 0x3F);   // Emerald Green
    pub const BTN_INACTIVE: ColorArgb = ColorArgb::rgb(0x4A, 0x4B, 0x50);   // Dim Gray

    // Window chrome & frames (Windows 11 Mica / macOS Ventura Dark)
    pub const WIN_CHROME: ColorArgb = ColorArgb::rgb(0x23, 0x25, 0x2F);
    pub const WIN_TITLEBAR_ACTIVE: ColorArgb = ColorArgb::rgb(0x24, 0x26, 0x2E);
    pub const WIN_TITLEBAR_INACTIVE: ColorArgb = ColorArgb::rgb(0x1B, 0x1C, 0x22);
    pub const WIN_BG_DARK: ColorArgb = ColorArgb::rgb(0x18, 0x19, 0x20);
    pub const WIN_BG_LIGHT: ColorArgb = ColorArgb::rgb(0xF5, 0xF6, 0xF8);
    pub const WIN_BORDER: ColorArgb = ColorArgb::rgb(0x3E, 0x41, 0x4D);

    // Desktop top menu bar (macOS style translucent header)
    pub const MENUBAR_BG: ColorArgb = ColorArgb::new(230, 0x12, 0x13, 0x18);
    pub const MENUBAR_TEXT: ColorArgb = ColorArgb::rgb(0xE0, 0xE2, 0xEC);

    // Floating Dock / Taskbar (macOS Sonoma / Windows 11 centered dock)
    pub const DOCK_BG: ColorArgb = ColorArgb::new(220, 0x20, 0x22, 0x2B);
    pub const DOCK_BORDER: ColorArgb = ColorArgb::new(180, 0x4A, 0x4E, 0x5E);
    pub const DOCK_ACTIVE_DOT: ColorArgb = ColorArgb::rgb(0x0A, 0x84, 0xFF);

    // Desktop wallpaper colors (Sonoma / Windows 11 Flow gradient)
    pub const WALLPAPER_TOP: ColorArgb = ColorArgb::rgb(0x0A, 0x19, 0x31);    // Deep Midnight Blue
    pub const WALLPAPER_MID: ColorArgb = ColorArgb::rgb(0x15, 0x3E, 0x75);    // Azure Navy
    pub const WALLPAPER_BOTTOM: ColorArgb = ColorArgb::rgb(0x6E, 0x25, 0x94); // Velvet Purple

    // Text & accent highlights
    pub const TEXT_PRIMARY: ColorArgb = ColorArgb::rgb(0xF5, 0xF5, 0xF7);
    pub const TEXT_MUTED: ColorArgb = ColorArgb::rgb(0x8E, 0x92, 0x9E);
    pub const ACCENT_BLUE: ColorArgb = ColorArgb::rgb(0x0A, 0x84, 0xFF);
    pub const ACCENT_GREEN: ColorArgb = ColorArgb::rgb(0x30, 0xD1, 0x58);
    pub const ACCENT_PURPLE: ColorArgb = ColorArgb::rgb(0xBF, 0x5A, 0xF2);
    pub const ACCENT_CYAN: ColorArgb = ColorArgb::rgb(0x32, 0xDE, 0xF9);
    pub const ACCENT_AMBER: ColorArgb = ColorArgb::rgb(0xFF, 0xD6, 0x0A);
}
