#!/usr/bin/env python3

from scapy.all import *
import os
from getmac import get_mac_address
import netifaces

# uid of the remote radio
radio_id = 10206

# futher usage for rq/rsp coordinates on different radio channels
#in_interface  = "lo"

# need to be set to appropriate local configuration
#out_interface = "{sending_network_interface_localpc}"  # i.e. "eth0"

out_interface = "eth0"
src_ip   = netifaces.ifaddresses(out_interface)[netifaces.AF_INET][0]['addr']
gate_mac = get_mac_address(ip = list(filter(lambda x: x[1] == out_interface, netifaces.gateways()[netifaces.AF_INET]))[0][0])
# offset 12.0.0.0 to radio_uid from decimal to ip in byte representation
dst_ip   = socket.inet_ntoa(struct.pack('!L', radio_id + 0x0c000000))
src_port = 4001
dst_port = 4001
eth_header  = Ether(dst=gate_mac)
ip_header   = IP(src=src_ip, dst=dst_ip)
udp_packet  = UDP(sport=src_port, dport=dst_port)
# see Wireshark dump / vgl. https://github.com/JarvisSmallhouse/gateway/blob/master/src/Protocols/LRRP.js
rq_payload  = b'\x05\x06\x22\x04\xc0\x00\x00\x01'

packet = eth_header / ip_header / udp_packet / Raw(load=rq_payload)

#packet.show()
rsp = srp(packet, iface=out_interface)
rsp_payload = rsp[0].res[0].answer.load

lat = int.from_bytes(rsp_payload[9:13]) * (180/4294967295)
lon = int.from_bytes(rsp_payload[13:17]) * (360/4294967295)

# print osm link
print(f'https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}')
exit(0)
