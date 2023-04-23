import json
import sys

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel

from socketio_thread import SocketioThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.state = ''
        self.setWindowTitle('PySide6 Window')
        self.socket = SocketioThread()
        self.socket.receive_state_signal.connect(self.state_received)
        self.socket.whoami_signal.connect(self.whoami_received)
        self.socket.run()

        # Create widgets
        self.label1 = QLabel()
        self.textbox1 = QTextEdit()
        self.button1 = QPushButton('Start Game')
        self.button1.pressed.connect(lambda: self.socket.start_game())
        self.button2 = QPushButton('Send State')
        self.button2.pressed.connect(lambda: self.socket.send_state(self.state))

        # Create layout
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.label1)
        vbox1.addWidget(self.textbox1)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.button1)
        hbox1.addWidget(self.button2)

        vbox1.addLayout(hbox1)

        self.socket.who_am_i()

        self.setLayout(vbox1)

    def state_received(self, state):
        self.state = state['xml']
        self.textbox1.setText(json.dumps(state, indent=4))

    def whoami_received(self, data):
        self.label1.setText(str(data))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
