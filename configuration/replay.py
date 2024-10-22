from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import numpy as np
from mechanics.tile import Tile
from mechanics.desk import ForegroundItem
from mechanics.board import Board
import sqlite3
import xml.etree.ElementTree as ET

class Replay(QGraphicsScene):
    def __init__(self, view, players, modeXML = False, path = 'history.db', parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1800, 1000)
        self.mode = modeXML
        self.view = None
        try:
            background_image = QImage(":/backgr/wood3.jpg")
            background_brush = QBrush(
                background_image.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            self.setBackgroundBrush(background_brush)
        except:
            self.setBackgroundBrush(QBrush(QColor(238, 238, 238)))
        self.tiles = []
        self.board = np.full((15, 40), None, dtype=object)

        self.tile_width = Tile.width
        self.tile_height = Tile.height
        self.foreground_item = ForegroundItem(self.tile_width * 20, self.tile_height * 2)
        self.foreground_item.setPos(self.sceneRect().width() / 2 - self.tile_width * 20 / 2, int(round(
            (self.sceneRect().height() - self.tile_height * 2) / self.tile_height)) * self.tile_height)
        self.addItem(self.foreground_item)

        self.players = players
        # umieszczenie nazw graczy
        self.player_name_items = []
        y = 800
        for i, player in enumerate(self.players):
            name_item = QGraphicsTextItem(player.name)
            name_item.setFont(QFont("Arial", 16, QFont.Bold))
            name_item.setDefaultTextColor(QColor(235, 235, 235))
            if i == 0:
                name_item.setDefaultTextColor(QColor(255, 100, 100))
            self.addItem(name_item)
            name_item.setPos(50, y)
            self.player_name_items.append(name_item)
            y += 30

        if modeXML:
            tree = ET.parse('history.xml')
            self.root = tree.getroot()
            board_tiles = tree.getroot().find('board_tiles')
            #move_indexes = [int(move.attrib['index']) for move in board_tiles.iter('move')]
            self.max_moves = int(board_tiles.findall('move')[-1].attrib['index'])
            if self.max_moves is None:
                self.max_moves = 0
            #max_moves = max(move_indexes)
            self.number_of_players = len(list(self.root)) - 2
            #print(self.number_of_players)
        else:
            conn = sqlite3.connect('history.db')
            self.cursor = conn.cursor()
            self.cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
            self.number_of_players = self.cursor.fetchone()[0] - 2
            # print(self.number_of_players)

            # self.cursor.execute('SELECT COUNT(DISTINCT move_index) FROM board_tiles')
            self.cursor.execute('SELECT MAX(move_index) FROM board_tiles')
            self.max_moves = self.cursor.fetchone()[0]
            if self.max_moves is None:
                self.max_moves = 0
            for i in range(self.number_of_players):
                self.cursor.execute(f'SELECT MAX(move_index) FROM player{i+1}_tiles')
                val = self.cursor.fetchone()[0]
                if val is not None and val > self.max_moves:
                    self.max_moves = val


        self.move_number = 0
        self.current_player_index = 0


        self.move_number_widget = QLabel(f"Move: {self.move_number}/{self.max_moves}")
        self.move_number_widget.setFont(QFont("Arial", 16))
        self.move_number_widget.setAlignment(Qt.AlignRight)
        self.addWidget(self.move_number_widget)
        self.move_number_widget.setGeometry(1400, 20, 350, 30)

        self.move_number_widget2 = QLabel(f"Before {players[self.current_player_index].name}'s move")
        self.move_number_widget2.setFont(QFont("Arial", 16))
        self.move_number_widget2.setAlignment(Qt.AlignRight)
        self.addWidget(self.move_number_widget2)
        self.move_number_widget2.setGeometry(1400, 80, 350, 30)

        self.move_number_widget3 = QLabel(f"Round: {int(self.move_number / (len(self.players) * 2) + 1)}")
        self.move_number_widget3.setFont(QFont("Arial", 16))
        self.move_number_widget3.setAlignment(Qt.AlignRight)
        self.addWidget(self.move_number_widget3)
        self.move_number_widget3.setGeometry(1400, 50, 350, 30)

        self.tiles_number_item = QGraphicsTextItem("Tiles to draw: " + str(len(self.tiles)))
        self.tiles_number_item.setFont(QFont("Arial", 16, QFont.Bold))
        self.tiles_number_item.setDefaultTextColor(QColor(235, 235, 235))
        self.addItem(self.tiles_number_item)
        self.tiles_number_item.setPos(1500, 900)

        self.jump_button = QPushButton("Jump into the moment")
        self.jump_button.clicked.connect(self.jump_into_moment)

        self.increment_button = QToolButton()
        self.increment_button.setIcon(self.create_arrow_icon(Qt.UpArrow))
        self.increment_button.clicked.connect(self.increment_move_number)
        self.decrement_button = QToolButton()
        self.decrement_button.setIcon(self.create_arrow_icon(Qt.DownArrow))
        self.decrement_button.clicked.connect(self.decrement_move_number)

        self.addWidget(self.increment_button)
        self.addWidget(self.decrement_button)

        self.increment_button.setGeometry(1600, 800, 50, 50)
        self.decrement_button.setGeometry(1500, 800, 50, 50)
        if self.mode:
            self.retrieve_tilesXML()
        else:
            self.retrieve_tiles()



    def jump_into_moment(self):
        # if self.view is not None:
        #     self.view.close()

        self.view = QGraphicsView()
        self.board_game = Board(self.view, self.players, False)

        #self.board.refresh_board()
        self.board_game.current_player_index = self.current_player_index
        self.board_game.tiles = self.tiles.copy()
        self.board_game.board = self.board.copy()

        self.view.setScene(self.board_game)
        self.view.setFixedSize(1810, 1020)
        self.view.setWindowTitle("Rummikub")
        icon = QIcon(":/joker/jok.png")
        self.view.setWindowIcon(icon)
        self.board_game.draw_tile()
        self.view.show()


    def increment_move_number(self):
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(235, 235, 235))
        self.move_number += 1
        if self.move_number > self.max_moves:
            self.move_number = self.max_moves
        self.current_player_index = int(self.move_number / 2 % self.number_of_players)
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(255, 100, 100))

        self.update_move_number()
        self.clear()
        if self.mode:
            self.retrieve_tilesXML()
        else:
            self.retrieve_tiles()

    def decrement_move_number(self):
        self.move_number -= 1
        if self.move_number < 0:
            self.move_number = 0
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(235, 235, 235))
        self.current_player_index = int(self.move_number / 2 % self.number_of_players)
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(255, 100, 100))
        self.update_move_number()
        self.clear()
        if self.mode:
            self.retrieve_tilesXML()
        else:
            self.retrieve_tiles()

    def retrieve_tiles(self):
        self.cursor.execute('SELECT * FROM board_tiles WHERE move_index = ?', (self.move_number,))
        tiles = self.cursor.fetchall()
        self.board = np.full((15, 40), None, dtype=object)
        for tile_data in tiles:
            number, color, row, col = tile_data[1:]
            if number == 0:
                tile = Tile(color, number, is_joker=True)
                self.board[row,col] = tile
            else:
                tile = Tile(color, number)
                self.board[row, col] = tile
            #print(self.board)
            tile.setPosFromIndices(row, col)
            self.addItem(tile)

        i = self.current_player_index + 1
        self.cursor.execute(f'SELECT * FROM player{i}_tiles WHERE move_index = ?', (self.move_number,))
        tiles = self.cursor.fetchall()
        self.players[i-1].tiles = []
        for i, tile_data in enumerate(tiles):
            number, color = tile_data[1:3]
            if number == 0:
                tile = Tile(color, number, is_joker=True)
            else:
                tile = Tile(color, number)
            tile.setPos(self.foreground_item.pos() + QPointF(
                (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
            self.addItem(tile)
            #self.players[i - 1].tiles.append(tile)
        self.cursor.execute(f'SELECT * FROM draw_tiles WHERE move_index = ?', (self.move_number,))
        tiles = self.cursor.fetchall()
        self.tiles = []
        for i, tile_data in enumerate(tiles):
            number, color = tile_data[1:3]
            if number == 0:
                tile = Tile(color, number, is_joker=True)
            else:
                tile = Tile(color, number)
            self.tiles.append(tile)
        self.tiles_number_item.setPlainText("Tiles to draw: " + str(len(self.tiles)))

    def retrieve_tilesXML(self):
        board_elem = self.root.find(f'board_tiles/move[@index="{self.move_number}"]')
        board_tiles = board_elem.findall('tile')

        for tile_elem in board_tiles:
            number = int(tile_elem.attrib['number'])
            color = tile_elem.attrib['color']
            row = int(tile_elem.attrib['row'])
            col = int(tile_elem.attrib['col'])

            if number == 0:
                tile = Tile(color, number, is_joker=True)
            else:
                tile = Tile(color, number)

            tile.setPosFromIndices(row, col)
            self.addItem(tile)

        i = self.current_player_index + 1
        player_elem = self.root.find(f'player{i}_tiles/move[@index="{self.move_number}"]')
        player_tiles = player_elem.findall('tile')

        for i, tile_elem in enumerate(player_tiles):
            number = int(tile_elem.attrib['number'])
            color = tile_elem.attrib['color']

            if number == 0:
                tile = Tile(color, number, is_joker=True)
            else:
                tile = Tile(color, number)

            tile.setPos(self.foreground_item.pos() + QPointF(
                (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
            self.addItem(tile)
        draw_elem = self.root.find(f'draw_tiles/move[@index="{self.move_number}"]')
        draw_tiles = draw_elem.findall('tile')
        self.tiles = []
        for i, tile_elem in enumerate(draw_tiles):
            number = int(tile_elem.attrib['number'])
            color = tile_elem.attrib['color']

            if number == 0:
                tile = Tile(color, number, is_joker=True)
            else:
                tile = Tile(color, number)
            self.tiles.append(tile)
            self.tiles_number_item.setPlainText("Tiles to draw: " + str(len(self.tiles)))


    def clear(self):
        for item in self.items():
            if isinstance(item, Tile):
                self.removeItem(item)

    def update_move_number(self):
        self.move_number_widget.setText(f"Move: {self.move_number}/{self.max_moves}")

        if self.move_number % 2 == 0:
            move_done = f"Before {self.players[self.current_player_index].name}'s move"
        else:
            move_done = f"After {self.players[self.current_player_index].name}'s move"

        self.move_number_widget2.setText(move_done)
        self.move_number_widget3.setText(f"Round: {int(self.move_number / (len(self.players) * 2) + 1)}")

    def create_arrow_icon(self, direction):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.translate(8, 8)
        painter.rotate(-90 if direction == Qt.UpArrow else 90)
        painter.drawPolygon(QPolygonF([QPointF(-12, -8), QPointF(0, 8), QPointF(12, -8)]))
        painter.end()
        return QIcon(pixmap)