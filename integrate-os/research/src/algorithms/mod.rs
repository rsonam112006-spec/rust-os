pub mod clock;
pub mod fifo;
pub mod lru;
pub mod optimal;
pub mod second_chance;

pub use clock::run_clock;
pub use fifo::run_fifo;
pub use lru::run_lru;
pub use optimal::run_optimal;
pub use second_chance::run_second_chance;
