from .graphics_directed_graph import GraphicsDirectedGraphNode, GraphicsDirectedGraphEdge, GraphicsDirectedGraph

from deZent_demo.view.utils import *
from deZent_demo.view.style.style import *
from deZent_demo.utils.config.config import *

from typing import cast, Any
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

@dataclass
class NetworkGraphNodeStyle(Style):
    ellipse_width: float = 60.0
    ellipse_height: float = 40.0
    ellipse_style: BorderedStyle = field(
        default_factory=lambda: BorderedStyle(
            QBrush(QColor(Qt.GlobalColor.lightGray)),
            LineStyle(
                QPen(
                    QColor(Qt.GlobalColor.darkGray),
                    2,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )
        )
    )

@dataclass
class NetworkGraphEdgeStyle(Style):
    edge_arrow_style: GraphicsArrowStyle = field(
        default_factory=lambda: GraphicsArrowStyle(
            20,
            45,
            LineStyle(
                QPen(
                    QColor(Qt.GlobalColor.gray),
                    4,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )
        )
    )

@dataclass
class NetworkGraphStyle(Style):
    node_spacing: QSizeF = field(
        default_factory=lambda: QSizeF(234.0, 234.0)
    )

class NetworkGraphNode(Styled[NetworkGraphNodeStyle], GraphicsDirectedGraphNode):

    @staticmethod
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

    def __init__(
        self,
        graph: NetworkGraph,
        style: NetworkGraphNodeStyle = NetworkGraphNodeStyle(),
        parent: QGraphicsItem | None = None,
        **kwargs: Any
    ) -> None:
        self._visu: QGraphicsEllipseItem = QGraphicsEllipseItem(0,0,0,0)
        
        super().__init__(
            style=style,
            graph=graph,
            parent=parent,
            **kwargs
        )
        
        self._visu.setParentItem(self)

    @override
    def on_style_change(self, new_style: NetworkGraphNodeStyle) -> None:
        self._visu.setRect(
            0.0, 0.0,
            new_style.ellipse_width, new_style.ellipse_height,
        )
        self._visu.setPen(new_style.ellipse_style.border.pen)
        self._visu.setBrush(new_style.ellipse_style.fill)
        return

    def link_to(self, node: NetworkGraphNode) -> NetworkGraphEdge:
        if not isinstance(self._graph, NetworkGraph):
            raise RuntimeError(f"Graph of NetworkGraphNode was not of type NetworkGraph!")
        edge: NetworkGraphEdge = NetworkGraphEdge(self._graph, self, node, parent=self._graph)
        self._graph.add_edge(edge)
        return edge

    def socket_pos(self, connecting_from: QPointF | None = None) -> QPointF:
        if connecting_from is None:
            return GraphicsDirectedGraphNode.socket_pos(self)
        hit: QPointF | None = self.ellipse_hit(connecting_from, self.center(), self.boundingRect().size())
        if hit is None:
            return GraphicsDirectedGraphNode.socket_pos(self)
        return hit

class NetworkGraphEdge(Styled[NetworkGraphEdgeStyle], GraphicsDirectedGraphEdge):

    def __init__(
        self,
        graph: NetworkGraph,
        begin: NetworkGraphNode,
        end: NetworkGraphNode,
        style: NetworkGraphEdgeStyle = NetworkGraphEdgeStyle(),
        parent: QGraphicsItem | None = None,
        **kwargs: Any
    ) -> None:
        self._visu: GraphicsArrow = GraphicsArrow(QPointF())
        
        super().__init__(
            style=style,
            graph=graph,
            begin=begin,
            end=end,
            parent=parent,
            **kwargs
        )

        self._visu.setParentItem(self)
        

    @override
    def on_style_change(self, new_style: NetworkGraphEdgeStyle) -> None:
        self._visu.set_style(new_style.edge_arrow_style)
        self.on_graphics_directed_graph_node_moved()
        return
    
    def on_graphics_directed_graph_node_moved(self) -> None:
        begin_node: NetworkGraphNode = cast(NetworkGraphNode, self.begin_node())
        end_node: NetworkGraphNode = cast(NetworkGraphNode, self.end_node())

        end_node_center_begin_node_local: QPointF = end_node.mapToItem(begin_node, end_node.center())
        begin_node_center_end_node_local: QPointF = begin_node.mapToItem(end_node, begin_node.center())

        begin_node_surface: QPointF = begin_node.mapToScene(begin_node.socket_pos(end_node_center_begin_node_local))
        end_node_surface: QPointF = end_node.mapToScene(end_node.socket_pos(begin_node_center_end_node_local))
        v: QPointF = end_node_surface - begin_node_surface
        self._visu.update_arrow(v)
        self._visu.setPos(begin_node_surface)

class NetworkGraph(Styled[NetworkGraphStyle], GraphicsDirectedGraph):

    @staticmethod
    def arrange_ring(
        nodes: list[NetworkGraphNode],
        center: QPointF,
        node_spacing: QSizeF
    ) -> None:
        node_count: int = len(nodes)

        if node_count < 3:
            raise RuntimeError(f"cannot arrange_ring with less than 3 nodes!")
        
        dphi: float = (2 * math.pi) / node_count

        for i, node in enumerate(nodes):
            phi: float = dphi * i

            node_extent: QSizeF = node.boundingRect().size()
            node_spacing_extent: QSizeF = node_spacing
            node_area_half_extent: QSizeF = (node_extent + node_spacing_extent) * 0.5

            on_ring_pos: QPointF = center + QPointF(
                node_area_half_extent.width()  * math.cos(phi),
                node_area_half_extent.height() * math.sin(phi)
            )

            node.set_center_pos(on_ring_pos)

    def __init__(
        self,
        style: NetworkGraphStyle = NetworkGraphStyle(),
        parent: QGraphicsItem | None = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            style=style,
            parent=parent,
            **kwargs
        )

    def create_node(self) -> NetworkGraphNode:
        return NetworkGraphNode(self, parent=self)

    def create_edge(self, begin: NetworkGraphNode, end: NetworkGraphNode) -> NetworkGraphEdge:
        return NetworkGraphEdge(self, begin, end, parent=self)