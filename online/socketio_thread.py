import uuid

import socketio
from PySide2.QtCore import QThread, Signal


class SocketioThread(QThread):

    #ip = 'localhost'
    #ip = '192.168.178.200'
    ip ='42.0.185.233'
    port = '50000'
    receive_state_signal = Signal(dict)
    whoami_signal = Signal(str)

    def __init__(self, nickname=uuid.uuid4().__str__()):
        super().__init__()
        self.sio = socketio.Client()
        self.nickname = 'Jakub'

    def run(self):
        @self.sio.on('receivestate')
        def on_message(data):
            print("Received new state")
            print(data)
            self.receive_state_signal.emit(data)

        @self.sio.on('whoami')
        def on_message(data):
            self.whoami_signal.emit(data)

        @self.sio.event
        def connect():
            print("connected")
            self.sio.emit('setnickname', self.nickname)

        @self.sio.event
        def connect_error(data):
            print("connection failed")

        @self.sio.event
        def disconnect():
            print("disconnected")

        self.sio.connect(f'http://{self.ip}:{self.port}')

    def send_state(self, xml):
        if self.sio.connected:
            self.sio.emit('sendstate', xml)

    def start_game(self):
        if self.sio.connected:
            self.sio.emit('startgame')

    def who_am_i(self):
        if self.sio.connected:
            self.sio.emit('whoami')
