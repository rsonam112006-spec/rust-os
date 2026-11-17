//! Kernel Lifecycle, Subsystem Initialization, and Halt Abstraction

use crate::kprintln;
use crate::drivers::vga::{Color, VGA_WRITER};

pub const KERNEL_NAME: &str = "Rust-MicroOS";
pub const KERNEL_VERSION: &str = "0.1.0-ca6";
pub const TARGET_PLATFORM: &str = "VirtualBox x86_64";

/// Prints the startup banner to VGA display and serial console
pub fn print_banner() {
    unsafe {
        VGA_WRITER.set_color(Color::LightCyan, Color::Black);
    }
    kprintln!("============================================================");
    kprintln!("  {} v{} ({})", KERNEL_NAME, KERNEL_VERSION, TARGET_PLATFORM);
    kprintln!("  Operating Systems Engineering -- CA-6 Educational Micro-OS  ");
    kprintln!("============================================================");
    unsafe {
        VGA_WRITER.set_color(Color::White, Color::Black);
    }
}

/// Halts the CPU safely.
/// In bare-metal x86_64, executes the `hlt` instruction in a loop.
pub fn halt_cpu() -> ! {
    loop {
        #[cfg(all(target_arch = "x86_64", not(feature = "std")))]
        unsafe {
            core::arch::asm!("hlt", options(nomem, nostack, preserves_flags));
        }
        #[cfg(any(not(target_arch = "x86_64"), feature = "std"))]
        {
            #[cfg(feature = "std")]
            std::thread::sleep(std::time::Duration::from_millis(100));
        }
    }
}
