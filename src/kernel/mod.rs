//! Kernel Core Modules and Subsystem Orchestration

pub mod core;
pub mod logger;

pub use self::core::{print_banner, halt_cpu, KERNEL_NAME, KERNEL_VERSION, TARGET_PLATFORM};
pub use self::logger::{KernelLogger, LogLevel, LOGGER};
