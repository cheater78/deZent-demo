from deZent_demo.utils.config.config import *
from deZent_demo.ui.style.style import *

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
)

@dataclass
class ControlOverlayContent():
    description_heading: str = "<current description heading>"
    description: str = "<current description>"
    next_step: str = "<next step>"
    next_step_button: str = "<next>"

@dataclass
class ControlOverlayStyle(Style):
    description_heading_label_style: LabelStyle = field(default_factory=lambda: LabelStyle(
        text_font=QFont('Arial', 12, weight=QFont.Weight.Bold)
    ))
    description_label_style: LabelStyle = field(default_factory=lambda: LabelStyle(
        text_font=QFont('Arial', 10, weight=QFont.Weight.Normal)
    ))
    next_step_label_style: LabelStyle = field(default_factory=lambda: LabelStyle())
    next_step_button_style: ButtonStyle = field(default_factory=lambda: ButtonStyle())

class ControlOverlay(Styled[ControlOverlayStyle], QWidget):

    def __init__(self,
                 content: ControlOverlayContent = ControlOverlayContent(),
                 style: ControlOverlayStyle = ControlOverlayStyle(),
                 parent: QWidget | None = None) -> None:
        
        self._description_heading_label: QLabel = QLabel()
        self._description_label: QLabel = QLabel()
        self._next_step_label: QLabel = QLabel()
        self._next_step_button: QPushButton = QPushButton()
        
        super().__init__(
            style=style,
            parent=parent,
        )
        
        self._layout: QGridLayout = QGridLayout(self)
        self._layout.addWidget(self._description_heading_label, 0, 0, 1, 2)
        self._layout.addWidget(self._description_label,         1, 0, 2, 2)
        self._layout.addWidget(self._next_step_label,           3, 0, 1, 1)
        self._layout.addWidget(self._next_step_button,          3, 1, 1, 1)

        self.set_content(content)

    def set_content(self, content: ControlOverlayContent) -> None:
        self._description_heading_label.setText(content.description_heading)
        self._description_label.setText(content.description)
        self._next_step_label.setText(content.next_step)
        self._next_step_button.setText(content.next_step_button)

    @override
    def on_style_change(self, new_style: ControlOverlayStyle) -> None:
        new_style.description_heading_label_style.apply(self._description_heading_label)
        new_style.description_label_style.apply(self._description_label)
        new_style.next_step_label_style.apply(self._next_step_label)
        new_style.next_step_button_style.apply(self._next_step_button)