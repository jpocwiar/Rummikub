from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import numpy as np
import graphics_rc

class Timer(QGraphicsItem):
    def __init__(self, board, parent=None):
        super().__init__(parent)
        self.time_left = 30000  # milliseconds
        self.font = QFont('Arial', 24)

        self.pixmap = QPixmap(":/clock/clock.png")
        self.board = board

    def boundingRect(self):
        return QRectF(0, 0, 200, 200)

    def paint(self, painter, option, widget):
        painter.drawPixmap(0, 0, self.pixmap)
        painter.setPen(QPen(QColor(255, 0, 0), 5, Qt.SolidLine, Qt.RoundCap))
        angle = (self.time_left / 1000) / 30 * 270 + 135
        length = 100
        x = 100 + length * np.cos(np.radians(angle))
        y = 100 + length * np.sin(np.radians(angle))
        painter.drawLine(QPointF(100, 100), QPointF(x, y))
        # rysowanie podziałki, można odkomentować jeżeli nie przeszkadza nam pętla
        painter.setPen(QPen(QColor(0, 0, 0), 3, Qt.SolidLine, Qt.RoundCap))
        painter.setRenderHint(QPainter.Antialiasing, True)
        #if self.time_left % 10 == 0:
        for i in range(0, 31):
            angle = 135 + i * 9
            x1 = 100 + 80 * np.cos(np.radians(angle))
            y1 = 100 + 80 * np.sin(np.radians(angle))
            x2 = 100 + 90 * np.cos(np.radians(angle))
            y2 = 100 + 90 * np.sin(np.radians(angle))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        painter.setFont(self.font)
        painter.setPen(QPen(QColor(0, 0, 0), 4))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.get_time_string())
        painter.setPen(QPen(QColor(155, 0, 0), 8, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(0, 0, 200, 200, 225 * 16, ((-self.time_left / 1000) / 30 * 270) * 16)



    def get_time_string(self):
        seconds = self.time_left // 1000
        milliseconds = (self.time_left % 1000) // 1
        return f'{seconds:02d}:{milliseconds:03d}'

    def update_time(self):
        self.time_left -= 5
        if self.time_left % 20 == 0 and self.time_left <= 0 and not self.board.timed_out: #pierwszy if po to, żeby się z rozpędu kilka razy nie wywoływał
            self.time_left = 30000
            #if not self.board.timed_out:

            self.board.timed_out = True
            self.board.make_move()
        #if self.time_left % 10:
        self.update()