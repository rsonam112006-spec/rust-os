//! Timer Subsystem (PIT and Monotonic Tick Counter)

pub mod pit;

pub use pit::{init_pit, on_timer_tick, get_ticks, reset_ticks, KERNEL_TICKS};
