
from deZent_demo.zanon.counting_data_structure.counting_bloom_filter import CBloomFilter

from enum import Enum
from typing import TypeVar, ClassVar, override
from bitarray.util import ba2int

from PySide6.QtCore import (
    QPointF,
    QRect, QRectF,
    Qt,
    QLine,
)
from PySide6.QtGui import (
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

# TODO: move to utils
def text_item_bounding_rect(text_item: QGraphicsSimpleTextItem) -> QRectF:
    path = QPainterPath()
    path.addText(0, 0, text_item.font(), text_item.text())
    
    rect: QRectF = text_item.boundingRect()
    tight_rect: QRectF = path.boundingRect()

    pos_x: float = (rect.width() - tight_rect.width()) / 2
    pos_y: float = (rect.height() - tight_rect.height()) / 2

    corrected_rect: QRectF = QRectF(
        pos_x, pos_y,
        tight_rect.width(), tight_rect.height()
    )
    return corrected_rect

class CBFPlotBar(QGraphicsRectItem):
    unit_height: ClassVar[int] = 4
    bar_width: ClassVar[int] = 4

    bar_border_color: ClassVar[QColor] = QColor(Qt.GlobalColor.blue)
    bar_border_width: ClassVar[int] = 2
    
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
    
    def set_value(self, value: int) -> None:
        self._value: int = value
        bar_rect: QRect = QRect(
            0, 0,
            self.bar_width, -(self._value * self.unit_height)
        )
        self.setRect(bar_rect)


class CBFPlotAxis(QGraphicsItem):
    unit_height: ClassVar[int] = 4
    bar_width: ClassVar[int] = 4
    bar_spacing: ClassVar[int] = 2

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
        self.length: int = (self.max_value - self.min_value) * self.unit_length + self.arrow_height

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
        
        axis_line: QLine = QLine(
            *self.__orient(0, 0),
            *self.__orient(0, -self.length),
        )
        self.line: QGraphicsLineItem = QGraphicsLineItem(axis_line, parent=self)
        self.line.setPen(self.line_pen)
        arrow_lline: QLine = QLine(
            *self.__orient(- int(self.arrow_width / 2), - self.length + self.arrow_height),
            *self.__orient(0, - self.length),
        )
        self.arrow_lline: QGraphicsLineItem = QGraphicsLineItem(arrow_lline, parent=self)
        self.arrow_lline.setPen(self.line_pen)
        arrow_rline: QLine = QLine(
            *self.__orient(+ int(self.arrow_width / 2), - self.length + self.arrow_height),
            *self.__orient(0, - self.length),
        )
        self.arrow_rline: QGraphicsLineItem = QGraphicsLineItem(arrow_rline, parent=self)
        self.arrow_rline.setPen(self.line_pen)

        self.markers: list[QGraphicsLineItem] = []
        self.marker_labels: list[QGraphicsSimpleTextItem] = []

        self.__add_marker(self.min_value)
        self.__add_marker(self.max_value)
        begin_marker_value: int = self.min_value + (self.marker_interval - (self.min_value % self.marker_interval))
        for i in range((self.max_value - self.min_value) // self.marker_interval):
            marker_value: int = begin_marker_value * (i + 1)
            self.__add_marker(marker_value)

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
        self.arrow_lline.paint(painter, option, widget)
        self.arrow_rline.paint(painter, option, widget)

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



class CBFPlot(QGraphicsWidget):
    bar_spacing: ClassVar[int] = 2

    def __init__(self,
        cbf: CBloomFilter | None = None,
        parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent=parent)
        
        self.cbf: CBloomFilter | None = cbf
        self.__create_plot()

    def __create_plot(self) -> None:
        if not self.cbf:
            return
        
        bars: list[CBFPlotBar] = []
        max_y: int = 0
        for i, bucket in enumerate(self.cbf.bit_array):
            value = ba2int(bucket)
            bar = CBFPlotBar(value, self)
            bar.setPos(i * (bar.bar_width + self.bar_spacing), 0)
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
            max_value=max_y,
            vertical=True,
            parent=self
        )



