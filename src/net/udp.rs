//! User Datagram Protocol (UDP - RFC 768)
//!
//! Provides lightweight connectionless datagram transport.

pub const UDP_HEADER_LEN: usize = 8;

#[derive(Debug, Clone)]
pub struct UdpDatagram<'a> {
    pub src_port: u16,
    pub dst_port: u16,
    pub length: u16,
    pub checksum: u16,
    pub payload: &'a [u8],
}

impl<'a> UdpDatagram<'a> {
    pub fn new(src_port: u16, dst_port: u16, payload: &'a [u8]) -> Self {
        let length = (UDP_HEADER_LEN + payload.len()) as u16;
        Self {
            src_port,
            dst_port,
            length,
            checksum: 0,
            payload,
        }
    }

    pub fn parse(buf: &'a [u8]) -> Result<Self, &'static str> {
        if buf.len() < UDP_HEADER_LEN {
            return Err("Buffer too short for UDP header");
        }

        let src_port = ((buf[0] as u16) << 8) | (buf[1] as u16);
        let dst_port = ((buf[2] as u16) << 8) | (buf[3] as u16);
        let length = ((buf[4] as u16) << 8) | (buf[5] as u16);
        let checksum = ((buf[6] as u16) << 8) | (buf[7] as u16);

        if (length as usize) < UDP_HEADER_LEN {
            return Err("UDP length field less than header size");
        }

        let payload_len = (length as usize) - UDP_HEADER_LEN;
        let payload = if UDP_HEADER_LEN + payload_len <= buf.len() {
            &buf[UDP_HEADER_LEN..UDP_HEADER_LEN + payload_len]
        } else {
            &buf[UDP_HEADER_LEN..]
        };

        Ok(Self {
            src_port,
            dst_port,
            length,
            checksum,
            payload,
        })
    }

    pub fn serialize(&self, out: &mut [u8]) -> Result<usize, &'static str> {
        let total_len = UDP_HEADER_LEN + self.payload.len();
        if out.len() < total_len {
            return Err("Buffer too small to serialize UDP datagram");
        }

        out[0] = (self.src_port >> 8) as u8;
        out[1] = (self.src_port & 0xFF) as u8;
        out[2] = (self.dst_port >> 8) as u8;
        out[3] = (self.dst_port & 0xFF) as u8;
        out[4] = (self.length >> 8) as u8;
        out[5] = (self.length & 0xFF) as u8;
        out[6] = 0; // Checksum optional in IPv4 UDP
        out[7] = 0;

        out[8..total_len].copy_from_slice(self.payload);

        Ok(total_len)
    }
}
