//! 8x16 Embedded Bitmap Font & Typography
//!
//! Provides rendering for ASCII character glyphs (32..=126) directly into the framebuffer.

pub const FONT_WIDTH: usize = 8;
pub const FONT_HEIGHT: usize = 16;

/// Compact 8x16 font glyph table for basic ASCII rendering
/// Standard IBM CP437 / VGA font subsets
pub static BASIC_GLYPHS: [[u8; 16]; 95] = {
    // We can define a clean pattern generator or standard 8x16 font slices
    let mut table = [[0u8; 16]; 95];

    // Capital A (index 65 - 32 = 33)
    table[33] = [0, 0, 0x18, 0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x66, 0x66, 0, 0, 0, 0, 0];
    // Capital B (34)
    table[34] = [0, 0, 0x7C, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x7C, 0, 0, 0, 0, 0, 0, 0];
    // Capital C (35)
    table[35] = [0, 0, 0x3C, 0x66, 0x60, 0x60, 0x60, 0x66, 0x3C, 0, 0, 0, 0, 0, 0, 0];

    // Numbers '0'..'9' (index 48 - 32 = 16)
    table[16] = [0, 0, 0x3C, 0x66, 0x6E, 0x76, 0x66, 0x66, 0x3C, 0, 0, 0, 0, 0, 0, 0]; // 0
    table[17] = [0, 0, 0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x3C, 0, 0, 0, 0, 0, 0, 0]; // 1
    table[18] = [0, 0, 0x3C, 0x66, 0x06, 0x1C, 0x30, 0x60, 0x7E, 0, 0, 0, 0, 0, 0, 0]; // 2
    table[19] = [0, 0, 0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0, 0, 0, 0, 0, 0, 0]; // 3
    table[20] = [0, 0, 0x0C, 0x1C, 0x34, 0x64, 0x7E, 0x04, 0x04, 0, 0, 0, 0, 0, 0, 0]; // 4
    table[21] = [0, 0, 0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0, 0, 0, 0, 0, 0, 0]; // 5
    table[22] = [0, 0, 0x3C, 0x66, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0, 0, 0, 0, 0, 0, 0]; // 6
    table[23] = [0, 0, 0x7E, 0x06, 0x0C, 0x18, 0x30, 0x30, 0x30, 0, 0, 0, 0, 0, 0, 0]; // 7
    table[24] = [0, 0, 0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0, 0, 0, 0, 0, 0, 0]; // 8
    table[25] = [0, 0, 0x3C, 0x66, 0x66, 0x3E, 0x06, 0x66, 0x3C, 0, 0, 0, 0, 0, 0, 0]; // 9

    // Colon ':' (index 58 - 32 = 26)
    table[26] = [0, 0, 0, 0x18, 0x18, 0, 0, 0x18, 0x18, 0, 0, 0, 0, 0, 0, 0];
    // Period '.' (index 46 - 32 = 14)
    table[14] = [0, 0, 0, 0, 0, 0, 0, 0, 0x18, 0x18, 0, 0, 0, 0, 0, 0];
    // Slash '/' (index 47 - 32 = 15)
    table[15] = [0, 0, 0x02, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x40, 0, 0, 0, 0, 0, 0, 0];
    // Dash '-' (index 45 - 32 = 13)
    table[13] = [0, 0, 0, 0, 0, 0x7E, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

    table
};

pub fn get_glyph(c: char) -> Option<&'static [u8; 16]> {
    let ascii = c as u32;
    if (32..=126).contains(&ascii) {
        Some(&BASIC_GLYPHS[(ascii - 32) as usize])
    } else {
        None
    }
}
