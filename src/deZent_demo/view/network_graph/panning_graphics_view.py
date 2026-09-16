from __future__ import annotations

from typing import ClassVar

from PySide6.QtCore import (
    QPoint,
    QPointF,
    QRectF,
    QSizeF,
    Qt,
)
from PySide6.QtGui import (
    QKeySequence,
    QMouseEvent,
    QResizeEvent,
    QShortcut,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QWidget,
)


class PanningGraphicsView(QGraphicsView):
    """
    QGraphicsView for panning and zooming.
    scene margins are relative to the content size
    """

    pan_key: ClassVar[Qt.MouseButton] = Qt.MouseButton.RightButton
    refit_key: ClassVar[QKeySequence] = QKeySequence("R")

    # Relative to content width/height.
    refit_scene_margin: ClassVar[QSizeF] = QSizeF(0.02, 0.02)

    # Relative to content width/height.
    pan_scene_margin: ClassVar[float] = 16.0

    # Fractional zoom change per wheel step.
    zoom_sensitivity: ClassVar[float] = 0.15

    minimum_content_size: ClassVar[float] = 4.0

    def __init__(
        self,
        /,
        graphics_scene: QGraphicsScene | None = None,
        pan_key: Qt.MouseButton = pan_key,
        refit_key: QKeySequence = refit_key,
        refit_scene_margin: QSizeF = refit_scene_margin,
        pan_scene_margin: float = pan_scene_margin,
        zoom_sensitivity: float = zoom_sensitivity,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._validate_configuration(
            refit_scene_margin=refit_scene_margin,
            pan_scene_margin=pan_scene_margin,
            zoom_sensitivity=zoom_sensitivity,
        )

        self._pan_key: Qt.MouseButton = pan_key
        self._refit_key: QKeySequence = refit_key
        self._refit_scene_margin: QSizeF = refit_scene_margin
        self._pan_scene_margin: float = pan_scene_margin
        self._zoom_factor: float = 1.0 + zoom_sensitivity

        self._panning: bool = False
        self._last_mouse_pos: QPointF = QPointF()
        self._last_cursor_shape: Qt.CursorShape = Qt.CursorShape.ArrowCursor

        self._navigation_rect: QRectF = QRectF()

        self.setScene(graphics_scene)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        # Panning is controlled explicitly through centerOn().
        # Zoom temporarily uses AnchorUnderMouse.
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

        self._refit_shortcut: QShortcut = QShortcut(self._refit_key, self)
        self._refit_shortcut.activated.connect(self.refit_view)

        self.update_navigation_area()
        self.refit_view()

    @staticmethod
    def _validate_configuration(
        refit_scene_margin: QSizeF,
        pan_scene_margin: float,
        zoom_sensitivity: float,
    ) -> None:
        """Validate configuration values."""
        if (
            refit_scene_margin.width() < 0.0
            or refit_scene_margin.height() < 0.0
        ):
            raise ValueError(
                "refit_scene_margin dimensions must be non-negative"
            )

        if pan_scene_margin < 0.0:
            raise ValueError("pan_scene_margin must be non-negative")

        if zoom_sensitivity <= -1.0:
            raise ValueError(
                "zoom_sensitivity must be greater than -1.0"
            )

    def _scene_content_rect(self) -> QRectF:
        """
        Return the bounding rectangle of all graphical scene content.

        Empty or invalid content produces an empty rectangle.
        """
        scene: QGraphicsScene | None = self.scene()
        if scene is None:  # pyright: ignore[reportUnnecessaryComparison]
            return QRectF()

        content_rect: QRectF = scene.itemsBoundingRect()
        if content_rect.isEmpty() or not content_rect.isValid():
            return QRectF()

        return content_rect

    @staticmethod
    def _expand_by_relative_margin(
        rect: QRectF,
        margin: QSizeF,
    ) -> QRectF:
        """
        Expand ``rect`` by margins relative to its own dimensions.
        """
        if rect.isEmpty() or not rect.isValid():
            return QRectF()

        margin_x: float = rect.width() * margin.width()
        margin_y: float = rect.height() * margin.height()

        return rect.adjusted(
            -margin_x,
            -margin_y,
            margin_x,
            margin_y,
        )

    def _refit_rect(self) -> QRectF:
        """Return the content rectangle plus the refit margin."""
        return self._expand_by_relative_margin(
            self._scene_content_rect(),
            self._refit_scene_margin,
        )

    def _navigation_rect_from_content(
        self,
        content_rect: QRectF,
    ) -> QRectF:
        """
        Build the navigation envelope around the scene content.

        The configured margin is intentionally relative to content size.
        """
        if content_rect.isEmpty() or not content_rect.isValid():
            return QRectF()

        content_width: float = max(
            content_rect.width(),
            self.minimum_content_size,
        )
        content_height: float = max(
            content_rect.height(),
            self.minimum_content_size,
        )

        margin_x: float = content_width * self._pan_scene_margin
        margin_y: float = content_height * self._pan_scene_margin

        return content_rect.adjusted(
            -margin_x,
            -margin_y,
            margin_x,
            margin_y,
        )

    def update_navigation_area(self) -> None:
        content_rect: QRectF = self._scene_content_rect()
        navigation_rect: QRectF = self._navigation_rect_from_content(
            content_rect
        )

        self._navigation_rect = navigation_rect

        if navigation_rect.isEmpty() or not navigation_rect.isValid():
            self.setSceneRect(QRectF())
            return

        self.setSceneRect(navigation_rect)
        self._clamp_view_to_navigation_area()

    def refit_view(self) -> None:
        """Fit the scene content plus its configured refit margin."""
        self.update_navigation_area()

        refit_rect: QRectF = self._refit_rect()
        if refit_rect.isEmpty() or not refit_rect.isValid():
            return

        self.fitInView(
            refit_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._clamp_view_to_navigation_area()

    def _viewport_scene_rect(self) -> QRectF:
        """Return the viewport bounds expressed in scene coordinates."""
        return self.mapToScene(self.viewport().rect()).boundingRect()

    def _clamped_view_center(
        self,
        viewport_rect: QRectF,
        desired_center: QPointF,
    ) -> QPointF:
        """
        Calculate the nearest legal viewport center.

        If the viewport is larger than the navigation area on one axis,
        that axis is centered because no valid panning range exists there.
        """
        navigation_rect: QRectF = self._navigation_rect
        viewport_width: float = viewport_rect.width()
        viewport_height: float = viewport_rect.height()

        if viewport_width >= navigation_rect.width():
            center_x: float = navigation_rect.center().x()
        else:
            half_width: float = viewport_width / 2.0
            center_x = max(  # clamp
                navigation_rect.left() + half_width,
                min(
                    desired_center.x(),
                    navigation_rect.right() - half_width,
                ),
            )

        if viewport_height >= navigation_rect.height():
            center_y: float = navigation_rect.center().y()
        else:
            half_height: float = viewport_height / 2.0
            center_y = max(  # clamp
                navigation_rect.top() + half_height,
                min(
                    desired_center.y(),
                    navigation_rect.bottom() - half_height,
                ),
            )

        return QPointF(center_x, center_y)

    def _clamp_view_to_navigation_area(self) -> None:
        """Keep the complete viewport inside the navigation area."""
        navigation_rect: QRectF = self._navigation_rect
        if navigation_rect.isEmpty() or not navigation_rect.isValid():
            return

        viewport_rect: QRectF = self._viewport_scene_rect()
        if viewport_rect.isEmpty() or not viewport_rect.isValid():
            return

        current_center: QPointF = viewport_rect.center()
        clamped_center: QPointF = self._clamped_view_center(
            viewport_rect,
            current_center,
        )

        if clamped_center != current_center:
            self.centerOn(clamped_center)

    def _pan_to_mouse_position(
        self,
        previous_mouse_pos: QPointF,
        current_mouse_pos: QPointF,
    ) -> None:
        """
        Pan so the scene follows the mouse cursor exactly.
        """
        previous_pos: QPoint = previous_mouse_pos.toPoint()
        current_pos: QPoint = current_mouse_pos.toPoint()

        scene_position_previous: QPointF = self.mapToScene(previous_pos)
        scene_position_current: QPointF = self.mapToScene(current_pos)

        scene_delta: QPointF = (
            scene_position_previous - scene_position_current
        )

        viewport_rect: QRectF = self._viewport_scene_rect()
        current_center: QPointF = viewport_rect.center()

        desired_center: QPointF = current_center + scene_delta
        clamped_center: QPointF = self._clamped_view_center(
            viewport_rect,
            desired_center,
        )

        self.centerOn(clamped_center)

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
