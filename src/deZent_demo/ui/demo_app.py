from __future__ import annotations
import sys
import math
from typing import Any
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,

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

from .scene_view import SceneView

class Node(QGraphicsRectItem):
    
    def __init__(self, position: QPointF, size: QSizeF = QSizeF(1, 1), color: QColor = QColor("lime")):
        super().__init__(QRectF(
                -size.width()/2,
                -size.height()/2,
                size.width(),
                size.height()
        ))

        self.edges: list [Edge] = []

        self.setBrush(QColor("blue"))
        pen: QPen = QPen(color)
        pen.setWidthF(0.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.setPos(position)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_path()
        return super().itemChange(change, value)

class Edge(QGraphicsPathItem):
    def __init__(self, a: Node, b: Node):
        super().__init__()

        self.a = a
        self.b = b

        pen = QPen(QColor("green"))
        pen.setWidthF(1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)

        a.add_edge(self)
        b.add_edge(self)

        self.update_path()

    def update_path(self):
        pa = self.a.scenePos()
        pb = self.b.scenePos()

        path = QPainterPath(pa)
        path.lineTo(pb)

        #mid_x = (pa.x() + pb.x()) / 2
        #path.cubicTo(QPointF(mid_x, pa.y()), QPointF(mid_x, pb.y()),pb)

        self.setPath(path)

class DemoWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        scene = QGraphicsScene()
        scene_dimensions: QRectF = QRectF(0, 0, 200, 200)
        # scene.setSceneRect(scene_dimensions)

        self.ce: Node
        self.nodes: list[Node] = []

        node_count: int = 7
        node_size: QSizeF = scene_dimensions.size() / (2 * node_count)
        margin: QSizeF = node_size / 2

        node_view_dimension: QSizeF = scene_dimensions.size() - margin

        self.ce = Node(scene_dimensions.center(), node_size, QColor("red"))
        scene.addItem(self.ce)

        for i in range(node_count):
            node_pos: QPointF = scene_dimensions.center() + QPointF( 0.5 * node_view_dimension.width() * math.cos( 2 * math.pi * (i / node_count) ), 0.5 *  node_view_dimension.height() * math.sin( 2 * math.pi * (i / node_count) ))
            self.nodes.append(Node(node_pos, node_size))
            scene.addItem(self.nodes[-1])

            if i != 0:
                scene.addItem(Edge(self.nodes[i - 1], self.nodes[i]))
            if i + 1 >= node_count:
                scene.addItem(Edge(self.nodes[i], self.nodes[0]))

            scene.addItem(Edge(self.nodes[i], self.ce))
        
        view = SceneView(scene)
        self.setCentralWidget(view)

        self.setWindowTitle("Local deZent demo")

class DemoApp(QApplication):

    def __init__(self) -> None:
        super().__init__(sys.argv)

        self.demo_window: DemoWindow = DemoWindow()

    def run(self) -> None:
        self.demo_window.show()

        exit_code: int = self.exec()
        sys.exit(exit_code)

    