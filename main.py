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
from board_online import BoardOnline
from replay import Replay


if __name__ == '__main__':
    app = QApplication(sys.argv)

    options_dialog = OptionsDialog()

    if options_dialog.exec_() == QDialog.Accepted:
        players = options_dialog.get_players()
        ip = options_dialog.ip_line_edit.text()
        port = options_dialog.port_line_edit.text()
        view = QGraphicsView()
        replay_pressed = options_dialog.get_button_pressed()
        mode_chosen = options_dialog.get_selected_radio_button()
        if replay_pressed == 1: #sql
            #path = options_dialog.db_path
            #board = Replay(view, players, False, path)
            board = Replay(view, players, False)
        elif replay_pressed == 2: #xml
            #path = options_dialog.db_path
            board = Replay(view, players, True)
        elif mode_chosen == "Online":
            board = BoardOnline(view, players, ip, port)
        else:
            board = Board(view, players)
        view.setScene(board)
        #board.set_ip_and_port(ip_and_port)

        view.setFixedSize(1810, 1020)
        view.setWindowTitle("Rummikub - Jakub Poćwiardowski 184827")
        icon = QIcon(":/joker/jok.png")
        view.setWindowIcon(icon)
        view.show()
        sys.exit(app.exec_())


