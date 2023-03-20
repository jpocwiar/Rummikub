from PySide2.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QPushButton
from PySide2.QtGui import QColor, QBrush, QPen, QFont, QPainter
from PySide2.QtCore import Qt, QRectF, QPointF
import random

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
        self.width = 50
        self.height = 80
        self.foreground_item = ForegroundItem(self.width * 10, self.height * 2) # Create an instance of ForegroundItem
        self.foreground_item.setPos(self.sceneRect().width() / 2 - self.width * 10 / 2, int(round((self.sceneRect().height() - self.height * 2)/self.height))*self.height)
        self.addItem(self.foreground_item) # Add the foreground item to the scene

        # Add a button to the top right corner of the QGraphicsView
        self.button = QPushButton('Draw Tile', view)
        self.button.setGeometry(1700, 10, 90, 30)  # Set the button position
        self.button.clicked.connect(self.draw_tile)  # Connect the button to a function that will draw a tile


    def draw_tile(self):
        tile = self.tiles.pop()
        self.user_tiles.append(tile)
        print(len(self.user_tiles))
        tile.setPos(((len(self.user_tiles) - 1) % 10) * self.width, int((len(self.user_tiles) - 1) / 10) * self.height)
        #self.user_tiles_group.addToGroup(tile)
        #self.addItem(self.user_tiles_group)
        #self.addItem(self.foreground_item)
        self.addItem(tile)

    def generate_tiles(self):
        # Generowanie klocków
        colours = [Qt.red, Qt.blue, Qt.yellow, Qt.black]
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
        x = int(round(pos.x() / self.width)) * self.width
        y = int(round(pos.y() / self.height)) * self.height
        return QPointF(x, y)


    def mousePressEvent(self, event):
        # Znajdowanie klocka, który został kliknięty
        items = self.items(event.scenePos())
        for item in items:
            if isinstance(item, Tile):
                self.drag_tile = item
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
            self.drag_tile.setPos(pos)
            self.drag_tile = None

if __name__ == '__main__':
    app = QApplication([])
    view = QGraphicsView()
    board = Board()

    view.setScene(board)
    board.generate_tiles()
    view.show()
    app.exec_()
