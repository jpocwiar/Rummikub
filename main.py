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


class Board(QGraphicsScene):
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
        #self.user_tiles = []
        self.selected_tiles = []
        self.board = np.full((15, 40), None, dtype=object)
        self.board_prev = self.board.copy()
        self.groups = []
        self.colours = [Qt.red, Qt.blue, Qt.darkYellow, Qt.black]
        self.players = players
        self.current_player_index = 0
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

        self.sort_by_number_button = QPushButton('Sort by Number', view)
        self.sort_by_number_button.setGeometry(1600, 70, 120, 30)
        self.sort_by_number_button.clicked.connect(
        self.sort_tiles_by_number)

        self.text_edit = QTextEdit(view)
        self.text_edit.setGeometry(1430, 870, 350, 100)
        self.text_edit.setReadOnly(True)
        self.logger = Logger(self.text_edit)
        #view.setCornerWidget(self.text_edit)

        self.generate_tiles()
        self.logger.log('Początek gry')
        #umieszczenie kafelków gracza
        for i, tile in enumerate(self.players[self.current_player_index].tiles):
            tile.setPos(self.foreground_item.pos() + QPointF(
                (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
            self.addItem(tile)

        self.timed_out = False
        self.timer = Timer(self)
        self.addItem(self.timer)
        self.timer.setPos(1550, 200)

        self.timer_timer = QTimer()
        self.timer_timer.timeout.connect(self.update_timer)
        self.timer_timer.start(5)

        self.player_name_items = []
        y = 800
        for i, player in enumerate(self.players):
            name_item = QGraphicsTextItem(player.name)
            name_item.setFont(QFont("Arial", 16, QFont.Bold))
            name_item.setDefaultTextColor(QColor(235, 235, 235))
            if i == self.current_player_index:
                name_item.setDefaultTextColor(QColor(255, 100, 100))  # set current player's name to red
            self.addItem(name_item)
            name_item.setPos(50, y)
            self.player_name_items.append(name_item)
            y += 30

        self.tiles_number_item = QGraphicsTextItem("Tiles to draw: " + str(len(self.tiles)))
        self.tiles_number_item.setFont(QFont("Arial", 16, QFont.Bold))
        self.tiles_number_item.setDefaultTextColor(QColor(235, 235, 235))
        self.addItem(self.tiles_number_item)
        self.tiles_number_item.setPos(1500, 810)

    def update_timer(self):
        self.timer.update_time()

    def restart_timer(self):
        #print("hello")
        self.timer.time_left = 30000
        self.timer.update()
        self.timed_out = False



    def switch_player(self):
        # przejdź do następnego gracza
        for tile in self.players[self.current_player_index].tiles:
            self.removeItem(tile)
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(235, 235, 235))
        # zmiana indeksu
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.tiles_number_item.setPlainText("Tiles to draw: " + str(len(self.tiles)))
        # Dodanie klocków następnego gracza
        for i, tile in enumerate(self.players[self.current_player_index].tiles):
            tile.setPos(self.foreground_item.pos() + QPointF(
                (i % 20) * self.tile_width, int(i / 20) * self.tile_height))
            self.addItem(tile)

        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(255, 100, 100))
        self.restart_timer()

    def make_move(self):
        if self.players[self.current_player_index].first_move:

            #own_board = np.subtract(self.board, self.board_prev)
            own_board = np.where(self.board == self.board_prev, None, self.board)
            #tu jest wersja bez pętli, ale nie da się tak zrobić dobrze jokerów w pierwszym ruchu (sumowanie)
            # func = lambda til: til.numer if not til.is_joker else 6
            # vfunc = np.vectorize(func)
            mask = np.where(own_board != None)
            #print(mask[1])
            own_tiles = own_board[mask]
            # sum_of_tiles = 0
            # if own_tiles.size >1:
            #     sum_of_tiles = np.sum(vfunc(own_tiles))
            # print(sum_of_tiles)
            sum_of_tiles = 0
            #print(own_tiles[1].numer)
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
                                # print("coś nie halo0" + str(i))
                                # print(mask[1][i])
                                # print(mask[1][i-1])
                                # print(mask[1][i+1])
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
                                #print("coś nie halo")
                                pass

                #print(sum_of_tiles)
                #self.logger.log(str(self.players[self.current_player_index].name) + " położył kombinację o wartości "+ str(sum_of_tiles))


            if len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and not self.timed_out:
                #print("Musisz wykonać ruch!")
                self.logger.error(str(self.players[self.current_player_index].name) + " nie wykonał ruchu!")
            elif self.check_move(own_board) and not len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and sum_of_tiles >=30:
                #print("ruch prawidłowy")
                self.logger.log(
                    str(self.players[self.current_player_index].name) + " położył kombinację o wartości " + str(
                        sum_of_tiles))
                self.board_prev = self.board.copy()
                self.players[self.current_player_index].tiles_prev = self.players[
                    self.current_player_index].tiles.copy()

                self.players[self.current_player_index].first_move = False #już nie pierwszy ruch
                self.switch_player()
            # elif (not self.check_move() and self.timed_out) or (sorted(self.players[self.current_player_index].tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour)) == sorted(self.players[self.current_player_index].tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour)))) and self.timed_out): #przy pierwszym ruchu może robić jakby osobny board? Zęby to 30 sprawdzać
            elif self.check_move(own_board) and not len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and sum_of_tiles < 30 and not self.timed_out:
                #print("Przy pierwszym ruchu konieczne jest wyłożenie klocków o łącznej wartości >=30!")
                self.logger.error(
                    self.players[self.current_player_index].name + " położył pierwszą kombinację o wartości " + str(
                        sum_of_tiles) + ". Przy pierwszym ruchu konieczne jest wyłożenie klocków o łącznej wartości >=30!")
            elif self.timed_out and (not self.check_move(own_board) or (
                    len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev)) or sum_of_tiles < 30):
                # przywróć stan poprzedni i przejdź do następnego gracza
                #print("ruch nieprawidłowy i czas minął!")
                self.logger.error(
                    self.players[self.current_player_index].name + " nie wykonał poprawnego ruchu i czas się skończył!")

                self.draw_tile()
                #print(self.timed_out)
            elif not self.check_move(own_board) and not self.timed_out:
                #print("ruch nieprawidłowy")
                self.logger.error(
                    self.players[self.current_player_index].name + " nie wykonał poprawnego ruchu!")
                # print(self.timed_out)
        #if sorted(self.players[self.current_player_index].tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour))) == sorted(self.players[self.current_player_index].tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour))) and not self.timed_out:
        #print("a" + str(len(self.players[self.current_player_index].tiles)))
        #print("b" + str(len(self.players[self.current_player_index].tiles_prev)))
        else:
            if len(self.players[self.current_player_index].tiles) == len(self.players[self.current_player_index].tiles_prev) and not self.timed_out:
                #print("Musisz wykonać ruch!")
                self.logger.error(str(self.players[self.current_player_index].name) + " nie wykonał ruchu!")
            elif self.check_move(self.board) and not len(self.players[self.current_player_index].tiles) == len(self.players[self.current_player_index].tiles_prev):
                #print("ruch prawidłowy")
                self.logger.log(
                    str(self.players[self.current_player_index].name) + " wykonał prawidłowy ruch i zostało mu " + str(
                        len(self.players[self.current_player_index].tiles)) + " klocków")
                if len(self.players[self.current_player_index].tiles) == 0:
                    self.logger.log("Wygrywa " + str(self.players[self.current_player_index].name) + "!")
                    msg_box = QMessageBox()
                    msg_box.setText("Wygrywa " + str(self.players[self.current_player_index].name) + "!")
                    msg_box.setWindowTitle("Message Box")
                    msg_box.setStandardButtons(QMessageBox.Ok)

                    response = msg_box.exec_()
                    sys.exit(app.exec_())
                self.board_prev = self.board.copy()
                self.players[self.current_player_index].tiles_prev = self.players[self.current_player_index].tiles.copy()
                self.switch_player()
            #elif (not self.check_move() and self.timed_out) or (sorted(self.players[self.current_player_index].tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour)) == sorted(self.players[self.current_player_index].tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour)))) and self.timed_out): #przy pierwszym ruchu może robić jakby osobny board? Zęby to 30 sprawdzać
            elif (not self.check_move(self.board) and self.timed_out) or (len(self.players[self.current_player_index].tiles) == len(self.players[self.current_player_index].tiles_prev) and self.timed_out):
                #przywróć stan poprzedni i przejdź do następnego gracza
                #print("ruch nieprawidłowy i czas minął!")
                self.logger.error(
                    self.players[self.current_player_index].name + " nie wykonał poprawnego ruchu i czas się skończył!")
                #print(self.players[self.current_player_index].tiles)
                #print(self.players[self.current_player_index].tiles_prev)
                # self.board = self.board_prev.copy()
                # self.players[self.current_player_index].tiles = self.players[self.current_player_index].tiles_prev.copy()
                self.draw_tile()
                #self.switch_player()
                #print(self.timed_out)
            elif not self.check_move(self.board) and not self.timed_out:
                #print("ruch nieprawidłowy")
                self.logger.error(str(self.players[self.current_player_index].name) + " - ruch nieprawidłowy!")
                #print(self.timed_out)


    def check_move(self,board):
        if self.is_every_element_grouped(board):
            #print("youp")
            for group in self.groups:
                non_joker = np.sum([not til.is_joker for til in group])
                #print(non_joker)
                if(non_joker <= 1):
                    self.logger.log(str(self.players[self.current_player_index].name) + "- kombinacja z dominacją jokerów")
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
                            self.logger.log(
                                str(self.players[self.current_player_index].name) + "- kombinacja jeden kolor, po kolei")
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
                            #print("te same cyfr")
                            self.logger.log(
                                str(self.players[
                                        self.current_player_index].name) + " - kombinacja tych samych cyfr")
                        else:
                            #print("źle")
                            return False
                    else:
                        print("źle")
                        return False
            return True
        else:
            #print("Za mało klocków")
            # self.logger.log(
            #     str(self.players[self.current_player_index].name) + "- za mało klocków w kombinacji")
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
                # groups.append(board[non_none_indices])
                # print("eeee")
            elif non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1:  # sprawdzanie czy obok siebie
                counter += 1
                group.append(board[non_none_indices[0][i], non_none_indices[1][i]])
                if i == non_none_indices[0].size - 1 and counter >= 3:
                    self.groups.append(group)
                    # print("aaaa")
                # print("ddddd")
            elif (not (non_none_indices[0][i] == y and non_none_indices[1][i] == x + 1) or i == non_none_indices[
                0].size) and counter < 3:
                # print(counter)

                # print("ccccc")
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
        self.players[self.current_player_index].tiles = sorted(self.players[self.current_player_index].tiles, key=lambda tile: colors.index(tile.colour))

        for index, tile in enumerate(self.players[self.current_player_index].tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.tile_width,
                                                             int(index / 20) * self.tile_height))

    def sort_tiles_by_number(self):
        self.players[self.current_player_index].tiles = sorted(self.players[self.current_player_index].tiles, key=lambda tile: tile.numer)

        for index, tile in enumerate(self.players[self.current_player_index].tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.tile_width,
                                                             int(index / 20) * self.tile_height))

    def draw_tile(self):
        if len(self.tiles) > 0:
            self.board = self.board_prev.copy()
            self.players[self.current_player_index].tiles = self.players[
                self.current_player_index].tiles_prev.copy()
            tile = self.tiles.pop()
            #self.user_tiles.append(tile)
            self.players[self.current_player_index].add_tile(tile)
            tile.setPos(self.foreground_item.pos() + QPointF(((len(self.players[self.current_player_index].tiles) - 1) % 20) * self.tile_width,
                                                             int((len(self.players[self.current_player_index].tiles) - 1) / 20) * self.tile_height))
            self.board_prev = self.board.copy()
            self.players[self.current_player_index].tiles_prev = self.players[
                self.current_player_index].tiles.copy()
            #self.addItem(tile)
            self.logger.log(str(self.players[self.current_player_index].name) + " dobrał klocek")
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
            sys.exit(app.exec_())

    def generate_tiles(self):
        # Generowanie klocków
        self.tiles = [Tile(colour, numer)
                      for colour in self.colours
                      for numer in range(1, 14)
                      for i in range(2)]

        self.tiles += [Tile(Qt.black, 0, is_joker=True),
                       Tile(Qt.red, 0, is_joker=True)]
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
        if ind_x > max_index_x - 10:
            ind_x = max_index_x - 10
        elif ind_x < 0:
            ind_x = - ind_x
        if ind_y > max_index_y - 10:
            ind_y = max_index_y - 10
        elif ind_y < 0:
            ind_y = -ind_y
        while self.board[ind_y, ind_x] is not None: #jak użytkownik chce położyć swój klocek na już istniejący, to zostaje on przestawiony w prawo
            ind_x+=1
        x = ind_x * self.tile_width
        y = ind_y * self.tile_height
        return QPointF(x, y)

    def refresh_board(self):
        mask = np.where(self.board != None)
        #print(len(mask[0]))
        if len(mask[0]) != 0:
            # print(mask[0][1])
            # print(mask[1][1])
            tiles = self.board[mask]
            for i, tile in enumerate(tiles):
                tile.setPosFromIndices(mask[0][i],mask[1][i])

    def possible_movements(self, tile):
        possible_moves = []
        #if not self.players[self.current_player_index].first_move:
        mask = (self.board[:, :-1] != None) & (self.board[:, 1:] == None)
        left_indices = np.column_stack(np.where(mask))
        left_indices[:, 1] += 1

        mask = (self.board[:, 1:] != None) & (self.board[:, :-1] == None)
        right_indices = np.column_stack(np.where(mask))
        if tile.is_joker:
            possible_moves = np.concatenate((left_indices, right_indices))
        else:
            for i in range(len(right_indices)):
                if self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 1] != None and self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 2] !=None:

                   if (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].is_joker or (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].numer == tile.numer + 1 and self.board[right_indices[:, 0][i] , right_indices[:, 1][i] + 1].colour == tile.colour)) and (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].is_joker or (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].numer == tile.numer + 2 and self.board[right_indices[:, 0][i] , right_indices[:, 1][i] + 2].colour == tile.colour)):
                       possible_moves.append((right_indices[i]))
                   elif (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].is_joker or (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 1].numer == tile.numer and self.board[
                       right_indices[:, 0][i], right_indices[:, 1][i] + 1].colour != tile.colour)) and (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].is_joker or (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 2].numer == tile.numer and self.board[
                       right_indices[:, 0][i], right_indices[:, 1][i] + 2].colour != tile.colour)) and (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 3] == None or self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 3].is_joker or (self.board[right_indices[:, 0][i], right_indices[:, 1][i] + 3].numer == tile.numer and self.board[
                       right_indices[:, 0][i], right_indices[:, 1][i] + 3].colour != tile.colour)):
                       possible_moves.append((right_indices[i]))
            for i in range(len(left_indices)):
                if self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 1] != None and self.board[
                    left_indices[:, 0][i], left_indices[:, 1][i] - 2] != None:
                    if (self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].is_joker or (
                            self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].numer == tile.numer - 1 and
                            self.board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 1].colour == tile.colour)) and (
                            self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].is_joker or (
                            self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].numer == tile.numer - 2 and
                            self.board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 2].colour == tile.colour)):
                        possible_moves.append((left_indices[i]))
                    elif (self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].is_joker or (
                            self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 1].numer == tile.numer and
                            self.board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 1].colour != tile.colour)) and (
                            self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].is_joker or (
                            self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 2].numer == tile.numer and
                            self.board[
                                left_indices[:, 0][i], left_indices[:, 1][i] - 2].colour != tile.colour)) and (
                            self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 3] == None or self.board[
                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].is_joker or (
                                    self.board[left_indices[:, 0][i], left_indices[:, 1][i] - 3].numer == tile.numer and
                                    self.board[
                                        left_indices[:, 0][i], left_indices[:, 1][i] - 3].colour != tile.colour)):
                        possible_moves.append((left_indices[i]))





            #indices = np.concatenate((left_indices, right_indices))
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
                if self.drag_tile in self.players[self.current_player_index].tiles and row < 10: #z pulpitu na planszę
                    #
                    self.board[row, col] = self.drag_tile
                    self.players[self.current_player_index].tiles.remove(self.drag_tile)
                elif self.drag_tile not in self.players[self.current_player_index].tiles and row >= 10 and self.drag_tile in self.players[self.current_player_index].tiles_prev: #z planszy na pulpit

                    self.players[self.current_player_index].tiles.append(self.drag_tile)
                elif self.drag_tile not in self.players[self.current_player_index].tiles and row >= 10 and not self.drag_tile in self.players[self.current_player_index].tiles_prev: #wzięcie nieswojego klocka
                    #print("Nie można przeciągać nieswojego klocka na pulpit!")
                    self.logger.error(str(self.players[self.current_player_index].name) + " podjął próbę kradzieży nieswojego klocka!")
                    pos = self.snap_to_grid(QPointF(self.sceneRect().width() / 2 + self.tile_width * 20 / 2, int(
                        round((self.sceneRect().height() - self.tile_height * 2) / self.tile_height)) * self.tile_height))
                elif self.drag_tile not in self.players[self.current_player_index].tiles and row < 10: #zmiana pozycji na planszy
                    self.board[row, col] = self.drag_tile
                self.drag_tile.setPos(pos)
            if self.drag_tile in self.selected_tiles:
                for interval, tile in enumerate(self.selected_tiles):
                    pos = self.snap_to_grid(tile.pos())

                    row = int(pos.y() / self.tile_height)
                    col = int(pos.x() / self.tile_width)
                    if tile in self.players[self.current_player_index].tiles and row < 10:

                        self.board[row, col] = tile
                        self.players[self.current_player_index].tiles.remove(tile)
                    elif tile not in self.players[self.current_player_index].tiles and row >= 10 and self.drag_tile in self.players[self.current_player_index].tiles_prev: #z planszy na pulpit

                        self.players[self.current_player_index].tiles.append(tile)
                    elif self.drag_tile not in self.players[
                        self.current_player_index].tiles and row >= 10 and not self.drag_tile in self.players[
                        self.current_player_index].tiles_prev:  # wzięcie nieswojego klocka
                        #print("Nie można przeciągać nieswojego klocka na pulpit!")
                        self.logger.error(str(self.players[
                                                  self.current_player_index].name) + " podjął próbę kradzieży nieswojego klocka!")
                        pos = self.snap_to_grid(QPointF(self.sceneRect().width() / 2 + self.tile_width * 20 / 2 + interval*self.tile_width, int(
                            round((self.sceneRect().height() - self.tile_height * 2) / self.tile_height)) * self.tile_height))
                    elif tile not in self.players[self.current_player_index].tiles and row < 10:
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
