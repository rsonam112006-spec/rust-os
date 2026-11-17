//! Structured Kernel Logger and Diagnostic Telemetry
//!
//! Provides synchronized diagnostic logging across both VGA screen and Serial COM1.
//! Formats all entries with monotonic system ticks, severity levels, and subsystem tags
//! for straightforward automated Python analysis.

use core::fmt;
use crate::drivers::{serial_print, vga_print};
use crate::timer::get_ticks;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
}

impl LogLevel {
    pub const fn as_str(&self) -> &'static str {
        match self {
            LogLevel::Trace => "TRACE",
            LogLevel::Debug => "DEBUG",
            LogLevel::Info  => "INFO ",
            LogLevel::Warn  => "WARN ",
            LogLevel::Error => "ERROR",
        }
    }
}

pub struct KernelLogger {
    min_level: LogLevel,
}

impl KernelLogger {
    pub const fn new() -> Self {
        Self {
            min_level: LogLevel::Trace,
        }
    }

    pub fn set_min_level(&mut self, level: LogLevel) {
        self.min_level = level;
    }

    pub fn log(&self, level: LogLevel, subsystem: &'static str, args: fmt::Arguments) {
        let tick = get_ticks();
        let level_str = level.as_str();

        // Standardized format: [TICK:00000] [LEVEL] [SUBSYSTEM] Message
        // Both serial output (for VirtualBox file log / Python parser) and VGA output
        serial_print(format_args!("[TICK:{:05}] [{}] [{:^10}] {}\n", tick, level_str, subsystem, args));
        vga_print(format_args!("[{:05}] [{}] [{}] {}\n", tick, level_str, subsystem, args));
    }
}

pub static LOGGER: KernelLogger = KernelLogger::new();

#[macro_export]
macro_rules! kprint {
    ($($arg:tt)*) => {
        $crate::drivers::serial_print(format_args!($($arg)*));
        $crate::drivers::vga_print(format_args!($($arg)*));
    };
}

#[macro_export]
macro_rules! kprintln {
    () => ($crate::kprint!("\n"));
    ($($arg:tt)*) => {
        $crate::kprint!("{}\n", format_args!($($arg)*));
    };
}

#[macro_export]
macro_rules! kinfo {
    ($subsystem:expr, $($arg:tt)*) => {
        $crate::kernel::logger::LOGGER.log(
            $crate::kernel::logger::LogLevel::Info,
            $subsystem,
            format_args!($($arg)*)
        );
    };
}

#[macro_export]
macro_rules! kwarn {
    ($subsystem:expr, $($arg:tt)*) => {
        $crate::kernel::logger::LOGGER.log(
            $crate::kernel::logger::LogLevel::Warn,
            $subsystem,
            format_args!($($arg)*)
        );
    };
}

#[macro_export]
macro_rules! kerror {
    ($subsystem:expr, $($arg:tt)*) => {
        $crate::kernel::logger::LOGGER.log(
            $crate::kernel::logger::LogLevel::Error,
            $subsystem,
            format_args!($($arg)*)
        );
    };
}

#[macro_export]
macro_rules! kdebug {
    ($subsystem:expr, $($arg:tt)*) => {
        $crate::kernel::logger::LOGGER.log(
            $crate::kernel::logger::LogLevel::Debug,
            $subsystem,
            format_args!($($arg)*)
        );
    };
}

#[macro_export]
macro_rules! ktrace {
    ($subsystem:expr, $($arg:tt)*) => {
        $crate::kernel::logger::LOGGER.log(
            $crate::kernel::logger::LogLevel::Trace,
            $subsystem,
            format_args!($($arg)*)
        );
    };
}
