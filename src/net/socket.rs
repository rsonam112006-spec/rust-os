//! Socket Layer Abstraction for Micro-OS
//!
//! Provides BSD-style socket management with stream (TCP), datagram (UDP),
//! and raw (ICMP) sockets for micro-kernel tasks.

use super::tcp::TcpState;
use super::types::Ipv4Addr;

pub const MAX_SOCKETS: usize = 16;
pub const SOCKET_BUFFER_SIZE: usize = 512;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SocketType {
    Stream,   // TCP
    Datagram, // UDP
    Raw,      // ICMP
}

#[derive(Debug, Clone, Copy)]
pub struct Socket {
    pub id: usize,
    pub socket_type: SocketType,
    pub local_ip: Ipv4Addr,
    pub local_port: u16,
    pub remote_ip: Ipv4Addr,
    pub remote_port: u16,
    pub tcp_state: TcpState,
    pub is_bound: bool,
    pub is_connected: bool,
    pub rx_len: usize,
    pub tx_len: usize,
    pub rx_buffer: [u8; SOCKET_BUFFER_SIZE],
    pub tx_buffer: [u8; SOCKET_BUFFER_SIZE],
}

impl Socket {
    pub const fn empty(id: usize) -> Self {
        Self {
            id,
            socket_type: SocketType::Stream,
            local_ip: Ipv4Addr::UNSPECIFIED,
            local_port: 0,
            remote_ip: Ipv4Addr::UNSPECIFIED,
            remote_port: 0,
            tcp_state: TcpState::Closed,
            is_bound: false,
            is_connected: false,
            rx_len: 0,
            tx_len: 0,
            rx_buffer: [0u8; SOCKET_BUFFER_SIZE],
            tx_buffer: [0u8; SOCKET_BUFFER_SIZE],
        }
    }
}

pub struct SocketTable {
    pub sockets: [Socket; MAX_SOCKETS],
    pub next_port: u16,
}

impl SocketTable {
    pub const fn new() -> Self {
        const INIT_SOCKET: Socket = Socket::empty(0);
        let mut arr = [INIT_SOCKET; MAX_SOCKETS];
        let mut i = 0;
        while i < MAX_SOCKETS {
            arr[i].id = i;
            i += 1;
        }
        Self {
            sockets: arr,
            next_port: 49152, // Ephemeral range start
        }
    }

    pub fn allocate_socket(&mut self, s_type: SocketType) -> Result<usize, &'static str> {
        for socket in self.sockets.iter_mut() {
            if socket.tcp_state == TcpState::Closed && !socket.is_bound && !socket.is_connected {
                socket.socket_type = s_type;
                socket.is_bound = false;
                socket.is_connected = false;
                socket.rx_len = 0;
                socket.tx_len = 0;
                if s_type == SocketType::Stream {
                    socket.tcp_state = TcpState::Closed;
                }
                return Ok(socket.id);
            }
        }
        Err("No free sockets in socket table")
    }

    pub fn bind(
        &mut self,
        sock_id: usize,
        ip: Ipv4Addr,
        mut port: u16,
    ) -> Result<u16, &'static str> {
        if sock_id >= MAX_SOCKETS {
            return Err("Invalid socket ID");
        }
        if port == 0 {
            port = self.next_port;
            self.next_port = self.next_port.wrapping_add(1);
            if self.next_port < 49152 {
                self.next_port = 49152;
            }
        }

        let sock = &mut self.sockets[sock_id];
        sock.local_ip = ip;
        sock.local_port = port;
        sock.is_bound = true;
        Ok(port)
    }

    pub fn connect(
        &mut self,
        sock_id: usize,
        remote_ip: Ipv4Addr,
        remote_port: u16,
    ) -> Result<(), &'static str> {
        if sock_id >= MAX_SOCKETS {
            return Err("Invalid socket ID");
        }
        let sock = &mut self.sockets[sock_id];
        sock.remote_ip = remote_ip;
        sock.remote_port = remote_port;
        if sock.socket_type == SocketType::Stream {
            sock.tcp_state = TcpState::Established;
        }
        sock.is_connected = true;
        Ok(())
    }

    pub fn send(&mut self, sock_id: usize, data: &[u8]) -> Result<usize, &'static str> {
        if sock_id >= MAX_SOCKETS {
            return Err("Invalid socket ID");
        }
        let sock = &mut self.sockets[sock_id];
        let copy_len = if data.len() < SOCKET_BUFFER_SIZE {
            data.len()
        } else {
            SOCKET_BUFFER_SIZE
        };
        sock.tx_buffer[..copy_len].copy_from_slice(&data[..copy_len]);
        sock.tx_len = copy_len;
        Ok(copy_len)
    }

    pub fn receive(&mut self, sock_id: usize, out: &mut [u8]) -> Result<usize, &'static str> {
        if sock_id >= MAX_SOCKETS {
            return Err("Invalid socket ID");
        }
        let sock = &mut self.sockets[sock_id];
        if sock.rx_len == 0 {
            return Ok(0);
        }
        let copy_len = if sock.rx_len < out.len() {
            sock.rx_len
        } else {
            out.len()
        };
        out[..copy_len].copy_from_slice(&sock.rx_buffer[..copy_len]);
        sock.rx_len = 0;
        Ok(copy_len)
    }

    pub fn close(&mut self, sock_id: usize) {
        if sock_id < MAX_SOCKETS {
            self.sockets[sock_id] = Socket::empty(sock_id);
        }
    }
}
