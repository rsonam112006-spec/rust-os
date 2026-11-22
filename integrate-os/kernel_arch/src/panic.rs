//! Kernel Panic Handler

use core::panic::PanicInfo;
use crate::vga::{Writer, Color};
use crate::serial::SerialPort;

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    let serial = SerialPort::new();
    serial.write_string("\n\n[!!!] KERNEL PANIC OCCURRED [!!!]\n");
    if let Some(location) = info.location() {
        serial.write_string("Location: ");
        serial.write_string(location.file());
        serial.write_string("\n");
    }

    let mut vga = Writer::new();
    vga.set_color(Color::LightRed, Color::Black);
    vga.write_string("\n\n[KERNEL PANIC]\n");
    if let Some(location) = info.location() {
        vga.write_string("At: ");
        vga.write_string(location.file());
        vga.write_string("\n");
    }

    unsafe {
        loop {
            core::arch::asm!("hlt");
        }
    }
}
