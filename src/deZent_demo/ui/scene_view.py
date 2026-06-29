from __future__ import annotations
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
)
from PySide6.QtGui import (
    QTransform,
    QWheelEvent,
    QResizeEvent,
    QMouseEvent,
)
from PySide6.QtCore import Qt, QPoint, QPointF

class SceneView(QGraphicsView):

    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setScene(scene)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self.camera = QPointF(0.0, 0.0)
        self.zoom = 1.0

        self._panning = False
        self._last_mouse = QPointF(0.0, 0.0)

        # self.fitInView(scene.sceneRect())
    
    def updateCamera(self):
        t = QTransform()
        t.scale(self.zoom, self.zoom)
        self.setTransform(t, False)
        self.centerOn(self.camera)

    def moveCamera(self, delta: QPointF | QPoint) -> None:
        self.camera += QPointF(delta)
        self.updateCamera()

    def wheelEvent(self, event: QWheelEvent):
        self.zoom *= 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.updateCamera()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.updateCamera()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_mouse = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._panning:
            delta = event.position() - self._last_mouse
            self._last_mouse = event.position()

            self.camera -= QPointF(
                delta.x() / self.zoom,
                delta.y() / self.zoom
            )

            self.updateCamera()

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)
