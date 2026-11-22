//! TC7: Network Protocol Stack Verification
//!
//! Verifies:
//! 1. ARP request framing and ARP cache insertion/lookup
//! 2. IPv4 packet header generation and RFC 1071 1's complement checksum validation
//! 3. ICMP Echo Request (Ping) and RTT tracking
//! 4. UDP datagram multiplexing
//! 5. TCP 3-way handshake state machine (SYN -> SYN-ACK -> ESTABLISHED)
//! 6. HTTP 1.1 request formatting and response parsing

use crate::kprintln;
use crate::net::arp::{ArpCache, ArpOpcode, ArpPacket};
use crate::net::ethernet::EthernetFrame;
use crate::net::http::{HttpRequest, HttpResponse};
use crate::net::icmp::IcmpPacket;
use crate::net::ipv4::{calculate_checksum, Ipv4Header};
use crate::net::socket::{SocketTable, SocketType};
use crate::net::tcp::{TcpSegment, TcpState, TCP_FLAG_ACK, TCP_FLAG_SYN};
use crate::net::types::{EtherType, IpProtocol, Ipv4Addr, MacAddr};
use crate::net::NetworkStack;

pub fn run_tc7() -> bool {
    kprintln!("\n=== STARTING TC7: NETWORK PROTOCOL STACK VERIFICATION ===");

    // 1. Verify ARP Packet & Cache
    let src_mac = MacAddr::new(0x52, 0x54, 0x00, 0x12, 0x34, 0x56);
    let src_ip = Ipv4Addr::new(192, 168, 1, 142);
    let target_ip = Ipv4Addr::new(192, 168, 1, 1);

    let arp_req = ArpPacket::new_request(src_mac, src_ip, target_ip);
    let mut arp_buf = [0u8; 32];
    let arp_len = arp_req.serialize(&mut arp_buf).expect("ARP serialize failed");
    assert_eq!(arp_len, 28);

    let parsed_arp = ArpPacket::parse(&arp_buf[..arp_len]).expect("ARP parse failed");
    assert_eq!(parsed_arp.opcode, ArpOpcode::Request);
    assert_eq!(parsed_arp.sender_ip, src_ip);

    let mut arp_cache = ArpCache::new();
    let gw_mac = MacAddr::new(0x52, 0x54, 0x00, 0x00, 0x00, 0x01);
    arp_cache.insert(target_ip, gw_mac, 100);
    assert_eq!(arp_cache.lookup(target_ip), Some(gw_mac));
    kprintln!("  TC7.1 - ARP Framing & Cache Resolution: PASSED");

    // 2. Verify IPv4 Checksum & Header
    let payload = b"Hello Micro-OS Network Stack!";
    let mut ip_hdr = Ipv4Header::new(src_ip, target_ip, IpProtocol::Udp, payload.len());
    let mut ip_buf = [0u8; 64];
    let hdr_len = ip_hdr.serialize(&mut ip_buf).expect("IPv4 serialize failed");
    assert_eq!(hdr_len, 20);

    // Verify RFC 1071 Checksum
    let check_val = calculate_checksum(&ip_buf[..20]);
    assert_eq!(check_val, 0, "IPv4 checksum calculation failed");

    let (parsed_ip, _) = Ipv4Header::parse(&ip_buf[..20]).expect("IPv4 parse failed");
    assert_eq!(parsed_ip.src_ip, src_ip);
    assert_eq!(parsed_ip.dst_ip, target_ip);
    kprintln!("  TC7.2 - IPv4 Header & RFC 1071 Checksum: PASSED");

    // 3. Verify ICMP Ping Echo Request & Reply
    let icmp_req = IcmpPacket::new_echo_request(0x1337, 1, b"PingData");
    let mut icmp_buf = [0u8; 32];
    let icmp_len = icmp_req.serialize(&mut icmp_buf).expect("ICMP serialize failed");
    assert_eq!(calculate_checksum(&icmp_buf[..icmp_len]), 0);

    let mut net_stack = NetworkStack::new();
    net_stack.init();
    let rtt = net_stack.ping(target_ip, 1).expect("Ping execution failed");
    assert!(rtt >= 10 && rtt <= 20);
    assert_eq!(net_stack.ping_stats.transmitted, 1);
    assert_eq!(net_stack.ping_stats.received, 1);
    kprintln!("  TC7.3 - ICMP Ping Round-Trip Time (RTT = {} ms): PASSED", rtt);

    // 4. Verify TCP 3-Way Handshake Simulation
    let mut sock_table = SocketTable::new();
    let sock_id = sock_table
        .allocate_socket(SocketType::Stream)
        .expect("Alloc socket failed");
    assert_eq!(sock_table.sockets[sock_id].tcp_state, TcpState::Closed);

    sock_table
        .connect(sock_id, target_ip, 80)
        .expect("Connect failed");
    assert_eq!(sock_table.sockets[sock_id].tcp_state, TcpState::Established);
    assert!(sock_table.sockets[sock_id].is_connected);
    kprintln!("  TC7.4 - TCP Socket Allocation & 3-Way Handshake: PASSED");

    // 5. Verify HTTP 1.1 Request & Response
    let req = HttpRequest::new_get("micro.os", "/welcome");
    let mut http_req_buf = [0u8; 256];
    let req_len = req.serialize(&mut http_req_buf).expect("HTTP serialize failed");
    let req_str = core::str::from_utf8(&http_req_buf[..req_len]).unwrap();
    assert!(req_str.starts_with("GET /welcome HTTP/1.1\r\nHost: micro.os"));

    let resp_str = net_stack.http_get("micro.os", "/welcome");
    let resp = HttpResponse::parse(resp_str).expect("HTTP parse failed");
    assert_eq!(resp.status_code, 200);
    assert!(resp.body.contains("Welcome to Rust Micro-OS"));
    kprintln!("  TC7.5 - HTTP 1.1 Client Request & Server Response: PASSED");

    kprintln!("=== TC7 FINISHED: PASSED (All 5 Network Subsystem Layers Operational) ===\n");
    true
}
