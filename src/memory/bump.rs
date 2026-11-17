//! Bump Allocator (Linear High-Speed Memory Allocator)
//!
//! Provides ultra-low latency linear allocation during early boot phases.
//! Allocates contiguously by incrementing a pointer; does not support individual deallocations.

pub struct BumpAllocator {
    heap_start: usize,
    heap_end: usize,
    next: usize,
    allocations: usize,
}

impl BumpAllocator {
    pub const fn new() -> Self {
        Self {
            heap_start: 0,
            heap_end: 0,
            next: 0,
            allocations: 0,
        }
    }

    /// Initializes the bump allocator with a dedicated memory region
    ///
    /// # Safety
    /// Caller must ensure the range [heap_start, heap_start + size) is valid unused memory.
    pub unsafe fn init(&mut self, heap_start: usize, size: usize) {
        self.heap_start = heap_start;
        self.heap_end = heap_start + size;
        self.next = heap_start;
        self.allocations = 0;
    }

    /// Allocates `size` bytes aligned to `align`
    pub fn allocate(&mut self, size: usize, align: usize) -> Option<*mut u8> {
        let current = self.next;
        // Align pointer up
        let aligned = (current + align - 1) & !(align - 1);
        let end = aligned.checked_add(size)?;

        if end <= self.heap_end {
            self.next = end;
            self.allocations += 1;
            Some(aligned as *mut u8)
        } else {
            None // Out of bump memory
        }
    }

    pub fn reset(&mut self) {
        self.next = self.heap_start;
        self.allocations = 0;
    }

    pub fn used_bytes(&self) -> usize {
        self.next.saturating_sub(self.heap_start)
    }

    pub fn total_bytes(&self) -> usize {
        self.heap_end.saturating_sub(self.heap_start)
    }
}
