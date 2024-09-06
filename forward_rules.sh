#!/bin/bash

sudo iptables -t nat -C POSTROUTING -o tun0 -j MASQUERADE || sudo iptables -t nat -A POSTROUTING -o tun0 -j MASQUERADE
sudo iptables -C FORWARD -i tun0 -j ACCEPT || sudo iptables -A FORWARD -i tun0 -j ACCEPT
sudo iptables -C FORWARD -o tun0 -j ACCEPT || sudo iptables -A FORWARD -o tun0 -j ACCEPT

sudo iptables -t nat -C POSTROUTING -o tun0 -j MASQUERADE || sudo iptables -t nat -A POSTROUTING -o tun0 -j MASQUERADE
sudo iptables -C FORWARD -i wlan1 -o tun0 -j ACCEPT || sudo iptables -A FORWARD -i wlan1 -o tun0 -j ACCEPT
sudo iptables -C FORWARD -i tun0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT || sudo iptables -A FORWARD -i tun0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT

sudo iptables -t nat -C POSTROUTING -o wlan0 -j MASQUERADE || sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sudo iptables -C FORWARD -i wlan1 -o wlan0 -j ACCEPT || sudo iptables -A FORWARD -i wlan1 -o wlan0 -j ACCEPT
sudo iptables -C FORWARD -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT || sudo iptables -A FORWARD -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT
