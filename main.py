#Jakub Poćwiardowski 184827

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
from board import Board
from replay import Replay


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # tworzenie okna dialogowego z opcjami
    options_dialog = OptionsDialog()

    if options_dialog.exec_() == QDialog.Accepted:
        players = options_dialog.get_players()
        ip_and_port = options_dialog.ip_line_edit.text()

        # inicjalizacja gry z wybranymi opcjami
        view = QGraphicsView()
        #board = Replay(view, players)
        board = Board(view, players)
        view.setScene(board)
        # ustaw adres IP i port dla gry
        #board.set_ip_and_port(ip_and_port)

        view.setFixedSize(1810, 1020)
        view.setWindowTitle("Rummikub - Jakub Poćwiardowski 184827")
        icon = QIcon(":/joker/jok.png")
        view.setWindowIcon(icon)
        view.show()
        sys.exit(app.exec_())

"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QGraphicsView()
    players = [Player("Player1"), Player("Player2"), Player("Player3"), Player("Player4")]
    #players = [Player("Player1"), Player("Player2")]
    board = Board(view, players)
    view.setScene(board)
    view.setFixedSize(1810, 1020)
    view.setWindowTitle("Rummikub - Jakub Poćwiardowski 184827")
    icon = QIcon(":/joker/jok.png")
    view.setWindowIcon(icon)
    view.show()
    sys.exit(app.exec_())
"""
