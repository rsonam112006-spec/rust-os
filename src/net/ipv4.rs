//! IPv4 Packet Protocol (RFC 791)
//!
//! Provides IPv4 packet construction, serialization, RFC 1071 header checksum
//! computation, and packet validation.

use super::types::{IpProtocol, Ipv4Addr};

pub const IPV4_MIN_HEADER_LEN: usize = 20;
pub const DEFAULT_TTL: u8 = 64;

#[derive(Debug, Clone)]
pub struct Ipv4Header {
    pub version: u8,
    pub ihl: u8,
    pub tos: u8,
    pub total_length: u16,
    pub identification: u16,
    pub flags_fragment: u16,
    pub ttl: u8,
    pub protocol: IpProtocol,
    pub checksum: u16,
    pub src_ip: Ipv4Addr,
    pub dst_ip: Ipv4Addr,
}

impl Ipv4Header {
    pub fn new(
        src_ip: Ipv4Addr,
        dst_ip: Ipv4Addr,
        protocol: IpProtocol,
        payload_len: usize,
    ) -> Self {
        let total_length = (IPV4_MIN_HEADER_LEN + payload_len) as u16;
        Self {
            version: 4,
            ihl: 5,
            tos: 0,
            total_length,
            identification: 0x1234,
            flags_fragment: 0x4000, // Don't fragment flag
            ttl: DEFAULT_TTL,
            protocol,
            checksum: 0,
            src_ip,
            dst_ip,
        }
    }

    pub fn parse(buf: &[u8]) -> Result<(Self, &[u8]), &'static str> {
        if buf.len() < IPV4_MIN_HEADER_LEN {
            return Err("Buffer too short for IPv4 header");
        }

        let ver_ihl = buf[0];
        let version = (ver_ihl >> 4) & 0x0F;
        let ihl = ver_ihl & 0x0F;
        if version != 4 {
            return Err("Invalid IPv4 version");
        }
        if ihl < 5 {
            return Err("Invalid IPv4 IHL");
        }
        let header_len = (ihl as usize) * 4;
        if buf.len() < header_len {
            return Err("Buffer smaller than IPv4 header length specified in IHL");
        }

        let tos = buf[1];
        let total_length = ((buf[2] as u16) << 8) | (buf[3] as u16);
        let identification = ((buf[4] as u16) << 8) | (buf[5] as u16);
        let flags_fragment = ((buf[6] as u16) << 8) | (buf[7] as u16);
        let ttl = buf[8];
        let protocol = IpProtocol::from(buf[9]);
        let checksum = ((buf[10] as u16) << 8) | (buf[11] as u16);

        let src_ip = Ipv4Addr::new(buf[12], buf[13], buf[14], buf[15]);
        let dst_ip = Ipv4Addr::new(buf[16], buf[17], buf[18], buf[19]);

        // Verify checksum over header
        let calculated_sum = calculate_checksum(&buf[..header_len]);
        if calculated_sum != 0 {
            return Err("IPv4 header checksum validation failed");
        }

        let payload_end = if (total_length as usize) <= buf.len() {
            total_length as usize
        } else {
            buf.len()
        };

        let payload = &buf[header_len..payload_end];

        Ok((
            Self {
                version,
                ihl,
                tos,
                total_length,
                identification,
                flags_fragment,
                ttl,
                protocol,
                checksum,
                src_ip,
                dst_ip,
            },
            payload,
        ))
    }

    pub fn serialize(&mut self, out: &mut [u8]) -> Result<usize, &'static str> {
        if out.len() < IPV4_MIN_HEADER_LEN {
            return Err("Buffer too small for IPv4 header serialization");
        }

        out[0] = (self.version << 4) | (self.ihl & 0x0F);
        out[1] = self.tos;
        out[2] = (self.total_length >> 8) as u8;
        out[3] = (self.total_length & 0xFF) as u8;
        out[4] = (self.identification >> 8) as u8;
        out[5] = (self.identification & 0xFF) as u8;
        out[6] = (self.flags_fragment >> 8) as u8;
        out[7] = (self.flags_fragment & 0xFF) as u8;
        out[8] = self.ttl;
        out[9] = self.protocol.into();
        out[10] = 0; // Checksum placeholder
        out[11] = 0;

        out[12..16].copy_from_slice(&self.src_ip.0);
        out[16..20].copy_from_slice(&self.dst_ip.0);

        // Compute 16-bit 1's complement internet checksum
        let sum = calculate_checksum(&out[..IPV4_MIN_HEADER_LEN]);
        self.checksum = sum;
        out[10] = (sum >> 8) as u8;
        out[11] = (sum & 0xFF) as u8;

        Ok(IPV4_MIN_HEADER_LEN)
    }
}

/// Computes standard Internet 1's complement checksum (RFC 1071)
pub fn calculate_checksum(data: &[u8]) -> u16 {
    let mut sum: u32 = 0;
    let mut i = 0;

    while i + 1 < data.len() {
        let word = ((data[i] as u32) << 8) | (data[i + 1] as u32);
        sum = sum.wrapping_add(word);
        i += 2;
    }

    if i < data.len() {
        let word = (data[i] as u32) << 8;
        sum = sum.wrapping_add(word);
    }

    while (sum >> 16) != 0 {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }

    !(sum as u16)
}
