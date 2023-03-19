from PySide2.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem
from PySide2.QtGui import QColor, QBrush, QPen
from PySide2.QtCore import Qt, QRectF

class Klocek(QGraphicsItem):
    def __init__(self, kolor, numer):
        super().__init__()
        self.rect = QRectF(0, 0, 50, 80)  # Ustawienie wymiarów klocka
        self.kolor = kolor  # Kolor klocka
        self.numer = numer  # Numer klocka

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        # Rysowanie klocka
        painter.setBrush(QBrush(self.kolor))
        painter.setPen(QPen(Qt.black))
        painter.drawRect(self.rect)

class Plansza(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 500, 500)  # Ustawienie wymiarów planszy
        self.setBackgroundBrush(QBrush(QColor(238, 238, 238)))  # Ustawienie tła planszy
        self.klocki = []  # Lista klocków

    def generuj_klocki(self):
        # Generowanie klocków
        kolory = [Qt.red, Qt.blue, Qt.yellow, Qt.green, Qt.black, Qt.magenta, Qt.cyan]
        for kolor in kolory:
            for numer in range(1, 14):
                klocek = Klocek(kolor, numer)
                klocek.setFlag(QGraphicsItem.ItemIsMovable)  # Ustawienie możliwości przesuwania klocka
                self.addItem(klocek)
                self.klocki.append(klocek)

    def mousePressEvent(self, event):
        # Znajdowanie klocka, który został kliknięty
        for klocek in self.klocki:
            if klocek.boundingRect().contains(event.scenePos()):
                self.drag_klocek = klocek
                break

    def mouseMoveEvent(self, event):
        # Przeciąganie klocka
        if hasattr(self, 'drag_klocek'):
            pos = event.scenePos() - self.drag_klocek.boundingRect().center()
            self.drag_klocek.setPos(pos)

    def mouseReleaseEvent(self, event):
        # Usuwanie klocka, jeśli zostanie upuszczony poza planszą
        if hasattr(self, 'drag_klocek'):
            if not self.sceneRect().contains(self.drag_klocek.sceneBoundingRect()):
                self.removeItem(self.drag_klocek)
                self.klocki.remove(self.drag_klocek)

if __name__ == '__main__':
    app = QApplication([])
    view = QGraphicsView()
    plansza = Plansza()
    plansza.generuj_klocki()
    view.setScene(plansza)
    view.show()
    app.exec_()
