from __future__ import annotations
from abc import abstractmethod
from typing import Any, TypeVar, Generic
from deZent_demo.utils.config.config import *
from PySide6.QtGui import Qt, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QLabel, QAbstractButton, QGraphicsView


@dataclass
class Style(Config):
    pass

StyleTypeT = TypeVar('StyleTypeT', bound = Style)
class Styled(Generic[StyleTypeT]):
    
    def __init__(
        self,
        style: StyleTypeT,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._style: StyleTypeT = style
        self.on_style_change(style)

    def get_style(self) -> StyleTypeT:
        return self._style
    
    def set_style(self, style: StyleTypeT):
        if self._style == style:
            return
        self.on_style_change(style)
        self._style = style

    @abstractmethod
    def on_style_change(self, new_style: StyleTypeT) -> None:
        pass


### QGraphicsItems

@dataclass
class ColorStyle(Style):
    color: QColor = field(default_factory=lambda: QColor(Qt.GlobalColor.magenta))

@dataclass
class LineStyle(Style):
    pen: QPen = field(default_factory=lambda: QPen())

@dataclass
class BorderedStyle(Style):
    fill: QBrush = field(default_factory=lambda: QBrush())
    border: LineStyle = field(default_factory=lambda: LineStyle())

@dataclass
class TextStyle(BorderedStyle): # NOTE: QGraphicsSimpleTextItem has fill and border
    font: QFont = QFont('Arial', 12)

### QWidgets

@dataclass
class LabelStyle(Style): # TODO: LabelStyle == TextStyle? (QLabel, QGraphicsSimpleTextItem)
    alignment: Qt.AlignmentFlag = field(default_factory=lambda: Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    text_font: QFont = QFont('Arial', 12)
    text_format: Qt.TextFormat = field(default_factory=lambda: Qt.TextFormat.PlainText)
    text_word_wrap: bool = True

    def apply(self, target: QLabel) -> None:
        target.setFont(self.text_font)
        target.setAlignment(self.alignment)
        target.setTextFormat(self.text_format)
        target.setWordWrap(self.text_word_wrap)

@dataclass
class ButtonStyle(Style):
    # TODO: populate as needed
    def apply(self, target: QAbstractButton) -> None:
        pass

@dataclass
class GraphicsViewStyle(Style):
    background_color: ColorStyle =  field(default_factory=lambda: ColorStyle(QColor(Qt.GlobalColor.white)))

    def apply(self, target: QGraphicsView) -> None:
        target.setBackgroundBrush(self.background_color.color)