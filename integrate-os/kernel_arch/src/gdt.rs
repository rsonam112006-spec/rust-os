//! Global Descriptor Table (GDT) for x86_64 Long Mode
//!
//! In 64-bit mode, segmentation is largely inactive, but the GDT remains mandatory for:
//! 1. Defining 64-bit Kernel Code and Data Segment Selectors (CS, DS, SS).
//! 2. Defining User-Mode segments for Ring 3 transitions.
//! 3. Registering the 16-byte Task State Segment (TSS) descriptor for IST stack switches.

use core::cell::UnsafeCell;
use crate::tss::TaskStateSegment;

/// Segment Selector representing an index into the GDT and privilege level.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SegmentSelector(pub u16);

impl SegmentSelector {
    pub const fn new(index: u16, rpl: u8) -> Self {
        SegmentSelector((index << 3) | ((rpl as u16) & 0b11))
    }

    pub const fn index(self) -> u16 {
        self.0 >> 3
    }

    pub const fn rpl(self) -> u8 {
        (self.0 & 0b11) as u8
    }
}

/// Segment Descriptor in 64-bit x86_64 architecture.
#[derive(Debug, Clone, Copy)]
pub enum Descriptor {
    /// Standard 8-byte code/data descriptor
    UserSegment(u64),
    /// 16-byte system segment descriptor (used by TSS in 64-bit mode)
    SystemSegment(u64, u64),
}

impl Descriptor {
    /// 64-bit Ring 0 Kernel Code Segment Descriptor:
    /// Present=1, Ring=0, Type=Executable/Readable, LongMode=1, DefaultSize=0
    pub const fn kernel_code_segment() -> Self {
        let flags: u64 = (1 << 47) | (1 << 44) | (1 << 43) | (1 << 41) | (1 << 53);
        Descriptor::UserSegment(flags)
    }

    /// 64-bit Ring 0 Kernel Data Segment Descriptor:
    /// Present=1, Ring=0, Type=Writable/Accessed
    pub const fn kernel_data_segment() -> Self {
        let flags: u64 = (1 << 47) | (1 << 44) | (1 << 41) | (1 << 40);
        Descriptor::UserSegment(flags)
    }

    /// 64-bit Ring 3 User Data Segment Descriptor
    pub const fn user_data_segment() -> Self {
        let flags: u64 = (1 << 47) | (3 << 45) | (1 << 44) | (1 << 41) | (1 << 40);
        Descriptor::UserSegment(flags)
    }

    /// 64-bit Ring 3 User Code Segment Descriptor
    pub const fn user_code_segment() -> Self {
        let flags: u64 = (1 << 47) | (3 << 45) | (1 << 44) | (1 << 43) | (1 << 41) | (1 << 53);
        Descriptor::UserSegment(flags)
    }

    /// 16-byte TSS System Segment Descriptor for 64-bit mode:
    /// Encodes base address (64-bit) and limit (16-bit) of the TSS.
    pub fn tss_segment(tss: &'static TaskStateSegment) -> Self {
        let ptr = tss as *const _ as u64;
        let limit = (core::mem::size_of::<TaskStateSegment>() - 1) as u64;

        // Low 8 bytes
        let mut low: u64 = limit & 0xFFFF;
        low |= (ptr & 0x00FF_FFFF) << 16;
        // Type: 0x9 (Available 64-bit TSS), S=0 (System), DPL=0, Present=1
        low |= 0x89u64 << 40;
        low |= ((limit >> 16) & 0x0F) << 48;
        low |= ((ptr >> 24) & 0xFF) << 56;

        // High 8 bytes: upper 32 bits of base address
        let high: u64 = (ptr >> 32) & 0xFFFF_FFFF;

        Descriptor::SystemSegment(low, high)
    }
}

/// Structure representing a pointer to the GDT for the `lgdt` instruction.
#[derive(Debug, Clone, Copy)]
#[repr(C, packed)]
pub struct DescriptorTablePointer {
    pub limit: u16,
    pub base: u64,
}

impl DescriptorTablePointer {
    pub fn get_limit(&self) -> u16 {
        self.limit
    }

    pub fn get_base(&self) -> u64 {
        self.base
    }
}

/// Global Descriptor Table holding segments and TSS descriptors.
pub struct GlobalDescriptorTable {
    table: [u64; 8],
    len: usize,
}

impl GlobalDescriptorTable {
    pub const fn new() -> Self {
        GlobalDescriptorTable {
            table: [0; 8],
            len: 1, // Entry 0 is always null descriptor
        }
    }

    /// Add a descriptor to the GDT and return its SegmentSelector.
    pub fn add_descriptor(&mut self, desc: Descriptor) -> SegmentSelector {
        let index = self.len;
        match desc {
            Descriptor::UserSegment(entry) => {
                assert!(index < self.table.len(), "GDT table overflow");
                self.table[index] = entry;
                self.len += 1;
                SegmentSelector::new(index as u16, 0)
            }
            Descriptor::SystemSegment(low, high) => {
                assert!(index + 1 < self.table.len(), "GDT table overflow for 16-byte TSS descriptor");
                self.table[index] = low;
                self.table[index + 1] = high;
                self.len += 2;
                SegmentSelector::new(index as u16, 0)
            }
        }
    }

    /// Generate the DescriptorTablePointer required for `lgdt`.
    pub fn pointer(&self) -> DescriptorTablePointer {
        DescriptorTablePointer {
            limit: (core::mem::size_of::<u64>() * self.len - 1) as u16,
            base: self.table.as_ptr() as u64,
        }
    }

    /// Return raw table slice
    pub fn raw_entries(&self) -> &[u64] {
        &self.table[..self.len]
    }
}

/// Selectors resulting from GDT initialization.
#[derive(Debug, Clone, Copy)]
pub struct Selectors {
    pub code_selector: SegmentSelector,
    pub data_selector: SegmentSelector,
    pub tss_selector: SegmentSelector,
}

struct GdtWrapper(UnsafeCell<GlobalDescriptorTable>);
unsafe impl Sync for GdtWrapper {}

static GDT: GdtWrapper = GdtWrapper(UnsafeCell::new(GlobalDescriptorTable::new()));

/// Construct and return the static system GDT.
pub fn init_gdt(tss: &'static TaskStateSegment) -> (&'static GlobalDescriptorTable, Selectors) {
    unsafe {
        let gdt = &mut *GDT.0.get();
        let mut new_gdt = GlobalDescriptorTable::new();
        let code = new_gdt.add_descriptor(Descriptor::kernel_code_segment());
        let data = new_gdt.add_descriptor(Descriptor::kernel_data_segment());
        let tss_sel = new_gdt.add_descriptor(Descriptor::tss_segment(tss));

        *gdt = new_gdt;
        let selectors = Selectors {
            code_selector: code,
            data_selector: data,
            tss_selector: tss_sel,
        };

        (&*GDT.0.get(), selectors)
    }
}
