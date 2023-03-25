from PySide2.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QPushButton, QMessageBox
from PySide2.QtGui import QColor, QBrush, QPen, QFont, QPainter
from PySide2.QtCore import Qt, QRectF, QPointF
import random
import numpy as np
import sys

class Tile(QGraphicsItem):
    def __init__(self, colour, numer, is_joker=False):
        super().__init__()
        self.width = 50
        self.height = 80
        self.rect = QRectF(0, 0, self.width, self.height)  # Ustawienie wymiarów klocka
        self.colour = colour  # colour klocka
        self.numer = numer  # Numer klocka
        self.is_joker = is_joker

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        # Rysowanie klocka
        painter.setBrush(QBrush(QColor(255, 249, 213)))
        painter.setPen(QPen(Qt.black))
        painter.drawRect(self.rect)

        # Rysowanie numeru klocka
        painter.setFont(QFont('Arial', 16))
        if(self.is_joker):
            numer_text = 'J'
        else:
            numer_text = str(self.numer)
        numer_rect = painter.fontMetrics().boundingRect(numer_text)
        numer_x = self.rect.center().x() - numer_rect.width() / 2
        numer_y = self.rect.center().y() - numer_rect.height() / 4
        painter.setPen(QPen(self.colour))
        painter.drawText(QPointF(numer_x, numer_y), numer_text)

class ForegroundItem(QGraphicsItem):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.rect = QRectF(0, 0, self.width, self.height)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(QColor(255, 255, 255, 0))) # Set the brush color to transparent
        painter.drawRect(self.rect)

class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1800, 1000)
        self.setBackgroundBrush(QBrush(QColor(238, 238, 238)))
        self.tiles = []
        self.user_tiles = []
        self.board = np.full((15, 40), None, dtype=object)
        self.groups = []
        self.width = 50
        self.height = 80
        self.foreground_item = ForegroundItem(self.width * 20, self.height * 2) # Create an instance of ForegroundItem
        self.foreground_item.setPos(self.sceneRect().width() / 2 - self.width * 20 / 2, int(round((self.sceneRect().height() - self.height * 2)/self.height))*self.height)
        self.addItem(self.foreground_item) # Add the foreground item to the scene

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
        self.accept_move.clicked.connect(self.check_move)  # Connect the button to a function that will sort tiles by color

        # Add a button to the top right corner of the QGraphicsView for sorting tiles by number
        self.sort_by_number_button = QPushButton('Sort by Number', view)
        self.sort_by_number_button.setGeometry(1600, 70, 120, 30)  # Set the button position
        self.sort_by_number_button.clicked.connect(
        self.sort_tiles_by_number)  # Connect the button to a function that will sort tiles by number

        self.generate_tiles()
    def check_move(self):
        #board_bin = np.where(self.board != None)
        #print(board_bin)
        # indices = np.where(
        #     np.logical_and(self.board != None, np.roll(self.board != None, -1, axis=1) & np.roll(self.board != None, -2, axis=1)))
        #
        # # Print the indices of the non-None elements that form a group of three or more
        # print(indices[0])
        if self.is_every_element_grouped():
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
                            print(unique_values)
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


                    for tile in group:
                        print(tile.numer)
                        print(tile.colour)
        else:
            print("nah")
            msg_box = QMessageBox()
            msg_box.setText("Układ musi zawierać co najmniej 3 klocki!")
            #msg_box.setWindowTitle("Message Box")
            msg_box.setStandardButtons(QMessageBox.Ok)

            response = msg_box.exec_()
            return


    def is_every_element_grouped(self):
        board = self.board
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
            #print(non_none_indices[0][i])
            #print(non_none_indices[1][i])
            #print(non_none_indices[0].size-1)
            #print(i)
            #print(counter)

            if counter == 0:
                counter += 1
                colors = []
                group = [board[non_none_indices[0][i],non_none_indices[1][i]]]
                #groups.append(board[non_none_indices])
                print("eeee")
            elif non_none_indices[0][i] == y and non_none_indices[1][i] == x+1: #sprawdzanie czy obok siebie
                counter += 1
                group.append(board[non_none_indices[0][i],non_none_indices[1][i]])
                if i == non_none_indices[0].size-1 and counter >= 3:
                    self.groups.append(group)
                    print("aaaa")
                print("ddddd")
            elif (not (non_none_indices[0][i] == y and non_none_indices[1][i] == x+1) or i == non_none_indices[0].size) and counter <3:
                #print(counter)

                print("ccccc")
                return False
            elif not (non_none_indices[0][i] == y and non_none_indices[1][i] == x+1) and counter >= 3:
                counter = 1
                self.groups.append(group)
                group = [board[non_none_indices[0][i], non_none_indices[1][i]]]
                colors = []
                print("bbbb")



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
        self.user_tiles = sorted(self.user_tiles, key=lambda tile: colors.index(tile.colour))

        for index, tile in enumerate(self.user_tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.width,
                                                             int(index / 20) * self.height))

    def sort_tiles_by_number(self):
        self.user_tiles = sorted(self.user_tiles, key=lambda tile: tile.numer)

        for index, tile in enumerate(self.user_tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 20) * self.width,
                                                             int(index / 20) * self.height))

    def draw_tile(self):
        tile = self.tiles.pop()
        self.user_tiles.append(tile)
        # Set the position of the tile relative to the ForegroundItem
        tile.setPos(self.foreground_item.pos() + QPointF(((len(self.user_tiles) - 1) % 20) * self.width,
                                                         int((len(self.user_tiles) - 1) / 20) * self.height))
        self.addItem(tile)

    def generate_tiles(self):
        # Generowanie klocków
        colours = [Qt.red, Qt.blue, QColor(254, 176, 0), Qt.black]
        for colour in colours:
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
        for i in range(14):
            self.draw_tile()

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
                break


    def mouseMoveEvent(self, event):
        # Przeciąganie klocka
        if hasattr(self, 'drag_tile') and self.drag_tile is not None:
            pos = event.scenePos() - self.drag_tile.boundingRect().center()
            self.drag_tile.setPos(pos)

    def mouseReleaseEvent(self, event):
        # Move the dropped tile to the closest grid position
        if hasattr(self, 'drag_tile') and self.drag_tile is not None:
            pos = self.snap_to_grid(self.drag_tile.pos())
            # Get the index of the position where the tile is dropped
            row = int(pos.y() / self.height)
            col = int(pos.x() / self.width)
            #print(row)
            #print(col)
            if self.drag_tile in self.user_tiles and row < 10:
                # Append the tile to the corresponding index on the board
                self.board[row, col] = self.drag_tile
                self.user_tiles.remove(self.drag_tile)
            #elif self.drag_tile in self.board and row >= 10:
            elif self.drag_tile not in self.user_tiles and row >= 10:
                # Append the tile to the corresponding index on the board
                #self.board
                self.user_tiles.append(self.drag_tile)
            #elif self.drag_tile in self.board and row < 10:
            elif self.drag_tile not in self.user_tiles and row < 10:
                self.board[row, col] = self.drag_tile
            self.drag_tile.setPos(pos)
            self.drag_tile = None
        #print(self.board)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QGraphicsView()
    board = Board(view)
    view.setScene(board)
    view.setFixedSize(1800, 1000) # Set the fixed size of the view
    view.show()
    sys.exit(app.exec_())
