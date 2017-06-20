#!/usr/bin/env python

import socket
import time
import threading

from flask import Flask, render_template
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

app = Flask(__name__)

@app.route('/')
def chart():
    return render_template('chart.html', sent_data=sent_data, recv_data=recv_data)

sent_data = None
recv_data = None

pubsub_obj.subscribe(**{'packet-data': message_handler})

subscriber_thread = Subscriber(sleep_time=1, daemon=True)
subscriber_thread.start()

try:
    app.run(port=Config.FLASK_PORT, debug=False)
except KeyboardInterrupt:
    subscriber_thread.stop()
