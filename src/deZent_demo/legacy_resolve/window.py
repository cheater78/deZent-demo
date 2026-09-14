from __future__ import annotations
from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsView,
)
from PySide6.QtCore import QRect

class Window(QMainWindow):

    def __init__(self,
                 title: str,
                 view: QGraphicsView):
        super().__init__()

        self.setWindowTitle(title)
        self.set_initial_window_size()
        self.setCentralWidget(view)

    def set_initial_window_size(self, width_ratio: float = 0.7, height_ratio: float = 0.7) -> None:
        screen = self.screen()
        geom = screen.availableGeometry()

        w = int(geom.width() * width_ratio)
        h = int(geom.height() * height_ratio)

        x = geom.x() + (geom.width() - w) // 2
        y = geom.y() + (geom.height() - h) // 2

        self.setGeometry(QRect(x, y, w, h))