#!/usr/bin/env python

import json

from config import Config

class DataStorage(object):
    def __init__(self, datas):
        self.datas = datas

    def separate(self):
        sent = []
        recv = []
        for data in self.datas:
            if data.type == 'sent':
                sent.append(data)
            elif data.type == 'recv':
                recv.append(data)
        return (sent, recv)

    def encode(self):
        return json.dumps([data.encode() for data in self.datas])

    @staticmethod
    def decode(encoded):
        datas = []
        for entry in json.loads(encoded):
            if Config.MODE == 'simple':
                datas.append(SimpleData.decode(entry))
            elif Config.MODE == 'detailed':
                datas.append(DetailedData.decode(entry))
        return DataStorage(datas)

class Data(object):
    def __init__(self):
        pass

    def encode(self):
        raise NotImplementedError

    @staticmethod
    def decode(self):
        raise NotImplementedError

class SimpleData(Data):
    def __init__(self, typ, ip, num_packets=None):
        super(SimpleData, self).__init__()
        self.type = typ
        self.ip = ip
        self.num_packets = num_packets

    def encode(self):
        return \
        {
            'type':         self.type,
            'ip':           self.ip,
            'num_packets':  self.num_packets
        }

    @staticmethod
    def decode(encoded):
        for key, value in encoded.iteritems():
            if 'type' in key:
                typ = value.strip()
            elif 'ip' in key:
                ip = value.strip()
            elif 'num_packets' in key:
                num_packets = value
        return SimpleData(typ, ip, num_packets)

class DetailedData(Data):
    def __init__(self, typ, ip, port, protocol, num_packets=None):
        super(DetailedData, self).__init__()
        self.type = typ
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.num_packets = num_packets

    def encode(self):
        return \
        {
            'type':         self.type,
            'ip':           self.ip,
            'port':         self.port,
            'protocol':     self.protocol,
            'num_packets':  self.num_packets
        }

    @staticmethod
    def decode(encoded):
        for key, value in encoded.iteritems():
            if 'type' in key:
                typ = value.strip()
            elif 'ip' in key:
                ip = value.strip()
            elif 'port' in key:
                port = value
            elif 'protocol' in key:
                protocol = value.strip()
            elif 'num_packets' in key:
                num_packets = value
        return DetailedData(typ, ip, port, protocol, num_packets)
