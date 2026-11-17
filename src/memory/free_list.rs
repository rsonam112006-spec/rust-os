//! Free-List Memory Allocator with Block Coalescing & Fragmentation Telemetry
//!
//! Provides dynamic variable-sized allocation, block splitting, contiguous free-block
//! coalescing, and exact fragmentation ratio measurement.

use core::mem::size_of;

pub const HEAP_BUFFER_SIZE: usize = 64 * 1024; // 64 KiB kernel heap

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct BlockHeader {
    pub size: usize,        // Usable payload size (excluding header)
    pub is_free: bool,
    pub next_offset: usize, // Offset in bytes from heap start (0 indicates none)
}

pub struct FreeListAllocator {
    heap: [u8; HEAP_BUFFER_SIZE],
    initialized: bool,
    pub total_allocations: usize,
    pub total_deallocations: usize,
}

impl FreeListAllocator {
    pub const fn new() -> Self {
        Self {
            heap: [0; HEAP_BUFFER_SIZE],
            initialized: false,
            total_allocations: 0,
            total_deallocations: 0,
        }
    }

    /// Initializes the root free block spanning the entire heap
    pub fn init(&mut self) {
        let header = BlockHeader {
            size: HEAP_BUFFER_SIZE - size_of::<BlockHeader>(),
            is_free: true,
            next_offset: 0,
        };
        unsafe {
            let ptr = self.heap.as_mut_ptr() as *mut BlockHeader;
            *ptr = header;
        }
        self.initialized = true;
    }

    /// Allocates `requested_size` bytes using First-Fit strategy with block splitting
    pub fn allocate(&mut self, requested_size: usize) -> Option<*mut u8> {
        if !self.initialized {
            self.init();
        }

        // Align requested size to 8 bytes
        let aligned_size = (requested_size + 7) & !7;
        let header_size = size_of::<BlockHeader>();
        let mut current_offset = 0usize;

        while current_offset < HEAP_BUFFER_SIZE {
            let header_ptr = unsafe {
                (self.heap.as_mut_ptr().add(current_offset)) as *mut BlockHeader
            };
            let header = unsafe { &mut *header_ptr };

            if header.is_free && header.size >= aligned_size {
                // Determine if the block can be split
                let excess = header.size.saturating_sub(aligned_size);
                if excess >= header_size + 16 {
                    // Split the block
                    let new_block_offset = current_offset + header_size + aligned_size;
                    let new_header_ptr = unsafe {
                        (self.heap.as_mut_ptr().add(new_block_offset)) as *mut BlockHeader
                    };
                    unsafe {
                        *new_header_ptr = BlockHeader {
                            size: excess - header_size,
                            is_free: true,
                            next_offset: header.next_offset,
                        };
                    }
                    header.size = aligned_size;
                    header.next_offset = new_block_offset;
                }

                header.is_free = false;
                self.total_allocations += 1;

                let payload_ptr = unsafe { (header_ptr as *mut u8).add(header_size) };
                return Some(payload_ptr);
            }

            if header.next_offset == 0 || header.next_offset <= current_offset {
                break;
            }
            current_offset = header.next_offset;
        }

        None // Out of memory / no suitable free block found
    }

    /// Deallocates a memory payload and immediately coalesces adjacent free blocks
    pub fn deallocate(&mut self, ptr: *mut u8) -> Result<(), &'static str> {
        let heap_start = self.heap.as_ptr() as usize;
        let ptr_val = ptr as usize;
        let header_size = size_of::<BlockHeader>();

        if ptr_val < heap_start + header_size || ptr_val >= heap_start + HEAP_BUFFER_SIZE {
            return Err("Invalid pointer: Address outside heap boundaries");
        }

        let header_ptr = (ptr_val - header_size) as *mut BlockHeader;
        let header = unsafe { &mut *header_ptr };

        if header.is_free {
            return Err("Double free detected: Memory block was already free");
        }

        header.is_free = true;
        self.total_deallocations += 1;

        // Perform contiguous coalescing to eliminate external fragmentation
        self.coalesce();

        Ok(())
    }

    /// Merges adjacent free blocks in the free-list
    pub fn coalesce(&mut self) {
        let mut current_offset = 0usize;
        let header_size = size_of::<BlockHeader>();

        while current_offset < HEAP_BUFFER_SIZE {
            let current_ptr = unsafe {
                (self.heap.as_mut_ptr().add(current_offset)) as *mut BlockHeader
            };
            let current = unsafe { &mut *current_ptr };

            if current.next_offset == 0 {
                break;
            }

            let next_offset = current.next_offset;
            let next_ptr = unsafe {
                (self.heap.as_mut_ptr().add(next_offset)) as *mut BlockHeader
            };
            let next = unsafe { &mut *next_ptr };

            // If both current and next blocks are free and adjacent, coalesce them
            if current.is_free && next.is_free && (current_offset + header_size + current.size == next_offset) {
                current.size += header_size + next.size;
                current.next_offset = next.next_offset;
                // Retry same block to check if subsequent block is also free
                continue;
            }

            current_offset = current.next_offset;
        }
    }

    /// Calculates memory metrics: (allocated_bytes, total_free_bytes, largest_free_block)
    pub fn memory_stats(&self) -> (usize, usize, usize) {
        if !self.initialized {
            return (0, HEAP_BUFFER_SIZE, HEAP_BUFFER_SIZE);
        }

        let mut allocated = 0usize;
        let mut total_free = 0usize;
        let mut largest_free = 0usize;
        let mut current_offset = 0usize;

        while current_offset < HEAP_BUFFER_SIZE {
            let header_ptr = unsafe {
                (self.heap.as_ptr().add(current_offset)) as *const BlockHeader
            };
            let header = unsafe { &*header_ptr };

            if header.is_free {
                total_free += header.size;
                if header.size > largest_free {
                    largest_free = header.size;
                }
            } else {
                allocated += header.size;
            }

            if header.next_offset == 0 || header.next_offset <= current_offset {
                break;
            }
            current_offset = header.next_offset;
        }

        (allocated, total_free, largest_free)
    }

    /// Calculates external fragmentation ratio:
    /// Fragmentation = 1.0 - (largest_free_block / total_free_bytes)
    /// Returns 0.0 if all free memory is perfectly consolidated.
    pub fn fragmentation_ratio(&self) -> f64 {
        let (_, total_free, largest_free) = self.memory_stats();
        if total_free == 0 {
            0.0
        } else {
            1.0 - (largest_free as f64 / total_free as f64)
        }
    }
}
