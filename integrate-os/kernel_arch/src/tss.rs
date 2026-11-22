//! Task State Segment (TSS) and Interrupt Stack Table (IST)
//!
//! In x86_64 Long Mode, the TSS provides:
//! 1. Privilege Stack Tables (RSP0, RSP1, RSP2) for privilege level transitions (e.g. Ring 3 -> Ring 0).
//! 2. Interrupt Stack Table (IST): 7 stack pointers for critical exceptions (Double Fault, Page Fault).

use core::cell::UnsafeCell;

/// Dedicated stack size for critical exception handling (16 KiB = 4 pages).
pub const EXCEPTION_STACK_SIZE: usize = 16 * 1024;

/// Interrupt Stack Table (IST) index for Double Fault exceptions.
pub const DOUBLE_FAULT_IST_INDEX: u16 = 0;

/// Interrupt Stack Table (IST) index for Page Fault exceptions.
pub const PAGE_FAULT_IST_INDEX: u16 = 1;

/// Raw 64-bit Task State Segment structure matching x86_64 hardware specifications.
#[derive(Debug, Clone, Copy)]
#[repr(C, packed)]
pub struct TaskStateSegment {
    reserved_1: u32,
    /// Privilege Stack Pointers (RSP0 = Ring 0 stack pointer)
    pub rsp: [u64; 3],
    reserved_2: u64,
    /// Interrupt Stack Table pointers (IST1 to IST7)
    pub ist: [u64; 7],
    reserved_3: u64,
    reserved_4: u16,
    /// I/O Map Base Address offset
    pub iomap_base: u16,
}

impl TaskStateSegment {
    /// Create a zero-initialized TSS with I/O map disabled.
    pub const fn new() -> Self {
        TaskStateSegment {
            reserved_1: 0,
            rsp: [0; 3],
            reserved_2: 0,
            ist: [0; 7],
            reserved_3: 0,
            reserved_4: 0,
            iomap_base: core::mem::size_of::<TaskStateSegment>() as u16,
        }
    }

    /// Set an IST entry stack pointer (0-indexed in array, maps to IST1-7 in hardware).
    pub fn set_ist(&mut self, index: usize, stack_top: u64) {
        if index < 7 {
            self.ist[index] = stack_top;
        }
    }

    /// Get an IST entry by value (avoids unaligned references to packed struct fields).
    pub fn get_ist(&self, index: usize) -> u64 {
        if index < 7 {
            self.ist[index]
        } else {
            0
        }
    }
}

/// Static dedicated stacks for Double Fault and Page Fault exception handling.
#[repr(align(16))]
pub struct ExceptionStack([u8; EXCEPTION_STACK_SIZE]);

impl ExceptionStack {
    pub const fn new() -> Self {
        ExceptionStack([0; EXCEPTION_STACK_SIZE])
    }

    /// Compute the top of the stack (stacks grow downwards in x86_64).
    pub fn top(&self) -> u64 {
        let bottom = self.0.as_ptr() as u64;
        bottom + EXCEPTION_STACK_SIZE as u64
    }
}

struct TSSWrapper(UnsafeCell<TaskStateSegment>);
unsafe impl Sync for TSSWrapper {}

static SYSTEM_TSS: TSSWrapper = TSSWrapper(UnsafeCell::new(TaskStateSegment::new()));
static DOUBLE_FAULT_STACK: ExceptionStack = ExceptionStack::new();
static PAGE_FAULT_STACK: ExceptionStack = ExceptionStack::new();

/// Initialize and return a static reference to the configured Task State Segment.
pub fn init_tss() -> &'static TaskStateSegment {
    unsafe {
        let tss = &mut *SYSTEM_TSS.0.get();
        tss.set_ist(DOUBLE_FAULT_IST_INDEX as usize, DOUBLE_FAULT_STACK.top());
        tss.set_ist(PAGE_FAULT_IST_INDEX as usize, PAGE_FAULT_STACK.top());
        &*SYSTEM_TSS.0.get()
    }
}
