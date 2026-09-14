from __future__ import annotations
from typing import ClassVar

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsScene
)
from PySide6.QtGui import (
    QWheelEvent,
    QMouseEvent,
    QKeySequence,
    QShortcut
)
from PySide6.QtCore import (
    Qt,
    QPointF,
    QSizeF,
    QRectF,
)

class PanningGraphicsView(QGraphicsView):
    pan_key: ClassVar[Qt.MouseButton] = Qt.MouseButton.RightButton
    refit_key: ClassVar[QKeySequence] = QKeySequence("R")
    refit_scene_margin: ClassVar[QSizeF] = QSizeF(0.02, 0.02)
    zoom_sensitivity: ClassVar[float] = 0.15 # change of scale

    def __init__(self,
                 /,
                 graphics_scene: QGraphicsScene | None = None,
                 pan_key: Qt.MouseButton = pan_key,
                 refit_key: QKeySequence = refit_key,
                 refit_scene_margin: QSizeF = refit_scene_margin,
                 zoom_sensitivity: float = zoom_sensitivity,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        if graphics_scene is not None:
            self.setScene(graphics_scene)

        # panning view -> no scrolling for lateral movement
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # pan by drag/dropping is handled manually
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        # transformation is handled manually
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

        self._zoom_scale: float = 1.0 + zoom_sensitivity
        self._pan_key: Qt.MouseButton = pan_key
        self._panning: bool = False
        self._last_mouse_pos: QPointF = QPointF()
        self._last_cursor_shape: Qt.CursorShape = Qt.CursorShape.ArrowCursor

        self._refit_key = refit_key
        self._refit_scene_margin: QSizeF = refit_scene_margin
        self._refit_shortcut = QShortcut(self._refit_key, self)
        self._refit_shortcut.activated.connect(self.refit_view)

        self.refit_view()

    def wheelEvent(self, event: QWheelEvent) -> None:
        zoom_scale: float = self._zoom_scale if event.angleDelta().y() > 0 else (1 / self._zoom_scale)

        cursor_scene_pos: QPointF = self.mapToScene(event.position().toPoint())
        self.scale(zoom_scale, zoom_scale)
        skewed_cursor_scene_pos: QPointF = self.mapToScene(event.position().toPoint())

        translation_correction: QPointF = skewed_cursor_scene_pos - cursor_scene_pos
        self.translate(translation_correction.x(), translation_correction.y())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == self._pan_key:
            self._panning = True
            self._last_mouse_pos = event.position()
            self._last_cursor_shape = self.cursor().shape()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == self._pan_key:
            self._panning = False
            self.setCursor(self._last_cursor_shape)
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:

        if self._panning:
            delta: QPointF = event.position() - self._last_mouse_pos
            self._last_mouse_pos = event.position()

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

    def refit_view(self) -> None:
        scene: QGraphicsScene | None = self.scene() # NOTE: can be None (contrary to declaration)
        if scene is None or not scene.items(): # pyright: ignore[reportUnnecessaryComparison]
            return
        scene_aabb: QRectF = scene.itemsBoundingRect()

        view_rect: QRectF = scene_aabb.adjusted(
            - scene_aabb.width()  * self.refit_scene_margin.width(),
            - scene_aabb.height() * self.refit_scene_margin.height(),
            + scene_aabb.width()  * self.refit_scene_margin.width(),
            + scene_aabb.height() * self.refit_scene_margin.height(),
        )

        self.fitInView(
            view_rect,
            Qt.AspectRatioMode.KeepAspectRatio
        )