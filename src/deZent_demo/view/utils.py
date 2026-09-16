import math
from typing import Any, TypeVar

from deZent_demo.view.style.style import *

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

    def __init__(
        self,
        /,
        parent: QGraphicsItem | None = None,
        **kwargs: Any
    ) -> None:
        super().__init__(parent=parent, **kwargs)

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

@dataclass
class GraphicsArrowStyle(Style):
    width: float = 10
    angle: int = 45
    line_style: LineStyle = field(
        default_factory=lambda: LineStyle(
            QPen(
                QColor(Qt.GlobalColor.white),
                2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
    )

class GraphicsArrow(Styled[GraphicsArrowStyle], GraphicsContainerItem):

    def __init__(
        self,
        /,
        v: QPoint | QPointF,
        style: GraphicsArrowStyle = GraphicsArrowStyle(),
        parent: QGraphicsItem | None = None,
        **kwargs: Any
    ) -> None:

        self.arrow_vector: QPointF = QPointF(v.x(), v.y())
        self.arrow_width: float = 0
        self.arrow_wing_angle: int = 45

        self.main_line: QGraphicsLineItem = QGraphicsLineItem()

        self.right: QPointF = QPointF()
        self.left: QPointF = QPointF()
        self.arrow_lline: QGraphicsLineItem = QGraphicsLineItem()
        self.arrow_rline: QGraphicsLineItem = QGraphicsLineItem()

        super().__init__(
            style=style,
            parent=parent,
            **kwargs
        )

        self.main_line.setParentItem(self)
        self.arrow_lline.setParentItem(self)
        self.arrow_rline.setParentItem(self)

    @override
    def on_style_change(self, new_style: GraphicsArrowStyle) -> None:
        self.update_arrow(style=new_style)
        return

    def update_arrow(
        self,
        v: QPoint | QPointF | None = None,
        style: GraphicsArrowStyle | None = None,
    ) -> None:
        style = style if style is not None else self.get_style()

        self.arrow_vector = QPointF(v.x(), v.y()) if v is not None else self.arrow_vector
        self.arrow_width = style.width
        self.arrow_wing_angle = style.angle

        self.main_line.setLine(
            QLineF(
                QPointF(0.0, 0.0),
                self.arrow_vector,
            )
        )
        self.main_line.setPen(style.line_style.pen)

        vn: QVector2D = QVector2D(self.arrow_vector)
        vn.normalize()

        a_rad: float = (style.angle / 180) * math.pi # deg to rad
        w_he: float = style.width / 2 # full width to half extent
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
        self.arrow_lline.setPen(style.line_style.pen)

        self.arrow_rline.setLine(
            QLineF(
                self.arrow_vector,
                self.left
            )
        )
        self.arrow_rline.setPen(style.line_style.pen)