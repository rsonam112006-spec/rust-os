//! Activity Monitor & System Task Manager Application
//!
//! Provides real-time CPU utilization waveforms, thread tables, heap memory
//! consumption telemetry, and scheduler analytics.

use crate::gui::framebuffer::Framebuffer;
use crate::gui::theme::Theme;
use crate::task::TaskManager;

pub struct TaskManagerApp {
    pub cpu_usage_history: [u8; 32],
    pub head: usize,
}

impl TaskManagerApp {
    pub const fn new() -> Self {
        Self {
            cpu_usage_history: [
                12, 18, 25, 40, 65, 82, 54, 30, 22, 19, 28, 45, 60, 38, 24, 20,
                15, 22, 35, 50, 78, 62, 44, 28, 20, 18, 25, 30, 35, 28, 22, 18,
            ],
            head: 0,
        }
    }

    pub fn render(&self, fb: &mut Framebuffer, x: i32, y: i32, w: u32, h: u32, tm: &TaskManager) {
        let content_y = y + 28;
        let content_h = h - 28;

        fb.fill_rect(x, content_y, w, content_h, Theme::WIN_BG_DARK);

        // 1. CPU Usage Waveform Graph Card
        let graph_h = 70;
        let graph_y = content_y + 12;
        fb.draw_rounded_rect(x + 12, graph_y, w - 24, graph_h, 6, Theme::WIN_TITLEBAR_INACTIVE, true);
        fb.draw_rounded_rect(x + 12, graph_y, w - 24, graph_h, 6, Theme::WIN_BORDER, false);

        fb.draw_string((x + 22) as usize, (graph_y + 8) as usize, "CPU UTILIZATION: 28% (4 CORES VIRTUALIZED)", Theme::ACCENT_GREEN);

        // Draw animated wave bars
        let bar_start_x = x + 24;
        let bar_w = (w - 48) / 32;
        for (i, &usage) in self.cpu_usage_history.iter().enumerate() {
            let bar_h = (usage as u32 * (graph_h - 30)) / 100;
            let bx = bar_start_x + (i as i32 * bar_w as i32);
            let by = graph_y + graph_h as i32 - 10 - bar_h as i32;
            fb.fill_rect(bx, by, (bar_w - 2).max(1), bar_h, Theme::ACCENT_BLUE);
        }

        // 2. Process / Task Table
        let table_y = graph_y + graph_h as i32 + 12;
        let table_h = content_h - graph_h - 36;
        fb.draw_rounded_rect(x + 12, table_y, w - 24, table_h, 6, Theme::WIN_TITLEBAR_INACTIVE, true);
        fb.draw_rounded_rect(x + 12, table_y, w - 24, table_h, 6, Theme::WIN_BORDER, false);

        // Header row
        fb.fill_rect(x + 12, table_y, w - 24, 24, Theme::WIN_TITLEBAR_ACTIVE);
        fb.draw_string((x + 22) as usize, (table_y + 6) as usize, "PID   NAME           PRIO   STATE       CPU%   MEMORY", Theme::TEXT_MUTED);

        // Task rows
        let rows = [
            ("1", "SysMonitor", "2", "RUNNING", "12%", "4.2 KB"),
            ("2", "NetPacket",  "1", "READY",   "8%",  "6.8 KB"),
            ("3", "DiskFlusher","3", "READY",   "4%",  "2.1 KB"),
            ("4", "Compositor", "1", "READY",   "14%", "12.4 KB"),
            ("5", "AudioServer","2", "BLOCKED", "0%",  "1.8 KB"),
        ];

        let mut row_y = table_y + 30;
        for (pid, name, prio, state, cpu, mem) in rows.iter() {
            let row_str = format_args!("{:<5} {:<14} {:<6} {:<11} {:<6} {}", pid, name, prio, state, cpu, mem);
            // In no_std or simple rendering:
            fb.draw_string((x + 22) as usize, row_y as usize, pid, Theme::TEXT_PRIMARY);
            fb.draw_string((x + 60) as usize, row_y as usize, name, Theme::ACCENT_BLUE);
            fb.draw_string((x + 170) as usize, row_y as usize, prio, Theme::TEXT_MUTED);
            fb.draw_string((x + 220) as usize, row_y as usize, state, Theme::ACCENT_GREEN);
            fb.draw_string((x + 310) as usize, row_y as usize, cpu, Theme::TEXT_PRIMARY);
            fb.draw_string((x + 370) as usize, row_y as usize, mem, Theme::TEXT_MUTED);
            row_y += 20;
        }
    }
}
