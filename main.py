from PySide2.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QPushButton
from PySide2.QtGui import QColor, QBrush, QPen, QFont, QPainter
from PySide2.QtCore import Qt, QRectF, QPointF
import random
import numpy as np

class Tile(QGraphicsItem):
    def __init__(self, colour, numer):
        super().__init__()
        self.width = 50
        self.height = 80
        self.rect = QRectF(0, 0, self.width, self.height)  # Ustawienie wymiarów klocka
        self.colour = colour  # colour klocka
        self.numer = numer  # Numer klocka

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        # Rysowanie klocka
        painter.setBrush(QBrush(QColor(255, 249, 213)))
        painter.setPen(QPen(Qt.black))
        painter.drawRect(self.rect)

        # Rysowanie numeru klocka
        painter.setFont(QFont('Arial', 16))
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
        self.width = 50
        self.height = 80
        self.foreground_item = ForegroundItem(self.width * 10, self.height * 2) # Create an instance of ForegroundItem
        self.foreground_item.setPos(self.sceneRect().width() / 2 - self.width * 10 / 2, int(round((self.sceneRect().height() - self.height * 2)/self.height))*self.height)
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

    def check_move(self):
        #board_bin = np.where(self.board != None)
        #print(board_bin)
        # indices = np.where(
        #     np.logical_and(self.board != None, np.roll(self.board != None, -1, axis=1) & np.roll(self.board != None, -2, axis=1)))
        #
        # # Print the indices of the non-None elements that form a group of three or more
        # print(indices[0])
        if self.is_every_element_grouped():
            print("youp")
        else:
            print("nah")


    def is_every_element_grouped(self):
        board = self.board
        # Get indices of non-None elements
        non_none_indices = np.where(board != None)
        print(non_none_indices)
        # Iterate over each index in the non_none_indices array
        for i in range(len(non_none_indices[0])):
            row = non_none_indices[0][i]
            col = non_none_indices[1][i]

            neighbors = []

            # Check if the current tile has at least two neighbors in adjacent horizontal axes
            if col > 0 and board[row][col - 1] is not None:
                neighbors.append(board[row][col - 1])
            if col < len(board[0]) - 1 and board[row][col + 1] is not None:
                neighbors.append(board[row][col + 1])

            # If the current tile has less than two neighbors, return False
            if len(neighbors) < 2:
                return False

            # Check if the current tile has the same index as its neighbors in the vertical axis
            for neighbor in neighbors:
                if neighbor is not None and neighbor.index != board[row][col].index:
                    return False

        # If all tiles have at least two neighbors and are in a group of three or more, return True
        return True

    def sort_tiles_by_color(self):
        colors = [Qt.red, Qt.blue, QColor(254, 176, 0), Qt.black]
        self.user_tiles = sorted(self.user_tiles, key=lambda tile: colors.index(tile.colour))

        for index, tile in enumerate(self.user_tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 10) * self.width,
                                                             int(index / 10) * self.height))

    def sort_tiles_by_number(self):
        self.user_tiles = sorted(self.user_tiles, key=lambda tile: tile.numer)

        for index, tile in enumerate(self.user_tiles):
            tile.setPos(self.foreground_item.pos() + QPointF((index % 10) * self.width,
                                                             int(index / 10) * self.height))

    def draw_tile(self):
        tile = self.tiles.pop()
        self.user_tiles.append(tile)
        # Set the position of the tile relative to the ForegroundItem
        tile.setPos(self.foreground_item.pos() + QPointF(((len(self.user_tiles) - 1) % 10) * self.width,
                                                         int((len(self.user_tiles) - 1) / 10) * self.height))
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
            print(row)
            print(col)
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
    app = QApplication([])
    view = QGraphicsView()
    board = Board()

    view.setScene(board)
    board.generate_tiles()
    view.show()
    app.exec_()
