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
            if data['type'] == 'sent':
                sent.append(data)
            elif data['type'] == 'recv':
                recv.append(data)
        return (sent, recv)

    def encode(self):
        return json.dumps([data.data for data in self.datas])

    @staticmethod
    def decode(encoded):
        datas = []
        for entry in json.loads(encoded):
            datas.append(entry)
        return DataStorage(datas)

class Data(object):
    def __init__(self, **kwargs):
        self.data = {}
        self.add(**kwargs)

    def add(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.data[k] = v
