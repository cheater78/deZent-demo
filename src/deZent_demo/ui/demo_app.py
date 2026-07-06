from __future__ import annotations
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
)
from PySide6.QtCore import QRect
from .scene import dZGraphScene
from .view import PanningView

class DemoWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Local deZent demo")
        self.set_initial_window_size()

        scene = dZGraphScene()
        view = PanningView(scene)
        self.setCentralWidget(view)

    def set_initial_window_size(self, width_ratio: float = 0.7, height_ratio: float = 0.7) -> None:
        screen = self.screen()
        geom = screen.availableGeometry()

        w = int(geom.width() * width_ratio)
        h = int(geom.height() * height_ratio)

        x = geom.x() + (geom.width() - w) // 2
        y = geom.y() + (geom.height() - h) // 2

        self.setGeometry(QRect(x, y, w, h))

class DemoApp(QApplication):

    def __init__(self) -> None:
        super().__init__(sys.argv)

        self.demo_window: DemoWindow = DemoWindow()

    def run(self) -> None:
        self.demo_window.show()

        exit_code: int = self.exec()
        sys.exit(exit_code)

    