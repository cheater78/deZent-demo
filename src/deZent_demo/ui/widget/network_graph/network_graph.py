from __future__ import annotations

from typing import cast, Any, Callable
import math

from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsSimpleTextItem,
    QGraphicsSceneMouseEvent,
)
from PySide6.QtGui import (
    QColor, 
    QPen,
)
from PySide6.QtCore import (
    Qt,
    QPointF,
    QSizeF,
)

from .graphics_directed_graph import GraphicsDirectedGraphNode, GraphicsDirectedGraphEdge, GraphicsDirectedGraph
from deZent_demo.ui.utils import *
from deZent_demo.ui.style.style import *
from deZent_demo.utils.config.config import *

@dataclass
class NetworkGraphNodeStyle(Style):
    ellipse_width: float = 100.0
    ellipse_height: float = 70.0
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
    label_style: TextStyle = field(
        default_factory=lambda: TextStyle(
            QBrush(QColor(Qt.GlobalColor.black)),
            LineStyle(QPen(QColor(Qt.GlobalColor.black), 1)),
            QFont('Arial', 12)
        )
    )

class NetworkGraphNode(Styled[NetworkGraphNodeStyle], GraphicsDirectedGraphNode):

    def __init__(
        self,
        graph: NetworkGraph,
        style: NetworkGraphNodeStyle = NetworkGraphNodeStyle(),
        parent: QGraphicsItem | None = None,
        **kwargs: Any
    ) -> None:
        self._visu: QGraphicsEllipseItem = QGraphicsEllipseItem(0,0,0,0)
        self._label: QGraphicsSimpleTextItem = QGraphicsSimpleTextItem()
        
        super().__init__(
            style=style,
            graph=graph,
            parent=parent,
            **kwargs
        )
        
        self._visu.setParentItem(self)
        self._label.setParentItem(self)

    @override
    def on_style_change(self, new_style: NetworkGraphNodeStyle) -> None:
        self._visu.setRect(
            0.0, 0.0,
            new_style.ellipse_width, new_style.ellipse_height,
        )
        self._visu.setPen(new_style.ellipse_style.border.pen)
        self._visu.setBrush(new_style.ellipse_style.fill)

        self._label.setPen(new_style.label_style.border.pen)
        self._label.setBrush(new_style.label_style.fill)
        self._label.setFont(new_style.label_style.font)
        self._label.setPos(self._visu.boundingRect().center() - self._label.boundingRect().center())

    def set_label(self, label: str) -> None:
        self._label.setText(label)
        self._label.setPos(self._visu.boundingRect().center() - self._label.boundingRect().center())

    def link_to(self, node: NetworkGraphNode) -> NetworkGraphEdge:
        if not isinstance(self._graph, NetworkGraph):
            raise RuntimeError(f"Graph of NetworkGraphNode was not of type NetworkGraph!")
        edge: NetworkGraphEdge = NetworkGraphEdge(self._graph, self, node, parent=self._graph)
        self._graph.add_edge(edge)
        return edge

    def socket_pos(self, connecting_from: QPointF | None = None) -> QPointF:
        if connecting_from is None:
            return GraphicsDirectedGraphNode.socket_pos(self)
        hit: QPointF | None = ellipse_hit(connecting_from, self.center(), self.boundingRect().size())
        if hit is None:
            return GraphicsDirectedGraphNode.socket_pos(self)
        return hit

class NetworkGraphGatewayNodeStyle(Style):
    #TODO
    pass

NetworkGraphGatewayNodeInteractionCB = Callable[[], None]

class NetworkGraphGatewayNode(NetworkGraphNode): # TODO: inheritance friendly Styled[]
    # TODO: cleanup, just PoC for now
    def __init__(
        self,
        graph: NetworkGraph,
        style: NetworkGraphNodeStyle = NetworkGraphNodeStyle(),
        parent: QGraphicsItem | None = None,
        **kwargs: Any
    ) -> None:
        self._interaction_token: QGraphicsEllipseItem = QGraphicsEllipseItem(0,0,0,0)
        self._coordinator_token: QGraphicsSimpleTextItem = QGraphicsSimpleTextItem("CCC")
        
        self._interaction_cb: NetworkGraphGatewayNodeInteractionCB | None = None

        super().__init__(graph, style, parent, **kwargs)

        self._interaction_token.setParentItem(self)
        self._interaction_token.setZValue(1) # raise TODO: edges are above, but this doesnt change it

        self._coordinator_token.setParentItem(self)
        self._coordinator_token.setZValue(1)

        self.set_interaction(False)
        self.set_coordinator(False)

    @override
    def on_style_change(self, new_style: NetworkGraphNodeStyle) -> None:
        super().on_style_change(new_style)

        self._interaction_token.setRect(
            0.0, 0.0,
            new_style.ellipse_height * 0.2, new_style.ellipse_height * 0.2,
        )
        self._interaction_token.setPen(QPen(QColor(Qt.GlobalColor.darkBlue), 1))
        self._interaction_token.setBrush(QColor(Qt.GlobalColor.blue))
        hit: QPointF | None = ellipse_hit(self._visu.boundingRect().center() + QPointF(+1.0, -1.0), self._visu.boundingRect().center(), self._visu.boundingRect().size())
        if hit is None:
            return
        self._interaction_token.setPos(hit - self._interaction_token.boundingRect().center())

        self._coordinator_token.setPen(QPen(QColor(Qt.GlobalColor.red), 1))
        self._coordinator_token.setBrush(QColor(Qt.GlobalColor.red))
        hit: QPointF | None = ellipse_hit(self._visu.boundingRect().center() + QPointF(-1.0, -1.0), self._visu.boundingRect().center(), self._visu.boundingRect().size())
        if hit is None:
            return
        self._coordinator_token.setPos(hit - self._coordinator_token.boundingRect().center())

    def set_interaction(self, enable: bool) -> None:
        self._interaction_token.setVisible(enable)

    def set_coordinator(self, enable: bool) -> None:
        self._coordinator_token.setVisible(enable)

    def set_interaction_cb(self, callback: NetworkGraphGatewayNodeInteractionCB | None) -> None:
        self._interaction_cb = callback

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        if not self._interaction_token.isVisible(): # interaction token visibility determines interactiveness
            return
        if event.button() == Qt.MouseButton.LeftButton \
            and self._interaction_cb is not None:
            self._interaction_cb()

        super().mouseDoubleClickEvent(event)


@dataclass
class NetworkGraphEdgeStyle(Style):
    edge_arrow_style: GraphicsArrowStyle = field(
        default_factory=lambda: GraphicsArrowStyle(
            10,
            0,
            LineStyle(
                QPen(
                    QColor(Qt.GlobalColor.gray),
                    2,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )
        )
    )

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
        self._visu.setZValue(0)
        

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

@dataclass
class NetworkGraphStyle(Style):
    node_spacing: QSizeF = field(
        default_factory=lambda: QSizeF(234.0, 234.0)
    )

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

        phi0: float = - (math.pi / 2) # start at the top
        dphi: float = (2 * math.pi) / node_count

        for i, node in enumerate(nodes):
            phi: float = dphi * i + phi0

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
        node = NetworkGraphNode(self, parent=self)
        self.add_node(node)
        return node

    def create_gateway_node(self) -> NetworkGraphGatewayNode:
        node = NetworkGraphGatewayNode(self, parent=self)
        self.add_node(node)
        return node

    def create_edge(self, begin: NetworkGraphNode, end: NetworkGraphNode) -> NetworkGraphEdge:
        return NetworkGraphEdge(self, begin, end, parent=self)