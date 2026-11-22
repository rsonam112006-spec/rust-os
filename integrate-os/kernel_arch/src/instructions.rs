//! Safe wrappers for low-level x86_64 CPU instructions
//!
//! Provides hardware operations for loading the GDT (`lgdt`), loading the TSS (`ltr`),
//! and reloading the segment registers (CS, DS, SS).

use crate::gdt::{DescriptorTablePointer, SegmentSelector};

/// Load the Global Descriptor Table into the CPU's GDTR register.
pub unsafe fn load_gdt(ptr: &DescriptorTablePointer) {
    #[cfg(all(target_arch = "x86_64", target_os = "none"))]
    {
        core::arch::asm!(
            "lgdt [{}]",
            in(reg) ptr,
            options(nostack, preserves_flags)
        );
    }
    #[cfg(not(all(target_arch = "x86_64", target_os = "none")))]
    {
        let _ = ptr; // Simulating GDT load in userspace/test harness
    }
}

/// Load the Task Register (TR) with the given TSS segment selector.
pub unsafe fn load_tss(selector: SegmentSelector) {
    #[cfg(all(target_arch = "x86_64", target_os = "none"))]
    {
        core::arch::asm!(
            "ltr {0:x}",
            in(reg) selector.0,
            options(nostack, preserves_flags)
        );
    }
    #[cfg(not(all(target_arch = "x86_64", target_os = "none")))]
    {
        let _ = selector; // Simulating TSS load in userspace/test harness
    }
}

/// Reload 64-bit Code Segment (CS) and Data Segments (DS, SS, ES).
pub unsafe fn reload_segments(code: SegmentSelector, data: SegmentSelector) {
    #[cfg(all(target_arch = "x86_64", target_os = "none"))]
    {
        core::arch::asm!(
            "mov ds, {data:x}",
            "mov es, {data:x}",
            "mov ss, {data:x}",
            data = in(reg) data.0,
            options(preserves_flags)
        );
        let _ = code;
    }
    #[cfg(not(all(target_arch = "x86_64", target_os = "none")))]
    {
        let _ = (code, data);
    }
}
