//! Network Protocol Stack Subsystem
//!
//! Provides a complete, zero-external-dependency network stack in Rust:
//! - Physical/Data Link: VirtualNic & IEEE 802.3 Ethernet II
//! - Network: IPv4 (RFC 791) & ARP (RFC 826)
//! - Transport: ICMP (RFC 792), UDP (RFC 768), TCP (RFC 793)
//! - Application: HTTP 1.1 client & micro-server

pub mod arp;
pub mod ethernet;
pub mod http;
pub mod icmp;
pub mod ipv4;
pub mod nic;
pub mod socket;
pub mod tcp;
pub mod types;
pub mod wifi;

pub use arp::{ArpCache, ArpPacket};
pub use ethernet::{EthernetFrame, ETHERNET_HEADER_LEN};
pub use http::{HttpRequest, HttpResponse};
pub use icmp::{IcmpPacket, PingStats};
pub use ipv4::{calculate_checksum, Ipv4Header};
pub use nic::VirtualNic;
pub use socket::{Socket, SocketTable, SocketType};
pub use tcp::{TcpSegment, TcpState};
pub use types::{EtherType, IpProtocol, Ipv4Addr, MacAddr};
pub use wifi::{WifiAdapter, WifiAuthMode, WifiBand, WifiNetwork, WifiState, MAX_WIFI_NETWORKS};

pub struct NetworkStack {
    pub nic: VirtualNic,
    pub wifi: WifiAdapter,
    pub arp_cache: ArpCache,
    pub socket_table: SocketTable,
    pub ping_stats: PingStats,
}

impl NetworkStack {
    pub const fn new() -> Self {
        let mac = MacAddr::new(0x52, 0x54, 0x00, 0x12, 0x34, 0x56);
        let wifi_mac = MacAddr::new(0x3C, 0x06, 0x30, 0xAB, 0xCD, 0xEF);
        let ip = Ipv4Addr::new(192, 168, 1, 142);
        Self {
            nic: VirtualNic::new("virtio-net0", mac, ip),
            wifi: WifiAdapter::new("wlan0", wifi_mac),
            arp_cache: ArpCache::new(),
            socket_table: SocketTable::new(),
            ping_stats: PingStats::new(),
        }
    }

    pub fn init(&mut self) {
        // Pre-populate default gateway into ARP cache
        self.arp_cache.insert(
            self.nic.gateway,
            MacAddr::new(0x52, 0x54, 0x00, 0x00, 0x00, 0x01),
            0,
        );
        // Pre-populate DNS server into ARP cache
        self.arp_cache.insert(
            self.nic.dns,
            MacAddr::new(0x52, 0x54, 0x00, 0x08, 0x08, 0x08),
            0,
        );

        // Auto-scan and associate with Wi-Fi network
        self.wifi.scan();
        let _ = self.wifi.connect("Home-Fiber-5G", "SecretWiFiPass123");
    }

    /// Performs active Wi-Fi scan and returns detected networks
    pub fn wifi_scan(&mut self) -> &[Option<WifiNetwork>] {
        self.wifi.scan()
    }

    /// Connects to a Wi-Fi Access Point with WPA2/WPA3 authentication
    pub fn wifi_connect(&mut self, ssid: &str, password: &str) -> Result<Ipv4Addr, &'static str> {
        self.wifi.connect(ssid, password)
    }

    /// Disconnects from current Wi-Fi network
    pub fn wifi_disconnect(&mut self) -> Result<(), &'static str> {
        self.wifi.disconnect()
    }

    /// Sends an ICMP Echo Request (Ping) to the target IPv4 address
    pub fn ping(&mut self, target_ip: Ipv4Addr, seq: u16) -> Result<u32, &'static str> {
        self.ping_stats.transmitted += 1;

        // Resolve target MAC (direct or via gateway)
        let resolved_mac = if target_ip.is_in_subnet(self.nic.ip, self.nic.netmask) {
            self.arp_cache.lookup(target_ip).unwrap_or(MacAddr::BROADCAST)
        } else {
            self.arp_cache.lookup(self.nic.gateway).unwrap_or(MacAddr::BROADCAST)
        };

        // Construct ICMP Echo Request payload
        let icmp_payload = b"RustMicroOS-PingEcho";
        let icmp = IcmpPacket::new_echo_request(0x1337, seq, icmp_payload);

        let mut icmp_buf = [0u8; 64];
        let icmp_len = icmp.serialize(&mut icmp_buf)?;

        // Construct IPv4 Header
        let mut ip_hdr = Ipv4Header::new(self.nic.ip, target_ip, IpProtocol::Icmp, icmp_len);
        let mut ip_buf = [0u8; 128];
        let ip_hdr_len = ip_hdr.serialize(&mut ip_buf)?;
        ip_buf[ip_hdr_len..ip_hdr_len + icmp_len].copy_from_slice(&icmp_buf[..icmp_len]);
        let total_ip_len = ip_hdr_len + icmp_len;

        // Construct Ethernet II Frame
        let eth = EthernetFrame {
            dst_mac: resolved_mac,
            src_mac: self.nic.mac,
            ether_type: EtherType::Ipv4,
            payload: &ip_buf[..total_ip_len],
        };

        let mut eth_buf = [0u8; 256];
        let eth_len = eth.serialize(&mut eth_buf)?;

        // Transmit out through NIC
        self.nic.transmit(&eth_buf[..eth_len])?;

        // Simulate network latency (deterministic RTT between 10ms - 15ms)
        let simulated_rtt = 10 + ((seq as u32 * 3) % 6);
        self.ping_stats.record_reply(simulated_rtt);

        Ok(simulated_rtt)
    }

    /// Performs an HTTP GET request to a simulated endpoint or server
    pub fn http_get<'a>(&mut self, host: &str, path: &str) -> &'static str {
        // Record packet transmission and reception
        let _ = self.nic.transmit(b"TCP SYN");
        let _ = self.nic.transmit(b"TCP ACK HTTP GET");
        self.nic.packets_rx += 2;
        self.nic.bytes_rx += 512;

        http::handle_local_http(path)
    }
}
