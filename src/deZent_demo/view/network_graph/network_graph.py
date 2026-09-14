from .graphics_directed_graph import GraphicsDirectedGraphNode, GraphicsDirectedGraphEdge, GraphicsDirectedGraph

from deZent_demo.view.utils import GraphicsArrow

from typing import ClassVar, cast
import math

from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsEllipseItem,
)
from PySide6.QtGui import (
    QColor, 
    QPen,
)
from PySide6.QtCore import Qt, QSizeF, QPointF

class NetworkGraphNode(GraphicsDirectedGraphNode):
    ui_ellipse_width: ClassVar[float] = 60.0
    ui_ellipse_height: ClassVar[float] = 40.0

    def __init__(self,
                 graph: NetworkGraph,
                 /,
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(graph, parent)
        
        self._visu: QGraphicsEllipseItem = QGraphicsEllipseItem(
            0.0, 0.0,
            self.ui_ellipse_width, self.ui_ellipse_height,
            parent=self
        )
        self._visu.setPen(QPen( # TODO style defaults
                            QColor(Qt.GlobalColor.white),
                            1,
                            Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap,
                            Qt.PenJoinStyle.RoundJoin))

    def link_to(self, node: NetworkGraphNode) -> NetworkGraphEdge:
        if not isinstance(self._graph, NetworkGraph):
            raise RuntimeError(f"Graph of NetworkGraphNode was not of type NetworkGraph!")
        edge: NetworkGraphEdge = NetworkGraphEdge(self._graph, self, node, self._graph)
        self._graph.add_edge(edge)
        return edge

    def socket_pos(self, connecting_from: QPointF | None = None) -> QPointF:
        if connecting_from is None:
            return GraphicsDirectedGraphNode.socket_pos(self)

        he_x, he_y = (self._visu.boundingRect().size() / 2).toTuple()
        d_x, d_y = (connecting_from - self.center()).toTuple()

        t = math.sqrt((d_x / he_x)**2 + (d_y / he_y)**2)
        if t == 0:
            return GraphicsDirectedGraphNode.socket_pos(self)

        return QPointF((d_x / t) + he_x, (d_y / t) + he_y)

class NetworkGraphEdge(GraphicsDirectedGraphEdge):
    ui_edge_arrow_width: ClassVar[float] = 10.0

    def __init__(self,
                 graph: NetworkGraph,
                 begin: NetworkGraphNode,
                 end: NetworkGraphNode,
                 /,
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(graph, begin, end, parent)

        self._visu: GraphicsArrow = GraphicsArrow(
            end.socket_pos() - begin.socket_pos(),
            self.ui_edge_arrow_width,
            parent=self
        )
        self._visu.setPos(begin.socket_pos())
    
    def on_graphics_directed_graph_node_moved(self) -> None:
        begin_node: NetworkGraphNode = cast(NetworkGraphNode, self.begin_node())
        end_node: NetworkGraphNode = cast(NetworkGraphNode, self.end_node())

        end_node_center_begin_node_local: QPointF = end_node.mapToItem(begin_node, end_node.center())
        begin_node_center_end_node_local: QPointF = begin_node.mapToItem(end_node, begin_node.center())

        begin_node_surface: QPointF = begin_node.mapToScene(begin_node.socket_pos(end_node_center_begin_node_local))
        end_node_surface: QPointF = end_node.mapToScene(end_node.socket_pos(begin_node_center_end_node_local))
        v: QPointF = end_node_surface - begin_node_surface
        self._visu.update_arrow(
            v=v
        )
        self._visu.setPos(begin_node_surface)

class NetworkGraph(GraphicsDirectedGraph):

    def __init__(self,
                 /,
                 parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)

    def create_node(self) -> NetworkGraphNode:
        return NetworkGraphNode(self, self)

    def create_edge(self, begin: NetworkGraphNode, end: NetworkGraphNode) -> NetworkGraphEdge:
        return NetworkGraphEdge(self, begin, end, self)

    def arrange_ring(self):
        node_spacing: QSizeF = QSizeF(200.0, 200.0) # TODO: currently const
        node_count: int = len(self._nodes)

        if node_count < 3:
            raise RuntimeError(f"cannot arrange_ring with less than 3 nodes!")
        
        dphi: float = (2 * math.pi) / node_count

        for i, node in enumerate(self.graphics_nodes()):
            phi: float = dphi * i

            node_extent: QSizeF = node.boundingRect().size()
            node_spacing_extent: QSizeF = node_spacing
            node_area_half_extent: QSizeF = (node_extent + node_spacing_extent) * 0.5

            on_ring_pos: QPointF = QPointF(
                node_area_half_extent.width()  * math.cos(phi),
                node_area_half_extent.height() * math.sin(phi)
            )

            node.set_center_pos(on_ring_pos)