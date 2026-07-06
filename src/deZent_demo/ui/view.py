from __future__ import annotations

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QWheelEvent, QMouseEvent, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QPointF, QSizeF

class PanningView(QGraphicsView):

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)

        self.setScene(scene)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # IMPORTANT: no scroll-based interaction at all
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.NoAnchor
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.NoAnchor
        )

        self._panning: bool = False
        self._last_mouse: QPointF = QPointF()

        shortcut = QShortcut(QKeySequence("R"), self)
        shortcut.activated.connect(self.reset_view)

        self.reset_view()

    # -----------------------------------------------------

    def wheelEvent(self, event: QWheelEvent) -> None:

        factor: float = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15

        old_scene_pos: QPointF = self.mapToScene(event.position().toPoint())

        self.scale(factor, factor)

        new_scene_pos: QPointF = self.mapToScene(event.position().toPoint())

        delta: QPointF = new_scene_pos - old_scene_pos
        self.translate(delta.x(), delta.y())

    # -----------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:

        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_mouse = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    # -----------------------------------------------------

    def mouseMoveEvent(self, event: QMouseEvent) -> None:

        if self._panning:

            delta: QPointF = event.position() - self._last_mouse
            self._last_mouse = event.position()

            # get current zoom scale
            transform = self.transform()
            sx = transform.m11()
            sy = transform.m22()

            # normalize delta into scene space
            dx = delta.x() / sx
            dy = delta.y() / sy

            self.translate(dx, dy)

            event.accept()
            return

        super().mouseMoveEvent(event)

    # -----------------------------------------------------

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:

        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)

    # -----------------------------------------------------

    def reset_view(self) -> None:
        margin: QSizeF = QSizeF(0.2, 0.2)

        items = self.scene().items()
        if not items:
            return

        rect = None

        for item in items:
            r = item.sceneBoundingRect()
            rect = r if rect is None else rect.united(r)

        if rect is not None:
            self.fitInView(
                rect.adjusted(
                    - rect.width()  * margin.width(),
                    - rect.height() * margin.height(),
                    + rect.width()  * margin.width(),
                    + rect.height() * margin.height(),
                ),
                Qt.AspectRatioMode.KeepAspectRatio
            )