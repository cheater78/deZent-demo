from __future__ import annotations
from typing import ClassVar, override

from PySide6.QtCore import (
    Qt,
    QPoint, QPointF,
    QRectF,
)
from PySide6.QtGui import (
    QMouseEvent,
    QResizeEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QWidget,
)

from deZent_demo.ui.view.graphics_scene_view import *
from deZent_demo.ui.utils import rect_clamped_rect_center


class PanningGraphicsView(GraphicsSceneView):
    """
    QGraphicsView for panning and zooming.
    """
    # TODO: clean this up
    pan_key: ClassVar[Qt.MouseButton] = Qt.MouseButton.RightButton

    # Relative to content width/height.
    pan_scene_margin: ClassVar[float] = 16.0

    # Fractional zoom change per wheel step.
    zoom_sensitivity: ClassVar[float] = 0.15

    minimum_content_size: ClassVar[float] = 4.0

    def __init__(
        self,
        pan_key: Qt.MouseButton = pan_key,
        pan_scene_margin: float = pan_scene_margin,
        zoom_sensitivity: float = zoom_sensitivity,
        scene: QGraphicsScene | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            scene=scene,
            parent=parent,
        )

        self._pan_key: Qt.MouseButton = pan_key
        self._pan_scene_margin: float = pan_scene_margin
        self._zoom_factor: float = 1.0 + zoom_sensitivity

        self._panning: bool = False
        self._last_mouse_pos: QPointF = QPointF()
        self._last_cursor_shape: Qt.CursorShape = Qt.CursorShape.ArrowCursor

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        # Panning is controlled explicitly through centerOn().
        # Zoom temporarily uses AnchorUnderMouse.
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
    
    def _navigation_rect(
        self,
    ) -> QRectF:
        """
        Build the navigation envelope around the scene content.
        """
        content_rect: QRectF = self._scene_content_bounding_rect()
        if content_rect.isEmpty() or not content_rect.isValid():
            return self._default_scene_rect

        content_width: float = max(content_rect.width(), self.minimum_content_size)
        content_height: float = max(content_rect.height(), self.minimum_content_size)

        margin_x: float = content_width * self._pan_scene_margin
        margin_y: float = content_height * self._pan_scene_margin

        return content_rect.adjusted(
            -margin_x,
            -margin_y,
            margin_x,
            margin_y,
        )

    @override
    def fit_scene_in_view(self) -> None:
        """
        Fit the scene content plus its configured refit margin into the viewport.
        """
        GraphicsSceneView.fit_scene_in_view(self)
        self.update_navigation_rect()
        self._clamp_view_to_navigation_area()

    def update_navigation_rect(self) -> None:
        navigation_rect: QRectF = self._navigation_rect()
        if navigation_rect.isEmpty() or not navigation_rect.isValid():
            self.setSceneRect(self._default_scene_rect)
            return
        
        self.setSceneRect(navigation_rect)

    def _clamp_view_to_navigation_area(self) -> None:
        """
        Keep the complete viewport inside the navigation area.
        """
        navigation_rect: QRectF = self._navigation_rect()
        if navigation_rect.isEmpty() or not navigation_rect.isValid():
            return

        viewport_rect: QRectF = self._viewport_scene_rect()
        if viewport_rect.isEmpty() or not viewport_rect.isValid():
            return
        
        clamped_center: QPointF = rect_clamped_rect_center(viewport_rect, navigation_rect)

        current_center: QPointF = viewport_rect.center()
        if clamped_center != current_center:
            self.centerOn(clamped_center)

    def _pan_to_mouse_position(
        self,
        previous_mouse_pos: QPointF,
        current_mouse_pos: QPointF,
    ) -> None:
        previous_pos: QPoint = previous_mouse_pos.toPoint()
        current_pos: QPoint = current_mouse_pos.toPoint()

        scene_position_previous: QPointF = self.mapToScene(previous_pos)
        scene_position_current: QPointF = self.mapToScene(current_pos)
        scene_delta: QPointF = (scene_position_previous - scene_position_current)

        viewport_rect: QRectF = self._viewport_scene_rect()
        current_center: QPointF = viewport_rect.center()

        self.centerOn(current_center + scene_delta)
        self._clamp_view_to_navigation_area()


    def _zoom_at_cursor(
        self,
        viewport_position: QPointF,
        factor: float,
    ) -> None:
        """
        Zoom around the scene position currently underneath the cursor.

        The cursor position defines the pivot of the transformation. No
        viewport recentering is performed.
        """
        cursor_position: QPoint = viewport_position.toPoint()
        cursor_scene_position: QPointF = self.mapToScene(cursor_position)

        transform = self.transform()
        transform.translate(
            cursor_scene_position.x(),
            cursor_scene_position.y(),
        )
        transform.scale(factor, factor)
        transform.translate(
            -cursor_scene_position.x(),
            -cursor_scene_position.y(),
        )

        self.setTransform(transform)


    def wheelEvent(self, event: QWheelEvent) -> None:
        wheel_delta: int = event.angleDelta().y()

        if wheel_delta == 0:
            event.ignore()
            return

        factor: float = (
            self._zoom_factor
            if wheel_delta > 0
            else 1.0 / self._zoom_factor
        )

        self._zoom_at_cursor(event.position(), factor)

        if self._panning:
            self._last_mouse_pos = event.position()

        self._clamp_view_to_navigation_area()

        event.accept()

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
            current_mouse_pos: QPointF = event.position()

            self._pan_to_mouse_position(
                self._last_mouse_pos,
                current_mouse_pos,
            )

            self._last_mouse_pos = current_mouse_pos
            event.accept()
            return

        super().mouseMoveEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._clamp_view_to_navigation_area()
