#!/usr/bin/env python

import socket
import time
import threading

from flask import Flask, render_template

from config import Config
from model import DataStorage

class ClientSocket(threading.Thread):
    def __init__(self, host, port, refresh_time):
        super(ClientSocket, self).__init__()
        print '[+] Client socket thread started'
        self.refresh_time = refresh_time
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((host, port))

    def run(self):
        while True:
            time.sleep(self.refresh_time)
            global sent_data
            global recv_data
            data_storage = DataStorage.decode(self.socket.recv(4096))
            sent_data, recv_data = data_storage.separate()
            print '[-] Update received'

socket_thread = ClientSocket(Config.HOST, Config.SOCKET_PORT, Config.REFRESH_TIME)
socket_thread.daemon = True
socket_thread.start()

sent_data = None
recv_data = None

app = Flask(__name__)

@app.route('/')
def chart():
    return render_template('chart.html', sent_data=sent_data, recv_data=recv_data)

try:
    app.run(port=Config.FLASK_PORT, debug=False)
except KeyboardInterrupt:
    socket_thread.socket.close()
