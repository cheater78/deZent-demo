
from PySide6.QtGui import QPaintEvent
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
)

class ControlOverlay(QWidget):

    def __init__(self,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._layout: QGridLayout = QGridLayout(self)

        self._description_label: QLabel = QLabel("<current description>")

        self._next_step_label: QLabel = QLabel("<next step>")
        self._next_step_button: QPushButton = QPushButton("->")

        self._layout.addWidget(self._description_label, 0, 0, 1, 2)

        self._layout.addWidget(self._next_step_label, 1, 0, 1, 1)
        self._layout.addWidget(self._next_step_button, 1, 1, 1, 1)

    