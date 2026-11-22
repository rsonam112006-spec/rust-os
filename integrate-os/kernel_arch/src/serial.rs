//! COM1 Serial Port Driver (0x3F8) for VirtualBox Serial Debugging

use core::fmt;

const COM1_DATA: u16 = 0x3F8;
const COM1_LINE_STATUS: u16 = 0x3FD;

pub struct SerialPort;

impl SerialPort {
    pub const fn new() -> Self {
        SerialPort
    }

    pub fn init(&self) {
        unsafe {
            outb(COM1_DATA + 1, 0x00); // Disable interrupts
            outb(COM1_DATA + 3, 0x80); // Enable DLAB (set baud rate divisor)
            outb(COM1_DATA + 0, 0x01); // Set divisor to 1 (115200 baud)
            outb(COM1_DATA + 1, 0x00);
            outb(COM1_DATA + 3, 0x03); // 8 bits, no parity, one stop bit
            outb(COM1_DATA + 2, 0xC7); // Enable FIFO, clear them, 14-byte threshold
            outb(COM1_DATA + 4, 0x0B); // IRQs enabled, RTS/DSR set
        }
    }

    pub fn write_byte(&self, byte: u8) {
        unsafe {
            while (inb(COM1_LINE_STATUS) & 0x20) == 0 {}
            outb(COM1_DATA, byte);
        }
    }

    pub fn write_string(&self, s: &str) {
        for byte in s.bytes() {
            if byte == b'\n' {
                self.write_byte(b'\r');
            }
            self.write_byte(byte);
        }
    }
}

impl fmt::Write for SerialPort {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        self.write_string(s);
        Ok(())
    }
}

#[inline]
unsafe fn outb(port: u16, val: u8) {
    core::arch::asm!(
        "out dx, al",
        in("dx") port,
        in("al") val,
        options(nomem, nostack, preserves_flags)
    );
}

#[inline]
unsafe fn inb(port: u16) -> u8 {
    let mut val: u8;
    core::arch::asm!(
        "in al, dx",
        out("al") val,
        in("dx") port,
        options(nomem, nostack, preserves_flags)
    );
    val
}
