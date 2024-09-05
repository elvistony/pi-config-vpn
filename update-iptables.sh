#!/bin/bash

# Define the path to your WireGuard configuration directory
WG_CONF_DIR="/etc/wireguard"

# Define the NAT table chain for masquerading
CHAIN="POSTROUTING"

# First, clear existing MASQUERADE rules for WireGuard interfaces
echo "Clearing existing MASQUERADE rules for WireGuard interfaces..."
sudo iptables -t nat -F $CHAIN

# Iterate over all .conf files in the WireGuard configuration directory
for conf_file in "$WG_CONF_DIR"/*.conf; do
    # Extract the interface name from the file (assuming it's named after the conf file)
    interface_name=$(basename "$conf_file" .conf)

    # Add a MASQUERADE rule for the current WireGuard interface
    echo "Adding MASQUERADE rule for $interface_name..."
    sudo iptables -t nat -A $CHAIN -o wlan0 -j MASQUERADE -s 10.0.0.0/8
done

echo "MASQUERADE rules updated."

# Optionally, save the iptables rules if needed (depends on your system)
# For Debian-based systems:
# sudo iptables-save > /etc/iptables/rules.v4
# For Red Hat-based systems:
# sudo service iptables save
