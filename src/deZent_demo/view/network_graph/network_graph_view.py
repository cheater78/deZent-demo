
from .panning_graphics_view import PanningGraphicsView
from .network_graph import NetworkGraph, NetworkGraphNode, NetworkGraphEdge

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QGraphicsRectItem,
)

# NOTE: QGraphicsView (which PanningGraphicsView is) is a QWidget
class NetworkGraphView(PanningGraphicsView):

    def __init__(self,
                 /,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._scene: QGraphicsScene = QGraphicsScene(parent=self)
        self._network_graph: NetworkGraph = NetworkGraph()

        # TODO: TEST
        ce_node = self._network_graph.create_node()
        self._network_graph.add_node(ce_node)

        firstnode: NetworkGraphNode | None = None
        lastnode: NetworkGraphNode | None = None
        for i in range(7):
            node = self._network_graph.create_node()
            self._network_graph.add_node(node)

            node.link_to(ce_node)

            if lastnode is not None:
                lastnode.link_to(node)
            else:
                firstnode = node
            lastnode = node
        if firstnode is not None and lastnode is not None:
            lastnode.link_to(firstnode)

        self._network_graph.arrange_ring()

        from ..utils import GraphicsArrow
        from PySide6.QtCore import Qt, QPointF, QRectF
        from PySide6.QtGui import (
            QColor, 
            QPen,
            QBrush,
        )

        arrow = GraphicsArrow(QPointF(0, 10), 3)
        self._scene.addItem(arrow)
        arrow.setPos(QPointF(0, -10))
        
        # TODO: TEST

        self._scene.addItem(self._network_graph)
        
        self.setScene(self._scene)
        self.refit_view()
