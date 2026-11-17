//! Hardware Device Drivers
//!
//! Exposes the UART serial port and VGA text console drivers.

pub mod serial;
pub mod vga;

pub use serial::{SerialPort, COM1, serial_print};
pub use vga::{Color, ColorCode, VgaWriter, VGA_WRITER, vga_print};

/// Initializes core hardware devices
pub fn init() {
    unsafe {
        COM1.init();
        VGA_WRITER.clear_screen();
    }
}
