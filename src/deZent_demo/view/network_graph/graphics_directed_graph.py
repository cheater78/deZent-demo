from abc import abstractmethod
from typing import Any, cast, override

from .directed_graph import DirectedGraphNode, DirectedGraphEdge, DirectedGraph
from deZent_demo.view.utils import GraphicsContainerItem

from PySide6.QtWidgets import (
    QGraphicsItem
)
from PySide6.QtCore import (
    QPointF,
)

class GraphicsDirectedGraphNode(DirectedGraphNode, GraphicsContainerItem):

    def __init__(self,
                 graph: GraphicsDirectedGraph,
                 /,
                 parent: QGraphicsItem | None = None) -> None:
        DirectedGraphNode.__init__(self, graph)
        GraphicsContainerItem.__init__(self, parent)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def socket_pos(self, connecting_from: QPointF | None = None) -> QPointF:
        return self.center()

    @override
    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        for directed_graph_edge in self.adjacent_edges():
            graphics_directed_graph_edge: GraphicsDirectedGraphEdge = cast(GraphicsDirectedGraphEdge, directed_graph_edge)
            graphics_directed_graph_edge.on_graphics_directed_graph_node_moved()
        return super().itemChange(change, value)

class GraphicsDirectedGraphEdge(DirectedGraphEdge, GraphicsContainerItem):

    def __init__(self,
                     graph: GraphicsDirectedGraph,
                     begin: GraphicsDirectedGraphNode,
                     end: GraphicsDirectedGraphNode,
                     /,
                     parent: QGraphicsItem | None = None) -> None:
        DirectedGraphEdge.__init__(self, graph, begin, end)
        GraphicsContainerItem.__init__(self, parent)

    @abstractmethod
    def on_graphics_directed_graph_node_moved(self) -> None:
        pass

class GraphicsDirectedGraph(DirectedGraph, GraphicsContainerItem):

    def __init__(self,
                 /,
                 parent: QGraphicsItem | None = None) -> None:
        DirectedGraph.__init__(self)
        GraphicsContainerItem.__init__(self, parent)

    def graphics_nodes(self) -> list[GraphicsDirectedGraphNode]:
        return cast(list[GraphicsDirectedGraphNode], self._nodes)
