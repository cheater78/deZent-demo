import math
from dataclasses import dataclass
from typing import TypeVar, override, overload

from PySide6.QtCore import (
    QPoint, QPointF,
    QRect, QRectF,
    Qt,
    QLineF,
)
from PySide6.QtGui import (
    QVector2D,
    QPainter, 
    QColor, 
    QBrush, 
    QPen,
    QFont,
    QPainterPath,
    QFontMetricsF,
    QTextLayout
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

ScalarT = TypeVar("ScalarT", int, float)
PointT = TypeVar("PointT", QPoint, QPointF)

def rect_grow_to_include(rect: QRectF, point: QPoint) -> QRectF:
    return rect.united(QRectF(point, point))

class Arrow(QGraphicsItem):

    def __init__(self,
                 /,
                 begin: QPoint | QPointF,
                 end: QPoint | QPointF,
                 width: float,
                 angle: int = 45,
                 line_pen: QPen = QPen(
                            QColor(Qt.GlobalColor.white),
                            1,
                            Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap,
                            Qt.PenJoinStyle.RoundJoin),
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)

        self.begin: QPointF = QPointF(begin.x(), begin.y())
        self.end: QPointF = QPointF(end.x(), end.y())

        self.line_pen: QPen = line_pen
        self.main_line: QGraphicsLineItem = QGraphicsLineItem(
            QLineF(
                begin,
                end,
            ),
            parent=self
        )
        self.main_line.setPen(self.line_pen)

        v: QVector2D = QVector2D(self.end - self.begin)
        v.normalize()

        a_rad: float = (angle / 180) * math.pi # deg to rad
        w_he: float = width / 2 # full width to half extent
        wings_on_main: float = w_he / math.tan(a_rad) # length of wings on main line
        wings_on_main_v: QVector2D = v * wings_on_main

        v_r: QVector2D = QVector2D(+ v.y(), - v.x()) # rotate cw half pi
        v_l: QVector2D = QVector2D(- v.y(), + v.x()) # rotate ccw half pi

        self.right: QPointF = (QVector2D(self.end) - wings_on_main_v + v_l * w_he).toPointF() # I miss glm alr
        self.left: QPointF = (QVector2D(self.end) - wings_on_main_v + v_r * w_he).toPointF()

        self.arrow_lline: QGraphicsLineItem = QGraphicsLineItem(
            QLineF(
                self.end,
                self.right
            ),
            parent=self
        )
        self.arrow_lline.setPen(self.line_pen)

        self.arrow_rline: QGraphicsLineItem = QGraphicsLineItem(
            QLineF(
                self.end,
                self.left
            ),
            parent=self
        )
        self.arrow_rline.setPen(self.line_pen)

    @override
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, /, widget: QWidget | None = None) -> None:
        self.main_line.paint(painter, option, widget)
        self.arrow_lline.paint(painter, option, widget)
        self.arrow_rline.paint(painter, option, widget)
        
    @override
    def boundingRect(self) -> QRectF:
        aabb: QRectF = QRectF(self.begin, self.end).normalized()
        rect_grow_to_include(aabb, self.left)
        rect_grow_to_include(aabb, self.right)
        return aabb