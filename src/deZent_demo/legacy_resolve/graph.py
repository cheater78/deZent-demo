from __future__ import annotations
import math
from typing import Any
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsPathItem,
)
from PySide6.QtGui import (
    QPen,
    QPainterPath,
    QColor
)
from PySide6.QtCore import Qt, QSizeF, QPointF, QRectF

def length(p: QPointF) -> float:
    return math.sqrt(QPointF.dotProduct(p, p))

def normalize(p: QPointF) -> QPointF:
    l = length(p)
    if l == 0:
        return QPointF(0.0, 0.0)
    return QPointF(p.x() / l, p.y() / l)

def clamp(p: QPointF, p_min: QPointF, p_max: QPointF) -> QPointF:
    return QPointF(
        max(p_min.x(), min(p.x(), p_max.x())),
        max(p_min.y(), min(p.y(), p_max.y())),
    )

class NodeSocket(QGraphicsRectItem):
    def __init__(self,
                position: QPointF,
                size: QSizeF = QSizeF(1, 1),
                border_color: QColor = QColor(90, 255, 10),
                border_width: float = 0.1,
                bg_color: QColor = QColor(10, 12, 15),
                parent: QGraphicsItem | None = None):
        super().__init__(
            QRectF(
                0, 0,
                size.width(),
                size.height()
            ),
            parent=parent
        )

        self.setPos(position)

        pen: QPen = QPen(border_color)
        pen.setWidthF(border_width)
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        self.setPen(pen)
        self.setBrush(bg_color)

class Node(QGraphicsRectItem):
    
    def __init__(self,
                 position: QPointF,
                 size: QSizeF = QSizeF(1, 1),
                 socket_position_relative: QPointF = QPointF(1.0, 1.0), # lower right corner
                 socket_size_relative: QSizeF = QSizeF(0.1, 0.1),
                 border_color: QColor = QColor(90, 255, 10),
                 border_width: float = 0.1,
                 bg_color: QColor = QColor(10, 12, 15),
                 parent: QGraphicsItem | None = None):
        super().__init__(
            QRectF(
                0.0, 0.0,
                size.width(),
                size.height()
            ),
            parent=parent
        )

        self.edges: list [Edge] = []

        self.setPos(position)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        pen: QPen = QPen(border_color)
        pen.setWidthF(border_width)
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        self.setPen(pen)
        self.setBrush(bg_color)

        node_socket_size: QSizeF = QSizeF(
            size.width() * socket_size_relative.width(),
            size.height() * socket_size_relative.height()
        )
        norm_node_socket_position_relative: QPointF = clamp(socket_position_relative, QPointF(0.0, 0.0), QPointF(1.0, 1.0))
        max_node_socket_offset: QSizeF = size - node_socket_size
        node_socket_position: QPointF = clamp(
            QPointF(
                size.width() * norm_node_socket_position_relative.x(),
                size.height() * norm_node_socket_position_relative.y()
            ),
            QPointF(0.0, 0.0),
            QPointF(max_node_socket_offset.width(), max_node_socket_offset.height())
        )

        self.node_socket: NodeSocket = NodeSocket(
            node_socket_position,
            node_socket_size,
            border_color=border_color,
            border_width=border_width * 0.6,
            bg_color=bg_color,
            parent=self,
        )

    def link(self, other: Node) -> Edge:
        return Edge(self, other)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_path()
        return super().itemChange(change, value)
    
    def get_socket_pos_scene(self) -> QPointF:
        socket_center_local: QPointF = self.node_socket.pos() + ( QPointF(self.node_socket.rect().width(), self.node_socket.rect().height()) / 2 )
        return self.mapToScene(socket_center_local)

class Edge(QGraphicsPathItem):
    def __init__(self, a: Node, b: Node):
        super().__init__()

        self.a = a
        self.b = b

        pen = QPen(QColor("green"))
        pen.setWidthF(0.1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setZValue(-100)

        a.add_edge(self)
        b.add_edge(self)

        self.update_path()

    def update_path(self):
        pa = self.a.get_socket_pos_scene()
        pb = self.b.get_socket_pos_scene()

        path = QPainterPath(pa)
        path.lineTo(pb)

        #mid_x = (pa.x() + pb.x()) / 2
        #path.cubicTo(QPointF(mid_x, pa.y()), QPointF(mid_x, pb.y()),pb)

        self.setPath(path)