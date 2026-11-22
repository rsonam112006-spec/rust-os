//! Transmission Control Protocol (TCP - RFC 793)
//!
//! Provides reliable, connection-oriented byte-stream abstraction, 3-way handshake,
//! segment parsing/serialization, and standard connection state transitions.

pub const TCP_MIN_HEADER_LEN: usize = 20;

pub const TCP_FLAG_FIN: u8 = 0x01;
pub const TCP_FLAG_SYN: u8 = 0x02;
pub const TCP_FLAG_RST: u8 = 0x04;
pub const TCP_FLAG_PSH: u8 = 0x08;
pub const TCP_FLAG_ACK: u8 = 0x10;
pub const TCP_FLAG_URG: u8 = 0x20;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TcpState {
    Closed,
    Listen,
    SynSent,
    SynReceived,
    Established,
    FinWait1,
    FinWait2,
    CloseWait,
    Closing,
    LastAck,
    TimeWait,
}

impl TcpState {
    pub const fn as_str(&self) -> &'static str {
        match self {
            TcpState::Closed => "CLOSED",
            TcpState::Listen => "LISTEN",
            TcpState::SynSent => "SYN_SENT",
            TcpState::SynReceived => "SYN_RCVD",
            TcpState::Established => "ESTABLISHED",
            TcpState::FinWait1 => "FIN_WAIT_1",
            TcpState::FinWait2 => "FIN_WAIT_2",
            TcpState::CloseWait => "CLOSE_WAIT",
            TcpState::Closing => "CLOSING",
            TcpState::LastAck => "LAST_ACK",
            TcpState::TimeWait => "TIME_WAIT",
        }
    }
}

#[derive(Debug, Clone)]
pub struct TcpSegment<'a> {
    pub src_port: u16,
    pub dst_port: u16,
    pub seq_num: u32,
    pub ack_num: u32,
    pub data_offset: u8,
    pub flags: u8,
    pub window_size: u16,
    pub checksum: u16,
    pub urgent_ptr: u16,
    pub payload: &'a [u8],
}

impl<'a> TcpSegment<'a> {
    pub fn new(
        src_port: u16,
        dst_port: u16,
        seq_num: u32,
        ack_num: u32,
        flags: u8,
        window_size: u16,
        payload: &'a [u8],
    ) -> Self {
        Self {
            src_port,
            dst_port,
            seq_num,
            ack_num,
            data_offset: 5, // 5 x 4 = 20 bytes
            flags,
            window_size,
            checksum: 0,
            urgent_ptr: 0,
            payload,
        }
    }

    pub fn is_syn(&self) -> bool {
        (self.flags & TCP_FLAG_SYN) != 0
    }

    pub fn is_ack(&self) -> bool {
        (self.flags & TCP_FLAG_ACK) != 0
    }

    pub fn is_fin(&self) -> bool {
        (self.flags & TCP_FLAG_FIN) != 0
    }

    pub fn is_rst(&self) -> bool {
        (self.flags & TCP_FLAG_RST) != 0
    }

    pub fn parse(buf: &'a [u8]) -> Result<Self, &'static str> {
        if buf.len() < TCP_MIN_HEADER_LEN {
            return Err("Buffer too short for TCP header");
        }

        let src_port = ((buf[0] as u16) << 8) | (buf[1] as u16);
        let dst_port = ((buf[2] as u16) << 8) | (buf[3] as u16);
        let seq_num = ((buf[4] as u32) << 24)
            | ((buf[5] as u32) << 16)
            | ((buf[6] as u32) << 8)
            | (buf[7] as u32);
        let ack_num = ((buf[8] as u32) << 24)
            | ((buf[9] as u32) << 16)
            | ((buf[10] as u32) << 8)
            | (buf[11] as u32);

        let data_offset = (buf[12] >> 4) & 0x0F;
        let flags = buf[13] & 0x3F;
        let window_size = ((buf[14] as u16) << 8) | (buf[15] as u16);
        let checksum = ((buf[16] as u16) << 8) | (buf[17] as u16);
        let urgent_ptr = ((buf[18] as u16) << 8) | (buf[19] as u16);

        let header_len = (data_offset as usize) * 4;
        if header_len < TCP_MIN_HEADER_LEN || buf.len() < header_len {
            return Err("Invalid TCP data offset");
        }

        let payload = &buf[header_len..];

        Ok(Self {
            src_port,
            dst_port,
            seq_num,
            ack_num,
            data_offset,
            flags,
            window_size,
            checksum,
            urgent_ptr,
            payload,
        })
    }

    pub fn serialize(&self, out: &mut [u8]) -> Result<usize, &'static str> {
        let total_len = TCP_MIN_HEADER_LEN + self.payload.len();
        if out.len() < total_len {
            return Err("Buffer too small to serialize TCP segment");
        }

        out[0] = (self.src_port >> 8) as u8;
        out[1] = (self.src_port & 0xFF) as u8;
        out[2] = (self.dst_port >> 8) as u8;
        out[3] = (self.dst_port & 0xFF) as u8;

        out[4] = (self.seq_num >> 24) as u8;
        out[5] = (self.seq_num >> 16) as u8;
        out[6] = (self.seq_num >> 8) as u8;
        out[7] = (self.seq_num & 0xFF) as u8;

        out[8] = (self.ack_num >> 24) as u8;
        out[9] = (self.ack_num >> 16) as u8;
        out[10] = (self.ack_num >> 8) as u8;
        out[11] = (self.ack_num & 0xFF) as u8;

        out[12] = (self.data_offset & 0x0F) << 4;
        out[13] = self.flags & 0x3F;
        out[14] = (self.window_size >> 8) as u8;
        out[15] = (self.window_size & 0xFF) as u8;
        out[16] = 0; // Checksum placeholder
        out[17] = 0;
        out[18] = (self.urgent_ptr >> 8) as u8;
        out[19] = (self.urgent_ptr & 0xFF) as u8;

        out[20..total_len].copy_from_slice(self.payload);

        Ok(total_len)
    }
}
