from deZent_demo.ui.view.graphics_scene_view import GraphicsSceneView
from .counting_bloom_filter_plot import CBFPlot
from deZent_demo.ui.style.style import *

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsScene,
)

@dataclass
class CBFPlotWidgetStyle(GraphicsViewStyle):
    pass # TODO: expose CBFPlot style

class CBFPlotWidget(Styled[CBFPlotWidgetStyle], GraphicsSceneView):
    def __init__(
        self,
        style: CBFPlotWidgetStyle = CBFPlotWidgetStyle(),
        scene: QGraphicsScene | None = None,
        parent: QWidget | None = None,
        **kwargs: Any,
    ) -> None:
        self._cbf_plot: CBFPlot = CBFPlot() 
        
        super().__init__(
            style=style,
            scene=scene,
            parent=parent,
            **kwargs,
        )
        
        self.scene().addItem(self._cbf_plot)
        #self.fit_scene_in_view()

    @override
    def on_style_change(self, new_style: CBFPlotWidgetStyle) -> None:
        new_style.apply(self)

    def plot(self) -> CBFPlot:
        return self._cbf_plot