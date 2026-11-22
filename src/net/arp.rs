//! Address Resolution Protocol (ARP - RFC 826)
//!
//! Resolves IPv4 addresses to 48-bit MAC addresses and maintains an in-memory
//! ARP cache table.

use super::types::{Ipv4Addr, MacAddr};

pub const ARP_HEADER_LEN: usize = 28;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u16)]
pub enum ArpOpcode {
    Request = 1,
    Reply = 2,
    Unknown(u16),
}

impl From<u16> for ArpOpcode {
    fn from(val: u16) -> Self {
        match val {
            1 => ArpOpcode::Request,
            2 => ArpOpcode::Reply,
            other => ArpOpcode::Unknown(other),
        }
    }
}

#[derive(Debug, Clone)]
pub struct ArpPacket {
    pub htype: u16, // Hardware type (Ethernet = 1)
    pub ptype: u16, // Protocol type (IPv4 = 0x0800)
    pub hlen: u8,   // Hardware address length (6 for MAC)
    pub plen: u8,   // Protocol address length (4 for IPv4)
    pub opcode: ArpOpcode,
    pub sender_mac: MacAddr,
    pub sender_ip: Ipv4Addr,
    pub target_mac: MacAddr,
    pub target_ip: Ipv4Addr,
}

impl ArpPacket {
    pub fn new_request(sender_mac: MacAddr, sender_ip: Ipv4Addr, target_ip: Ipv4Addr) -> Self {
        Self {
            htype: 1,
            ptype: 0x0800,
            hlen: 6,
            plen: 4,
            opcode: ArpOpcode::Request,
            sender_mac,
            sender_ip,
            target_mac: MacAddr::ZERO,
            target_ip,
        }
    }

    pub fn new_reply(
        sender_mac: MacAddr,
        sender_ip: Ipv4Addr,
        target_mac: MacAddr,
        target_ip: Ipv4Addr,
    ) -> Self {
        Self {
            htype: 1,
            ptype: 0x0800,
            hlen: 6,
            plen: 4,
            opcode: ArpOpcode::Reply,
            sender_mac,
            sender_ip,
            target_mac,
            target_ip,
        }
    }

    pub fn parse(buf: &[u8]) -> Result<Self, &'static str> {
        if buf.len() < ARP_HEADER_LEN {
            return Err("Buffer too short for ARP packet");
        }

        let htype = ((buf[0] as u16) << 8) | (buf[1] as u16);
        let ptype = ((buf[2] as u16) << 8) | (buf[3] as u16);
        let hlen = buf[4];
        let plen = buf[5];
        let opcode_val = ((buf[6] as u16) << 8) | (buf[7] as u16);
        let opcode = ArpOpcode::from(opcode_val);

        let sender_mac = MacAddr::new(buf[8], buf[9], buf[10], buf[11], buf[12], buf[13]);
        let sender_ip = Ipv4Addr::new(buf[14], buf[15], buf[16], buf[17]);
        let target_mac = MacAddr::new(buf[18], buf[19], buf[20], buf[21], buf[22], buf[23]);
        let target_ip = Ipv4Addr::new(buf[24], buf[25], buf[26], buf[27]);

        Ok(Self {
            htype,
            ptype,
            hlen,
            plen,
            opcode,
            sender_mac,
            sender_ip,
            target_mac,
            target_ip,
        })
    }

    pub fn serialize(&self, out: &mut [u8]) -> Result<usize, &'static str> {
        if out.len() < ARP_HEADER_LEN {
            return Err("Buffer too small to serialize ARP packet");
        }

        out[0] = (self.htype >> 8) as u8;
        out[1] = (self.htype & 0xFF) as u8;
        out[2] = (self.ptype >> 8) as u8;
        out[3] = (self.ptype & 0xFF) as u8;
        out[4] = self.hlen;
        out[5] = self.plen;

        let op_val = match self.opcode {
            ArpOpcode::Request => 1u16,
            ArpOpcode::Reply => 2u16,
            ArpOpcode::Unknown(v) => v,
        };
        out[6] = (op_val >> 8) as u8;
        out[7] = (op_val & 0xFF) as u8;

        out[8..14].copy_from_slice(&self.sender_mac.0);
        out[14..18].copy_from_slice(&self.sender_ip.0);
        out[18..24].copy_from_slice(&self.target_mac.0);
        out[24..28].copy_from_slice(&self.target_ip.0);

        Ok(ARP_HEADER_LEN)
    }
}

pub const ARP_CACHE_CAPACITY: usize = 16;

#[derive(Debug, Clone, Copy)]
pub struct ArpEntry {
    pub ip: Ipv4Addr,
    pub mac: MacAddr,
    pub valid: bool,
    pub timestamp: u64,
}

pub struct ArpCache {
    entries: [ArpEntry; ARP_CACHE_CAPACITY],
}

impl ArpCache {
    pub const fn new() -> Self {
        Self {
            entries: [ArpEntry {
                ip: Ipv4Addr::UNSPECIFIED,
                mac: MacAddr::ZERO,
                valid: false,
                timestamp: 0,
            }; ARP_CACHE_CAPACITY],
        }
    }

    pub fn insert(&mut self, ip: Ipv4Addr, mac: MacAddr, tick: u64) {
        // Update existing entry if present
        for entry in self.entries.iter_mut() {
            if entry.valid && entry.ip == ip {
                entry.mac = mac;
                entry.timestamp = tick;
                return;
            }
        }

        // Otherwise insert in first free slot
        for entry in self.entries.iter_mut() {
            if !entry.valid {
                entry.ip = ip;
                entry.mac = mac;
                entry.valid = true;
                entry.timestamp = tick;
                return;
            }
        }

        // If table full, replace the oldest slot (slot 0 for simplicity)
        self.entries[0] = ArpEntry {
            ip,
            mac,
            valid: true,
            timestamp: tick,
        };
    }

    pub fn lookup(&self, ip: Ipv4Addr) -> Option<MacAddr> {
        for entry in self.entries.iter() {
            if entry.valid && entry.ip == ip {
                return Some(entry.mac);
            }
        }
        None
    }
}
