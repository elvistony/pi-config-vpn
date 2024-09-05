#!/bin/bash

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Function to add MASQUERADE rule if it doesn't exist
add_masquerade_rule() {
    local interface=$1
    local rule_exists=$(sudo iptables -t nat -C POSTROUTING -o "$interface" -j MASQUERADE 2>/dev/null)
    
    if [ "$rule_exists" ]; then
        echo "MASQUERADE rule for $interface already exists."
    else
        sudo iptables -t nat -A POSTROUTING -o "$interface" -j MASQUERADE
        echo "Added MASQUERADE rule for $interface."
    fi
}

# Function to add FORWARD rule if it doesn't exist
add_forward_rule() {
    local in_interface=$1
    local out_interface=$2
    local rule_exists=$(sudo iptables -C FORWARD -i "$in_interface" -o "$out_interface" -j ACCEPT 2>/dev/null)
    
    if [ "$rule_exists" ]; then
        echo "FORWARD rule from $in_interface to $out_interface already exists."
    else
        sudo iptables -A FORWARD -i "$in_interface" -o "$out_interface" -j ACCEPT
        echo "Added FORWARD rule from $in_interface to $out_interface."
    fi
}

# Function to add reverse FORWARD rule if it doesn't exist
add_reverse_forward_rule() {
    local in_interface=$1
    local out_interface=$2
    local rule_exists=$(sudo iptables -C FORWARD -i "$out_interface" -o "$in_interface" -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null)
    
    if [ "$rule_exists" ]; then
        echo "Reverse FORWARD rule from $out_interface to $in_interface already exists."
    else
        sudo iptables -A FORWARD -i "$out_interface" -o "$in_interface" -m state --state RELATED,ESTABLISHED -j ACCEPT
        echo "Added reverse FORWARD rule from $out_interface to $in_interface."
    fi
}

# Add MASQUERADE rules for WireGuard interfaces
for wg_conf in /etc/wireguard/*.conf; do
    wg_interface=$(basename "$wg_conf" .conf)
    add_masquerade_rule "$wg_interface"
done

# Add FORWARD rules for wlan1 to WireGuard and vice versa
for wg_conf in /etc/wireguard/*.conf; do
    wg_interface=$(basename "$wg_conf" .conf)
    add_forward_rule "wlan1" "$wg_interface"
    add_reverse_forward_rule "$wg_interface" "wlan1"
done

# Add MASQUERADE rule for wlan0
add_masquerade_rule "wlan0"

# Add FORWARD rules for wlan1 to wlan0 and vice versa
add_forward_rule "wlan1" "wlan0"
add_reverse_forward_rule "wlan0" "wlan1"
