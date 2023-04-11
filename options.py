from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from player import Player

class OptionsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rummikub - Konfiguracja")
        self.resize(500, 300)
        icon = QIcon(":/joker/jok.png")
        self.setWindowIcon(icon)

        #self.setStyleSheet('background-image: url(":/backgr/wood3.jpg");')
        #self.setStyleSheet("background-color: navy; color: white;")
        vbox = QVBoxLayout()
        self.number_of_players_group_box = QGroupBox("Liczba graczy")
        self.one_player_radio_button = QRadioButton("1 gracz")
        self.one_player_radio_button.setChecked(True)
        self.two_players_radio_button = QRadioButton("2 graczy")
        self.three_players_radio_button = QRadioButton("3 graczy")
        self.four_players_radio_button = QRadioButton("4 graczy")
        self.ai_radio_button = QRadioButton("AI")
        vbox_number_of_players = QVBoxLayout()
        vbox_number_of_players.addWidget(self.one_player_radio_button)
        vbox_number_of_players.addWidget(self.two_players_radio_button)
        vbox_number_of_players.addWidget(self.three_players_radio_button)
        vbox_number_of_players.addWidget(self.four_players_radio_button)
        vbox_number_of_players.addWidget(self.ai_radio_button)
        self.number_of_players_group_box.setLayout(vbox_number_of_players)
        vbox.addWidget(self.number_of_players_group_box)

        self.players_group_box = QGroupBox("Nazwy graczy")
        hbox_players = QHBoxLayout()
        self.player1_line_edit = QLineEdit()
        self.player2_line_edit = QLineEdit()
        self.player3_line_edit = QLineEdit()
        self.player4_line_edit = QLineEdit()
        self.player1_line_edit.setEnabled(True)
        self.player2_line_edit.setEnabled(False)
        self.player3_line_edit.setEnabled(False)
        self.player4_line_edit.setEnabled(False)
        hbox_players.addWidget(QLabel("Gracz 1:"))
        hbox_players.addWidget(self.player1_line_edit)
        hbox_players.addWidget(QLabel("Gracz 2:"))
        hbox_players.addWidget(self.player2_line_edit)
        hbox_players.addWidget(QLabel("Gracz 3:"))
        hbox_players.addWidget(self.player3_line_edit)
        hbox_players.addWidget(QLabel("Gracz 4:"))
        hbox_players.addWidget(self.player4_line_edit)
        self.players_group_box.setLayout(hbox_players)
        vbox.addWidget(self.players_group_box)

        self.ip_and_port_group_box = QGroupBox("Adres IP i port")
        hbox_ip_and_port = QHBoxLayout()
        self.ip_line_edit = QLineEdit()
        ip_validator = QRegularExpressionValidator(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\:[0-9]{1,5}\b", self)
        self.ip_line_edit.setValidator(ip_validator)
        self.ip_line_edit.setPlaceholderText("Adres IP:port")
        hbox_ip_and_port.addWidget(QLabel("IP: "))
        hbox_ip_and_port.addWidget(self.ip_line_edit)
        self.ip_and_port_group_box.setLayout(hbox_ip_and_port)
        vbox.addWidget(self.ip_and_port_group_box)

        self.save_options_button = QPushButton("Zapisz opcje")
        vbox.addWidget(self.save_options_button)
        self.setLayout(vbox)
        self.save_options_button.clicked.connect(self.save_options)

        # Połącz sygnał zdarzenia zmiany stanu przycisków wyboru liczby graczy z metodą set_player_name_fields_enabled()
        self.one_player_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.two_players_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.three_players_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.four_players_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.ai_radio_button.toggled.connect(self.set_player_name_fields_enabled)

    def save_options(self):
        number_of_players = 0
        if self.one_player_radio_button.isChecked():
            number_of_players = 1
        elif self.two_players_radio_button.isChecked():
            number_of_players = 2
        elif self.ai_radio_button.isChecked():
            number_of_players = -1

        ip_and_port = self.ip_line_edit.text()

        options = {
            "number_of_players": number_of_players,
            "ip_and_port": ip_and_port,
        }
        # with open("options.json", "w") as f:
        #     json.dump(options, f)

        self.accept()

    def get_players(self):
        number_of_players = 0
        players = []
        if self.one_player_radio_button.isChecked():
            number_of_players = 1
            players = [Player(self.player1_line_edit.text() or "Player1")]
        elif self.two_players_radio_button.isChecked():
            number_of_players = 2
            players = [Player(self.player1_line_edit.text() or "Player1"), Player(self.player2_line_edit.text() or "Player2")]
        elif self.three_players_radio_button.isChecked():
            number_of_players = 3
            players = [Player(self.player1_line_edit.text() or "Player1"), Player(self.player2_line_edit.text() or "Player2"), Player(self.player3_line_edit.text() or "Player3")]
        elif self.four_players_radio_button.isChecked():
            number_of_players = 4
            players = [Player(self.player1_line_edit.text() or "Player1"), Player(self.player2_line_edit.text() or "Player2"), Player(self.player3_line_edit.text() or "Player3"), Player(self.player4_line_edit.text() or "Player4")]
        elif self.ai_radio_button.isChecked():
            number_of_players = -1
            players = [Player(self.player1_line_edit.text() or "Player1"), Player("AI")]

        return players

    def set_player_name_fields_enabled(self):
        # Ustaw stan aktywności pól do wprowadzania nazw graczy w zależności od wybranego przycisku wyboru liczby graczy
        if self.one_player_radio_button.isChecked():
            self.player1_line_edit.setEnabled(True)
            self.player2_line_edit.setEnabled(False)
            self.player3_line_edit.setEnabled(False)
            self.player4_line_edit.setEnabled(False)
        elif self.two_players_radio_button.isChecked():
            self.player1_line_edit.setEnabled(True)
            self.player2_line_edit.setEnabled(True)
            self.player3_line_edit.setEnabled(False)
            self.player4_line_edit.setEnabled(False)
        elif self.three_players_radio_button.isChecked():
            self.player1_line_edit.setEnabled(True)
            self.player2_line_edit.setEnabled(True)
            self.player3_line_edit.setEnabled(True)
            self.player4_line_edit.setEnabled(False)
        elif self.four_players_radio_button.isChecked():
            self.player1_line_edit.setEnabled(True)
            self.player2_line_edit.setEnabled(True)
            self.player3_line_edit.setEnabled(True)
            self.player4_line_edit.setEnabled(True)
        elif self.ai_radio_button.isChecked():
            self.player1_line_edit.setEnabled(True)
            self.player2_line_edit.setEnabled(False)
            self.player3_line_edit.setEnabled(False)
            self.player4_line_edit.setEnabled(False)