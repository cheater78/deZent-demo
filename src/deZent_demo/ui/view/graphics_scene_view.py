from __future__ import annotations
from typing import ClassVar

from PySide6.QtCore import (
    Qt,
    QPoint, QPointF,
    QSizeF,
    QRectF,
)
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QWidget,
)

from deZent_demo.ui.utils import rect_expand_by_relative_margin

class GraphicsSceneView(QGraphicsView):
    _default_scene_rect: ClassVar[QRectF] = QRectF(-1.0, -1.0, +1.0, +1.0) # default = NDC

    relative_fit_scene_margin: ClassVar[QSizeF] = QSizeF(0.01, 0.01) # TODO: move to [...]Style? - has to support inheritance

    def __init__(
        self,
        scene: QGraphicsScene | None = None,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self._scene: QGraphicsScene = scene if scene is not None else QGraphicsScene(parent=self)
        self.setScene(self._scene)

    def fit_scene_in_view(self) -> None:
        """
        Fit the scene content plus its configured refit margin into the viewport.
        """

        refit_rect: QRectF = self._fit_scene_rect()
        if refit_rect.isEmpty() or not refit_rect.isValid():
            refit_rect = self._default_scene_rect

        self.fitInView(
            refit_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def _fit_scene_rect(self) -> QRectF:
        return rect_expand_by_relative_margin(
            self._scene_content_bounding_rect(),
            self.relative_fit_scene_margin
        )

    def _scene_content_bounding_rect(self) -> QRectF:
        """
        Return the bounding rectangle of all graphical scene content.
        """

        # NOTE: contrary to PySide's definition scene can be None
        scene: QGraphicsScene | None = self.scene()
        if scene is None:  # pyright: ignore[reportUnnecessaryComparison]
            return self._default_scene_rect

        content_rect: QRectF = scene.itemsBoundingRect() # qt provides the scene's AABB alr
        if content_rect.isEmpty() or not content_rect.isValid():
            return self._default_scene_rect

        return content_rect

    def _viewport_scene_rect(self) -> QRectF:
        """
        Return the viewport bounds in scene coordinates.
        """
        return self.mapToScene(self.viewport().rect()).boundingRect() 

    def move_scene_to_view(self, scene_pos: QPointF, view_pos: QPoint) -> None:
        current: QPointF = self.mapToScene(view_pos)
        offset: QPointF = scene_pos - current

        current_center: QPointF = self.mapToScene(
            QPoint(
                self.viewport().width() // 2,
                self.viewport().height() // 2
            )
        )

        self.centerOn(current_center + offset)