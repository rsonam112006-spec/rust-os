//! Virtual Network Interface Card (VirtualNic)
//!
//! Provides hardware abstraction for virtual network adapters (virtio-net / e1000).
//! Manages RX/TX ring buffers, interface metrics, link status, and addressing.

use super::types::{Ipv4Addr, MacAddr};

pub const RING_BUFFER_SIZE: usize = 16;
pub const MAX_PACKET_LEN: usize = 1518;

#[derive(Clone, Copy)]
pub struct PacketSlot {
    pub len: usize,
    pub data: [u8; MAX_PACKET_LEN],
    pub valid: bool,
}

impl PacketSlot {
    pub const fn empty() -> Self {
        Self {
            len: 0,
            data: [0u8; MAX_PACKET_LEN],
            valid: false,
        }
    }
}

pub struct VirtualNic {
    pub name: &'static str,
    pub mac: MacAddr,
    pub ip: Ipv4Addr,
    pub netmask: Ipv4Addr,
    pub gateway: Ipv4Addr,
    pub dns: Ipv4Addr,
    pub link_up: bool,

    // Performance & telemetry counters
    pub packets_tx: u64,
    pub packets_rx: u64,
    pub bytes_tx: u64,
    pub bytes_rx: u64,
    pub dropped_packets: u64,

    // Internal transmission & reception queues
    pub tx_queue: [PacketSlot; RING_BUFFER_SIZE],
    pub rx_queue: [PacketSlot; RING_BUFFER_SIZE],
    pub tx_head: usize,
    pub tx_tail: usize,
    pub rx_head: usize,
    pub rx_tail: usize,
}

impl VirtualNic {
    pub const fn new(name: &'static str, mac: MacAddr, ip: Ipv4Addr) -> Self {
        Self {
            name,
            mac,
            ip,
            netmask: Ipv4Addr::new(255, 255, 255, 0),
            gateway: Ipv4Addr::new(192, 168, 1, 1),
            dns: Ipv4Addr::new(8, 8, 8, 8),
            link_up: true,
            packets_tx: 0,
            packets_rx: 0,
            bytes_tx: 0,
            bytes_rx: 0,
            dropped_packets: 0,
            tx_queue: [PacketSlot::empty(); RING_BUFFER_SIZE],
            rx_queue: [PacketSlot::empty(); RING_BUFFER_SIZE],
            tx_head: 0,
            tx_tail: 0,
            rx_head: 0,
            rx_tail: 0,
        }
    }

    pub fn transmit(&mut self, packet: &[u8]) -> Result<(), &'static str> {
        if !self.link_up {
            return Err("Network link is down");
        }
        if packet.len() > MAX_PACKET_LEN {
            return Err("Packet exceeds MTU limit");
        }

        let slot = &mut self.tx_queue[self.tx_tail];
        slot.len = packet.len();
        slot.data[..packet.len()].copy_from_slice(packet);
        slot.valid = true;

        self.tx_tail = (self.tx_tail + 1) % RING_BUFFER_SIZE;
        self.packets_tx += 1;
        self.bytes_tx += packet.len() as u64;

        Ok(())
    }

    pub fn receive(&mut self, out: &mut [u8]) -> Result<Option<usize>, &'static str> {
        if !self.link_up {
            return Ok(None);
        }

        let slot = &mut self.rx_queue[self.rx_head];
        if !slot.valid {
            return Ok(None);
        }

        let len = slot.len;
        if out.len() < len {
            return Err("Buffer too small for incoming packet");
        }

        out[..len].copy_from_slice(&slot.data[..len]);
        slot.valid = false;
        self.rx_head = (self.rx_head + 1) % RING_BUFFER_SIZE;
        self.packets_rx += 1;
        self.bytes_rx += len as u64;

        Ok(Some(len))
    }

    pub fn inject_packet(&mut self, packet: &[u8]) -> Result<(), &'static str> {
        let slot = &mut self.rx_queue[self.rx_tail];
        if slot.valid {
            self.dropped_packets += 1;
            return Err("RX ring buffer full");
        }

        let copy_len = if packet.len() < MAX_PACKET_LEN {
            packet.len()
        } else {
            MAX_PACKET_LEN
        };
        slot.len = copy_len;
        slot.data[..copy_len].copy_from_slice(&packet[..copy_len]);
        slot.valid = true;
        self.rx_tail = (self.rx_tail + 1) % RING_BUFFER_SIZE;

        Ok(())
    }
}
