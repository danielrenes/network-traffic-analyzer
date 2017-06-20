#!/usr/bin/env python

import socket
import time
import threading

from netifaces import ifaddresses
from scapy.all import *

from config import Config
from model import SimpleData, DetailedData, DataStorage

class Sniffer(threading.Thread):
    def __init__(self, iface):
        super(Sniffer, self).__init__()
        print '[+] Packet sniffer thread started'
        self.iface = iface

    def run(self):
        sniff(iface=self.iface, prn=self.handle_packet)

    def handle_packet(self, pkt):
        global stats

        src = None
        dst = None
        sport = None
        dport = None
        protocol = None

        if IP in pkt:
            src = pkt[IP].src
            dst = pkt[IP].dst

        if src != myip and dst != myip:
            return

        if TCP in pkt:
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            protocol = tcp_reverse[sport] if dst == myip else tcp_reverse[dport]
        elif UDP in pkt:
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            protocol = udp_reverse[sport] if dst == myip else udp_reverse[dport]

        if src is None or dst is None or sport is None or dport is None or protocol is None:
            return

        if Config.MODE == 'simple':
            packet = SimplePacket(src, dst)
        elif Config.MODE == 'detailed':
            packet = DetailedPacket(src, dst, sport, dport, protocol)

        stats.add(packet)

class ServerSocket(threading.Thread):
    def __init__(self, host, port, refresh_time):
        super(ServerSocket, self).__init__()
        print '[+] Server socket thread started'
        self.refresh_time = refresh_time
        self.data_storage = None
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.conn = None

    def run(self):
        self.socket.listen(1)
        self.conn = self.socket.accept()[0]
        while True:
            time.sleep(self.refresh_time)
            self.pull()
            if self.data_storage is not None:
                self.push()
                print '[-] Update sent'

    def pull(self):
        self.data_storage = stats.convert()

    def push(self):
        self.conn.send(self.data_storage.encode())

class Statistics(object):
    def __init__(self):
        self.packets = []
        self.num_packets = {}

    def add(self, packet):
        if packet in self.packets:
            self.num_packets[packet] += 1
            idx = self.packets.index(packet) - 1
            while self.num_packets[packet] > self.num_packets[self.packets[idx]] and idx >= 0:
                self.packets[idx], self.packets[idx + 1] = self.packets[idx + 1], self.packets[idx]
                idx -= 1
        else:
            self.packets.append(packet)
            self.num_packets[packet] = 1

    def convert(self):
        conv_all = []
        for packet in self.packets:
            conv_one = packet.convert()
            conv_one.num_packets = self.num_packets[packet]
            conv_all.append(conv_one)
        return DataStorage(conv_all)

class Packet(object):
    def __init__(self, src, dst, sport=None, dport=None, protocol=None):
        self.src = src
        self.dst = dst
        self.sport = sport
        self.dport = dport
        self.protocol = protocol

    def convert(self):
        if self.src == myip:
            typ = "sent"
            ip = lookup(self.dst)
            port = self.dport
        else:
            typ = "recv"
            ip = lookup(self.src)
            port = self.sport
        protocol = self.protocol

        if Config.MODE == 'simple':
            return SimpleData(typ, ip)
        elif Config.MODE == 'detailed':
            return DetailedData(typ, ip, port, protocol)

    def __hash__(self):
        return hash((self.src, self.dst, self.sport, self.dport, self.protocol))

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not __eq__(other)

class SimplePacket(Packet):
    def __init__(self, src, dst):
        super(SimplePacket, self).__init__(src, dst)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.src == other.src and self.dst == other.dst
        else:
            return false

class DetailedPacket(Packet):
    def __init__(self, src, dst, sport, dport, protocol):
        super(DetailedPacket, self).__init__(src, dst, sport, dport, protocol)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

def lookup(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return ip

tcp_reverse = dict((TCP_SERVICES[k], k) for k in TCP_SERVICES.keys())
udp_reverse = dict((UDP_SERVICES[k], k) for k in UDP_SERVICES.keys())
myip = ifaddresses(Config.IFACE)[2][0]['addr']
stats = Statistics()

sniffer_thread = Sniffer(Config.IFACE)
sniffer_thread.daemon = True
sniffer_thread.start()

socket_thread = ServerSocket(Config.HOST, Config.SOCKET_PORT, Config.REFRESH_TIME)
socket_thread.daemon = True
socket_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    socket_thread.socket.close()
