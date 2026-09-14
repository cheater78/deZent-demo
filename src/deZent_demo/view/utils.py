import math
from typing import TypeVar

from PySide6.QtCore import (
    QPoint, QPointF,
    QRectF,
    Qt,
    QLineF,
)
from PySide6.QtGui import (
    QVector2D,
    QPainter, 
    QColor, 
    QPen,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

class GraphicsContainerItem(QGraphicsItem):

    def __init__(self,
                 /,
                 parent: QGraphicsItem | None = None) -> None:
        QGraphicsItem.__init__(self, parent)

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              /,
              widget: QWidget | None = None) -> None:
        return

    def boundingRect(self) -> QRectF:
        return self.childrenBoundingRect()

    def center(self) -> QPointF:
        return self.boundingRect().center()

    def set_center_pos(self, pos: QPointF) -> None:
        self.setPos(pos - self.center())


ScalarT = TypeVar("ScalarT", int, float)
PointT = TypeVar("PointT", QPoint, QPointF)

def rect_grow_to_include(rect: QRectF, point: QPoint | QPointF) -> QRectF:
    return rect.united(QRectF(point, point))

class GraphicsArrow(GraphicsContainerItem):

    def __init__(self,
                 /,
                 v: QPoint | QPointF,
                 width: float,
                 angle: int = 45,
                 line_pen: QPen | None = None,
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)

        self.arrow_vector: QPointF = QPointF()
        self.arrow_width: float = 0
        self.arrow_wing_angle: int = 45

        line_pen = line_pen if line_pen is not None else QPen(
            QColor(Qt.GlobalColor.white),
            1,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        self.line_pen: QPen = line_pen
        self.main_line: QGraphicsLineItem = QGraphicsLineItem(parent=self)

        self.right: QPointF = QPointF()
        self.left: QPointF = QPointF()
        self.arrow_lline: QGraphicsLineItem = QGraphicsLineItem(parent=self)
        self.arrow_rline: QGraphicsLineItem = QGraphicsLineItem(parent=self)

        self.__update(v, width, angle, line_pen)

    def __update(self,
                 v: QPoint | QPointF,
                 width: float,
                 angle: int,
                 line_pen: QPen) -> None:
        self.arrow_vector = QPointF(v.x(), v.y())
        self.arrow_width = width
        self.arrow_wing_angle = angle

        self.line_pen = line_pen
        self.main_line.setLine(
            QLineF(
                QPointF(0.0, 0.0),
                self.arrow_vector,
            )
        )
        self.main_line.setPen(self.line_pen)

        vn: QVector2D = QVector2D(self.arrow_vector)
        vn.normalize()

        a_rad: float = (angle / 180) * math.pi # deg to rad
        w_he: float = width / 2 # full width to half extent
        wings_on_main: float = w_he / math.tan(a_rad) # length of wings on main line
        wings_on_main_v: QVector2D = vn * wings_on_main

        v_r: QVector2D = QVector2D(+ vn.y(), - vn.x()) # rotate cw half pi
        v_l: QVector2D = QVector2D(- vn.y(), + vn.x()) # rotate ccw half pi

        self.right = (QVector2D(self.arrow_vector) - wings_on_main_v + v_l * w_he).toPointF() # I miss glm alr
        self.left = (QVector2D(self.arrow_vector) - wings_on_main_v + v_r * w_he).toPointF()

        self.arrow_lline.setLine(
            QLineF(
                self.arrow_vector,
                self.right
            )
        )
        self.arrow_lline.setPen(self.line_pen)

        self.arrow_rline.setLine(
            QLineF(
                self.arrow_vector,
                self.left
            )
        )
        self.arrow_rline.setPen(self.line_pen)

    def update_arrow(self,
                     v: QPoint | QPointF| None = None,
                     width: float | None = None,
                     angle: int | None = None,
                     line_pen: QPen | None = None) -> None:
        self.__update(
            v if v is not None else self.arrow_vector,
            width if width is not None else self.arrow_width,
            angle if angle is not None else self.arrow_wing_angle,
            line_pen if line_pen is not None else self.line_pen
        )