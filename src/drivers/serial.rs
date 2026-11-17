//! 16550 UART Serial Driver for COM1 (I/O Port 0x3F8)
//!
//! Provides the primary serial logging transport for the Micro-OS.
//! In Oracle VirtualBox, COM1 is configured to pipe output directly to a host file
//! (e.g., `traces/virtualbox_serial.log`), enabling external Python log parsers to analyze traces.

use core::fmt;
use core::sync::atomic::{AtomicBool, Ordering};

const COM1_PORT: u16 = 0x3F8;

static SERIAL_INITIALIZED: AtomicBool = AtomicBool::new(false);

/// Minimal wrapper for x86 I/O port output
#[inline]
unsafe fn outb(port: u16, val: u8) {
    #[cfg(all(target_arch = "x86_64", not(feature = "std")))]
    {
        core::arch::asm!(
            "out dx, al",
            in("dx") port,
            in("al") val,
            options(nomem, nostack, preserves_flags)
        );
    }
    #[cfg(any(not(target_arch = "x86_64"), feature = "std"))]
    {
        let _ = (port, val);
    }
}

/// Minimal wrapper for x86 I/O port input
#[inline]
unsafe fn inb(port: u16) -> u8 {
    #[cfg(all(target_arch = "x86_64", not(feature = "std")))]
    {
        let val: u8;
        core::arch::asm!(
            "in al, dx",
            out("al") val,
            in("dx") port,
            options(nomem, nostack, preserves_flags)
        );
        val
    }
    #[cfg(any(not(target_arch = "x86_64"), feature = "std"))]
    {
        let _ = port;
        0
    }
}

pub struct SerialPort {
    port: u16,
}

impl SerialPort {
    pub const fn new(port: u16) -> Self {
        Self { port }
    }

    /// Initializes the 16550 UART device at the given I/O port.
    ///
    /// # Safety
    /// Modifies hardware I/O ports. Must only be executed during kernel hardware initialization.
    pub unsafe fn init(&mut self) {
        // Disable all interrupts
        outb(self.port + 1, 0x00);
        // Enable DLAB (set baud rate divisor)
        outb(self.port + 3, 0x80);
        // Set divisor to 3 (38400 baud) or 1 (115200 baud) - low byte
        outb(self.port + 0, 0x01);
        // High byte
        outb(self.port + 1, 0x00);
        // 8 bits, no parity, one stop bit
        outb(self.port + 3, 0x03);
        // Enable FIFO, clear them, with 14-byte threshold
        outb(self.port + 2, 0xC7);
        // IRQs enabled, RTS/DSR set
        outb(self.port + 4, 0x0B);

        SERIAL_INITIALIZED.store(true, Ordering::SeqCst);
    }

    /// Writes a single byte to the UART transmitter buffer
    pub fn write_byte(&mut self, byte: u8) {
        #[cfg(feature = "std")]
        {
            use std::io::Write;
            let _ = std::io::stdout().write_all(&[byte]);
        }

        #[cfg(not(feature = "std"))]
        {
            unsafe {
                // Wait for the transmit FIFO buffer to be empty (Line Status Register bit 5)
                while (inb(self.port + 5) & 0x20) == 0 {}
                outb(self.port, byte);
            }
        }
    }

    /// Writes an entire string slice to the serial port
    pub fn write_string(&mut self, s: &str) {
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

pub static mut COM1: SerialPort = SerialPort::new(COM1_PORT);

/// Thread-safe public helper to write to COM1
pub fn serial_print(args: fmt::Arguments) {
    use core::fmt::Write;
    unsafe {
        let _ = COM1.write_fmt(args);
    }
}
