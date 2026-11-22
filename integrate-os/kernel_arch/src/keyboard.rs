//! PS/2 Keyboard Driver (Ports 0x60, 0x64)

const DATA_PORT: u16 = 0x60;
const STATUS_PORT: u16 = 0x64;

#[inline]
unsafe fn inb(port: u16) -> u8 {
    let mut val: u8;
    core::arch::asm!(
        "in al, dx",
        out("al") val,
        in("dx") port,
        options(nomem, nostack, preserves_flags)
    );
    val
}

pub enum KeyAction {
    Char(char),
    Enter,
    Backspace,
    None,
}

pub struct Keyboard;

impl Keyboard {
    pub const fn new() -> Self {
        Keyboard
    }

    /// Non-blocking check for a pending scancode
    pub fn read_scancode(&self) -> Option<u8> {
        unsafe {
            let status = inb(STATUS_PORT);
            if (status & 0x01) != 0 {
                Some(inb(DATA_PORT))
            } else {
                None
            }
        }
    }

    /// Converts a scancode to an ASCII character or special action
    pub fn scancode_to_key(&self, scancode: u8) -> KeyAction {
        // High bit set means key release (break code)
        if (scancode & 0x80) != 0 {
            return KeyAction::None;
        }

        match scancode {
            0x1C => KeyAction::Enter,
            0x0E => KeyAction::Backspace,
            0x39 => KeyAction::Char(' '),
            0x02 => KeyAction::Char('1'),
            0x03 => KeyAction::Char('2'),
            0x04 => KeyAction::Char('3'),
            0x05 => KeyAction::Char('4'),
            0x06 => KeyAction::Char('5'),
            0x07 => KeyAction::Char('6'),
            0x08 => KeyAction::Char('7'),
            0x09 => KeyAction::Char('8'),
            0x0A => KeyAction::Char('9'),
            0x0B => KeyAction::Char('0'),
            0x0C => KeyAction::Char('-'),
            0x10 => KeyAction::Char('q'),
            0x11 => KeyAction::Char('w'),
            0x12 => KeyAction::Char('e'),
            0x13 => KeyAction::Char('r'),
            0x14 => KeyAction::Char('t'),
            0x15 => KeyAction::Char('y'),
            0x16 => KeyAction::Char('u'),
            0x17 => KeyAction::Char('i'),
            0x18 => KeyAction::Char('o'),
            0x19 => KeyAction::Char('p'),
            0x1E => KeyAction::Char('a'),
            0x1F => KeyAction::Char('s'),
            0x20 => KeyAction::Char('d'),
            0x21 => KeyAction::Char('f'),
            0x22 => KeyAction::Char('g'),
            0x23 => KeyAction::Char('h'),
            0x24 => KeyAction::Char('j'),
            0x25 => KeyAction::Char('k'),
            0x26 => KeyAction::Char('l'),
            0x2C => KeyAction::Char('z'),
            0x2D => KeyAction::Char('x'),
            0x2E => KeyAction::Char('c'),
            0x2F => KeyAction::Char('v'),
            0x30 => KeyAction::Char('b'),
            0x31 => KeyAction::Char('n'),
            0x32 => KeyAction::Char('m'),
            _ => KeyAction::None,
        }
    }
}
