from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import random
import numpy as np
import sys
import clock_rc
from timer import Timer
from tile import Tile
from player import Player
from desk import ForegroundItem


class Board(QGraphicsScene):
    def __init__(self, view, players, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1800, 1000)

        try:
            background_image = QImage("wood3.jpg")
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
        self.colours = [Qt.red, Qt.blue, QColor(254, 176, 0), Qt.black]
        self.players = players  # list of players
        self.current_player_index = 0  # index of the current player in the list


        self.width = 50
        self.height = 80
        self.foreground_item = ForegroundItem(self.width * 20, self.height * 2) # Create an instance of ForegroundItem
        self.foreground_item.setPos(self.sceneRect().width() / 2 - self.width * 20 / 2, int(round((self.sceneRect().height() - self.height * 2)/self.height))*self.height)
        self.addItem(self.foreground_item) # Add the foreground item to the scene

        self.selection_rect = None
        self.selection_start_pos = None
        self.mouse_offsets = []

        # Add a button to the top right corner of the QGraphicsView
        self.button = QPushButton('Draw Tile', view)
        self.button.setGeometry(1600, 500, 90, 30)  # Set the button position
        self.button.clicked.connect(self.draw_tile)  # Connect the button to a function that will draw a tile

        # Add a button to the top right corner of the QGraphicsView for sorting tiles by color
        self.sort_by_color_button = QPushButton('Sort by Color', view)
        self.sort_by_color_button.setGeometry(1600, 40, 120, 30)  # Set the button position
        self.sort_by_color_button.clicked.connect(
        self.sort_tiles_by_color)  # Connect the button to a function that will sort tiles by color

        self.accept_move = QPushButton('Accept move', view)
        self.accept_move.setGeometry(1600, 540, 120, 30)  # Set the button position
        self.accept_move.clicked.connect(self.make_move)

        # Add a button to the top right corner of the QGraphicsView for sorting tiles by number
        self.sort_by_number_button = QPushButton('Sort by Number', view)
        self.sort_by_number_button.setGeometry(1600, 70, 120, 30)  # Set the button position
        self.sort_by_number_button.clicked.connect(
        self.sort_tiles_by_number)  # Connect the button to a function that will sort tiles by number

        self.generate_tiles()
        #dodanie do planszy klocków pierwszego gracza
        for i, tile in enumerate(self.players[self.current_player_index].tiles):
            tile.setPos(self.foreground_item.pos() + QPointF(
                (i % 20) * self.width, int(i / 20) * self.height))
            self.addItem(tile)

        self.timed_out = False
        self.timer = Timer(self)
        self.addItem(self.timer)
        self.timer.setPos(1550, 200)

        self.timer_timer = QTimer()
        self.timer_timer.timeout.connect(self.update_timer)
        self.timer_timer.start(1)  # milliseconds

        # Add player names to the board
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
        self.tiles_number_item.setPos(1500, 900)

    def update_timer(self):
        self.timer.update_time()

    def restart_timer(self):
        #print("hello")
        self.timer.time_left = 30000  # Reset the timer to 30 seconds
        self.timer.update()  # Update the timer display
        self.timed_out = False  # Set the timed_out variable to False



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
                (i % 20) * self.width, int(i / 20) * self.height))
            self.addItem(tile)

        # update player name items to highlight current player
        self.player_name_items[self.current_player_index].setDefaultTextColor(QColor(255, 100, 100))
        self.restart_timer()

    def make_move(self):
        if self.players[self.current_player_index].first_move:
            #tu trzeba sprawdzać czy suma kloców wrzuconych jest >=30

            #own_board = np.subtract(self.board, self.board_prev)
            own_board = np.where(self.board == self.board_prev, None, self.board)
            #print(self.board)
            #print(self.board_prev)
            #print(own_board)
            func = lambda til: til.numer
            vfunc = np.vectorize(func)
            own_tiles = own_board[np.where(own_board != None)]
            sum_of_tiles = 0
            if own_tiles.size >1:
                sum_of_tiles = np.sum(vfunc(own_tiles))
            print(sum_of_tiles)
            if len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and not self.timed_out:
                print("Musisz wykonać ruch!")
            elif self.check_move(own_board) and not len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and sum_of_tiles >=30:
                print("ruch prawidłowy")
                self.board_prev = self.board.copy()
                self.players[self.current_player_index].tiles_prev = self.players[
                    self.current_player_index].tiles.copy()

                self.players[self.current_player_index].first_move = False #już nie pierwszy ruch
                self.switch_player()
            # elif (not self.check_move() and self.timed_out) or (sorted(self.players[self.current_player_index].tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour)) == sorted(self.players[self.current_player_index].tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour)))) and self.timed_out): #przy pierwszym ruchu może robić jakby osobny board? Zęby to 30 sprawdzać
            elif self.check_move(own_board) and not len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev) and sum_of_tiles < 30 and not self.timed_out:
                print("Przy pierwszym ruchu konieczne jest wyłożenie klocków o łącznej wartości >=30!")
            elif self.timed_out and (not self.check_move(own_board) or (
                    len(self.players[self.current_player_index].tiles) == len(
                    self.players[self.current_player_index].tiles_prev)) or sum_of_tiles < 30):
                # przywróć stan poprzedni i przejdź do następnego gracza
                print("ruch nieprawidłowy i czas minął!")
                print(self.players[self.current_player_index].tiles)
                print(self.players[self.current_player_index].tiles_prev)
                self.board = self.board_prev.copy()
                self.players[self.current_player_index].tiles = self.players[
                    self.current_player_index].tiles_prev.copy()
                self.switch_player()
                print(self.timed_out)
            elif not self.check_move(own_board) and not self.timed_out:
                print("ruch nieprawidłowy")
                # print(self.timed_out)
        #if sorted(self.players[self.current_player_index].tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour))) == sorted(self.players[self.current_player_index].tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour))) and not self.timed_out:
        #print("a" + str(len(self.players[self.current_player_index].tiles)))
        #print("b" + str(len(self.players[self.current_player_index].tiles_prev)))
        else:
            if len(self.players[self.current_player_index].tiles) == len(self.players[self.current_player_index].tiles_prev) and not self.timed_out:
                print("Musisz wykonać ruch!")
            elif self.check_move(self.board) and not len(self.players[self.current_player_index].tiles) == len(self.players[self.current_player_index].tiles_prev):
                print("ruch prawidłowy")
                self.board_prev = self.board.copy()
                self.players[self.current_player_index].tiles_prev = self.players[self.current_player_index].tiles.copy()
                self.switch_player()
            #elif (not self.check_move() and self.timed_out) or (sorted(self.players[self.current_player_index].tiles, key=lambda tile: (tile.numer, self.colours.index(tile.colour)) == sorted(self.players[self.current_player_index].tiles_prev, key=lambda tile: (tile.numer, self.colours.index(tile.colour)))) and self.timed_out): #przy pierwszym ruchu może robić jakby osobny board? Zęby to 30 sprawdzać
            elif (not self.check_move(self.board) and self.timed_out) or (len(self.players[self.current_player_index].tiles) == len(self.players[self.current_player_index].tiles_prev) and self.timed_out):
                #przywróć stan poprzedni i przejdź do następnego gracza
                print("ruch nieprawidłowy i czas minął!")
                print(self.players[self.current_player_index].tiles)
                print(self.players[self.current_player_index].tiles_prev)
                self.board = self.board_prev.copy()
                self.players[self.current_player_index].tiles = self.players[self.current_player_index].tiles_prev.copy()
                self.switch_player()
                print(self.timed_out)
            elif not self.check_move(self.board) and not self.timed_out:
                print("ruch nieprawidłowy")
                #print(self.timed_out)

    def check_move(self,board):
        if self.is_every_element_grouped(board):
            #print("youp")
            for group in self.groups:
                non_joker = np.sum([not til.is_joker for til in group])
                if(non_joker <= 1):
                    print("ok")
                else:
                    colors = set(str(til.colour) for til in group if not til.is_joker)
                    color_count = len(colors)
                    print("kolory: " + str(color_count))
                    if color_count == 1:
                        unique_values = set(til.numer - idx for idx, til in enumerate(group) if not til.is_joker)
                        if len(unique_values) == 1 and not unique_values == {0} and not next(iter(unique_values)) + len(group) - 1 >= 14:
                            #print(unique_values)
                            print("po kolei")
                        else:
                            print("nie po kolei")
                            return False
                    elif color_count == non_joker and len(group) <= 4:
                        values = set(til.numer for til in group if not til.is_joker)
                        if len(values) == 1:
                            print("te same cyfr")
                        else:
                            print("źle")
                            return False
                    else:
                        print("źle")
                        return False
            return True
        else:
            print("Za mało klocków")
            #msg_box = QMessageBox()
            #msg_box.setText("Układ musi zawierać co najmniej 3 klocki!")
            #msg_box.setWindowTitle("Message Box")
            #msg_box.setStandardButtons(QMessageBox.Ok)

            #response = msg_box.exec_()
            return False


    def is_every_element_grouped(self, board):
        #board = self.board
        # Get indices of non-None elements
        non_none_indices = np.where(board != None)
        #print(non_none_indices)
        # Iterate over each index in the non_none_indices array
        counter = 0
        colors = []
        self.groups = []
        if non_none_indices[0].size < 3:
            return False
        for i in range(non_none_indices[0].size):

            if counter == 0:
                counter += 1
                group = [board[non_none_indices[0][i],non_none_indices[1][i]]]
                #groups.append(board[non_none_indices])
                #print("eeee")
            elif non_none_indices[0][i] == y and non_none_indices[1][i] == x+1: #sprawdzanie czy obok siebie
                counter += 1
                group.append(board[non_none_indices[0][i],non_none_indices[1][i]])
                if i == non_none_indices[0].size-1 and counter >= 3:
                    self.groups.append(group)
                    #print("aaaa")
                #print("ddddd")
            elif (not (non_none_indices[0][i] == y and non_none_indices[1][i] == x+1) or i == non_none_indices[0].size) and counter <3:
                #print(counter)

                #print("ccccc")
                return False
            elif not (non_none_indices[0][i] == y and non_none_indices[1][i] == x+1) and counter >= 3:
                counter = 1
                self.groups.append(group)
                group = [board[non_none_indices[0][i], non_none_indices[1][i]]]
                #print("bbbb")


            y = non_none_indices[0][i]
            x = non_none_indices[1][i]
            color = board[non_none_indices[0][i],non_none_indices[1][i]].colour
            number = board[non_none_indices[0][i], non_none_indices[1][i]].numer
            #print(number)
        #print(counter)
        if counter < 3:
            return False
        print(len(self.groups))
        return True



    def sort_tiles_by_color(self):
        colors = [Qt.red, Qt.blue, QColor(254, 176, 0), Qt.black]
        #self.user_tiles = sorted(self.user_tiles, key=lambda tile: colors.index(tile.colour))
        self.players[self.current_player_index].tiles = sorted(self.players[self.current_player_index].tiles, key=lambda tile: colors.index(tile.colour))

        for index, tile in enumerate(self.players[self.current_player_index].tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.width,
                                                             int(index / 20) * self.height))

    def sort_tiles_by_number(self):
        self.players[self.current_player_index].tiles = sorted(self.players[self.current_player_index].tiles, key=lambda tile: tile.numer)

        for index, tile in enumerate(self.players[self.current_player_index].tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.width,
                                                             int(index / 20) * self.height))

    def draw_tile(self):
        tile = self.tiles.pop()
        #self.user_tiles.append(tile)
        self.players[self.current_player_index].add_tile(tile)
        # Set the position of the tile relative to the ForegroundItem
        tile.setPos(self.foreground_item.pos() + QPointF(((len(self.players[self.current_player_index].tiles) - 1) % 20) * self.width,
                                                         int((len(self.players[self.current_player_index].tiles) - 1) / 20) * self.height))
        self.addItem(tile)

    def generate_tiles(self):
        # Generowanie klocków
        #colours = [Qt.red, Qt.blue, QColor(254, 176, 0), Qt.black]
        for colour in self.colours:
            for numer in range(1, 14):
                for i in range(2):
                    tile = Tile(colour, numer)
                    tile.setFlag(QGraphicsItem.ItemIsMovable)  # Ustawienie możliwości przesuwania klocka
                    #self.addItem(tile)
                    self.tiles.append(tile)
        tile = Tile(Qt.black, 0, is_joker=True)
        self.tiles.append(tile)
        tile = Tile(Qt.red, 0, is_joker=True)
        self.tiles.append(tile)
        random.shuffle(self.tiles)
        for j in range(len(players)):
            for i in range(14):
                #self.draw_tile()
                tile = self.tiles.pop()
                # self.user_tiles.append(tile)
                self.players[self.current_player_index].add_tile(tile)
            self.players[self.current_player_index].tiles_prev = self.players[self.current_player_index].tiles.copy()
            self.current_player_index= (self.current_player_index + 1) % len(players)

    def snap_to_grid(self, pos):
        # Obliczenie pozycji klocka na siatce
        ind_x = int(round(pos.x() / self.width))
        ind_y = int(round(pos.y() / self.height))
        while self.board[ind_y, ind_x] is not None:
            ind_x+=1
        x = ind_x * self.width
        y = ind_y * self.height
        return QPointF(x, y)


    def mousePressEvent(self, event):
        # Znajdowanie klocka, który został kliknięty
        items = self.items(event.scenePos())
        for item in items:
            if isinstance(item, Tile):
                self.drag_tile = item

                if self.drag_tile in self.board:
                    pos = self.drag_tile.pos()
                    # Get the index of the position where the tile is dropped
                    row = int(pos.y() / self.height)
                    col = int(pos.x() / self.width)
                    self.board[row, col] = None
                if self.drag_tile in self.selected_tiles:
                    for tile in self.selected_tiles:
                        pos_til = tile.pos()
                        self.mouse_offsets.append(pos_til - self.drag_tile.pos())
                        if tile in self.board:
                            row = int(pos_til.y() / self.height)
                            col = int(pos_til.x() / self.width)
                            self.board[row, col] = None

                break
        else:
            self.selected_tiles = []
            self.mouse_offsets = []
            self.selection_start_pos = event.scenePos()
            self.selection_rect = QGraphicsRectItem()
            self.selection_rect.setPen(QPen(Qt.black, 2, Qt.DotLine))
            self.addItem(self.selection_rect)


    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_tile') and self.drag_tile is not None:
            if not self.drag_tile in self.selected_tiles:
                pos = event.scenePos() - self.drag_tile.boundingRect().center()
                self.drag_tile.setPos(pos)
            if self.drag_tile in self.selected_tiles:
                for tile, offset in zip(self.selected_tiles, self.mouse_offsets):
                    #print(offset)
                    pos = event.scenePos() - tile.boundingRect().center() + offset
                    tile.setPos(pos)
        elif self.selection_rect is not None:
            rect = QRectF(self.selection_start_pos, event.scenePos())
            self.selection_rect.setRect(rect.normalized())

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_tile') and self.drag_tile is not None:
            if not self.drag_tile in self.selected_tiles:
                pos = self.snap_to_grid(self.drag_tile.pos())
                # Get the index of the position where the tile is dropped
                row = int(pos.y() / self.height)
                col = int(pos.x() / self.width)
                if self.drag_tile in self.players[self.current_player_index].tiles and row < 10: #z pulpitu na planszę
                    # Append the tile to the corresponding index on the board
                    self.board[row, col] = self.drag_tile
                    self.players[self.current_player_index].tiles.remove(self.drag_tile)
                elif self.drag_tile not in self.players[self.current_player_index].tiles and row >= 10 and self.drag_tile in self.players[self.current_player_index].tiles_prev: #z planszy na pulpit
                    # Append the tile to the corresponding index on the board
                    self.players[self.current_player_index].tiles.append(self.drag_tile)
                elif self.drag_tile not in self.players[self.current_player_index].tiles and row >= 10 and not self.drag_tile in self.players[self.current_player_index].tiles_prev: #wzięcie nieswojego klocka
                    print("Nie można przeciągać nieswojego klocka na pulpit!")
                    pos = self.snap_to_grid(QPointF(self.sceneRect().width() / 2 + self.width * 20 / 2, int(
                        round((self.sceneRect().height() - self.height * 2) / self.height)) * self.height))
                elif self.drag_tile not in self.players[self.current_player_index].tiles and row < 10: #zmiana pozycji na planszy
                    self.board[row, col] = self.drag_tile
                self.drag_tile.setPos(pos)
            if self.drag_tile in self.selected_tiles:
                for interval, tile in enumerate(self.selected_tiles):
                    pos = self.snap_to_grid(tile.pos())
                    # Get the index of the position where the tile is dropped
                    row = int(pos.y() / self.height)
                    col = int(pos.x() / self.width)
                    if tile in self.players[self.current_player_index].tiles and row < 10:
                        # Append the tile to the corresponding index on the board
                        self.board[row, col] = tile
                        self.players[self.current_player_index].tiles.remove(tile)
                    elif tile not in self.players[self.current_player_index].tiles and row >= 10 and self.drag_tile in self.players[self.current_player_index].tiles_prev: #z planszy na pulpit
                        # Append the tile to the corresponding index on the board
                        self.players[self.current_player_index].tiles.append(tile)
                    elif self.drag_tile not in self.players[
                        self.current_player_index].tiles and row >= 10 and not self.drag_tile in self.players[
                        self.current_player_index].tiles_prev:  # wzięcie nieswojego klocka
                        print("Nie można przeciągać nieswojego klocka na pulpit!")
                        pos = self.snap_to_grid(QPointF(self.sceneRect().width() / 2 + self.width * 20 / 2 + interval*self.width, int(
                            round((self.sceneRect().height() - self.height * 2) / self.height)) * self.height))
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
    #players = [Player("Player1"), Player("Player2"), Player("Player3"), Player("Player4")]
    players = [Player("Player1"), Player("Player2")]
    board = Board(view, players)
    view.setScene(board)
    view.setFixedSize(1810, 1020) # Set the fixed size of the view
    view.show()
    sys.exit(app.exec_())
