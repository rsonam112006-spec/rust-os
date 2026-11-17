//! VGA Text Mode Driver (Physical Address 0xB8000)
//!
//! Provides the visual console on the VirtualBox display screen.
//! Supports 80x25 characters, 16 foreground/background colors, scrolling,
//! and carriage return/newline processing.

use core::fmt;

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
pub struct ColorCode(u8);

impl ColorCode {
    pub const fn new(foreground: Color, background: Color) -> ColorCode {
        ColorCode((background as u8) << 4 | (foreground as u8))
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(C)]
struct ScreenChar {
    ascii_character: u8,
    color_code: ColorCode,
}

pub const BUFFER_HEIGHT: usize = 25;
pub const BUFFER_WIDTH: usize = 80;

#[repr(transparent)]
struct Buffer {
    chars: [[ScreenChar; BUFFER_WIDTH]; BUFFER_HEIGHT],
}

pub struct VgaWriter {
    column_position: usize,
    row_position: usize,
    color_code: ColorCode,
    #[cfg(feature = "std")]
    simulated_buffer: [[ScreenChar; BUFFER_WIDTH]; BUFFER_HEIGHT],
}

impl VgaWriter {
    pub const fn new() -> Self {
        Self {
            column_position: 0,
            row_position: 0,
            color_code: ColorCode::new(Color::White, Color::Black),
            #[cfg(feature = "std")]
            simulated_buffer: [[ScreenChar {
                ascii_character: b' ',
                color_code: ColorCode::new(Color::White, Color::Black),
            }; BUFFER_WIDTH]; BUFFER_HEIGHT],
        }
    }

    pub fn set_color(&mut self, foreground: Color, background: Color) {
        self.color_code = ColorCode::new(foreground, background);
    }

    pub fn write_byte(&mut self, byte: u8) {
        match byte {
            b'\n' => self.new_line(),
            b'\r' => self.column_position = 0,
            byte => {
                if self.column_position >= BUFFER_WIDTH {
                    self.new_line();
                }

                let row = self.row_position;
                let col = self.column_position;
                let color_code = self.color_code;

                #[cfg(not(feature = "std"))]
                {
                    let buffer = unsafe { &mut *(0xb8000 as *mut Buffer) };
                    buffer.chars[row][col] = ScreenChar {
                        ascii_character: byte,
                        color_code,
                    };
                }

                #[cfg(feature = "std")]
                {
                    self.simulated_buffer[row][col] = ScreenChar {
                        ascii_character: byte,
                        color_code,
                    };
                }

                self.column_position += 1;
            }
        }
    }

    pub fn write_string(&mut self, s: &str) {
        for byte in s.bytes() {
            match byte {
                // Printable ASCII byte or newline
                0x20..=0x7e | b'\n' | b'\r' => self.write_byte(byte),
                // Not part of printable ASCII range
                _ => self.write_byte(0xfe),
            }
        }
    }

    fn new_line(&mut self) {
        if self.row_position < BUFFER_HEIGHT - 1 {
            self.row_position += 1;
        } else {
            // Scroll screen up by 1 row
            self.scroll_up();
        }
        self.column_position = 0;
    }

    fn scroll_up(&mut self) {
        #[cfg(not(feature = "std"))]
        {
            let buffer = unsafe { &mut *(0xb8000 as *mut Buffer) };
            for row in 1..BUFFER_HEIGHT {
                for col in 0..BUFFER_WIDTH {
                    let character = buffer.chars[row][col];
                    buffer.chars[row - 1][col] = character;
                }
            }
            self.clear_row(BUFFER_HEIGHT - 1);
        }

        #[cfg(feature = "std")]
        {
            for row in 1..BUFFER_HEIGHT {
                for col in 0..BUFFER_WIDTH {
                    self.simulated_buffer[row - 1][col] = self.simulated_buffer[row][col];
                }
            }
            self.clear_row(BUFFER_HEIGHT - 1);
        }
    }

    fn clear_row(&mut self, row: usize) {
        let blank = ScreenChar {
            ascii_character: b' ',
            color_code: self.color_code,
        };

        #[cfg(not(feature = "std"))]
        {
            let buffer = unsafe { &mut *(0xb8000 as *mut Buffer) };
            for col in 0..BUFFER_WIDTH {
                buffer.chars[row][col] = blank;
            }
        }

        #[cfg(feature = "std")]
        {
            for col in 0..BUFFER_WIDTH {
                self.simulated_buffer[row][col] = blank;
            }
        }
    }

    pub fn clear_screen(&mut self) {
        for row in 0..BUFFER_HEIGHT {
            self.clear_row(row);
        }
        self.row_position = 0;
        self.column_position = 0;
    }
}

impl fmt::Write for VgaWriter {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        self.write_string(s);
        Ok(())
    }
}

pub static mut VGA_WRITER: VgaWriter = VgaWriter::new();

pub fn vga_print(args: fmt::Arguments) {
    use core::fmt::Write;
    unsafe {
        let _ = VGA_WRITER.write_fmt(args);
    }
}
