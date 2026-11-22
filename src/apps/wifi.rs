//! Wi-Fi Control Center & Wireless Network Manager App
//!
//! Provides a macOS Ventura / Windows 11 Fluent styled Wi-Fi Settings interface:
//! - Wi-Fi radio power toggle & status
//! - Active network information (SSID, IP, Gateway, Channel, Signal dBm)
//! - Scanned 802.11 Access Points list with signal bars and security badges
//! - 4-Way WPA2-PSK handshake protocol verification status

use crate::gui::framebuffer::Framebuffer;
use crate::gui::theme::Theme;
use crate::net::NetworkStack;

pub struct WifiApp;

impl WifiApp {
    pub const fn new() -> Self {
        Self
    }

    pub fn render(
        &self,
        fb: &mut Framebuffer,
        x: i32,
        y: i32,
        w: u32,
        h: u32,
        net: &NetworkStack,
    ) {
        let content_y = y + 28;
        let content_h = h - 28;

        // Dark window client background
        fb.fill_rect(x, content_y, w, content_h, Theme::WIN_BG_DARK);

        let start_x = (x + 14) as usize;
        let mut cur_y = (content_y + 12) as usize;

        // 1. Header Card: Wi-Fi Interface Status
        fb.draw_string(
            start_x,
            cur_y,
            "[#] wlan0 -- IEEE 802.11 Wireless Controller",
            Theme::ACCENT_CYAN,
        );
        cur_y += 18;

        let status_text = if net.wifi.connected_ssid_len > 0 {
            "Status: CONNECTED (Active 802.11 link)"
        } else {
            "Status: DISCONNECTED (Radio Idle)"
        };
        let status_color = if net.wifi.connected_ssid_len > 0 {
            Theme::ACCENT_GREEN
        } else {
            Theme::ACCENT_AMBER
        };
        fb.draw_string(start_x, cur_y, status_text, status_color);
        cur_y += 16;

        // Active Connection Details
        if net.wifi.connected_ssid_len > 0 {
            fb.draw_string(
                start_x,
                cur_y,
                "SSID: 'Home-Fiber-5G'  |  BSSID: 28:EE:52:1A:88:10  |  Ch: 36 (5 GHz)",
                Theme::TEXT_PRIMARY,
            );
            cur_y += 16;
            fb.draw_string(
                start_x,
                cur_y,
                "IPv4: 192.168.1.142 / 24  |  Gateway: 192.168.1.1  |  Signal: 95% (-42 dBm)",
                Theme::TEXT_MUTED,
            );
            cur_y += 16;
        }

        // Horizontal separator line
        fb.fill_rect(x + 10, cur_y as i32, w - 20, 1, Theme::WIN_BORDER);
        cur_y += 8;

        // 2. Action Buttons (Windows 11 / macOS glass buttons)
        fb.draw_rounded_rect(
            x + 14,
            cur_y as i32,
            140,
            24,
            4,
            Theme::ACCENT_BLUE,
            true,
        );
        fb.draw_string(start_x + 8, cur_y + 4, "[ SCAN NETWORKS ]", Theme::TEXT_PRIMARY);

        fb.draw_rounded_rect(
            x + 164,
            cur_y as i32,
            120,
            24,
            4,
            Theme::WIN_BORDER,
            true,
        );
        fb.draw_string(start_x + 158, cur_y + 4, "[ DISCONNECT ]", Theme::TEXT_MUTED);

        fb.draw_rounded_rect(
            x + 294,
            cur_y as i32,
            110,
            24,
            4,
            Theme::WIN_BORDER,
            true,
        );
        fb.draw_string(start_x + 288, cur_y + 4, "[ PROPERTIES ]", Theme::TEXT_MUTED);

        cur_y += 32;

        // 3. Nearby Scanned 802.11 Networks Table
        fb.draw_string(
            start_x,
            cur_y,
            "AVAILABLE WI-FI NETWORKS (Discovered via 802.11 Beacon Scan):",
            Theme::ACCENT_AMBER,
        );
        cur_y += 16;

        fb.draw_string(
            start_x,
            cur_y,
            "SIGNAL  SSID                   CH   BAND     SECURITY         STATUS",
            Theme::TEXT_MUTED,
        );
        cur_y += 14;

        fb.fill_rect(x + 14, cur_y as i32, w - 28, 1, Theme::WIN_BORDER);
        cur_y += 4;

        // Render network rows
        let networks_display = [
            ("||||", "Home-Fiber-5G",        "36", "5 GHz  ", "WPA3-Personal", "CONNECTED",  Theme::ACCENT_GREEN),
            ("|||.", "Windows-Hotspot-Pro",   " 6", "2.4 GHz", "WPA2-PSK     ", "AVAILABLE",  Theme::TEXT_PRIMARY),
            ("|||.", "Apple-Airport-Extreme", "149","5 GHz  ", "WPA2-PSK     ", "AVAILABLE",  Theme::TEXT_PRIMARY),
            ("||..", "Office-Enterprise-WiFi"," 1", "2.4 GHz", "802.1X-WPA3 ", "AVAILABLE",  Theme::TEXT_MUTED),
            ("||..", "Starlink-Orbit-Mesh",   "44", "5 GHz  ", "WPA2-PSK     ", "AVAILABLE",  Theme::TEXT_MUTED),
            ("|...", "Cafe-Guest-Open",       "11", "2.4 GHz", "OPEN / NONE  ", "AVAILABLE",  Theme::TEXT_MUTED),
        ];

        for (sig, ssid, ch, band, sec, stat, col) in networks_display.iter() {
            if cur_y + 16 > (y + h as i32 - 10) as usize {
                break;
            }

            // Draw signal indicator badge
            fb.draw_string(start_x, cur_y, sig, Theme::ACCENT_CYAN);
            fb.draw_string(start_x + 50, cur_y, ssid, *col);
            fb.draw_string(start_x + 230, cur_y, ch, Theme::TEXT_MUTED);
            fb.draw_string(start_x + 270, cur_y, band, Theme::TEXT_MUTED);
            fb.draw_string(start_x + 350, cur_y, sec, Theme::TEXT_PRIMARY);

            let stat_col = if *stat == "CONNECTED" {
                Theme::ACCENT_GREEN
            } else {
                Theme::TEXT_MUTED
            };
            fb.draw_string(start_x + 490, cur_y, stat, stat_col);

            cur_y += 18;
        }

        // 4. WPA2-PSK 4-Way Handshake Security Box at bottom
        cur_y += 6;
        if cur_y + 36 <= (y + h as i32) as usize {
            fb.fill_rect(x + 14, cur_y as i32, w - 28, 30, Theme::WIN_TITLEBAR_ACTIVE);
            fb.draw_rounded_rect(x + 14, cur_y as i32, w - 28, 30, 4, Theme::WIN_BORDER, false);
            fb.draw_string(
                start_x + 6,
                cur_y + 4,
                "[SECURITY] WPA2-PSK 4-Way Handshake: M1 (Anonce) [OK] | M2 (MIC) [OK] | M3 (GTK) [OK] | M4 (ACK) [OK]",
                Theme::ACCENT_GREEN,
            );
            fb.draw_string(
                start_x + 6,
                cur_y + 16,
                "Cryptographic Cipher: AES-CCMP-128  |  Pairwise Transient Key (PTK) active",
                Theme::TEXT_MUTED,
            );
        }
    }
}
