
from deZent_demo.zanon.counting_data_structure.counting_bloom_filter import CBloomFilter
from deZent_demo.ami.measurement import MeasurementKey
from deZent_demo.ui.utils import *

from enum import Enum
import math
from typing import TypeVar, ClassVar, override
from abc import abstractmethod
from bitarray.util import ba2int

from PySide6.QtCore import (
    QRect, QRectF,
    Qt,
    QLineF,
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

class PlotFocus(set[int]):
    pass

class PlotSection(QGraphicsItem):
    def __init__(self, /, parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)

    @abstractmethod
    def size(self) -> float:
        pass
    
class PlotSectionFocusSeparator(PlotSection):
    pass

class PlotBar(QGraphicsRectItem):
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

class CBFPlot(QGraphicsWidget):

    def __init__(self,
        cbf: CBloomFilter | None = None,
        focus: set[int] = set[int](),
        parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent=parent)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.__init_plot(cbf, focus)
        self.__create_plot()

    def __init_plot(self, cbf: CBloomFilter | None = None, focus: set[int] = set[int](), scene_dimensions: QSizeF = QSizeF(800, 300)) -> None:
        self.cbf: CBloomFilter | None = cbf

        self.dimensions: QSizeF = scene_dimensions

        self.shift_zero_to_right: bool = True

        # plot focus: show only specified bars, all if empty
        self.focus: set[int] = focus
        self.focus_neighbor_extent: int = 3

        # plot native dimensions
        self.__set_logical_size()

        self.focus_spacing_scale: float = 1.6 # TODO

        x_offset: int = self.x_min
        self.bar_count: int = 0
        self.focus_spacer_count: int = 0
        if self.focus:
            for f in sorted(self.focus):
                upper: int = f + self.focus_neighbor_extent
                if upper < x_offset:
                    continue
                lower: int = max(x_offset, f - self.focus_neighbor_extent)

                section_zero: bool = lower <= 0 and upper >= 0 and self.shift_zero_to_right
                if (lower > (x_offset + 1)) and not section_zero:
                    self.focus_spacer_count += 1
                elif section_zero:
                    self.bar_count += 1 # zero offset
                x_offset = upper
                self.bar_count += (upper - lower) + 1
        else:
            self.bar_count = (self.x_max - self.x_min)
        
        self.x_scale: float = self.dimensions.width() / (self.bar_count + (self.focus_spacing_scale * self.focus_spacer_count))
        self.y_scale: float = self.dimensions.height() / (self.y_max - self.y_min)

        # focus config
        
        self.focus_spacing: float = self.x_scale * self.focus_spacing_scale

        self.focus_arrow_scale: float = 0.04 * self.y_max # TODO
        self.focus_arrow_size: float = self.y_scale * self.focus_arrow_scale
        self.focus_arrow_width_scale: float = 0.4 # TODO
        self.focus_arrow_width: float = self.focus_arrow_width_scale * self.x_scale
        self.focus_arrow_margin_scale: float = 0.03 * self.y_max # TODO
        self.focus_arrow_margin: float = self.y_scale * self.focus_arrow_margin_scale
        
        self.focus_arrow_color: QColor = QColor(Qt.GlobalColor.red)
        self.focus_arrow_line_width: float = 2 # TODO
        self.focus_arrow_line_pen: QPen = QPen(self.focus_arrow_color, self.focus_arrow_line_width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.focus_arrows: dict[int, Arrow] = {}

        # bar config
        self.bars: dict[int, QGraphicsRectItem] = {}
        self.bar_border_color: QColor = QColor(24, 96, 16)
        self.bar_border_width: float = 0.0 # TODO
        self.bar_border_pen: QPen = QPen(self.bar_border_color, self.bar_border_width)
        self.bar_infill_color: QColor = QColor(24, 96, 16)
        self.bar_infill_brush: QBrush = QBrush(self.bar_infill_color)

        self.bar_sec_border_color: QColor = QColor(24, 96, 16)
        self.bar_sec_border_width: float = 0.0 # TODO
        self.bar_sec_border_pen: QPen = QPen(self.bar_sec_border_color, self.bar_sec_border_width)
        self.bar_sec_infill_color: QColor = QColor(24, 64, 16)
        self.bar_sec_infill_brush: QBrush = QBrush(self.bar_sec_infill_color)

        self.bar_interval: float = self.x_scale
        self.bar_width_scale: float = 0.62 # TODO
        self.bar_width: float = self.bar_interval * self.bar_width_scale
        self.bar_spacing_scale: float = 1.0 - self.bar_width_scale
        self.bar_spacing: float = self.bar_interval * self.bar_spacing_scale

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
        self.xaxis_lines: list[QGraphicsLineItem] = []
        self.xaxis_arrow_len: float = (self.y_max - self.y_min) * self.y_scale * self.axis_arrow_scale
        self.xaxis_arrow: Arrow = Arrow(QPoint(), QPoint(0, -1), int(self.axis_marker_width))
        self.xaxis_markers: dict[int, QGraphicsLineItem] = {}
        self.xaxis_marker_labels: dict[int, QGraphicsSimpleTextItem] = {}
        self.xaxis_size: float = 0.0

        # focus average
        self.focus_avg_line: QGraphicsLineItem = QGraphicsLineItem(parent=self)
        self.focus_avg_line_label: QGraphicsSimpleTextItem = QGraphicsSimpleTextItem(parent=self)
        self.focus_avg_line_color: QColor = QColor(Qt.GlobalColor.red)
        self.focus_avg_line_width: float = 1 # TODO
        self.focus_avg_line_pen: QPen = QPen(self.focus_avg_line_color, self.focus_avg_line_width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.focus_avg_line_label_color: QColor = QColor(Qt.GlobalColor.red)
        self.focus_avg_line_label_brush: QBrush = QBrush(self.focus_avg_line_label_color)
        self.focus_avg_line_label_spacing: float = 1 # TODO

        self.__cluster_focus_sections()

    def set_size(self, x: float, y: float) -> None:
        self.__clear_plot()
        self.__init_plot(self.cbf, self.focus, scene_dimensions=QSizeF(x, y))
        self.__create_plot()
        self.update()
        self.scene().update()

    def __clear_plot(self) -> None:
        for item in self.childItems():
            self.scene().removeItem(item)
        
    def clear_plot(self) -> None:
        self.__clear_plot()
        self.__init_plot()

    def update_cbf(self, cbf: CBloomFilter, focus: set[int] = set[int]()) -> None:
        self.__clear_plot()
        self.__init_plot(cbf, focus)
        self.__create_plot()
        self.update()
        self.scene().update()
    
    def __set_logical_size(self) -> None:
        # reset to defaults
        self.x_min: int = 0
        self.y_min: int = 0
        self.x_max: int = 5 # some non zero x axis size
        self.y_max: int = 2 # some non zero y axis size

        if not self.cbf:
            return

        self.x_max = self.cbf.m
        for arg, bucket in enumerate(self.cbf.bit_array):
            if self.focus and arg not in self.focus and not any([ abs(f - arg) <= self.focus_neighbor_extent for f in self.focus]):
                continue
            value = ba2int(bucket)
            if value > self.y_max:
                self.y_max = value

    def __cluster_focus_sections(self) -> None:
        self.sections: dict[int, tuple[set[int], float]] = {}

        if not self.focus:
            return

        sorted_focus: list[int] = sorted(self.focus)

        section_deno: int = sorted_focus[0]
        for arg in sorted_focus:
            if self.sections and sorted(self.sections[section_deno][0])[-1] + (2 * self.focus_neighbor_extent) >= arg:
                self.sections[section_deno][0].add(arg)
            else: # new section
                self.sections[arg] = ({ arg }, 0 )
                section_deno = arg
        
        for sdeno, s in self.sections.items():
            sorted_section: list[int] = sorted(s[0])

            section_first_neighbor: int = max(sorted_section[0] - self.focus_neighbor_extent, self.x_min)
            section_last_neighbor: int = min(sorted_section[-1] + self.focus_neighbor_extent, self.x_max)
            section_neighbor_count: int = 1 + section_last_neighbor - section_first_neighbor
            section_bars_size: float = self.bar_interval * section_neighbor_count
            section_size: float = section_bars_size + (0 if self.shift_zero_to_right and section_first_neighbor == 0 else self.focus_spacing)

            self.sections[sdeno] = (s[0], section_size)

        print(f"sections: {self.sections}")

    def __create_plot(self) -> None:
        if not self.cbf:
            return
        
        for arg, bucket in enumerate(self.cbf.bit_array):
            if self.focus and arg not in self.focus and not any([ abs(f - arg) <= self.focus_neighbor_extent for f in self.focus]):
                continue
            value = ba2int(bucket)
            self.__set_bar(arg, value, primary=(not self.focus or arg in self.focus))
            if self.focus and arg in self.focus:
                self.__set_bar_marker(arg, value)

        self.__set_xaxis()
        self.__set_yaxis(max(1, math.floor((self.y_max - self.y_min) / 10)))

        self.__set_focus_avg()

    def __yaxis_pos(self, value: int) -> float:
        assert value >= self.y_min
        assert value <= self.y_max

        ymin_axis_offset: float = 0.0 * self.y_scale # start at y_min normally
        return -1.0 * (value - self.y_min) * self.y_scale + ymin_axis_offset

    def __xaxis_zero_shift(self) -> bool:
        mag: int = (self.x_max - self.x_min)
        for focus in sorted(self.focus):
            if abs(focus) > mag:
                break
            mag = abs(focus)
            if mag <= self.focus_neighbor_extent:
                return self.shift_zero_to_right
        else:
            return self.shift_zero_to_right and (self.x_min == 0)
        return False

    def __xaxis_pos(self, argument: int) -> float:
        assert argument >= self.x_min
        assert argument <= self.x_max

        zero_offset: float = self.bar_interval if self.__xaxis_zero_shift() else 0
        xpos: float = zero_offset

        if not self.focus or not self.sections:
            xpos_plot_local: int = argument - self.x_min
            xpos += self.bar_interval * xpos_plot_local
            return xpos
        else:
            closest_section_focus: tuple[int, int, int] = (0, 0, 0) # section, focus, neighbor

            sorted_sections: list[tuple[int, tuple[set[int], float]]] = sorted(self.sections.items())
            sorted_sections_break: bool = False
            for sitem in sorted_sections:
                sdeno, s = sitem

                sorted_section: list[int] = sorted(s[0])
                if argument + self.focus_neighbor_extent < sdeno:
                    #TODO: interpolate if needed
                    break
                if argument > sorted_section[-1] + self.focus_neighbor_extent:
                    continue

                # argument in range of section
                
                best_focus_dist: int = (self.x_max - self.x_min)
                for focus in sorted_section:
                    if argument + self.focus_neighbor_extent < focus:
                        #TODO: interpolate if needed
                        sorted_sections_break = True
                        break
                    # skip all foci that do not have argument in their upper neighborhood
                    if argument > focus + self.focus_neighbor_extent:
                        continue
                    # reached a focus with argument in its neighborhood
                    # assign argument to closest neighborhood
                    current_focus_dist: int = abs(focus - argument)
                    if best_focus_dist > current_focus_dist:
                        closest_section_focus = (sdeno, focus, argument)
                        best_focus_dist = current_focus_dist

                if sorted_sections_break:
                    break
            
            for sitem in sorted_sections:
                sdeno, s = sitem
                section_size: float = s[1]
                sorted_section: list[int] = sorted(s[0])

                # accumulate precomputed section sizes for all lower sections
                if closest_section_focus[0] > sorted_section[-1] + self.focus_neighbor_extent: # section upper bound check
                    xpos += section_size
                    continue

                # omit focus_spacing when lowest neighbor is 0
                section_spacer: float = 0 if (self.shift_zero_to_right and sorted_section[0] <= self.focus_neighbor_extent) else self.focus_spacing
                
                # hit section reached
                bar_count: int = abs(closest_section_focus[2] - max((sdeno - self.focus_neighbor_extent), self.x_min))
                bars_size: float = self.bar_interval * bar_count

                xpos += section_spacer + bars_size
                break
            
            return xpos
    
    def __set_xaxis_marker(self, argument: int) -> None:
        marker: QGraphicsLineItem = QGraphicsLineItem(
            self.__xaxis_pos(argument), - self.axis_marker_width / 2,
            self.__xaxis_pos(argument), + self.axis_marker_width / 2,
            parent=self
        )
        marker.setPen(self.axis_line_pen)
        self.xaxis_markers[argument] = marker

        marker_label: QGraphicsSimpleTextItem = QGraphicsSimpleTextItem(
            f"{argument}",
            parent=self
        )
        marker_label.setBrush(self.axis_marker_label_brush)
        marker_label_font: QFont = marker_label.font()
        marker_label_font.setPointSize(self.axis_marker_label_font_size)

        text_aabb: QRectF = marker_label.boundingRect()
        marker_label.setPos(
            + self.__xaxis_pos(argument) - (text_aabb.width() / 2),
            + (self.axis_marker_width / 2) + self.axis_marker_label_spacing
        )
        self.xaxis_marker_labels[argument] = marker_label

    def __set_xaxis_spacer(self, x_pos: float) -> float:
        spacer_line_count: int = 3
        spacer_unit: float = self.focus_spacing / (2 * spacer_line_count + 1)

        spacer_line: QLineF = QLineF(
            0, 0,
            spacer_unit, 0,
        )

        xpos: float = x_pos + spacer_unit # start segement with empty unit

        for _ in range(spacer_line_count):
            self.xaxis_lines.append(QGraphicsLineItem(spacer_line, parent=self))
            self.xaxis_lines[-1].setPen(self.axis_line_pen)
            self.xaxis_lines[-1].setPos(xpos, 0)
            xpos += spacer_unit # spacer_line
            xpos += spacer_unit # empty unit

        return (xpos - x_pos)

    def __set_xaxis(self, marker_spacing: int = 50) -> None:
        self.xaxis_lines = []
        self.xaxis_markers = {}
        self.xaxis_marker_labels = {}
        
        x_pos: float = 0.0

        segment0_xsize: float = 0
        if not self.focus or not self.sections:
            segment0_xsize = self.__xaxis_pos(int(self.x_max))
        else:
            segment0_xsize = 0

        segment0: QLineF = QLineF(
            x_pos, 0,
            x_pos + segment0_xsize, 0,
        )
        self.xaxis_lines.append(QGraphicsLineItem(segment0, parent=self))
        self.xaxis_lines[-1].setPen(self.axis_line_pen)
        x_pos += segment0_xsize

        if not self.focus:
            self.__set_xaxis_marker(self.x_min)
            self.__set_xaxis_marker(self.x_max)
            begin_marker_value: int = self.x_min + (marker_spacing - (self.x_min % marker_spacing))
            for i in range((self.x_max - self.x_min) // marker_spacing):
                marker_value: int = begin_marker_value * (i + 1)
                self.__set_xaxis_marker(marker_value)
        else:
            sorted_sections: list[tuple[int, tuple[set[int], float]]] = sorted(self.sections.items())

            for sitem in sorted_sections:
                sdeno, s = sitem

                sorted_section: list[int] = sorted(s[0])
                section_first_neighbor: int = max(sorted_section[0] - self.focus_neighbor_extent, self.x_min)
                section_last_neighbor: int = min(sorted_section[-1] + self.focus_neighbor_extent, self.x_max)
                section_neighbor_count: int = 1 + section_last_neighbor - section_first_neighbor

                if section_first_neighbor != 0:
                    x_pos += self.__set_xaxis_spacer(x_pos)

                for bar in range(math.floor(section_first_neighbor), int(section_first_neighbor) + int(section_neighbor_count)):
                    self.__set_xaxis_marker(bar)

                segmenti: QLineF = QLineF(
                    0, 0,
                    self.__xaxis_pos(section_last_neighbor) - self.__xaxis_pos(section_first_neighbor) + self.bar_interval, 0,
                )
                self.xaxis_lines.append(QGraphicsLineItem(segmenti, parent=self))
                self.xaxis_lines[-1].setPen(self.axis_line_pen)
                self.xaxis_lines[-1].setPos(self.__xaxis_pos(section_first_neighbor) - (self.bar_interval / 2), 0)

                x_pos = self.__xaxis_pos(section_last_neighbor) + (self.bar_interval / 2)

        self.xaxis_arrow: Arrow = Arrow(
            QPointF(0, 0),
            QPointF(int(self.xaxis_arrow_len), 0),
            int(self.axis_marker_width),
            line_pen=self.axis_line_pen,
            parent=self
        )
        self.xaxis_arrow.setPos(x_pos, 0)

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

    def __set_yaxis(self, marker_spacing: int = 1) -> None:
        self.yaxis_markers = {}
        self.yaxis_marker_labels = {}

        yaxis_len: float = (self.y_max - self.y_min) * self.y_scale

        self.yaxis_arrow: Arrow = Arrow(
            QPointF(0, - yaxis_len),
            QPointF(0, - yaxis_len - self.yaxis_arrow_len),
            int(self.axis_marker_width),
            line_pen=self.axis_line_pen,
            parent=self
        )

        yaxis_line: QLineF = QLineF(
            0, 0,
            0, -yaxis_len,
        )
        self.yaxis_line = QGraphicsLineItem(yaxis_line, parent=self)
        self.yaxis_line.setPen(self.axis_line_pen)

        self.__set_yaxis_marker(math.floor(self.y_min))
        self.__set_yaxis_marker(math.ceil(self.y_max))
        begin_marker_value: int = math.floor(self.y_min) + (marker_spacing - (math.floor(self.y_min) % marker_spacing))
        for i in range((math.ceil(self.y_max) - math.floor(self.y_min)) // marker_spacing):
            marker_value: int = begin_marker_value * (i + 1)
            self.__set_yaxis_marker(marker_value)

    def __set_bar(self, argument: int, value: int, primary: bool = True) -> None:
        bar_rect_item: QGraphicsRectItem = self.bars.get(argument, QGraphicsRectItem(parent=self))
        bar_rect_item.setPen(self.bar_border_pen if primary else self.bar_sec_border_pen)        
        bar_rect_item.setBrush(self.bar_infill_brush if primary else self.bar_sec_infill_brush)
        # hcentered bar, bot to top (-y)
        bar_rect: QRectF = QRectF(
            0,              self.__yaxis_pos(0),
            self.bar_width, self.__yaxis_pos(value)
        )
        bar_rect_item.setRect(bar_rect)
        bar_rect_item.setPos(self.__xaxis_pos(argument) - (self.bar_width / 2), self.__yaxis_pos(0))
        bar_rect_item.setZValue(-1)
        self.bars[argument] = bar_rect_item
        # print(f"Bar [{argument},{value}] at posx: {self.__xaxis_pos(argument)}")

    def __set_bar_marker(self, argument: int, value: int) -> None:
        arrow: Arrow = Arrow(
            QPointF(0, - self.focus_arrow_size),
            QPointF(0, 0),
            width=self.focus_arrow_width,
            line_pen=self.focus_arrow_line_pen,
            parent=self
        )
        arrow.setPos(self.__xaxis_pos(argument), self.__yaxis_pos(self.y_max) - self.focus_arrow_size - self.focus_arrow_margin)
        arrow.setZValue(1)
        self.focus_arrows[argument] = arrow

    def __set_focus_avg(self) -> None:
        if not self.focus or not self.cbf:
            return
        value: int = self.y_max + 1
        arg: int = 0
        for f in sorted(self.focus):
            bucket_v: int = ba2int(self.cbf.bit_array[f])
            if bucket_v < value:
                value = bucket_v
                arg = f


        # lower_focus_neighbor: int = max(self.x_min, min(self.focus) - self.focus_neighbor_extent) # TODO obsolete?
        upper_focus_neighbor: int = min(self.x_max, max(self.focus) + self.focus_neighbor_extent)

        focus_avg_line_size: float = self.__xaxis_pos(upper_focus_neighbor) + (self.bar_interval / 2)
        focus_avg_line: QLineF = QLineF(
            0, 0,
            focus_avg_line_size, 0,
        )
        self.focus_avg_line = QGraphicsLineItem(focus_avg_line, parent=self)
        self.focus_avg_line.setPen(self.focus_avg_line_pen) # TODO
        self.focus_avg_line.setPos(0, self.__yaxis_pos(value))
        self.focus_avg_line.setZValue(-0.1)

        self.focus_avg_line_label = QGraphicsSimpleTextItem(
            f"{value}",
            parent=self
        )
        self.focus_avg_line_label.setBrush(self.focus_avg_line_label_brush)
        label_font: QFont = self.focus_avg_line_label.font()
        label_font.setPointSize(self.axis_marker_label_font_size)

        text_aabb: QRectF = self.focus_avg_line_label.boundingRect()
        self.focus_avg_line_label.setPos(
            self.__xaxis_pos(arg) - (text_aabb.width() / 2),
            self.__yaxis_pos(value) + self.focus_avg_line_label_spacing
        )
        self.focus_avg_line_label.setZValue(-0.1)

    @override
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, /, widget: QWidget | None = None) -> None:
        # painter.drawRect(self.boundingRect())
        return super().paint(painter, option, widget)

    @override
    def boundingRect(self) -> QRectF:
        aabb: QRectF = QRectF(
            0, 0,
            self.dimensions.width(), - self.dimensions.height()
        )
        return aabb.normalized()
