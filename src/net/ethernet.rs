//! IEEE 802.3 Ethernet II Frame Abstraction
//!
//! Handles encapsulation, decapsulation, and validation of Ethernet II frames.

use super::types::{EtherType, MacAddr};

pub const ETHERNET_HEADER_LEN: usize = 14;
pub const MIN_FRAME_LEN: usize = 60;
pub const MAX_PAYLOAD_LEN: usize = 1500;
pub const MAX_FRAME_LEN: usize = ETHERNET_HEADER_LEN + MAX_PAYLOAD_LEN; // 1514

#[derive(Debug, Clone)]
pub struct EthernetFrame<'a> {
    pub dst_mac: MacAddr,
    pub src_mac: MacAddr,
    pub ether_type: EtherType,
    pub payload: &'a [u8],
}

impl<'a> EthernetFrame<'a> {
    pub fn parse(buffer: &'a [u8]) -> Result<Self, &'static str> {
        if buffer.len() < ETHERNET_HEADER_LEN {
            return Err("Frame too short for Ethernet header");
        }

        let dst_mac = MacAddr::new(
            buffer[0], buffer[1], buffer[2], buffer[3], buffer[4], buffer[5],
        );
        let src_mac = MacAddr::new(
            buffer[6], buffer[7], buffer[8], buffer[9], buffer[10], buffer[11],
        );
        let ether_val = ((buffer[12] as u16) << 8) | (buffer[13] as u16);
        let ether_type = EtherType::from(ether_val);

        let payload = &buffer[ETHERNET_HEADER_LEN..];

        Ok(Self {
            dst_mac,
            src_mac,
            ether_type,
            payload,
        })
    }

    pub fn serialize(&self, out: &mut [u8]) -> Result<usize, &'static str> {
        let total_len = ETHERNET_HEADER_LEN + self.payload.len();
        if out.len() < total_len {
            return Err("Output buffer too small for Ethernet frame");
        }

        out[0..6].copy_from_slice(&self.dst_mac.0);
        out[6..12].copy_from_slice(&self.src_mac.0);
        let ether_val: u16 = self.ether_type.into();
        out[12] = (ether_val >> 8) as u8;
        out[13] = (ether_val & 0xFF) as u8;
        out[14..total_len].copy_from_slice(self.payload);

        Ok(total_len)
    }
}
