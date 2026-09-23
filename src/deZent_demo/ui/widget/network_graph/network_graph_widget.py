from PySide6.QtWidgets import (
    QWidget,
)

from ...view.panning_graphics_view import PanningGraphicsView
from .network_graph import NetworkGraph
from deZent_demo.ui.style.style import *

@dataclass
class NetworkGraphWidgetStyle(GraphicsViewStyle):
    pass # TODO: expose NetworkGraph style

class NetworkGraphWidget(Styled[NetworkGraphWidgetStyle], PanningGraphicsView):

    def __init__(
        self,
        style: NetworkGraphWidgetStyle = NetworkGraphWidgetStyle(),
        parent: QWidget | None = None) -> None:

        self._network_graph: NetworkGraph = NetworkGraph()

        super().__init__(
            style=style,
            parent=parent
        )

        self.scene().addItem(self._network_graph)
        self.fit_scene_in_view()

    def graph(self) -> NetworkGraph:
        return self._network_graph

    @override
    def on_style_change(self, new_style: NetworkGraphWidgetStyle) -> None:
        new_style.apply(self)

