from typing import Callable

from PySide6.QtWidgets import (
    QWidget
)
from PySide6.QtGui import (
    QResizeEvent,
)

LayerStackResizeCB = Callable[[QResizeEvent], None]

class LayerStackWidget(QWidget):
    """
    LayerStack-ish widget, currently supports 2 layers only

    While a proper LayerStack would implement proper event propagation
    and hit detection, this is sufficient for now
    """

    def __init__(self, resize_cb: LayerStackResizeCB | None = None):
        super().__init__()
        self._resize_cb: LayerStackResizeCB | None = resize_cb

    def set_resize_cb(self, resize_cb: LayerStackResizeCB | None = None) -> None:
        self._resize_cb = resize_cb

    def makeLayer(self, widget: QWidget) -> None:
        widget.setParent(self)
        widget.lower()

    def makeOverlay(self, widget: QWidget) -> None:
        widget.setParent(self)
        widget.raise_()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._resize_cb is not None:
            self._resize_cb(event)
