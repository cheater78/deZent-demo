
from .panning_graphics_view import PanningGraphicsView
from .network_graph import NetworkGraph, NetworkGraphNode

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsScene,
)

# NOTE: QGraphicsView (which PanningGraphicsView is) is a QWidget
class NetworkGraphView(PanningGraphicsView):

    def __init__(self,
                 /,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._scene: QGraphicsScene = QGraphicsScene(parent=self)
        self._network_graph: NetworkGraph = NetworkGraph()

        self._scene.addItem(self._network_graph)
        
        self.setScene(self._scene)
        self.refit_view()

    def graph(self) -> NetworkGraph:
        return self._network_graph
    
    def create_node(self) -> NetworkGraphNode:
        node = self._network_graph.create_node()
        self._network_graph.add_node(node)
        return node

