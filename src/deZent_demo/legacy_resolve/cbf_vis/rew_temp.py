from collections.abc import Iterator
from dataclasses import dataclass, field

from deZent_demo.zanon.counting_data_structure.counting_bloom_filter import CBloomFilter
from deZent_demo.ui.utils import *

import math
from typing import Iterable, TypeVar, ClassVar, override
from abc import abstractmethod
from bitarray.util import ba2int

from PySide6.QtCore import (
    QRectF,
    Qt,
    QLineF,
    QSizeF,
)
from PySide6.QtGui import (
    QPainter, 
    QColor, 
    QBrush, 
    QPen,
    QFont,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
    QGraphicsWidget,
)

@dataclass
class SceneSize():
    size: float = 1.0
    x_size: float = 1.0
    y_size: float = 1.0

@dataclass
class PlotBoundaries():
    x_min: float
    x_max: float
    y_min: float
    y_max: float

class PlotSectionFocusSeparatorStyle():
    section_scale: float = 0.62


class PlotSectionBarStyle():
    border_color: QColor = QColor(64, 64, 196)
    border_width: float = 0.0
    border_pen: QPen = QPen(
        border_color,
        border_width,
        Qt.PenStyle.NoPen,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin
    )
    infill_color: QColor = QColor(64, 64, 196)
    infill_brush: QBrush = QBrush(infill_color)

    section_scale: float = 1.0
    bar_width_scale: float = 0.62


class PlotSectionBarSecondaryStyle():
    section_scale: QSizeF = QSizeF(1.0, 1.0)
    bar_width_scale: float = 0.62

    border_color: QColor = QColor(64, 64, 64)
    border_width: float = 0.0
    border_pen: QPen = QPen(
        border_color,
        border_width,
        Qt.PenStyle.NoPen,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin
    )
    infill_color: QColor = QColor(64, 64, 64)
    infill_brush: QBrush = QBrush(infill_color)

class CBFPlotAxis(QGraphicsItem):
    unit_height: ClassVar[int] = 4
    bar_width: ClassVar[int] = 4
    bar_spacing: ClassVar[int] = 2

    z_layer: ClassVar[int] = -1

    line_width: ClassVar[int] = 4
    arrow_height: ClassVar[int] = 8
    arrow_width: ClassVar[int] = 8
    marker_width: ClassVar[int] = 8

    marker_label_axis_distance: ClassVar[int] = 4
    marker_label_font_size: ClassVar[int] = 1

    line_color: ClassVar[QColor] = QColor(Qt.GlobalColor.green)
    marker_label_font_color: ClassVar[QColor] = QColor(Qt.GlobalColor.green)

    marker_interval: ClassVar[int] = 10

    def __init__(self,
                 /,
                 min_value: int = 0,
                 max_value: int = 100,
                 vertical: bool = True,
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)

        self.vertical: bool = vertical

        self.min_value: int = min_value
        self.max_value: int = max_value
        
        self.unit_length: int = self.unit_height if self.vertical else (self.bar_width + self.bar_spacing)
        self.length: int = (self.max_value - self.min_value) * self.unit_length

        self.line_pen: QPen = QPen(
            self.line_color,
            self.line_width,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        )

        self.marker_label_brush: QBrush = QBrush(
            self.marker_label_font_color
        )

        self.arrow: GraphicsArrow = GraphicsArrow(QPoint(*self.__orient(0, -self.length)), QPoint(*self.__orient(0, -self.length - self.arrow_height)), self.arrow_width, line_pen=self.line_pen, parent=self)
        
        axis_line: QLine = QLine(
            *self.__orient(0, 0),
            *self.__orient(0, -self.length),
        )
        self.line: QGraphicsLineItem = QGraphicsLineItem(axis_line, parent=self)
        self.line.setPen(self.line_pen)

        self.markers: list[QGraphicsLineItem] = []
        self.marker_labels: list[QGraphicsSimpleTextItem] = []

        self.__add_marker(self.min_value)
        self.__add_marker(self.max_value)
        begin_marker_value: int = self.min_value + (self.marker_interval - (self.min_value % self.marker_interval))
        for i in range((self.max_value - self.min_value) // self.marker_interval):
            marker_value: int = begin_marker_value * (i + 1)
            self.__add_marker(marker_value)

        self.setZValue(self.z_layer)

    def __add_marker(self, value: int) -> None:
        marker: QGraphicsLineItem = QGraphicsLineItem(
            *self.__orient(- int(self.marker_width / 2), - value * self.unit_length),
            *self.__orient(+ int(self.marker_width / 2), - value * self.unit_length),
            parent=self
        )
        marker.setPen(self.line_pen)
        self.markers.append(marker)

        marker_label: QGraphicsSimpleTextItem = QGraphicsSimpleTextItem(
            f"{value}",
            parent=self
        )
        marker_label.setBrush(self.marker_label_brush)
        marker_label_font: QFont = marker_label.font()
        marker_label_font.setPointSize(self.marker_label_font_size)

        text_aabb: QRectF = marker_label.boundingRect()
        if self.vertical:
            marker_label.setPos(
                - (self.marker_width / 2) - self.marker_label_axis_distance - text_aabb.width(),
                - value * self.unit_length - (text_aabb.height() / 2)
            )
        else:
            marker_label.setPos(
                + value * self.unit_length - (text_aabb.width() / 2),
                + (self.marker_width / 2) + self.marker_label_axis_distance
            )
        self.marker_labels.append(marker_label)

    
    TypeNameT = TypeVar("TypeNameT", int, float)
    def __orient(self, v_x: TypeNameT, v_y: TypeNameT) -> tuple[TypeNameT, TypeNameT]:
        return (v_x, v_y) if self.vertical else (- v_y, - v_x)

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              /,
              widget: QWidget | None = None) -> None:
        
        self.line.paint(painter, option, widget)

        for marker in self.markers:
            marker.paint(painter, option, widget)

    @override
    def boundingRect(self) -> QRectF:
        x_size: int = max(self.arrow_width,self.marker_width)
        aabb: QRectF = QRectF(
            - int(x_size / 2), 0,
            + int(x_size / 2), self.length
        )
        return aabb

class PlotFocus(set[int]):
    
    def __init__(self, iterable: Iterable[int]) -> None:
        self._set: set[int] = set[int](iterable)
        self._sorted: list[int] = []
        self._dirty: bool = True

    def add(self, element: int) -> None:
        self._dirty = True
        self._set.add(element)

    def remove(self, element: int) -> None:
        self._dirty = True
        self._set.remove(element)

    def __contains__(self, o: object) -> bool:
        return self._set.__contains__(o)

    def __iter__(self) -> Iterator[int]:
        if self._dirty:
            self._dirty = False
            self._sorted = sorted(self._set)
        return self._sorted.__iter__()

    def __len__(self) -> int:
        return self._set.__len__()
    
class PlotSection(QGraphicsItem):
    def __init__(self, /, parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)

    @abstractmethod
    def size_relative(self) -> QRectF:
        pass

    
    def size(self) -> QRectF:
        pass

class PlotSectionAxisStyle():
    line_color: QColor = QColor(Qt.GlobalColor.white)
    line_width: float = 1.0
    line_pen: QPen = QPen(
        line_color,
        line_width,
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin
    )
    arrow_scale: float = 0.05
    marker_color: QColor = QColor(Qt.GlobalColor.gray)
    marker_line_width: float = 1.0
    marker_scale: float = 0.02
    marker_pen: QPen = QPen(
        marker_color,
        marker_line_width,
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin
    )
    marker_interval_scale: float = 0.1
    marker_label_color: QColor = QColor(Qt.GlobalColor.darkGray)
    marker_label_brush: QBrush = QBrush(marker_label_color)
    marker_label_spacing_scale: float = 0.04
    marker_label_font_size: int = 1

    section_scale: float = 1.0

class PlotSectionYAxis(PlotSection):
    def __init__(self,
                    boundaries: PlotBoundaries,
                    style: PlotSectionAxisStyle = PlotSectionAxisStyle(),
                    size: SceneSize | None = None,
                    parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent=parent)
        self.__init_axis(boundaries, style, size)

    def __init_axis(self,
                   boundaries: PlotBoundaries,
                   style: PlotSectionAxisStyle,
                   size: SceneSize | None) -> None:

        self._plot_boundaries: PlotBoundaries = boundaries
        self._size: SceneSize | None = size
        self._style: PlotSectionAxisStyle = style

        self.axis_line: QGraphicsLineItem = QGraphicsLineItem(parent=self)
        self.markers: dict[int, QGraphicsLineItem] = { }
        self.marker_labels: dict[int, QGraphicsSimpleTextItem] = { }

        self.axis_size: float = (self._plot_boundaries.y_max - self._plot_boundaries.y_min)
        self.arrow_len: float = self.axis_size * self._style.arrow_scale
        self.marker_width: float = self.axis_size * self._style.marker_scale
        self.marker_spacing: float = self.axis_size * self._style.marker_label_spacing_scale
        self.marker_interval: float = self.axis_size * self._style.marker_interval_scale

        self.axis_len: float = self.axis_size

        if self._size is not None:
            self.axis_len = self.axis_size * self._size.y_size
            self.arrow_len *= self._size.y_size
            self.marker_width *= self._size.size
            self.marker_spacing *= self._size.size

        self.axis_line = QGraphicsLineItem(QLineF(
            0, 0,
            0, - self.axis_len,
        ), parent=self)
        self.axis_line.setPen(self._style.line_pen)
        self.arrow: GraphicsArrow = GraphicsArrow(QPointF(), QPointF(0, - self.arrow_len), self.marker_width, line_pen=self._style.line_pen, parent=self)

        marker_value: float = math.floor(self._plot_boundaries.y_min)
        for _ in range(math.ceil(self.axis_size / self.marker_interval) + 1):
            self.__set_yaxis_marker(int(marker_value))
            marker_value += self.marker_interval

    def __set_yaxis_marker(self, value: int) -> None:
            y_size: float = self._size.y_size if self._size else 1.0
            marker: QGraphicsLineItem = QGraphicsLineItem(
                - self.marker_width / 2, value * y_size,
                + self.marker_width / 2, value * y_size,
                parent=self
            )
            marker.setPen(self._style.marker_pen)
            self.markers[value] = marker
    
            marker_label: QGraphicsSimpleTextItem = QGraphicsSimpleTextItem(
                f"{value}",
                parent=self
            )
            marker_label.setBrush(self._style.marker_label_brush)
            marker_label_font: QFont = marker_label.font()
            marker_label_font.setPointSize(self._style.marker_label_font_size)
    
            text_aabb: QRectF = marker_label.boundingRect()
            marker_label.setPos(
                - (self.marker_width / 2) - self.marker_spacing - text_aabb.width(),
                value * y_size - (text_aabb.height() / 2)
            )
            self.marker_labels[value] = marker_label

class PlotSectionFocusSeparator(PlotSection):
    pass
   
class PlotSectionBar(PlotSection):

    def __init__(self,
                 value: int,
                 style: PlotSectionBarStyle = PlotSectionBarStyle(),
                 size: SceneSize | None = None,
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent=parent)
        self.__init_bar(value, style, size)
    
    def __init_bar(self,
                   value: int,
                   style: PlotSectionBarStyle,
                   size: SceneSize | None) -> None:
        self._value: int = value
        self._size: SceneSize | None = size
        self._style: PlotSectionBarStyle = style

        self._section_size: float = 0
        self._bar_width: float = 0
        self._bar_spacing: float = 0
        if self._size is not None:
            self._section_size = self._size.x_size * self._style.section_scale
            self._bar_width = self._section_size * self._style.bar_width_scale
            self._bar_spacing = self._section_size * (1.0 - self._style.bar_width_scale)

        self._rect: QGraphicsRectItem = QGraphicsRectItem()
        self._rect.setPen(self._style.border_pen)
        self._rect.setBrush(self._style.infill_brush)

        if self._size is not None:
            self._rect.setRect(QRectF(
                - self._bar_width / 2, -(self._value * self._size.y_size),
                + self._bar_width / 2, 0.0
            ))
            self._rect.setPos(self._bar_spacing / 2, 0)
    
    def set_value(self, value: int) -> None:
        self.__init_bar(value, self._style, self._size)

    @override
    def size_relative(self) -> QRectF:
        return self._style.section_scale

    @override
    def size(self) -> QRectF:
        return self._section_size

    def boundingRect(self) -> QRectF:
        
        return 