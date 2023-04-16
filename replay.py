from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import random
import numpy as np
import sys
import graphics_rc
from timer import Timer
from tile import Tile
from player import Player
from desk import ForegroundItem
from logger import Logger
from options import OptionsDialog
from database import DatabaseSQL, DatabaseXML
from board import Board
import sqlite3
import xml.etree.ElementTree as ET

class Replay(QGraphicsScene):
    def __init__(self, view, players, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1800, 1000)

        try:
            background_image = QImage(":/backgr/wood3.jpg")
            background_brush = QBrush(
                background_image.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            self.setBackgroundBrush(background_brush)
        except:
            self.setBackgroundBrush(QBrush(QColor(238, 238, 238)))
        self.tiles = []


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

        tree = ET.parse('history.xml')

        self.root = tree.getroot()

        self.move_number = 0
        self.current_player_index = 0
        conn = sqlite3.connect('history.db')
        self.cursor = conn.cursor()
        self.cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
        self.number_of_players = self.cursor.fetchone()[0] - 2
        #print(self.number_of_players)

        #self.cursor.execute('SELECT COUNT(DISTINCT move_index) FROM board_tiles')
        self.cursor.execute('SELECT MAX(move_index) FROM board_tiles')
        self.max_moves = self.cursor.fetchone()[0]
        if self.max_moves is None:
            self.max_moves = 0

        self.move_number_widget = QLabel(f"Ruch: {self.move_number}/{self.max_moves}")
        self.move_number_widget.setFont(QFont("Arial", 16))
        self.move_number_widget.setAlignment(Qt.AlignRight)
        self.addWidget(self.move_number_widget)
        self.move_number_widget.setGeometry(1400, 20, 350, 30)

        self.move_number_widget2 = QLabel(f"Przed ruchem {players[self.current_player_index].name}")
        self.move_number_widget2.setFont(QFont("Arial", 16))
        self.move_number_widget2.setAlignment(Qt.AlignRight)
        self.addWidget(self.move_number_widget2)
        self.move_number_widget2.setGeometry(1400, 80, 350, 30)

        self.move_number_widget3 = QLabel(f"Kolejka: {int(self.move_number / (len(self.players) * 2) + 1)}")
        self.move_number_widget3.setFont(QFont("Arial", 16))
        self.move_number_widget3.setAlignment(Qt.AlignRight)
        self.addWidget(self.move_number_widget3)
        self.move_number_widget3.setGeometry(1400, 50, 350, 30)

        # self.increment_button = QPushButton("+")
        # self.increment_button.clicked.connect(self.increment_move_number)
        # self.decrement_button = QPushButton("-")
        # self.decrement_button.clicked.connect(self.decrement_move_number)

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

        #self.retrieve_tilesXML()
        self.retrieve_tiles()

    def increment_move_number(self):
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(235, 235, 235))
        self.move_number += 1
        if self.move_number > self.max_moves:
            self.move_number = self.max_moves
        self.current_player_index = int(self.move_number / 2 % self.number_of_players)
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(255, 100, 100))

        self.update_move_number()
        self.clear()
        #self.retrieve_tilesXML()
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
        #self.retrieve_tilesXML()
        self.retrieve_tiles()

    def retrieve_tiles(self):
        # retrieve the tiles for the current move from the database
        self.cursor.execute('SELECT * FROM board_tiles WHERE move_index = ?', (self.move_number,))
        tiles = self.cursor.fetchall()

        # iterate over the tiles and place them on the board
        for tile_data in tiles:
            number, color, row, col = tile_data[1:]
            if number == 0:
                tile = Tile(color, number, is_joker=True)
            else:
                tile = Tile(color, number)
            #print(tile)
            tile.setPosFromIndices(row, col)
            self.addItem(tile)

        i = self.current_player_index + 1
        self.cursor.execute(f'SELECT * FROM player{i}_tiles WHERE move_index = ?', (self.move_number,))
        tiles = self.cursor.fetchall()
        for i, tile_data in enumerate(tiles):
            number, color = tile_data[1:3]
            if number == 0:
                tile = Tile(color, number, is_joker=True)
            else:
                tile = Tile(color, number)
            tile.setPos(self.foreground_item.pos() + QPointF(
                (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
            self.addItem(tile)

    def retrieve_tilesXML(self):
        # retrieve the tiles for the current move from the XML file
        board_elem = self.root.find(f'board_tiles/move[@index="{self.move_number}"]')
        board_tiles = board_elem.findall('tile')

        # iterate over the tiles and place them on the board
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

    def clear(self):
        # remove only Tile objects from the scene
        for item in self.items():
            if isinstance(item, Tile):
                self.removeItem(item)

    def update_move_number(self):
        self.move_number_widget.setText(f"Ruch: {self.move_number}/{self.max_moves}")

        if self.move_number % 2 == 0:
            move_done = f"Przed ruchem {self.players[self.current_player_index].name}"
        else:
            move_done = f"Po ruchu {self.players[self.current_player_index].name}"

        self.move_number_widget2.setText(move_done)
        self.move_number_widget3.setText(f"Kolejka: {int(self.move_number / (len(self.players) * 2) + 1)}")

    def create_arrow_icon(self, direction):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.translate(8, 8)
        painter.rotate(-90 if direction == Qt.UpArrow else 90)
        painter.drawPolygon(QPolygonF([QPointF(-6, -4), QPointF(0, 4), QPointF(6, -4)]))
        painter.end()
        return QIcon(pixmap)