//! VGA Text Mode Buffer Driver (80x25 characters at 0xb8000)
//! Provides Windows 11 Fluent Graphical Desktop Rendering & Window Terminal

use core::fmt;

pub const BUFFER_HEIGHT: usize = 25;
pub const BUFFER_WIDTH: usize = 80;
pub const VGA_BUFFER_ADDR: usize = 0xb8000;

pub const WIN_TOP_ROW: usize = 2;
pub const WIN_BOT_ROW: usize = 22;
pub const WIN_LEFT_COL: usize = 2;
pub const WIN_RIGHT_COL: usize = 77;

pub const CONTENT_TOP_ROW: usize = 11;
pub const CONTENT_BOT_ROW: usize = 21;
pub const CONTENT_LEFT_COL: usize = 4;
pub const CONTENT_RIGHT_COL: usize = 75;

#[allow(dead_code)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum Color {
    Black = 0,
    Blue = 1,
    Green = 2,
    Cyan = 3,
    Red = 4,
    Magenta = 5,
    Brown = 6,
    LightGray = 7,
    DarkGray = 8,
    LightBlue = 9,
    LightGreen = 10,
    LightCyan = 11,
    LightRed = 12,
    Pink = 13,
    Yellow = 14,
    White = 15,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(transparent)]
pub struct ColorCode(pub u8);

impl ColorCode {
    pub const fn new(foreground: Color, background: Color) -> ColorCode {
        ColorCode((background as u8) << 4 | (foreground as u8))
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(C)]
pub struct ScreenChar {
    pub ascii_character: u8,
    pub color_code: ColorCode,
}

pub struct Writer {
    pub column_position: usize,
    pub row_position: usize,
    pub current_color: ColorCode,
    buffer: *mut ScreenChar,
}

impl Writer {
    pub const fn new() -> Self {
        Writer {
            column_position: CONTENT_LEFT_COL,
            row_position: CONTENT_TOP_ROW,
            current_color: ColorCode::new(Color::White, Color::Black),
            buffer: VGA_BUFFER_ADDR as *mut ScreenChar,
        }
    }

    pub fn set_color(&mut self, fg: Color, bg: Color) {
        self.current_color = ColorCode::new(fg, bg);
    }

    pub fn write_string(&mut self, s: &str) {
        self.write_window_str(s, Color::LightRed);
    }

    #[inline]
    pub fn write_cell(&mut self, row: usize, col: usize, ascii: u8, fg: Color, bg: Color) {
        if row < BUFFER_HEIGHT && col < BUFFER_WIDTH {
            let idx = row * BUFFER_WIDTH + col;
            let sc = ScreenChar {
                ascii_character: ascii,
                color_code: ColorCode::new(fg, bg),
            };
            unsafe {
                self.buffer.add(idx).write_volatile(sc);
            }
        }
    }

    pub fn write_str_at(&mut self, row: usize, col: usize, text: &str, fg: Color, bg: Color) {
        let mut curr_col = col;
        for b in text.bytes() {
            if curr_col >= BUFFER_WIDTH {
                break;
            }
            self.write_cell(row, curr_col, b, fg, bg);
            curr_col += 1;
        }
    }

    pub fn clear_screen(&mut self) {
        let blank = ScreenChar {
            ascii_character: b' ',
            color_code: ColorCode::new(Color::White, Color::Black),
        };
        for i in 0..(BUFFER_HEIGHT * BUFFER_WIDTH) {
            unsafe {
                self.buffer.add(i).write_volatile(blank);
            }
        }
        self.column_position = 0;
        self.row_position = 0;
    }

    /// Renders the complete Windows 11 Fluent Graphical Desktop Environment
    pub fn draw_windows11_desktop(&mut self) {
        // 1. Fill desktop background with Royal Blue
        for r in 0..BUFFER_HEIGHT {
            for c in 0..BUFFER_WIDTH {
                self.write_cell(r, c, b' ', Color::White, Color::Blue);
            }
        }

        // 2. Top Menu Bar (Row 0): LightGray background, Black text
        let top_menu = " Win11 Fluent OS   File   Edit   View   Terminal   Wi-Fi   Settings   Help     ";
        for c in 0..BUFFER_WIDTH {
            let b = if c < top_menu.len() { top_menu.as_bytes()[c] } else { b' ' };
            self.write_cell(0, c, b, Color::Black, Color::LightGray);
        }

        // 3. Bottom Taskbar (Row 24): LightGray background, Black text
        let taskbar = " [24C Sunny]  [Start] [Search] [Term] [Files] [Store]  [WiFi: Jain_Student 82%] 14:12 ";
        for c in 0..BUFFER_WIDTH {
            let b = if c < taskbar.len() { taskbar.as_bytes()[c] } else { b' ' };
            self.write_cell(24, c, b, Color::Black, Color::LightGray);
        }

        // 4. Centered Windows 11 Terminal Window Borders (Rows 2..22, Cols 2..77)
        // Top border with Title & Window Controls
        self.write_cell(WIN_TOP_ROW, WIN_LEFT_COL, 0xC9, Color::Yellow, Color::Black); // ╔
        for c in (WIN_LEFT_COL + 1)..WIN_RIGHT_COL {
            self.write_cell(WIN_TOP_ROW, c, 0xCD, Color::Yellow, Color::Black); // ═
        }
        self.write_cell(WIN_TOP_ROW, WIN_RIGHT_COL, 0xBB, Color::Yellow, Color::Black); // ╗

        // Title and controls in border:
        self.write_str_at(WIN_TOP_ROW, 4, "[ Win11 Terminal: Lenovo@RustOS ]", Color::White, Color::Black);
        self.write_str_at(WIN_TOP_ROW, 68, "[-][+][X]", Color::LightCyan, Color::Black);

        // Window Interior (Black background) & Side Borders (║)
        for r in (WIN_TOP_ROW + 1)..WIN_BOT_ROW {
            self.write_cell(r, WIN_LEFT_COL, 0xBA, Color::Yellow, Color::Black); // ║
            for c in (WIN_LEFT_COL + 1)..WIN_RIGHT_COL {
                self.write_cell(r, c, b' ', Color::White, Color::Black);
            }
            self.write_cell(r, WIN_RIGHT_COL, 0xBA, Color::Yellow, Color::Black); // ║
        }

        // Bottom border
        self.write_cell(WIN_BOT_ROW, WIN_LEFT_COL, 0xC8, Color::Yellow, Color::Black); // ╚
        for c in (WIN_LEFT_COL + 1)..WIN_RIGHT_COL {
            self.write_cell(WIN_BOT_ROW, c, 0xCD, Color::Yellow, Color::Black); // ═
        }
        self.write_cell(WIN_BOT_ROW, WIN_RIGHT_COL, 0xBC, Color::Yellow, Color::Black); // ╝

        // 5. Window Header Content (Rows 3 to 10)
        self.write_str_at(3, 4, "Windows 11 Fluent Rust OS [Version 10.0.22631.3296 - 64-bit Long Mode]", Color::White, Color::Black);
        self.write_str_at(4, 4, "Hardware: Intel(R) Core(TM) i7-13620H  *  Intel(R) Wi-Fi 6 AX203", Color::White, Color::Black);
        self.write_str_at(5, 4, "Wi-Fi AP: 'Jain_Student' (5 GHz, Ch 108, Signal 82%) - Connected OK", Color::LightGreen, Color::Black);
        self.write_str_at(6, 4, "Storage : 512 MB Virtual RAM Disk  *  Memory: 4096 MB (4-Level Paging)", Color::LightCyan, Color::Black);

        let divider = "----------------------------------------------------------------------";
        self.write_str_at(7, 4, divider, Color::DarkGray, Color::Black);
        self.write_str_at(8, 4, "Research: Page Replacement Under Locality (FIFO, LRU, Optimal, Clock)", Color::Yellow, Color::Black);
        self.write_str_at(9, 4, "Commands: help, wifi, wifi scan, ping, benchmark, anomaly, snap, apt, clear", Color::LightCyan, Color::Black);
        self.write_str_at(10, 4, divider, Color::DarkGray, Color::Black);

        // 6. Reset prompt cursor
        self.row_position = CONTENT_TOP_ROW;
        self.column_position = CONTENT_LEFT_COL;
        self.write_str_at(CONTENT_TOP_ROW, CONTENT_LEFT_COL, "C:\\Users\\Lenovo> ", Color::White, Color::Black);
        self.column_position = CONTENT_LEFT_COL + 16;
    }

    /// Write character inside the Windows 11 terminal window with scrolling
    pub fn write_window_byte(&mut self, byte: u8, fg: Color) {
        match byte {
            b'\n' => self.new_window_line(),
            b => {
                if self.column_position >= CONTENT_RIGHT_COL {
                    self.new_window_line();
                }
                self.write_cell(self.row_position, self.column_position, b, fg, Color::Black);
                self.column_position += 1;
            }
        }
    }

    /// Write string inside the Windows 11 terminal window
    pub fn write_window_str(&mut self, s: &str, fg: Color) {
        for b in s.bytes() {
            self.write_window_byte(b, fg);
        }
    }

    /// Handles newlines and smooth scrolling inside the window container
    pub fn new_window_line(&mut self) {
        if self.row_position < CONTENT_BOT_ROW {
            self.row_position += 1;
        } else {
            // Scroll content rows (CONTENT_TOP_ROW + 1 .. CONTENT_BOT_ROW) up by 1
            for r in (CONTENT_TOP_ROW + 1)..=CONTENT_BOT_ROW {
                for c in (WIN_LEFT_COL + 1)..WIN_RIGHT_COL {
                    let from_idx = r * BUFFER_WIDTH + c;
                    let to_idx = (r - 1) * BUFFER_WIDTH + c;
                    unsafe {
                        let sc = self.buffer.add(from_idx).read_volatile();
                        self.buffer.add(to_idx).write_volatile(sc);
                    }
                }
            }
            // Clear the bottom content line
            for c in (WIN_LEFT_COL + 1)..WIN_RIGHT_COL {
                self.write_cell(CONTENT_BOT_ROW, c, b' ', Color::White, Color::Black);
            }
        }
        self.column_position = CONTENT_LEFT_COL;
    }

    /// Backspace inside window container, protected by min_col
    pub fn backspace_window(&mut self, min_col: usize) {
        if self.column_position > min_col {
            self.column_position -= 1;
            self.write_cell(self.row_position, self.column_position, b' ', Color::White, Color::Black);
        }
    }
}

impl fmt::Write for Writer {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        self.write_window_str(s, Color::White);
        Ok(())
    }
}
