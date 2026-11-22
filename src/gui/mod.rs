//! Desktop Graphical User Interface (GUI) Subsystem
//!
//! Provides a macOS & Windows 11 fluent desktop environment with:
//! - 32-bit TrueColor Linear Framebuffer (1024x768)
//! - 2D software rendering (alpha blending, gradients, rounded corners, shadows)
//! - Window server & compositor with z-ordering, dragging, and focus
//! - macOS traffic light buttons (🔴 Close, 🟡 Minimize, 🟢 Maximize)
//! - Floating application dock and top translucent menu bar

pub mod compositor;
pub mod desktop;
pub mod font;
pub mod framebuffer;
pub mod theme;
pub mod window;

pub use compositor::{Compositor, MAX_WINDOWS};
pub use desktop::Desktop;
pub use font::{FONT_HEIGHT, FONT_WIDTH};
pub use framebuffer::Framebuffer;
pub use theme::{ColorArgb, Theme};
pub use window::{AppType, Window, TITLEBAR_HEIGHT};

/// Creates the default Micro-OS desktop with pre-configured windows
pub fn create_default_desktop() -> Compositor {
    let mut comp = Compositor::new();

    // 1. Network Navigator & Browser Window
    let win_net = Window::new(
        1,
        "Network Navigator & Diagnostic Center",
        60,
        60,
        520,
        360,
        AppType::Browser,
    );
    let _ = comp.add_window(win_net);

    // 2. PowerTerminal Shell Window
    let win_term = Window::new(
        2,
        "PowerTerminal (micro-os:~$)",
        240,
        140,
        540,
        340,
        AppType::Terminal,
    );
    let _ = comp.add_window(win_term);

    // 3. Wi-Fi Control Center & Wireless Manager
    let win_wifi = Window::new(
        3,
        "Wi-Fi Settings (wlan0 802.11ax)",
        360,
        90,
        560,
        360,
        AppType::Wifi,
    );
    let _ = comp.add_window(win_wifi);

    // Focus Wi-Fi window by default
    comp.focus_window(2);

    comp
}
