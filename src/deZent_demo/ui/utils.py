import math
from typing import Any, TypeVar

from deZent_demo.ui.style.style import *

from PySide6.QtCore import (
    QPoint, QPointF,
    QSizeF,
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

def rect_grow_to_include(
    rect: QRectF,
    point: QPoint | QPointF
) -> QRectF:
    return rect.united(QRectF(point, point))

def rect_expand_by_relative_margin(
    rect: QRectF,
    margin: QSizeF,
) -> QRectF:
    """
    Expand ``rect`` by margins relative to its own dimensions.
    """
    if rect.isEmpty() or not rect.isValid():
        return QRectF()

    margin_x: float = rect.width() * margin.width()
    margin_y: float = rect.height() * margin.height()

    return rect.adjusted(
        -margin_x,
        -margin_y,
        margin_x,
        margin_y,
    )

def rect_clamped_rect_center(
    rect: QRectF,
    clamp: QRectF,
) -> QPointF:
    desired_center: QPointF = rect.center()
    viewport_width: float = rect.width()
    viewport_height: float = rect.height()

    center_x: float = 0.0
    center_y: float = 0.0

    if viewport_width >= clamp.width():
        center_x = clamp.center().x()
    else:
        viewport_half_width: float = viewport_width / 2.0
        lower_bound: float = clamp.left() + viewport_half_width
        upper_bound: float = clamp.right() - viewport_half_width
        center_x = max(lower_bound, min(desired_center.x(), upper_bound)) # clamp

    if viewport_height >= clamp.height():
        center_y: float = clamp.center().y()
    else:
        viewport_half_height: float = viewport_height / 2.0
        lower_bound: float = clamp.top() + viewport_half_height
        upper_bound: float = clamp.bottom() - viewport_half_height
        center_y = max(lower_bound, min(desired_center.y(), upper_bound)) # clamp

    return QPointF(center_x, center_y)

def ellipse_hit(
    hit_origin: QPointF,
    ellipse_center: QPointF,
    ellipse_size: QSizeF,
) -> QPointF | None:
    he_x, he_y = (ellipse_size / 2).toTuple()
    d_x, d_y = (hit_origin - ellipse_center).toTuple()

    if he_x == 0 \
        or he_y == 0:
        return None
    t = math.sqrt((d_x / he_x)**2 + (d_y / he_y)**2)
    if t == 0:
        return None

    return QPointF((d_x / t) + he_x, (d_y / t) + he_y)

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

        angle: float = style.angle % 90

        if angle > 0.0:
            vn: QVector2D = QVector2D(self.arrow_vector)
            vn.normalize()

            a_rad: float = (angle / 180) * math.pi # deg to rad
            w_he: float = style.width / 2 # full width to half extent
            wings_on_main: float = w_he / math.tan(a_rad) # length of wings on main line
            wings_on_main_v: QVector2D = vn * wings_on_main

            v_r: QVector2D = QVector2D(+ vn.y(), - vn.x()) # rotate cw half pi
            v_l: QVector2D = QVector2D(- vn.y(), + vn.x()) # rotate ccw half pi

            self.right = (QVector2D(self.arrow_vector) - wings_on_main_v + v_l * w_he).toPointF() # I miss glm alr
            self.left = (QVector2D(self.arrow_vector) - wings_on_main_v + v_r * w_he).toPointF()
        else: # angle == 0, make them vanish -> just a line
            self.right = self.arrow_vector
            self.left = self.arrow_vector

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