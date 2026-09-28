from deZent_demo.ui.view.graphics_scene_view import GraphicsSceneView
from .counting_bloom_filter_plot import *
from deZent_demo.ui.style.style import *
from deZent_demo.ui.utils import *

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QPushButton,
    QStyle,
)
from PySide6.QtGui import (
    QResizeEvent,
    QPalette
)
from PySide6.QtCore import (
    QSize
)

@dataclass
class CBFPlotWidgetStyle(GraphicsViewStyle):
    cbf_plot_style: CBFPlotStyle = field(default_factory=lambda: CBFPlotStyle())

class CBFPlotWidget(Styled[CBFPlotWidgetStyle], GraphicsSceneView):

    def __init__(
        self,
        style: CBFPlotWidgetStyle = CBFPlotWidgetStyle(),
        scene: QGraphicsScene | None = None,
        parent: QWidget | None = None,
        **kwargs: Any,
    ) -> None:
        self._cbf_plot: CBFPlot = CBFPlot()
        self._close_button = QPushButton()

        super().__init__(
            style=style,
            scene=scene,
            parent=parent,
            **kwargs,
        )
        
        self.scene().addItem(self._cbf_plot)

        self._close_button.setParent(self)
        self._close_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        )
        self._close_button.setFlat(True)
        self._close_button.setAutoFillBackground(False) # hide background
        palette = self._close_button.palette()
        palette.setColor(QPalette.ColorRole.Button, Qt.GlobalColor.lightGray)
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        self._close_button.setPalette(palette)
        self._close_button.clicked.connect(self.hide)

    @override
    def on_style_change(self, new_style: CBFPlotWidgetStyle) -> None:
        new_style.apply(self)
        self._cbf_plot.set_style(new_style.cbf_plot_style)

    def plot(self) -> CBFPlot:
        return self._cbf_plot

    @override
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event) 

        size: QSize = self._close_button.sizeHint()
        self._close_button.setGeometry(
            self.width() - size.width(),
            0,
            size.width(),
            size.height(),
        )
