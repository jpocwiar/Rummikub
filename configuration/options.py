from PySide2.QtWidgets import *
from PySide2.QtGui import *
from mechanics.player import Player
import json
import os


class OptionsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rummikub - Configuration")
        self.resize(500, 300)
        icon = QIcon(":/joker/jok.png")
        self.setWindowIcon(icon)

        #self.setStyleSheet('background-image: url(":/backgr/wood3.jpg");')
        #self.setStyleSheet("background-color: navy; color: white;")
        vbox = QVBoxLayout()

        # Create a QHBoxLayout for the "Liczba graczy" group box
        hbox_number_of_players = QHBoxLayout()
        self.number_of_players_group_box = QGroupBox("Number of players")
        self.one_player_radio_button = QRadioButton("1 Player")
        self.one_player_radio_button.setChecked(True)
        self.two_players_radio_button = QRadioButton("2 Players")
        self.three_players_radio_button = QRadioButton("3 Players")
        self.four_players_radio_button = QRadioButton("4 Players")
        self.ai_radio_button = QRadioButton("AI")
        self.ai_radio_multiple_button = QRadioButton("AI - 4 Players")
        self.online_radio_button = QRadioButton("Online")
        vbox_number_of_players = QVBoxLayout()
        vbox_number_of_players.addWidget(self.one_player_radio_button)
        vbox_number_of_players.addWidget(self.two_players_radio_button)
        vbox_number_of_players.addWidget(self.three_players_radio_button)
        vbox_number_of_players.addWidget(self.four_players_radio_button)
        vbox_number_of_players.addWidget(self.ai_radio_button)
        vbox_number_of_players.addWidget(self.ai_radio_multiple_button)
        vbox_number_of_players.addWidget(self.online_radio_button)
        self.number_of_players_group_box.setLayout(vbox_number_of_players)
        self.number_of_players_group_box.setMaximumWidth(self.width() / 2)
        hbox_number_of_players.addWidget(self.number_of_players_group_box)

        vbox_replay = QVBoxLayout()
        self.replay_group_box = QGroupBox("Load data")
        self.replay_button = QPushButton("Recreate previous game using DB")
        vbox_replay.addWidget(self.replay_button)
        self.replay_button.clicked.connect(self.replay_game)
        self.replay_buttonXML = QPushButton("Recreate previous game using XML")
        vbox_replay.addWidget(self.replay_buttonXML)
        self.replay_buttonXML.clicked.connect(self.replay_gameXML)
        self.load_options_button = QPushButton("Load options")
        vbox_replay.addWidget(self.load_options_button)
        self.load_options_button.clicked.connect(self.load_options_from_file)
        self.replay_group_box.setLayout(vbox_replay)
        self.replay_group_box.setMaximumWidth(self.width() / 2)
        hbox_number_of_players.addWidget(self.replay_group_box)

        vbox.addLayout(hbox_number_of_players)

        self.players_group_box = QGroupBox("Players names")
        hbox_players = QHBoxLayout()
        self.player1_line_edit = QLineEdit()
        self.player2_line_edit = QLineEdit()
        self.player3_line_edit = QLineEdit()
        self.player4_line_edit = QLineEdit()
        self.player1_line_edit.setEnabled(True)
        self.player2_line_edit.setEnabled(False)
        self.player3_line_edit.setEnabled(False)
        self.player4_line_edit.setEnabled(False)
        hbox_players.addWidget(QLabel("Player 1:"))
        hbox_players.addWidget(self.player1_line_edit)
        hbox_players.addWidget(QLabel("Player 2:"))
        hbox_players.addWidget(self.player2_line_edit)
        hbox_players.addWidget(QLabel("Player 3:"))
        hbox_players.addWidget(self.player3_line_edit)
        hbox_players.addWidget(QLabel("Player 4:"))
        hbox_players.addWidget(self.player4_line_edit)
        self.players_group_box.setLayout(hbox_players)

        vbox.addWidget(self.players_group_box)

        self.ip_and_port_group_box = QGroupBox("IP Address and port")
        hbox_ip_and_port = QHBoxLayout()
        self.ip_line_edit = QLineEdit()
        self.port_line_edit = QLineEdit()
        #ip_validator = QRegularExpressionValidator(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", self)
        #self.ip_line_edit.setInputMask("000.000.000.000/00;_")
        self.ip_line_edit.setInputMask("000.000.000.000;_")
        self.port_line_edit.setInputMask("00000;_")

        self.ip_line_edit.setPlaceholderText("IP address")
        self.port_line_edit.setPlaceholderText("Port")
        hbox_ip_and_port.addWidget(QLabel("IP: "))
        hbox_ip_and_port.addWidget(self.ip_line_edit)
        hbox_ip_and_port.addWidget(QLabel("Port: "))
        hbox_ip_and_port.addWidget(self.port_line_edit)
        self.ip_and_port_group_box.setLayout(hbox_ip_and_port)
        vbox.addWidget(self.ip_and_port_group_box)
        #
        # self.replay_button = QPushButton("Odtwórz grę")
        # vbox.addWidget(self.replay_button)
        # self.replay_button.clicked.connect(self.replay_game)

        self.save_options_button = QPushButton("Save options and play")
        vbox.addWidget(self.save_options_button)
        self.setLayout(vbox)
        self.save_options_button.clicked.connect(self.save_options)

        self.replay = 0

        self.one_player_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.two_players_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.three_players_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.four_players_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.ai_radio_button.toggled.connect(self.set_player_name_fields_enabled)
        self.ai_radio_multiple_button.toggled.connect(self.set_player_name_fields_enabled)
        self.online_radio_button.toggled.connect(self.set_player_name_fields_enabled)

        self.load_options()

    def load_file(self):

        file_path, _ = QFileDialog.getOpenFileName(None, "Select file to load", "", "Database (*.db);;XML (*.xml)")

        if file_path:
            if file_path.endswith('.db'):
                self.replay_game(file_path)
            elif file_path.endswith('.xml'):
                self.replay_gameXML(file_path)


    def replay_game(self):
        if not os.path.exists('history.db'):
            QMessageBox.critical(self, 'Error', 'No history.db file.')
            return
        self.replay = 1
        self.load_options()
        self.accept()

    def replay_gameXML(self):
        if not os.path.exists('history.xml'):
            QMessageBox.critical(self, 'Error', 'No history.xml file.')
            return
        self.replay = 2
        self.load_options()
        self.accept()

    def get_button_pressed(self):
        return self.replay

    def save_options(self):
        self.replay = 0
        player1_name = ""
        player2_name = ""
        player3_name = ""
        player4_name = ""
        if self.one_player_radio_button.isChecked():
            mode = 1
            player1_name = self.player1_line_edit.text() or "Player1"
        elif self.two_players_radio_button.isChecked():
            mode = 2
            player1_name = self.player1_line_edit.text() or "Player1"
            player2_name = self.player2_line_edit.text() or "Player2"
        elif self.three_players_radio_button.isChecked():
            mode = 3
            player1_name = self.player1_line_edit.text() or "Player1"
            player2_name = self.player2_line_edit.text() or "Player2"
            player3_name = self.player3_line_edit.text() or "Player3"
        elif self.four_players_radio_button.isChecked():
            mode = 4
            player1_name = self.player1_line_edit.text() or "Player1"
            player2_name = self.player2_line_edit.text() or "Player2"
            player3_name = self.player3_line_edit.text() or "Player3"
            player4_name = self.player4_line_edit.text() or "Player4"
        elif self.ai_radio_button.isChecked():
            mode = "AI"
            player1_name = self.player1_line_edit.text() or "Player1"
        elif self.ai_radio_multiple_button.isChecked():
            mode = "AI multiple"
            player1_name = self.player1_line_edit.text() or "Player1"
        elif self.online_radio_button.isChecked():
            mode = "online"
            player1_name = self.player1_line_edit.text() or "Player1"

        ip = self.ip_line_edit.text()
        # ip_with_mask = self.ip_line_edit.text()
        # ip, mask = ip_with_mask.split("/")
        port = self.port_line_edit.text()


        options = {
            "mode": mode,
            "ip": ip,
            #"mask": mask,
            "port": port,
            "player1_name": player1_name,
            "player2_name": player2_name,
            "player3_name" : player3_name,
            "player4_name" : player4_name,
        }
        with open("options.json", "w") as f:
             json.dump(options, f)

        self.accept()

    def load_options_from_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Choose options file", "", "JSON files (*.json)")
        self.load_options(file)

    def load_options(self, file="options.json"):
        try:
            with open(file, "r") as f:
                options = json.load(f)

                mode = options["mode"]
                if mode == 1:
                    self.one_player_radio_button.setChecked(True)
                elif mode == 2:
                    self.two_players_radio_button.setChecked(True)
                elif mode == 3:
                    self.three_players_radio_button.setChecked(True)
                elif mode == 4:
                    self.four_players_radio_button.setChecked(True)
                elif mode == "AI":
                    self.ai_radio_button.setChecked(True)
                elif mode == "AI multiple":
                    self.ai_radio_multiple_button.setChecked(True)
                elif mode == "online":
                    self.online_radio_button.setChecked(True)

                ip = options["ip"]
                #mask = options["mask"]
                port = options["port"]
                #self.ip_line_edit.setText(f"{ip}/{mask}")
                self.ip_line_edit.setText(ip)
                self.port_line_edit.setText(port)

                self.player1_line_edit.setText(options.get("player1_name", ""))
                self.player2_line_edit.setText(options.get("player2_name", ""))
                self.player3_line_edit.setText(options.get("player3_name", ""))
                self.player4_line_edit.setText(options.get("player4_name", ""))

                self.set_player_name_fields_enabled()
        except FileNotFoundError:
            pass

    def get_players(self):
        players = []
        if self.one_player_radio_button.isChecked():
            players = [Player(self.player1_line_edit.text() or "Player1")]
        elif self.two_players_radio_button.isChecked():
            players = [Player(self.player1_line_edit.text() or "Player1"), Player(self.player2_line_edit.text() or "Player2")]
        elif self.three_players_radio_button.isChecked():
            players = [Player(self.player1_line_edit.text() or "Player1"), Player(self.player2_line_edit.text() or "Player2"), Player(self.player3_line_edit.text() or "Player3")]
        elif self.four_players_radio_button.isChecked():
            players = [Player(self.player1_line_edit.text() or "Player1"), Player(self.player2_line_edit.text() or "Player2"), Player(self.player3_line_edit.text() or "Player3"), Player(self.player4_line_edit.text() or "Player4")]
        elif self.ai_radio_button.isChecked():
            players = [Player(self.player1_line_edit.text() or "Player1"), Player("AI", True)]
        elif self.ai_radio_multiple_button.isChecked():
            players = [Player(self.player1_line_edit.text() or "Player1"), Player("AI", True), Player("AI2", True), Player("AI3", True)]
        elif self.online_radio_button.isChecked():
            players = [Player(self.player1_line_edit.text() or "Player1"), Player("Player2"), Player("Player3")]

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
        elif self.ai_radio_button.isChecked() or self.ai_radio_multiple_button.isChecked():
            self.player1_line_edit.setEnabled(True)
            self.player2_line_edit.setEnabled(False)
            self.player3_line_edit.setEnabled(False)
            self.player4_line_edit.setEnabled(False)
        elif self.online_radio_button.isChecked():
            self.player1_line_edit.setEnabled(True)
            self.player2_line_edit.setEnabled(False)
            self.player3_line_edit.setEnabled(False)
            self.player4_line_edit.setEnabled(False)

    def get_selected_radio_button(self):
        if self.one_player_radio_button.isChecked():
            return "1 Player"
        elif self.two_players_radio_button.isChecked():
            return "2 Players"
        elif self.three_players_radio_button.isChecked():
            return "3 Players"
        elif self.four_players_radio_button.isChecked():
            return "4 Players"
        elif self.ai_radio_button.isChecked():
            return "AI"
        elif self.ai_radio_multiple_button.isChecked():
            return "AI multiple"
        elif self.online_radio_button.isChecked():
            return "Online"