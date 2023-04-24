from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import random
import numpy as np
import graphics_rc
from timer import Timer
from tile import Tile
from player import Player
from desk import ForegroundItem
from logger import Logger
from options import OptionsDialog
from database import DatabaseSQL, DatabaseXML
import socket
import threading
import select
import sys
import time
import os
import json
import xml.etree.ElementTree as ET

from socketio_thread import SocketioThread

class BoardOnline(QGraphicsScene):
    def __init__(self, view, players, ip, port, save_data = False, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1800, 1000)


        self.current_sid = 0
        self.sid = 0
        self.my_index = 0
        self.ip_address = ip
        self.port = port
        self.socket = SocketioThread()
        self.socket.receive_state_signal.connect(self.state_received)
        self.socket.whoami_signal.connect(self.whoami_received)
        self.socket.run()
        self.socket.who_am_i()
        self.beginning = True
        self.first_move = True
        try:
            background_image = QImage(":/backgr/wood3.jpg")
            background_brush = QBrush(
                background_image.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            self.setBackgroundBrush(background_brush)
        except:
            self.setBackgroundBrush(QBrush(QColor(238, 238, 238)))
        self.tiles = []
        self.my_tiles = []
        self.my_tiles_prev = []
        self.move_number = 0
        #self.user_tiles = []
        self.selected_tiles = []
        self.board = np.full((15, 40), None, dtype=object)
        self.board_prev = self.board.copy()
        self.groups = []
        #self.colours = [Qt.red, Qt.blue, Qt.darkYellow, Qt.black]
        self.colours = ["red", "blue", "yellow", "black"]
        self.players = players
        self.current_player_index = 0
        self.is_my_turn = False
        self.red_rects = []

        self.tile_width = Tile.width
        self.tile_height = Tile.height
        self.foreground_item = ForegroundItem(self.tile_width * 20, self.tile_height * 2)
        self.foreground_item.setPos(self.sceneRect().width() / 2 - self.tile_width * 20 / 2, int(round((self.sceneRect().height() - self.tile_height * 2)/self.tile_height))*self.tile_height)
        self.addItem(self.foreground_item)

        self.selection_rect = None
        self.selection_start_pos = None
        self.mouse_offsets = []

        self.snap_rect = None

        self.button = QPushButton('Draw Tile', view)
        self.button.setGeometry(1600, 500, 90, 30)
        self.button.clicked.connect(self.draw_tile)

        self.sort_by_color_button = QPushButton('Sort by Color', view)
        self.sort_by_color_button.setGeometry(1600, 40, 120, 30)
        self.sort_by_color_button.clicked.connect(
        self.sort_tiles_by_color)

        self.accept_move = QPushButton('Accept move', view)
        self.accept_move.setGeometry(1600, 540, 120, 30)
        self.accept_move.clicked.connect(self.make_move)

        self.button1 = QPushButton('Start Game', view)
        self.button1.setGeometry(1600, 570, 120, 30)
        self.button1.pressed.connect(lambda: self.socket.start_game())

        self.sort_by_number_button = QPushButton('Sort by Number', view)
        self.sort_by_number_button.setGeometry(1600, 70, 120, 30)
        self.sort_by_number_button.clicked.connect(
        self.sort_tiles_by_number)

        self.logger = Logger(view)
        self.logger.setGeometry(1430, 870, 350, 100)

        self.chat_output = QTextEdit(view)
        self.chat_output.setGeometry(1430, 600, 400, 180)

        self.chat_input = QLineEdit(view)
        self.chat_input.setGeometry(1430, 780, 300, 30)

        self.send_button = QPushButton("Wyślij", view)
        self.send_button.setGeometry(1740, 780, 90, 30)
        self.send_button.clicked.connect(self.send_message)

        self.save_data = save_data
        if save_data:
            self.database = DatabaseSQL(len(self.players))
            self.databaseXML = DatabaseXML(len(self.players))
        #self.database.init_db()

        #self.generate_tiles()
        #self.save_to_db()
        #self.logger.log('Początek gry')
        #umieszczenie kafelków gracza
        for i, tile in enumerate(self.my_tiles):
            tile.setPos(self.foreground_item.pos() + QPointF(
                (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
            self.addItem(tile)

        self.timed_out = False
        self.timer = Timer(self)
        self.addItem(self.timer)
        self.timer.setPos(1550, 200)

        self.timer_timer = QTimer()
        self.timer_timer.timeout.connect(self.update_timer)
        if True:
            self.timer_timer.start(5)

        #umieszczenie nazw graczy
        self.player_name_items = []
        y = 800
        for i, player in enumerate(self.players):
            name_item = QGraphicsTextItem(player.name)
            name_item.setFont(QFont("Arial", 16, QFont.Bold))
            name_item.setDefaultTextColor(QColor(235, 235, 235))
            if i == self.current_sid:
                name_item.setDefaultTextColor(QColor(255, 100, 100))
            self.addItem(name_item)
            name_item.setPos(50, y)
            self.player_name_items.append(name_item)
            y += 30

        self.tiles_number_item = QGraphicsTextItem("Tiles to draw: " + str(len(self.tiles)))
        self.tiles_number_item.setFont(QFont("Arial", 16, QFont.Bold))
        self.tiles_number_item.setDefaultTextColor(QColor(235, 235, 235))
        self.addItem(self.tiles_number_item)
        self.tiles_number_item.setPos(1500, 810)

        self.notification_item = QGraphicsTextItem("Czekanie na dołączenie użytkownika...")
        self.notification_item.setFont(QFont("Arial", 16, QFont.Bold))
        self.notification_item.setDefaultTextColor(QColor(235, 235, 235))
        self.addItem(self.notification_item)
        self.notification_item.setPos(10, 10)



    def read_xml(self, xml_string):
        #print("wlazlem")
        self.clear()
        colors = ['black','black','blue','yellow','red']

        root = ET.fromstring(xml_string)

        # board_elem = root.find(f'turn')
        # board_tiles = board_elem.findall('tile')

        for i in range(3):
            self.player_name_items[i].setPlainText(self.state['players'][i])
            self.player_name_items[i].setDefaultTextColor(QColor(255, 255, 255))
        for i, sid in enumerate(self.state['sids']):
            if sid == self.current_sid:
                self.player_name_items[i].setDefaultTextColor(QColor(255, 100, 100))

        for container in root.findall('./board/container'):
            container_values = container.text.split(',')
            index = int(container_values[0])
            colo = int(container_values[1])
            val = int(container_values[2])
            if int(val) == 0:
                tile = Tile(colors[colo], int(val), is_joker=True)
            else:
                tile = Tile(colors[colo], int(val))
            #print(tile)
            row = int(index / 24)
            col = int(index % 24)
            self.board[row,col] = tile

            tile.setPosFromIndices(row, col)
            self.addItem(tile)
        self.board_prev = self.board.copy()
        #print(self.board)
        if self.beginning:
            self.my_tiles = []
            #me = root.findall("player")[0]
            me = root.findall("player")[self.my_index]
            tiles = me.findall("tile")

            for i,tile in enumerate(tiles):
                values = tile.text.split(',')
                colo = values[0]
                #print(colo)
                value = values[1]
                #print(value)
                if int(value) == 0:
                    tile = Tile(colors[int(colo)], int(value), is_joker=True)
                else:
                    tile = Tile(colors[int(colo)], int(value))
                self.my_tiles.append(tile)
                tile.setPos(self.foreground_item.pos() + QPointF(
                    (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
                self.addItem(tile)
        draw_elem = root.find(f'bag')
        draw_tiles = draw_elem.findall('tile')
        self.tiles = []
        for tile_elem in draw_tiles:
            #print('dodajdddde')
            values = tile_elem.text.split(',')
            colo = values[0]
            value = int(values[1])

            if value == 0:
                tile = Tile(colors[int(colo)], int(value), is_joker=True)
            else:
                tile = Tile(colors[int(colo)], int(value))
            self.tiles.append(tile)
            self.tiles_number_item.setPlainText("Tiles to draw: " + str(len(self.tiles)))

        if self.beginning:
            self.beginning = False
            self.my_tiles_prev = self.my_tiles.copy()
            #print(self.my_tiles_prev)

        self.refresh_board()
        #print("aaa")

    def create_xml(self):
        xml_string = self.state['xml']
        tree = ET.ElementTree(ET.fromstring(xml_string))
        turn_root = tree.getroot()
        turn_root[0].clear()
        colors = {'None':0, 'black':1, 'blue':2, 'yellow':3, 'red':4}
        # bag
        bag_element = ET.SubElement(turn_root, 'bag')
        for tile in self.tiles:
            tile_element = ET.SubElement(turn_root[0], 'tile')
            if tile.is_joker:
                tile_element.text = f'{0},{0}'
            else:
                tile_element.text = f'{colors[tile.colour]},{tile.numer}'
        turn_root[1].clear()
        # board
        board_element = ET.SubElement(turn_root, 'board')
        indices = np.where(self.board != None)
        #print("aaa" + str(self.board))
        for i in range(indices[0].size):
            tile = self.board[indices[0][i], indices[1][i]]
            tile_element = ET.SubElement(turn_root[1], 'container')
            index = indices[0][i] * 24 + indices[1][i]
            if tile.is_joker:
                tile_element.text = f'{index},{0},{0}'
            else:
                tile_element.text = f'{index},{colors[tile.colour]},{tile.numer}'
            # tile_elem = ET.SubElement(board_element, 'tile',
            #                           {'number': str(tile.numer), 'color': tile.colour, 'row': str(indices[0][i]),
            #                            'col': str(indices[1][i])})
        # players
        #for player in players:
        turn_root[2 + self.my_index].clear()
        #player_element = ET.SubElement(turn_root, 'player')
        if self.first_move:
            turn_root[2 + self.my_index].set('first_move', str(True))
        else:
            turn_root[2 + self.my_index].set('first_move', str(False))
        for tile in self.my_tiles:
            tile_element = ET.SubElement(turn_root[2 + self.my_index], 'tile')
            if tile.is_joker:
                tile_element.text = f'{0},{0}'
            else:
                tile_element.text = f'{colors[tile.colour]},{tile.numer}'
        #root2 = ET.fromstring(self.state['xml'])
        print(self.state['xml'])
        # player2 = root2.findall('.//player')[1]
        # new_player = ET.SubElement(root2, 'player', first_move=player.get('first_move'))
        # new_player.text = '\n'
        # for tile in player.findall('.//tile'):
        #     new_tile = ET.SubElement(new_player, 'tile')
        #     new_tile.text = tile.text
        #     new_tile.tail = '\n'
        # new_player.tail = '\n'
        # for player in root2.findall('player')[1:]:
        #     new_player = ET.SubElement(turn_root, 'player')
        #     new_player.set('first_move', player.get('first_move'))
        #     for tile in player.findall('tile'):
        #         new_tile = ET.SubElement(new_player, 'tile')
        #         new_tile.text = tile.text

        tree = ET.ElementTree(turn_root)
        xml_string = ET.tostring(tree.getroot()).decode()
        return xml_string

    def clear(self):
        for item in self.items():
            if isinstance(item, Tile) and item in self.board:
                self.removeItem(item)

    def send_message(self):
        message = self.chat_input.text()
        print(message)
        if message == 'q':
            self.server_socket.sendall(message.encode())
            self.server_socket.close()
            sys.exit()
        elif message:
            self.server_socket.sendall(message.encode('utf-8'))
            self.server_socket.sendall(message.encode())
            # self.message_history.setAlignment(Qt.AlignRight)
            # self.message_history.append(message)

        self.chat_input.clear()

    def handle_server(self):
        while True:
            try:
                ready_to_read, _, _ = select.select([self.server_socket], [], [], 0.1)
                if self.server_socket in ready_to_read:
                    data = self.server_socket.recv(1024)
                    if not data:
                        break
                    elif data.startswith(b'SIZE'):
                        filesize = int(data[5:])
                        filename = f"received_{int(time.time())}.docx"
                        with open(filename, 'wb') as f:
                            data = self.server_socket.recv(1024)
                            total_recv = len(data)
                            f.write(data)
                            while total_recv < filesize:
                                data = self.server_socket.recv(1024)
                                total_recv += len(data)
                                f.write(data)

                        self.chat_output.append(f'File {filename} received')
                    else:
                        message = data.decode('utf-8')
                        self.chat_output.append(message.replace("\r", ""))
            except:
                break

        self.server_socket.close()
        sys.exit()

    def state_received(self, state):
        self.state = state
        self.current_sid = str(self.state['current_player']['sid'])
        self.my_index = self.state['sids'].index(self.sid)
        self.chat_output.setText(json.dumps(state, indent=4))
        print(self.state['xml'])
        if self.state['xml'] != "":
            self.read_xml(self.state['xml'])

    def whoami_received(self, data):
        self.notification_item.setPlainText(str(data))
        self.sid = str(data)

    def update_timer(self):
        if self.sid == self.current_sid:
            self.timer.update_time()
        else:
            self.restart_timer()

    def restart_timer(self):
        self.timer.time_left = 30000
        self.timer.update()
        self.timed_out = False

    def save_to_db(self):
        if self.save_data:
            player = self.players[self.current_player_index]
            self.database.save_to_db(self.current_player_index, self.board, player.tiles,self.tiles, self.move_number)
            self.databaseXML.save_to_db(self.current_player_index, self.board, player.tiles, self.tiles, self.move_number)
            self.move_number += 1

    def switch_player(self):
        # przejdź do następnego gracza
        # for tile in self.my_tiles:
        #     self.removeItem(tile)
        #self.player_name_items[self.current_sid].setDefaultTextColor(QColor(235, 235, 235))
        #zapisanie ruchu do database
        self.save_to_db()
        # zmiana indeksu
        #self.current_player_index = (self.current_player_index + 1) % len(self.players)
        # zapisanie do database stanu sprzed ruchu
        self.save_to_db()
        self.tiles_number_item.setPlainText("Tiles to draw: " + str(len(self.tiles)))
        # Dodanie klocków następnego gracza
        # for i, tile in enumerate(self.my_tiles):
        #     tile.setPos(self.foreground_item.pos() + QPointF(
        #         (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
        #     self.addItem(tile)
        for i in range(3):
            self.player_name_items[i].setPlainText(self.state['players'][i])
        for i, sid in enumerate(self.state['sids']):
            if sid == self.current_sid:
                self.player_name_items[i].setDefaultTextColor(QColor(255, 100, 100))

        self.state['xml'] = self.create_xml()
        #self.state = self.create_xml()
        #print("xml: " + self.state['xml'])
        #self.socket.send_state(self.state['xml'])
        #print(self.board)
        self.socket.send_state(self.create_xml())
        self.restart_timer()

    def make_move(self):
        if self.first_move:

            own_board = np.where(self.board == self.board_prev, None, self.board)
            mask = np.where(own_board != None)
            own_tiles = own_board[mask]
            sum_of_tiles = 0
            if len(own_tiles) >=3:
                for i, tile in enumerate(own_tiles):
                    sum_of_tiles+=tile.numer
                    if tile.is_joker:
                        if i>0 and i<len(own_tiles)-1 and mask[1][i]==mask[1][i-1]+1 and mask[1][i] == mask[1][i+1]-1: #czy joker jest pomiędzy dwoma innymi elementami
                            if own_tiles[i-1].is_joker:
                                sum_of_tiles += own_tiles[i+1].numer
                            elif own_tiles[i+1].is_joker:
                                sum_of_tiles += own_tiles[i - 1].numer
                            else:
                                sum_of_tiles+= int((own_tiles[i-1].numer+own_tiles[i+1].numer)/2)
                        elif i==0 or mask[1][i]!=mask[1][i-1]+1: # gdy joker jest na lewym skraju
                            try:
                                if own_tiles[i+1].is_joker:
                                    sum_of_tiles+= own_tiles[i+2].numer
                                elif own_tiles[i+2].is_joker:
                                    sum_of_tiles+= own_tiles[i+1].numer
                                else:
                                    sum_of_tiles+= own_tiles[i+1].numer-(own_tiles[i+2].numer - own_tiles[i+1].numer)
                            except:
                                pass
                        elif i==len(own_tiles)-1 or mask[1][i]!=mask[1][i+1]-1: #jeśli joker na końcu serii
                            try:
                                if own_tiles[i - 1].is_joker:
                                    sum_of_tiles+= own_tiles[i-2].numer
                                elif own_tiles[i-2].is_joker:
                                    sum_of_tiles+= own_tiles[i-1].numer
                                else:
                                    sum_of_tiles+= own_tiles[i-1].numer-(own_tiles[i-2].numer - own_tiles[i-1].numer)
                            except:
                                pass



            if len(self.my_tiles) == len(
                    self.my_tiles_prev) and not self.timed_out:
                #print("Musisz wykonać ruch!")
                self.logger.error(str(self.players[0].name) + " nie wykonał pierwszego ruchu!")
            elif self.check_move(own_board) and not len(self.my_tiles) == len(
                    self.my_tiles_prev) and sum_of_tiles >=30:
                #print("ruch prawidłowy")
                self.logger.log(
                    str(self.players[0].name) + " położył kombinację o wartości " + str(
                        sum_of_tiles))
                self.board_prev = self.board.copy()
                self.my_tiles_prev = self.my_tiles.copy()

                self.first_move = False #już nie pierwszy ruch
                self.switch_player()
            elif self.check_move(own_board) and not len(self.my_tiles) == len(
                    self.my_tiles_prev) and sum_of_tiles < 30 and not self.timed_out:
                self.logger.error(
                    self.players[0].name + " położył pierwszą kombinację o wartości " + str(
                        sum_of_tiles) + ". Przy pierwszym ruchu konieczne jest wyłożenie klocków o łącznej wartości >=30!")
            elif self.timed_out and (not self.check_move(own_board) or (
                    len(self.my_tiles) == len(
                    self.my_tiles_prev)) or sum_of_tiles < 30):
                self.logger.error(
                    self.players[0].name + " nie wykonał poprawnego pierwszego ruchu i czas się skończył!")

                self.draw_tile()
            elif not self.check_move(own_board) and not self.timed_out:
                self.logger.error(
                    self.players[0].name + " nie wykonał poprawnego pierwszego ruchu!")
        else:
            if len(self.my_tiles) == len(self.my_tiles_prev) and not self.timed_out:
                #print("Musisz wykonać ruch!")
                self.logger.error(str(self.players[0].name) + " nie wykonał ruchu!")
            elif self.check_move(self.board) and not len(self.my_tiles) == len(self.my_tiles_prev):
                #print("ruch prawidłowy")
                self.logger.log(
                    str(self.players[0].name) + " wykonał prawidłowy ruch i zostało mu " + str(
                        len(self.my_tiles)) + " klocków")
                if len(self.my_tiles) == 0:
                    self.logger.log("Wygrywa " + str(self.players[0].name) + "!")
                    self.save_to_db()
                    msg_box = QMessageBox()
                    msg_box.setText("Wygrywa " + str(self.players[0].name) + "!")
                    msg_box.setWindowTitle("Message Box")
                    msg_box.setStandardButtons(QMessageBox.Ok)

                    response = msg_box.exec_()
                    sys.exit()
                self.board_prev = self.board.copy()
                self.my_tiles_prev = self.my_tiles.copy()
                self.switch_player()
            #elif (not self.check_move() and self.timed_out) or (sorted(self.my_tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour)) == sorted(self.my_tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour)))) and self.timed_out): #przy pierwszym ruchu może robić jakby osobny board? Zęby to 30 sprawdzać
            elif (not self.check_move(self.board) and self.timed_out) or (len(self.my_tiles) == len(self.my_tiles_prev) and self.timed_out):
                #przywróć stan poprzedni i przejdź do następnego gracza
                #print("ruch nieprawidłowy i czas minął!")
                self.logger.error(
                    self.players[0].name + " nie wykonał poprawnego ruchu i czas się skończył!")
                self.draw_tile()
            elif not self.check_move(self.board) and not self.timed_out:
                self.logger.error(str(self.players[0].name) + " - ruch nieprawidłowy!")


    def check_move(self,board):
        if self.is_every_element_grouped(board):
            #print("youp")
            for group in self.groups:
                non_joker = np.sum([not til.is_joker for til in group])
                #print(non_joker)
                if(non_joker <= 1):
                    self.logger.log(str(self.players[0].name) + "- kombinacja z dominacją jokerów")
                    #pass
                else:
                    colors = set(str(til.colour) for til in group if not til.is_joker)
                    color_count = len(colors)
                    #print("kolory: " + str(color_count))
                    if color_count == 1:
                        unique_values = set(til.numer - idx for idx, til in enumerate(group) if not til.is_joker)
                        if len(unique_values) == 1 and not unique_values == {0} and not next(iter(unique_values)) + len(group) - 1 >= 14:
                            #print(unique_values)
                            #print("po kolei")
                            # self.logger.log(
                            #     str(self.players[0).name + "- kombinacja jeden kolor, po kolei")
                            pass
                        else:
                            #print("nie po kolei")
                            # self.logger.error(
                            #     str(self.players[
                            #             self.current_player_index].name) + "- kombinacja nie po kolei")
                            return False
                    elif color_count == non_joker and len(group) <= 4:
                        values = set(til.numer for til in group if not til.is_joker)
                        if len(values) == 1:
                            pass
                            #print("te same cyfr")
                            # self.logger.log(
                            #     str(self.players[
                            #             self.current_player_index].name) + " - kombinacja tych samych cyfr")
                        else:
                            #print("źle")
                            return False
                    else:
                        #print("źle")
                        return False
            return True
        else:
            #print("Za mało klocków")
            # self.logger.log(
            #     str(self.players[0).name + "- za mało klocków w kombinacji")
            #msg_box = QMessageBox()
            #msg_box.setText("Układ musi zawierać co najmniej 3 klocki!")
            #msg_box.setWindowTitle("Message Box")
            #msg_box.setStandardButtons(QMessageBox.Ok)

            #response = msg_box.exec_()
            return False

    def is_every_element_grouped(self, board):
        # board = self.board
        non_none_indices = np.where(board != None)
        counter = 0
        self.groups = []
        if non_none_indices[0].size < 3:
            return False
        for i in range(non_none_indices[0].size):

            if counter == 0:
                counter += 1
                group = [board[non_none_indices[0][i], non_none_indices[1][i]]]
            elif non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1:  # sprawdzanie czy obok siebie
                counter += 1
                group.append(board[non_none_indices[0][i], non_none_indices[1][i]])
                if i == non_none_indices[0].size - 1 and counter >= 3:
                    self.groups.append(group)

            elif (not (non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1) or i == non_none_indices[
                0].size) and counter < 3:
                return False
            elif not (non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1) and counter >= 3:
                counter = 1
                self.groups.append(group)
                group = [board[non_none_indices[0][i], non_none_indices[1][i]]]
                # print("bbbb")

            y = non_none_indices[0][i]
            x = non_none_indices[1][i]
        if counter < 3:
            return False
        # print(len(self.groups))
        return True

    def sort_tiles_by_color(self):
        colors = self.colours
        #self.user_tiles = sorted(self.user_tiles, key=lambda tile: colors.index(tile.colour))
        self.my_tiles = sorted(self.my_tiles, key=lambda tile: colors.index(tile.colour))

        for index, tile in enumerate(self.my_tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.tile_width,
                                                             int(index / 20) * self.tile_height))

    def sort_tiles_by_number(self):
        self.my_tiles = sorted(self.my_tiles, key=lambda tile: tile.numer)

        for index, tile in enumerate(self.my_tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.tile_width,
                                                             int(index / 20) * self.tile_height))

    def draw_tile(self):
        if len(self.tiles) > 0:
            self.board = self.board_prev.copy()
            self.my_tiles = self.my_tiles_prev.copy()
            tile = self.tiles.pop()
            #self.user_tiles.append(tile)
            self.my_tiles.append(tile)
            tile.setPos(self.foreground_item.pos() + QPointF(((len(self.my_tiles) - 1) % 20) * self.tile_width,
                                                             int((len(self.my_tiles) - 1) / 20) * self.tile_height))
            self.board_prev = self.board.copy()
            self.my_tiles_prev = self.my_tiles.copy()
            self.addItem(tile)
            self.logger.log(str(self.players[0].name) + " dobrał klocek")
            self.switch_player()
            #print(self.board)
            #print(self.board_prev)
            self.refresh_board()
        else:
            # to na wypadek rzadkiej sytuacji kiedy zabraknie klocków do dobrania
            min_player = min(self.players, key=lambda player: len(player.tiles))
            self.logger.error("Nie można dobrać więcej klocków! Koniec gry!")
            self.logger.log("Wygrywa " + min_player.name)
            msg_box = QMessageBox()
            msg_box.setText("Nie można dobrać więcej klocków! Koniec gry! \n Wygrywa " + min_player.name)
            msg_box.setWindowTitle("Message Box")
            msg_box.setStandardButtons(QMessageBox.Ok)

            response = msg_box.exec_()
            sys.exit()

    def generate_tiles(self):
        # Generowanie klocków
        self.tiles = [Tile(colour, numer)
                      for colour in self.colours
                      for numer in range(1, 14)
                      for i in range(2)]

        self.tiles += [Tile("black", 0, is_joker=True),
                       Tile("red", 0, is_joker=True)]
        random.shuffle(self.tiles)
        for player in self.players:
            player.tiles = self.tiles[:14]
            player.tiles_prev = player.tiles.copy()
            self.tiles = self.tiles[14:]
        self.current_player_index = 0

    def snap_to_grid(self, pos):
        # Obliczenie pozycji klocka na siatce
        ind_x = int(round(pos.x() / self.tile_width))
        ind_y = int(round(pos.y() / self.tile_height))
        max_index_x = int(self.width()/self.tile_width)
        max_index_y = int(self.width()/self.tile_width)
        # if ind_x > max_index_x - 10:
        #     ind_x = max_index_x - 10
        if ind_x > 23:
            ind_x = 23
        elif ind_x < 0:
            ind_x = - ind_x
        # if ind_y > max_index_y - 10:
        #     ind_y = max_index_y - 10
        if ind_y == 9 or ind_y >= 12:
            ind_y = 8
        elif ind_y < 0:
            ind_y = -ind_y
        while self.board[ind_y, ind_x] is not None: #jak użytkownik chce położyć swój klocek na już istniejący, to zostaje on przestawiony w prawo
            if ind_x < 23:
                ind_x+=1
            else:
                ind_x-=1
        x = ind_x * self.tile_width
        y = ind_y * self.tile_height
        return QPointF(x, y)

    def refresh_board(self):
        mask = np.where(self.board != None)
        #print(len(mask[0]))
        if len(mask[0]) != 0:
            tiles = self.board[mask]
            for i, tile in enumerate(tiles):
                tile.setPosFromIndices(mask[0][i],mask[1][i])
                if tile not in self.board:
                    self.addItem(tile)

    def possible_movements(self, tile):
        possible_moves = []
        if self.first_move:
            board = np.where(self.board == self.board_prev, None, self.board)
        else:
            board = self.board
        # if not self.first_move:
        mask = (board[:, :-1] != None) & (board[:, 1:] == None)
        left_indices = np.column_stack(np.where(mask))
        left_indices[:, 1] += 1

        mask = (board[:, 1:] != None) & (board[:, :-1] == None)
        right_indices = np.column_stack(np.where(mask))
        if tile.is_joker:
            # possible_moves = np.concatenate((left_indices, right_indices))
            left_mask = np.zeros(len(left_indices), dtype=bool)
            for i, idx in enumerate(left_indices):
                left_tile = board[idx[0], idx[1] - 1]
                left_left_tile = board[idx[0], idx[1] - 2]
                if left_tile is not None and left_tile.numer < 13 and left_left_tile is not None and (left_left_tile.numer == left_tile.numer - 1 or left_left_tile.is_joker):
                    left_mask[i] = True
                elif left_tile is not None and left_left_tile is not None and (left_left_tile.numer == left_tile.numer or left_left_tile.is_joker) and board[idx[0], idx[1] - 4] is None:
                    left_mask[i] = True
            possible_left_indices = left_indices[left_mask]

            right_mask = np.zeros(len(right_indices), dtype=bool)
            for i, idx in enumerate(right_indices):
                right_tile = board[idx[0], idx[1] + 1]
                right_right_tile = board[idx[0], idx[1] + 2]
                if right_tile is not None and right_tile.numer >= 2 and right_right_tile is not None and (right_right_tile.numer == right_tile.numer + 1 or right_right_tile.is_joker):
                    right_mask[i] = True
                elif right_tile is not None and right_right_tile is not None and (right_right_tile.numer == right_tile.numer or right_right_tile.is_joker) and board[idx[0], idx[1] + 4] is None:
                    right_mask[i] = True
            possible_right_indices = right_indices[right_mask]

            possible_moves = np.concatenate((possible_left_indices, possible_right_indices))
        else:
            for i in range(len(right_indices)):
                if board[right_indices[:, 0][i], right_indices[:, 1][i] + 1] != None and board[
                    right_indices[:, 0][i], right_indices[:, 1][i] + 2] != None:

                    if (board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].numer == tile.numer + 1 and
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].colour == tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].numer == tile.numer + 2 and
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].colour == tile.colour)) and (
                            board[
                                right_indices[:, 0][i], right_indices[:, 1][i] + 3] == None or
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 3].is_joker or  (board[
                                                                                            right_indices[:, 0][i],
                                                                                            right_indices[:, 1][
                                                                                                i] + 3].numer == tile.numer + 3 and
                                                                                        board[
                                                                                            right_indices[:, 0][i],
                                                                                            right_indices[:, 1][
                                                                                                i] + 3].colour == tile.colour)):
                        possible_moves.append((right_indices[i]))
                    elif (board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].numer == tile.numer and board[
                        right_indices[:, 0][i], right_indices[:, 1][i] + 1].colour != tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].is_joker or (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].numer == tile.numer and board[
                        right_indices[:, 0][i], right_indices[:, 1][i] + 2].colour != tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 3] == None or board[
                        right_indices[:, 0][i], right_indices[:, 1][i] + 3].is_joker or (board[
                                                                                             right_indices[:, 0][i],
                                                                                             right_indices[:, 1][
                                                                                                 i] + 3].numer == tile.numer and
                                                                                         board[
                                                                                             right_indices[:, 0][i],
                                                                                             right_indices[:, 1][
                                                                                                 i] + 3].colour != tile.colour)) and (
                            board[right_indices[:, 0][i], right_indices[:, 1][i] + 4] == None):
                        possible_moves.append((right_indices[i]))
            for i in range(len(left_indices)):
                if board[left_indices[:, 0][i], left_indices[:, 1][i] - 1] != None and board[
                    left_indices[:, 0][i], left_indices[:, 1][i] - 2] != None:
                    if (board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].numer == tile.numer - 1 and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 1].colour == tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].numer == tile.numer - 2 and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 2].colour == tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 3] == None or board[
                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].is_joker or (
                                    board[left_indices[:, 0][i], left_indices[:, 1][
                                                                     i] - 3].numer == tile.numer - 3 and
                                    board[
                                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].colour == tile.colour)):
                        possible_moves.append((left_indices[i]))
                    elif (board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].numer == tile.numer and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 1].colour != tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].is_joker or (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].numer == tile.numer and
                            board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 2].colour != tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 3] == None or board[
                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].is_joker or (
                                    board[left_indices[:, 0][i], left_indices[:, 1][i] - 3].numer == tile.numer and
                                    board[
                                        left_indices[:, 0][i], left_indices[:, 1][
                                                                   i] - 3].colour != tile.colour)) and (
                            board[left_indices[:, 0][i], left_indices[:, 1][i] - 4] == None):
                        possible_moves.append((left_indices[i]))

            # indices = np.concatenate((left_indices, right_indices))
        return possible_moves



    def mousePressEvent(self, event):
        # Znajdowanie klocka, który został kliknięty
        item = self.itemAt(event.scenePos(), QTransform())

        if isinstance(item, Tile):
            self.drag_tile = item
            self.snap_rect = QGraphicsRectItem(
                QRectF(self.snap_to_grid(event.scenePos()), QSizeF(self.tile_width, self.tile_height)))
            self.snap_rect.setBrush(QBrush(QColor(Qt.white)))
            self.snap_rect.setOpacity(0.5)
            self.addItem(self.snap_rect)

            if self.drag_tile in self.board:
                pos = self.drag_tile.pos()
                row = int(pos.y() / self.tile_height)
                col = int(pos.x() / self.tile_width)
                self.board[row, col] = None
            if self.drag_tile in self.selected_tiles:
                for tile in self.selected_tiles:
                    pos_til = tile.pos()
                    self.mouse_offsets.append(pos_til - self.drag_tile.pos())
                    if tile in self.board:
                        row = int(pos_til.y() / self.tile_height)
                        col = int(pos_til.x() / self.tile_width)
                        self.board[row, col] = None

            possible_moves = self.possible_movements(self.drag_tile)

            if len(possible_moves) > 0:
                for move in possible_moves:
                    x, y = move[1] * self.tile_width, move[0] * self.tile_height
                    rect = QGraphicsRectItem(QRectF(x, y, self.tile_width, self.tile_height))
                    rect.setBrush(QBrush(QColor(Qt.red)))
                    rect.setOpacity(0.5)
                    rect.setZValue(-1)
                    self.addItem(rect)
                    self.red_rects.append(rect)

        else:
            self.selected_tiles = []
            self.mouse_offsets = []
            self.selection_start_pos = event.scenePos()
            self.selection_rect = QGraphicsRectItem()
            self.selection_rect.setPen(QPen(Qt.black, 2, Qt.DotLine))
            self.addItem(self.selection_rect)



    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_tile') and self.drag_tile is not None:
            if self.snap_rect is not None:
                snap_pos = self.snap_to_grid(event.scenePos() - self.drag_tile.boundingRect().center())
                self.snap_rect.setRect(QRectF(snap_pos, QSizeF(self.tile_width, self.tile_height)))
                self.snap_rect.setZValue(-1)
            if not self.drag_tile in self.selected_tiles:
                pos = event.scenePos() - self.drag_tile.boundingRect().center()
                self.drag_tile.setPos(pos)
            if self.drag_tile in self.selected_tiles:
                [tile.setPos(event.scenePos() - tile.boundingRect().center() + offset) for tile, offset in
                 zip(self.selected_tiles, self.mouse_offsets)]
        elif self.selection_rect is not None:
            rect = QRectF(self.selection_start_pos, event.scenePos())
            self.selection_rect.setRect(rect.normalized())

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_tile') and self.drag_tile is not None:
            if self.snap_rect is not None:
                # prostokąt pokazujący możl. ruchu
                self.removeItem(self.snap_rect)
                self.snap_rect = None
            # prostokąty podpowiadające - usuwanie
            for rect in self.red_rects:
                self.removeItem(rect)
            self.red_rects = []

            if not self.drag_tile in self.selected_tiles:
                pos = self.snap_to_grid(self.drag_tile.pos())
                row = int(pos.y() / self.tile_height)
                col = int(pos.x() / self.tile_width)
                if self.drag_tile in self.my_tiles and row < 10: #z pulpitu na planszę
                    #
                    self.board[row, col] = self.drag_tile
                    self.my_tiles.remove(self.drag_tile)
                elif self.drag_tile not in self.my_tiles and row >= 10 and self.drag_tile in self.my_tiles_prev: #z planszy na pulpit

                    self.my_tiles.append(self.drag_tile)
                elif self.drag_tile not in self.my_tiles and row >= 10 and not self.drag_tile in self.my_tiles_prev: #wzięcie nieswojego klocka
                    #print("Nie można przeciągać nieswojego klocka na pulpit!")
                    self.logger.error(str(self.players[0].name) + " podjął próbę kradzieży nieswojego klocka!")
                    pos = self.snap_to_grid(QPointF(self.sceneRect().width() / 2 + self.tile_width * 20 / 2, int(
                        round((self.sceneRect().height() - self.tile_height * 2) / self.tile_height)) * self.tile_height))
                elif self.drag_tile not in self.my_tiles and row < 10: #zmiana pozycji na planszy
                    self.board[row, col] = self.drag_tile
                self.drag_tile.setPos(pos)
            if self.drag_tile in self.selected_tiles:
                for interval, tile in enumerate(self.selected_tiles):
                    pos = self.snap_to_grid(tile.pos())

                    row = int(pos.y() / self.tile_height)
                    col = int(pos.x() / self.tile_width)
                    if tile in self.my_tiles and row < 10:

                        self.board[row, col] = tile
                        self.my_tiles.remove(tile)
                    elif tile not in self.my_tiles and row >= 10 and self.drag_tile in self.my_tiles_prev: #z planszy na pulpit

                        self.my_tiles.append(tile)
                    elif self.drag_tile not in self.players[
                        self.current_player_index].tiles and row >= 10 and not self.drag_tile in self.players[
                        self.current_player_index].tiles_prev:  # wzięcie nieswojego klocka
                        #print("Nie można przeciągać nieswojego klocka na pulpit!")
                        self.logger.error(str(self.players[
                                                  self.current_player_index].name) + " podjął próbę kradzieży nieswojego klocka!")
                        pos = self.snap_to_grid(QPointF(self.sceneRect().width() / 2 + self.tile_width * 20 / 2 + interval*self.tile_width, int(
                            round((self.sceneRect().height() - self.tile_height * 2) / self.tile_height)) * self.tile_height))
                    elif tile not in self.my_tiles and row < 10:
                        self.board[row, col] = tile
                    tile.setPos(pos)
            self.drag_tile = None
        elif self.selection_rect is not None:
            selected_items = self.items(self.selection_rect.rect())
            for item in selected_items:
                if isinstance(item, Tile):
                    self.selected_tiles.append(item)
                    #print(item.numer)
            #print(len(self.selected_tiles))
            self.removeItem(self.selection_rect)
            self.selection_rect = None
            self.selection_start_pos = None
