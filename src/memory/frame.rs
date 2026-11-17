//! Physical Frame Allocator (4 KiB Page Frames)
//!
//! Tracks physical memory frames using a compact bitmask.

pub const PAGE_SIZE: usize = 4096;
pub const TOTAL_FRAMES: usize = 1024; // 4 MiB managed physical space

pub struct FrameAllocator {
    bitmap: [u64; TOTAL_FRAMES / 64],
    allocated_count: usize,
}

impl FrameAllocator {
    pub const fn new() -> Self {
        Self {
            bitmap: [0; TOTAL_FRAMES / 64],
            allocated_count: 0,
        }
    }

    /// Allocates the first available 4 KiB physical page frame
    pub fn allocate_frame(&mut self) -> Option<usize> {
        for (i, word) in self.bitmap.iter_mut().enumerate() {
            if *word != u64::MAX {
                let bit = (!*word).trailing_zeros() as usize;
                *word |= 1 << bit;
                self.allocated_count += 1;
                let frame_idx = i * 64 + bit;
                return Some(frame_idx * PAGE_SIZE);
            }
        }
        None // Out of physical frames
    }

    /// Deallocates a previously allocated page frame
    pub fn deallocate_frame(&mut self, addr: usize) -> Result<(), &'static str> {
        let frame_idx = addr / PAGE_SIZE;
        if frame_idx >= TOTAL_FRAMES {
            return Err("Frame address out of managed physical boundary");
        }
        let word_idx = frame_idx / 64;
        let bit = frame_idx % 64;
        if (self.bitmap[word_idx] & (1 << bit)) == 0 {
            return Err("Double frame deallocation detected");
        }
        self.bitmap[word_idx] &= !(1 << bit);
        self.allocated_count -= 1;
        Ok(())
    }

    pub fn stats(&self) -> (usize, usize) {
        (self.allocated_count, TOTAL_FRAMES - self.allocated_count)
    }
}
