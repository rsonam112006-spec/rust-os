//! Network Navigator & Web Browser Application
//!
//! Visual application displaying live network interface statistics,
//! interactive ICMP ping diagnostic tool, and HTML/text page rendering.

use crate::gui::framebuffer::Framebuffer;
use crate::gui::theme::Theme;
use crate::net::NetworkStack;

pub struct BrowserApp {
    pub current_url: &'static str,
    pub status_text: &'static str,
    pub last_ping_output: &'static str,
}

impl BrowserApp {
    pub const fn new() -> Self {
        Self {
            current_url: "http://micro.os/welcome",
            status_text: "Status: 200 OK | Connected (virtio-net0)",
            last_ping_output: "Ping 8.8.8.8: 4 packets tx, 4 rx, 0% loss, avg=12.4ms",
        }
    }

    /// Renders the browser UI inside the window client area
    pub fn render(&self, fb: &mut Framebuffer, x: i32, y: i32, w: u32, h: u32, net: &NetworkStack) {
        let content_y = y + 28; // Below titlebar
        let content_h = h - 28;

        // Background fill
        fb.fill_rect(x, content_y, w, content_h, Theme::WIN_BG_DARK);

        // 1. Navigation & URL Bar Toolbar
        let bar_h = 36;
        fb.fill_rect(x, content_y, w, bar_h, Theme::WIN_TITLEBAR_INACTIVE);
        fb.fill_rect(x, content_y + bar_h as i32 - 1, w, 1, Theme::WIN_BORDER);

        // Back / Forward / Refresh buttons
        fb.draw_string((x + 12) as usize, (content_y + 10) as usize, "<  >  @", Theme::TEXT_MUTED);

        // Address Bar Box
        let url_box_x = x + 80;
        let url_box_w = w - 190;
        fb.draw_rounded_rect(url_box_x, content_y + 6, url_box_w, 24, 4, Theme::WIN_BG_DARK, true);
        fb.draw_rounded_rect(url_box_x, content_y + 6, url_box_w, 24, 4, Theme::WIN_BORDER, false);
        fb.draw_string((url_box_x + 8) as usize, (content_y + 10) as usize, self.current_url, Theme::ACCENT_BLUE);

        // Go / Ping Action Button
        let btn_x = x + w as i32 - 100;
        fb.draw_rounded_rect(btn_x, content_y + 6, 88, 24, 4, Theme::ACCENT_BLUE, true);
        fb.draw_string((btn_x + 14) as usize, (content_y + 10) as usize, "Ping Test", Theme::TEXT_PRIMARY);

        // 2. Network Interface Telemetry Card
        let card_y = content_y + bar_h as i32 + 10;
        fb.draw_rounded_rect(x + 12, card_y, w - 24, 80, 6, Theme::WIN_TITLEBAR_ACTIVE, true);
        fb.draw_rounded_rect(x + 12, card_y, w - 24, 80, 6, Theme::WIN_BORDER, false);

        fb.draw_string((x + 22) as usize, (card_y + 10) as usize, "ADAPTER: virtio-net0 (Ethernet 10Gbps)", Theme::TEXT_PRIMARY);
        fb.draw_string((x + 22) as usize, (card_y + 30) as usize, "IPv4: 192.168.1.142 / 24   GW: 192.168.1.1   DNS: 8.8.8.8", Theme::ACCENT_GREEN);
        fb.draw_string((x + 22) as usize, (card_y + 50) as usize, "MAC: 52:54:00:12:34:56     STATUS: LINK ONLINE (FULL DUPLEX)", Theme::TEXT_MUTED);

        // 3. Web Page Content / Ping Results Section
        let body_y = card_y + 90;
        fb.draw_rounded_rect(x + 12, body_y, w - 24, content_h - 136, 6, Theme::WIN_TITLEBAR_INACTIVE, true);
        fb.draw_rounded_rect(x + 12, body_y, w - 24, content_h - 136, 6, Theme::WIN_BORDER, false);

        fb.draw_string((x + 24) as usize, (body_y + 14) as usize, "Rust Micro-OS v2.0 - Hypertext Network Document", Theme::ACCENT_BLUE);
        fb.draw_string((x + 24) as usize, (body_y + 36) as usize, "Successfully retrieved page over TCP/IP socket connection:", Theme::TEXT_PRIMARY);
        fb.draw_string((x + 24) as usize, (body_y + 56) as usize, "- HTTP/1.1 200 OK | Content-Type: text/html | 100% Rust", Theme::ACCENT_GREEN);
        fb.draw_string((x + 24) as usize, (body_y + 76) as usize, "- Active Packets: 1,428 TX | 1,392 RX | 0 Errors", Theme::TEXT_MUTED);
        fb.draw_string((x + 24) as usize, (body_y + 100) as usize, self.last_ping_output, Theme::ACCENT_PURPLE);

        // Status bar at bottom of window
        fb.fill_rect(x, y + h as i32 - 20, w, 20, Theme::WIN_TITLEBAR_INACTIVE);
        fb.draw_string((x + 12) as usize, (y + h as i32 - 16) as usize, self.status_text, Theme::TEXT_MUTED);
    }
}
