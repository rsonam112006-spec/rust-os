//! VGA Text Mode Buffer Driver (80x25 characters at 0xb8000)
//! Pure bare-metal Rust OS terminal driver with hardware scrolling

use core::fmt;

pub const BUFFER_HEIGHT: usize = 25;
pub const BUFFER_WIDTH: usize = 80;
pub const VGA_BUFFER_ADDR: usize = 0xb8000;

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
    pub color_code: ColorCode,
    buffer: *mut ScreenChar,
}

impl Writer {
    pub const fn new() -> Self {
        Writer {
            column_position: 0,
            row_position: 0,
            color_code: ColorCode::new(Color::White, Color::Black),
            buffer: VGA_BUFFER_ADDR as *mut ScreenChar,
        }
    }

    pub fn set_color(&mut self, foreground: Color, background: Color) {
        self.color_code = ColorCode::new(foreground, background);
    }

    pub fn clear_screen(&mut self) {
        let blank = ScreenChar {
            ascii_character: b' ',
            color_code: self.color_code,
        };
        for i in 0..(BUFFER_HEIGHT * BUFFER_WIDTH) {
            unsafe {
                self.buffer.add(i).write_volatile(blank);
            }
        }
        self.column_position = 0;
        self.row_position = 0;
    }

    pub fn backspace(&mut self, min_col: usize) {
        if self.column_position > min_col {
            self.column_position -= 1;
            let char_idx = self.row_position * BUFFER_WIDTH + self.column_position;
            let blank = ScreenChar {
                ascii_character: b' ',
                color_code: self.color_code,
            };
            unsafe {
                self.buffer.add(char_idx).write_volatile(blank);
            }
        }
    }

    pub fn write_byte(&mut self, byte: u8) {
        match byte {
            b'\n' => self.new_line(),
            byte => {
                if self.column_position >= BUFFER_WIDTH {
                    self.new_line();
                }
                let row = self.row_position;
                let col = self.column_position;
                let char_idx = row * BUFFER_WIDTH + col;
                unsafe {
                    self.buffer.add(char_idx).write_volatile(ScreenChar {
                        ascii_character: byte,
                        color_code: self.color_code,
                    });
                }
                self.column_position += 1;
            }
        }
    }

    pub fn write_string(&mut self, s: &str) {
        for byte in s.bytes() {
            match byte {
                0x20..=0x7e | b'\n' => self.write_byte(byte),
                _ => self.write_byte(0xfe),
            }
        }
    }

    pub fn new_line(&mut self) {
        if self.row_position < BUFFER_HEIGHT - 1 {
            self.row_position += 1;
        } else {
            for row in 1..BUFFER_HEIGHT {
                for col in 0..BUFFER_WIDTH {
                    let from_idx = row * BUFFER_WIDTH + col;
                    let to_idx = (row - 1) * BUFFER_WIDTH + col;
                    unsafe {
                        let c = self.buffer.add(from_idx).read_volatile();
                        self.buffer.add(to_idx).write_volatile(c);
                    }
                }
            }
            let blank = ScreenChar {
                ascii_character: b' ',
                color_code: self.color_code,
            };
            for col in 0..BUFFER_WIDTH {
                let idx = (BUFFER_HEIGHT - 1) * BUFFER_WIDTH + col;
                unsafe {
                    self.buffer.add(idx).write_volatile(blank);
                }
            }
        }
        self.column_position = 0;
    }
}

impl fmt::Write for Writer {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        self.write_string(s);
        Ok(())
    }
}
