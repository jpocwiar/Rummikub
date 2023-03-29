from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


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

    def setPosFromIndices(self, i, j):
        self.setPos(j * self.width, i * self.height)