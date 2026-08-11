
from deZent_demo.zanon.counting_data_structure.counting_bloom_filter import CBloomFilter
from deZent_demo.ami.measurement import MeasurementKey
from deZent_demo.ui.utils import *

from enum import Enum
import math
from typing import TypeVar, ClassVar, override
from bitarray.util import ba2int

from PySide6.QtCore import (
    QRect, QRectF,
    Qt,
    QLine,
    QSizeF,
)
from PySide6.QtGui import (
    QVector2D,
    QPainter, 
    QColor, 
    QBrush, 
    QPen,
    QFont,
    QPainterPath,
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

class CBFPlotBar(QGraphicsRectItem):
    unit_height: ClassVar[int] = 4
    bar_width: ClassVar[int] = 4

    z_layer: ClassVar[int] = 1

    bar_border_color: ClassVar[QColor] = QColor(Qt.GlobalColor.blue)
    bar_border_width: ClassVar[int] = 0
    
    bar_infill_color: ClassVar[QColor] = QColor(Qt.GlobalColor.darkBlue)


    def __init__(self,
                 value: int = 0,
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent=parent)

        border_pen: QPen = QPen(
            self.bar_border_color,
            self.bar_border_width
        )
        self.setPen(border_pen)

        infill_brush: QBrush = QBrush(
            self.bar_infill_color
        )
        self.setBrush(infill_brush)

        self._value: int = value
        self.set_value(value)

        self.setZValue(self.z_layer)
    
    def set_value(self, value: int) -> None:
        self._value: int = value
        bar_rect: QRectF = QRectF(
            - self.bar_width / 2, 0.0,
            + self.bar_width / 2, -(self._value * self.unit_height)
        )
        self.setRect(bar_rect)



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

        self.arrow: Arrow = Arrow(QPoint(*self.__orient(0, -self.length)), QPoint(*self.__orient(0, -self.length - self.arrow_height)), self.arrow_width, line_pen=self.line_pen, parent=self)
        
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

Scope = list[int]

class ScopedCBFPlotAxis(QGraphicsItem):
    unit_height: ClassVar[int] = 4
    bar_width: ClassVar[int] = 4
    bar_spacing: ClassVar[int] = 2

    scope_spacing: ClassVar[int] = 4

    z_layer: ClassVar[int] = -1

    line_width: ClassVar[int] = 4
    arrow_height: ClassVar[int] = 8
    arrow_width: ClassVar[int] = 8
    marker_width: ClassVar[int] = 8

    marker_label_axis_distance: ClassVar[int] = 4
    marker_label_font_size: ClassVar[int] = 1

    line_color: ClassVar[QColor] = QColor(Qt.GlobalColor.green)
    marker_label_font_color: ClassVar[QColor] = QColor(Qt.GlobalColor.green)

    def __init__(self,
                     /,
                     scope: Scope,
                     max_value: int,
                     parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)

        self.max_value: int = max_value
        self.scope: Scope = scope
                
        self.unit_length: int = self.bar_width + self.bar_spacing
        self.length: int = (len(self.scope) * 3 + 2) * self.unit_length

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

        self.arrow: Arrow = Arrow(QPoint(0, -self.length), QPoint(0, -self.length - self.arrow_height), self.arrow_width, line_pen=self.line_pen, parent=self)

        self.axis_lines: list[QGraphicsLineItem] = []
        self.axis_spacer_lines: list[QGraphicsLineItem] = []
        self.markers: list[QGraphicsLineItem] = []
        self.marker_labels: list[QGraphicsSimpleTextItem] = []

        def spacer_lines(y: int, x1: int, x2: int) -> list[QGraphicsLineItem]:
            size: int = x2 - x1
            segment_size: int = size // 5

            line1: QLine = QLine(
                x1 + 1 * segment_size, y,
                x1 + 2 * segment_size, y,
            )

            line2: QLine = QLine(
                x1 + 3 * segment_size, y,
                x1 + 4 * segment_size, y,
            )

            lines: list[QGraphicsLineItem] = []
            lines.append(QGraphicsLineItem(
                line1,
                parent=self
            ))
            lines[-1].setPen(self.line_pen)
            lines.append(QGraphicsLineItem(
                line2,
                parent=self
            ))
            lines[-1].setPen(self.line_pen)
            return lines

        x: int = 0
        self.__add_marker(0)
        self.axis_lines.append(QGraphicsLineItem(
            x, 0,
            self.bar_spacing, 0, parent=self
        ))
        self.axis_lines[-1].setPen(self.line_pen)
        x += self.bar_spacing

        self.axis_spacer_lines.extend(spacer_lines(0, x, x + self.scope_spacing))
        x += self.scope_spacing

        for index in self.scope:
            pass

        #TODO: questionable - maybe scopes are x axis + bars (partial diagrams)
        # push all code back into diagram - abstract primitives like arrow, x/y marker + label, bar?, scope_spacer!, but not axis as a whole
        # provide functions to add these things easily
        
        # final options:
        # full or k = 1,2,...


class CBFPlot(QGraphicsWidget):

    def __init__(self,
        cbf: CBloomFilter | None = None,
        parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent=parent)

        self.cbf: CBloomFilter | None = cbf

        self.scene_dimension: QSizeF = QSizeF(850, 250)

        # plot focus: show only specified bars, all if empty
        self.focus: set[int] = set[int]()
        self.focus_neighbors: int = 1
        self.focus_spacing_scale: float = 0.62 # TODO
        self.focus_spacing: float = 1 # TODO use focus_spacing_scale for a relative size

        # plot native dimensions
        self.x_min: float = 0
        self.x_max: float = 0
        self.y_min: float = 0
        self.y_max: float = 0
        self.__fit_to_cbf() # determine from data

        self.x_scale: float = self.scene_dimension.width() / (self.x_max - self.x_min) # size of an x-unit
        self.y_scale: float = self.scene_dimension.height() / (self.y_max - self.y_min) # size of an y-unit

        # bar config
        self.bars: dict[int, QGraphicsRectItem] = {}
        self.bar_border_color: QColor = QColor(Qt.GlobalColor.green)
        self.bar_border_width: float = 0.0 # TODO
        self.bar_border_pen: QPen = QPen(self.bar_border_color, self.bar_border_width)
        self.bar_infill_color: QColor = QColor(Qt.GlobalColor.darkGreen)
        self.bar_infill_brush: QBrush = QBrush(self.bar_infill_color)

        self.bar_width_scale: float = 0.62 # TODO
        self.bar_width: float = self.x_scale * self.bar_width_scale
        self.bar_spacing_scale: float = 1.0 - self.bar_width_scale
        self.bar_spacing: float = self.x_scale * self.bar_spacing_scale

        # axis config
        self.axis_color: QColor = QColor(Qt.GlobalColor.white)
        self.axis_line_width: float = 1 # TODO
        self.axis_line_pen: QPen = QPen(self.axis_color, self.axis_line_width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.axis_arrow_scale: float = 0.05
        self.axis_marker_color: QColor = QColor(Qt.GlobalColor.gray)
        self.axis_marker_width: float = 2 # TODO
        self.axis_marker_pen: QPen = QPen(self.axis_marker_color, self.axis_marker_width,
                    Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.axis_marker_label_color: QColor = QColor(Qt.GlobalColor.gray)
        self.axis_marker_label_brush: QBrush = QBrush(self.axis_marker_color)
        self.axis_marker_label_spacing: float = 1.0 # TODO
        self.axis_marker_label_font_size: int = 1 # TODO

        # y axis config
        self.yaxis_line: QGraphicsLineItem = QGraphicsLineItem(parent=self)
        self.yaxis_arrow_len: float = (self.y_max - self.y_min) * self.y_scale * self.axis_arrow_scale
        self.yaxis_arrow: Arrow = Arrow(QPoint(), QPoint(0, -1), int(self.axis_marker_width))
        self.yaxis_markers: dict[int, QGraphicsLineItem] = {}
        self.yaxis_marker_labels: dict[int, QGraphicsSimpleTextItem] = {}

        # x axis config

        self.__create_plot()

    def __fit_to_cbf(self) -> None:

        self.x_min = 0
        self.y_min = 0

        self.x_max = 0
        self.y_max = 0

        if not self.cbf:
            return

        self.x_max = self.cbf.m
        self.y_max = 0
        for bucket in self.cbf.bit_array:
            value = ba2int(bucket)
            if value > self.y_max:
                self.y_max = value


    def __create_plot(self) -> None:
        if not self.cbf:
            return
        
        bars: list[CBFPlotBar] = []
        max_y: int = 0
        for i, bucket in enumerate(self.cbf.bit_array):
            value = ba2int(bucket)
            bar = CBFPlotBar(value, self)
            bar.setPos(i * (bar.bar_width + self.bar_spacing) + self.bar_spacing / 2, 0)
            bars.append(bar)
            if value > max_y:
                max_y = value

        x_axis: CBFPlotAxis = CBFPlotAxis(
            min_value=0,
            max_value=self.cbf.m,
            vertical=False,
            parent=self
        )
        y_axis: CBFPlotAxis = CBFPlotAxis(
            min_value=0,
            max_value=10 * math.ceil(max_y / 10),
            vertical=True,
            parent=self
        )

    def __create_plot_new(self) -> None:
        if not self.cbf:
            return

        self.bars: dict[int, QGraphicsRectItem] = {}
        for arg, bucket in enumerate(self.cbf.bit_array):
            value = ba2int(bucket)
            self.__set_bar(arg, value)

        x_axis: CBFPlotAxis = CBFPlotAxis(
            min_value=0,
            max_value=self.cbf.m,
            vertical=False,
            parent=self
        )
        self.__set_yaxis(0, 10 * math.ceil(self.y_max / 10))

    def __yaxis_pos(self, value: int) -> float:
        assert value >= self.y_min
        assert value <= self.y_max

        ymin_axis_offset: float = 0.0 * self.y_scale # start at y_min normally
        return -1.0 * (value - self.y_min) * self.y_scale + ymin_axis_offset


    def __xaxis_pos(self, argument: int) -> float:
        assert argument >= self.x_min
        assert argument <= self.x_max

        xmin_axis_offset: float = 1.0 * self.x_scale # set min x arg to first bar, instead of on the y axis
        return (argument - self.x_min) * self.x_scale + xmin_axis_offset

    def __set_xaxis(self, min: float = 0, max: float = 10, marker_spacing: float = 10) -> None:
        pass

    def __set_yaxis_marker(self, value: int) -> None:
        marker: QGraphicsLineItem = QGraphicsLineItem(
            - self.axis_marker_width / 2, self.__yaxis_pos(value),
            + self.axis_marker_width / 2, self.__yaxis_pos(value),
            parent=self
        )
        marker.setPen(self.axis_line_pen)
        self.yaxis_markers[value] = marker

        marker_label: QGraphicsSimpleTextItem = QGraphicsSimpleTextItem(
            f"{value}",
            parent=self
        )
        marker_label.setBrush(self.axis_marker_label_brush)
        marker_label_font: QFont = marker_label.font()
        marker_label_font.setPointSize(self.axis_marker_label_font_size)

        text_aabb: QRectF = marker_label.boundingRect()
        marker_label.setPos(
            - (self.axis_marker_width / 2) - self.axis_marker_label_spacing - text_aabb.width(),
            self.__yaxis_pos(value) - (text_aabb.height() / 2)
        )
        self.yaxis_marker_labels[value] = marker_label

    def __set_yaxis(self, min: float = 0, max: float = 10, marker_spacing: int = 10) -> None: #TODO args unused?!
        yaxis_len: float = (self.y_max - self.y_min) * self.y_scale

        self.arrow: Arrow = Arrow(
            QPoint(0, - int(yaxis_len)),
            QPoint(0, - int(yaxis_len) - int(self.yaxis_arrow_len)),
            int(self.axis_marker_width),
            line_pen=self.axis_line_pen,
            parent=self
        )

        yaxis_line: QLine = QLine(
            0, 0,
            0, -int(yaxis_len),
        )
        self.yaxis_line = QGraphicsLineItem(yaxis_line, parent=self)
        self.yaxis_line.setPen(self.axis_line_pen)
        

        self.yaxis_markers = {}
        self.yaxis_marker_labels = {}

        self.__set_yaxis_marker(math.floor(self.y_min))
        self.__set_yaxis_marker(math.ceil(self.y_max))
        begin_marker_value: int = math.floor(self.y_min) + (marker_spacing - (math.floor(self.y_min) % marker_spacing))
        for i in range((math.ceil(self.y_max) - math.floor(self.y_min)) // marker_spacing):
            marker_value: int = begin_marker_value * (i + 1)
            self.__set_yaxis_marker(marker_value)

    def __set_bar(self, argument: int, value: int) -> None:
        bar_rect_item: QGraphicsRectItem = QGraphicsRectItem(parent=self)
        bar_rect_item.setPen(self.bar_border_pen)        
        bar_rect_item.setBrush(self.bar_infill_brush)
        # hcentered bar, bot to top (-y)
        bar_rect: QRectF = QRectF(
            - self.bar_width / 2, self.__yaxis_pos(0),
            + self.bar_width / 2, self.__yaxis_pos(value)
        )
        bar_rect_item.setRect(bar_rect)
        bar_rect_item.setPos(self.__xaxis_pos(argument), self.__yaxis_pos(0))
        self.bars[argument] = bar_rect_item

    


