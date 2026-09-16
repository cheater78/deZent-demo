from __future__ import annotations
from abc import abstractmethod
from typing import Any, TypeVar, Generic
from deZent_demo.utils.config.config import *
from PySide6.QtGui import QColor, QPen, QBrush

@dataclass
class Style(Config):
    pass

@dataclass
class ColorStyle(Style):
    color: QColor = field(default_factory=lambda: QColor())

@dataclass
class LineStyle(Style):
    pen: QPen = field(default_factory=lambda: QPen())

@dataclass
class BorderedStyle(Style):
    fill: QBrush = field(default_factory=lambda: QBrush())
    border: LineStyle = field(default_factory=lambda: LineStyle())

# TODO: TextStyle

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

    def get_style(self):
        return self._style
    
    def set_style(self, style: StyleTypeT):
        self.on_style_change(style)
        self._style = style

    @abstractmethod
    def on_style_change(self, new_style: StyleTypeT) -> None:
        pass

