#!/usr/bin/env python

import time
import threading

from flask import Flask, render_template, request, jsonify
from redis.client import PubSubWorkerThread

from config import Config
from model import DataStorage
from msg_queue import pubsub_obj

class Subscriber(PubSubWorkerThread):
    def __init__(self, sleep_time, daemon):
        super(Subscriber, self).__init__(pubsub_obj, sleep_time)
        self.daemon = daemon
        print '[+] Redis subscriber running'

def message_handler(msg):
    global sent_data
    global recv_data
    data_storage = DataStorage.decode(msg['data'])
    sent_data, recv_data = data_storage.separate()
    print '[-] Update received'

sent_data = None
recv_data = None

app = Flask(__name__)

@app.route('/')
def chart():
    return render_template('chart.html', sent_data=sent_data, recv_data=recv_data)

@app.route('/refresh', methods=['GET'])
def refresh():
    last_index_sent = int(request.args.get('last_index_sent'))
    last_index_recv = int(request.args.get('last_index_recv'))

    if sent_data is None:
        sent_data_since_index = []
    else:
        sent_data_since_index = sent_data[last_index_sent:]

    if recv_data is None:
        recv_data_since_index = []
    else:
        recv_data_since_index = recv_data[last_index_recv:]

    print '[-] Client refreshed'
    return jsonify({'sent': sent_data_since_index, 'recv': recv_data_since_index})

pubsub_obj.subscribe(**{'packet-data': message_handler})

subscriber_thread = Subscriber(sleep_time=1, daemon=True)
subscriber_thread.start()

try:
    app.run(port=Config.FLASK_PORT, debug=False)
except KeyboardInterrupt:
    subscriber_thread.stop()
