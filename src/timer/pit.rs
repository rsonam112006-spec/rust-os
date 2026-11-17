//! 8254 Programmable Interval Timer (PIT) Driver
//!
//! Generates periodic hardware timer ticks (Channel 0, I/O Port 0x40).
//! Drives preemptive scheduling quantum expiration and monotonic time tracking.

use core::sync::atomic::{AtomicU64, Ordering};

const PIT_CHANNEL_0_DATA: u16 = 0x40;
const PIT_COMMAND_REG: u16 = 0x43;
const PIT_BASE_FREQUENCY: u32 = 1193182; // 1.193182 MHz

pub static KERNEL_TICKS: AtomicU64 = AtomicU64::new(0);

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

/// Initializes the 8254 PIT chip to fire IRQ0 at `target_hz` frequency.
///
/// # Safety
/// Directly accesses legacy x86 hardware I/O ports.
pub unsafe fn init_pit(target_hz: u32) {
    let divisor = (PIT_BASE_FREQUENCY / target_hz.max(18)) as u16;

    // Command byte: Channel 0, Access mode lobyte/hibyte, Mode 3 (Square wave generator)
    outb(PIT_COMMAND_REG, 0x36);
    outb(PIT_CHANNEL_0_DATA, (divisor & 0xFF) as u8);
    outb(PIT_CHANNEL_0_DATA, ((divisor >> 8) & 0xFF) as u8);
}

/// Called on every timer tick (from IRQ0 ISR or simulated clock)
pub fn on_timer_tick() -> u64 {
    KERNEL_TICKS.fetch_add(1, Ordering::SeqCst) + 1
}

pub fn get_ticks() -> u64 {
    KERNEL_TICKS.load(Ordering::SeqCst)
}

pub fn reset_ticks() {
    KERNEL_TICKS.store(0, Ordering::SeqCst);
}
