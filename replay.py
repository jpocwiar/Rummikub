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
        self.move_number = 0
        self.current_player_index = 0
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
            if i == self.current_player_index:
                name_item.setDefaultTextColor(QColor(255, 100, 100))
            self.addItem(name_item)
            name_item.setPos(50, y)
            self.player_name_items.append(name_item)
            y += 30

            # retrieve the tiles for the current move from the database
            self.cursor.execute('SELECT * FROM board_tiles WHERE move_index = ?', (self.move_number))
            tiles = self.cursor.fetchall()

            # iterate over the tiles and place them on the board
            for tile_data in tiles:
                number, color, row, col = tile_data[1:]
                tile = Tile(color, number)
                tile.setPosFromIndices(row, col)