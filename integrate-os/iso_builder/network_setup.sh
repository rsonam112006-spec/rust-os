#!/bin/bash
# Integrate OS - Unified Wi-Fi and LAN Network Configuration Subsystem
# Supports Intel AX203 Wi-Fi 6 (iwlwifi) and standard Ethernet adapters

set -e

echo "=========================================================="
echo "          INTEGRATE OS - NETWORK MANAGEMENT ENGINE        "
echo "=========================================================="

# 1. Hardware Interface Detection
echo -e "\n[*] Step 1: Detecting Physical & Virtual Network Interfaces..."
WIRELESS_IF=$(ip -o link show | awk -F': ' '{print $2}' | grep -E '^wl' | head -n 1 || true)
ETHERNET_IF=$(ip -o link show | awk -F': ' '{print $2}' | grep -E '^(eth|en)' | head -n 1 || true)

if [ -n "$WIRELESS_IF" ]; then
    echo "  [+] Wireless Interface Detected : $WIRELESS_IF"
    MAC_WLAN=$(cat /sys/class/net/"$WIRELESS_IF"/address 2>/dev/null || echo "Unknown")
    echo "      MAC Address                 : $MAC_WLAN"
else
    echo "  [-] No native wireless interface found (or running in VM bridged mode)"
fi

if [ -n "$ETHERNET_IF" ]; then
    echo "  [+] Ethernet Interface Detected : $ETHERNET_IF"
    MAC_ETH=$(cat /sys/class/net/"$ETHERNET_IF"/address 2>/dev/null || echo "Unknown")
    echo "      MAC Address                 : $MAC_ETH"
else
    echo "  [-] No Ethernet interface found"
fi

# 2. Wi-Fi Scanner Engine
scan_wifi() {
    local iface="$1"
    echo -e "\n[*] Step 2: Scanning Available Wi-Fi Networks on $iface..."
    if command -v nmcli >/dev/null 2>&1; then
        nmcli device wifi list ifname "$iface" || true
    elif command -v iw >/dev/null 2>&1; then
        ip link set "$iface" up 2>/dev/null || true
        iw dev "$iface" scan | grep -E "SSID:|signal:|freq:" | head -n 20 || true
    elif command -v iwlist >/dev/null 2>&1; then
        iwlist "$iface" scan | grep -E "ESSID:|Quality|Signal" | head -n 20 || true
    else
        echo "  [!] Wireless scanning tools (nmcli/iw) not loaded in minimal mode."
    fi
}

if [ -n "$WIRELESS_IF" ]; then
    scan_wifi "$WIRELESS_IF"
fi

# 3. LAN / Ethernet DHCP Configuration
configure_ethernet() {
    local iface="$1"
    echo -e "\n[*] Step 3: Checking Ethernet Interface ($iface)..."
    local CURRENT_IP=$(ip -4 addr show dev "$iface" 2>/dev/null | awk '/inet / {print $2}')
    if [ -n "$CURRENT_IP" ]; then
        echo "  [+] Active IPv4 lease already established: $CURRENT_IP"
    else
        echo "  [*] Requesting DHCP lease on $iface..."
        ip link set "$iface" up 2>/dev/null || true
        if command -v dhclient >/dev/null 2>&1; then
            timeout 5 dhclient -1 -v "$iface" 2>/dev/null || true
        elif command -v udhcpc >/dev/null 2>&1; then
            udhcpc -i "$iface" -n -q -t 3 2>/dev/null || true
        fi
    fi
}

if [ -n "$ETHERNET_IF" ]; then
    configure_ethernet "$ETHERNET_IF"
fi

# 4. Connectivity Diagnostics
echo -e "\n[*] Step 4: Testing End-to-End Network Connectivity..."

# Test A: IP Assignment
echo -n "  [Test A] IP Address Assignment: "
IP_ADDR=$(ip -4 addr show scope global | awk '/inet / {print $2}' | head -n 1)
if [ -n "$IP_ADDR" ]; then
    echo "PASS ($IP_ADDR)"
else
    echo "FAIL (No global IPv4 assigned)"
fi

# Test B: Default Gateway
echo -n "  [Test B] Gateway Reachability : "
GATEWAY=$(ip route | awk '/default/ {print $3}' | head -n 1)
if [ -n "$GATEWAY" ]; then
    echo "PASS ($GATEWAY)"
else
    echo "FAIL (No default route)"
fi

# Test C: DNS Resolution
echo -n "  [Test C] DNS Resolution       : "
if getent hosts google.com >/dev/null 2>&1 || host google.com >/dev/null 2>&1; then
    RESOLVED_IP=$(getent hosts google.com | awk '{print $1}' | head -n 1)
    echo "PASS (google.com -> $RESOLVED_IP)"
else
    echo "FAIL (Unable to resolve DNS names)"
fi

# Test D: Internet Ping (ICMP)
echo -n "  [Test D] Internet Access (Ping): "
if ping -c 2 -W 3 8.8.8.8 >/dev/null 2>&1; then
    RTT=$(ping -c 2 -W 3 8.8.8.8 | awk -F '/' 'END {print $5}')
    echo "PASS (Avg RTT = ${RTT} ms)"
else
    echo "FAIL (Packet loss to 8.8.8.8)"
fi

# Test E: HTTP Request
echo -n "  [Test E] HTTP Web Access       : "
if command -v curl >/dev/null 2>&1; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://www.google.com || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        echo "PASS (HTTP $HTTP_CODE OK)"
    else
        echo "FAIL (HTTP response code $HTTP_CODE)"
    fi
else
    echo "SKIPPED (curl not installed)"
fi

echo -e "\n=========================================================="
echo "Network configuration & diagnostic suite complete."
echo "=========================================================="
