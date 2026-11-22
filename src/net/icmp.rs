//! Internet Control Message Protocol (ICMP - RFC 792)
//!
//! Provides ICMP Echo Request and Echo Reply mechanisms for the OS `ping` command.

use super::ipv4::calculate_checksum;

pub const ICMP_HEADER_LEN: usize = 8;

pub const ICMP_TYPE_ECHO_REPLY: u8 = 0;
pub const ICMP_TYPE_DEST_UNREACHABLE: u8 = 3;
pub const ICMP_TYPE_ECHO_REQUEST: u8 = 8;

#[derive(Debug, Clone)]
pub struct IcmpPacket<'a> {
    pub icmp_type: u8,
    pub code: u8,
    pub checksum: u16,
    pub identifier: u16,
    pub sequence_number: u16,
    pub payload: &'a [u8],
}

impl<'a> IcmpPacket<'a> {
    pub fn new_echo_request(identifier: u16, sequence_number: u16, payload: &'a [u8]) -> Self {
        Self {
            icmp_type: ICMP_TYPE_ECHO_REQUEST,
            code: 0,
            checksum: 0,
            identifier,
            sequence_number,
            payload,
        }
    }

    pub fn new_echo_reply(identifier: u16, sequence_number: u16, payload: &'a [u8]) -> Self {
        Self {
            icmp_type: ICMP_TYPE_ECHO_REPLY,
            code: 0,
            checksum: 0,
            identifier,
            sequence_number,
            payload,
        }
    }

    pub fn parse(buf: &'a [u8]) -> Result<Self, &'static str> {
        if buf.len() < ICMP_HEADER_LEN {
            return Err("Buffer too short for ICMP header");
        }

        let icmp_type = buf[0];
        let code = buf[1];
        let checksum = ((buf[2] as u16) << 8) | (buf[3] as u16);
        let identifier = ((buf[4] as u16) << 8) | (buf[5] as u16);
        let sequence_number = ((buf[6] as u16) << 8) | (buf[7] as u16);
        let payload = &buf[ICMP_HEADER_LEN..];

        // Verify checksum
        if calculate_checksum(buf) != 0 {
            return Err("ICMP checksum failure");
        }

        Ok(Self {
            icmp_type,
            code,
            checksum,
            identifier,
            sequence_number,
            payload,
        })
    }

    pub fn serialize(&self, out: &mut [u8]) -> Result<usize, &'static str> {
        let total_len = ICMP_HEADER_LEN + self.payload.len();
        if out.len() < total_len {
            return Err("Buffer too small for ICMP packet");
        }

        out[0] = self.icmp_type;
        out[1] = self.code;
        out[2] = 0; // Checksum placeholder
        out[3] = 0;
        out[4] = (self.identifier >> 8) as u8;
        out[5] = (self.identifier & 0xFF) as u8;
        out[6] = (self.sequence_number >> 8) as u8;
        out[7] = (self.sequence_number & 0xFF) as u8;
        out[8..total_len].copy_from_slice(self.payload);

        // Checksum covers entire ICMP header and data
        let sum = calculate_checksum(&out[..total_len]);
        out[2] = (sum >> 8) as u8;
        out[3] = (sum & 0xFF) as u8;

        Ok(total_len)
    }
}

/// Statistics tracker for live ping execution
#[derive(Debug, Clone, Copy)]
pub struct PingStats {
    pub transmitted: u32,
    pub received: u32,
    pub min_rtt_ms: u32,
    pub max_rtt_ms: u32,
    pub sum_rtt_ms: u32,
}

impl PingStats {
    pub const fn new() -> Self {
        Self {
            transmitted: 0,
            received: 0,
            min_rtt_ms: u32::MAX,
            max_rtt_ms: 0,
            sum_rtt_ms: 0,
        }
    }

    pub fn record_reply(&mut self, rtt_ms: u32) {
        self.received += 1;
        self.sum_rtt_ms += rtt_ms;
        if rtt_ms < self.min_rtt_ms {
            self.min_rtt_ms = rtt_ms;
        }
        if rtt_ms > self.max_rtt_ms {
            self.max_rtt_ms = rtt_ms;
        }
    }

    pub fn avg_rtt_ms(&self) -> f32 {
        if self.received == 0 {
            0.0
        } else {
            self.sum_rtt_ms as f32 / self.received as f32
        }
    }

    pub fn packet_loss_pct(&self) -> f32 {
        if self.transmitted == 0 {
            0.0
        } else {
            ((self.transmitted - self.received) as f32 / self.transmitted as f32) * 100.0
        }
    }
}
