from __future__ import annotations

from bitarray.util import ba2int

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
)
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import Qt, QPointF, QSizeF, QRectF
from deZent_demo.zanon.counting_data_structure.counting_bloom_filter import *


class CBFHistogram(QGraphicsObject):

    def __init__(
        self,
        position: QPointF,
        size: QSizeF = QSizeF(1, 1),
        spacing: float = 1.0,
        cbf: CBloomFilter | None = None,
        parent: QGraphicsItem | None = None,
    ) -> None:

        super().__init__(parent=parent)
        self.setPos(position)
        self.setZValue(100)

        self.cbf: CBloomFilter | None = cbf

        self.size: QSizeF = size
        self.spacing: float = spacing

        self._bar_width: float = self.size.width() - 2 * self.spacing
        self._max_counter: int = 0

        self._bars: list[QGraphicsRectItem] = []
        self._labels: list[QGraphicsSimpleTextItem] = []    

    def boundingRect(self) -> QRectF:
        return QRectF(
            0, 0,
            self.size.width(), self.size.height()
        )

    def paint(self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: QWidget | None = None,) -> None:
        painter.setPen(QPen(Qt.GlobalColor.magenta, 0.05))
        # painter.drawLine( # TODO: invis -> move up(-) by fontsize.y
        #     QPointF(0, self.size.height()),
        #     QPointF(self.size.width(), self.size.height())
        # )
        # painter.drawRect(self.boundingRect()) # Debug

    def update_cbf(self, cbf: CBloomFilter) -> None:

        self.cbf = cbf
        self._bar_width: float = (self.size.width() - ((cbf.m - 1) * self.spacing)) / cbf.m
        self._max_counter: int = (1 << cbf.N) - 1

        self._update_items()

        baseline = self.size.height()
        for i, bucket in enumerate(cbf.bit_array):
            x = i * (self._bar_width + self.spacing)

            label = self._labels[i]
            label_rect = label.mapRectToParent(label.boundingRect())
            label.setPos(
                x + ((self._bar_width - label_rect.width()) * 0.5),
                (baseline - label_rect.height()),
            )

            value = ba2int(bucket)

            if self._max_counter > 0:
                bar_height = (value / self._max_counter) * self.size.height()
            else:
                bar_height = 0.0

            self._bars[i].setRect(
                QRectF(
                    x,
                    (baseline - label_rect.height()) - bar_height,
                    self._bar_width,
                    bar_height,
                )
            )

    def _update_items(self) -> None:
        self._bars = []
        self._labels = []

        if not self.cbf:
            return
        
        bar_color: QColor = QColor(70, 130, 255)
        brush = QBrush(bar_color)
        pen = QPen(bar_color, 0.01)

        for i in range(self.cbf.m):

            bar = QGraphicsRectItem(self)
            bar.setBrush(brush)
            bar.setPen(pen)

            self._bars.append(bar)

            label = QGraphicsSimpleTextItem(str(i), self)

            font = label.font()
            font.setPointSizeF(1)
            label.setFont(font)
            label_pen: QPen = QPen(Qt.GlobalColor.white)
            label_pen.setWidthF(0.1)
            label_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            label.setPen(label_pen)
            label.setScale(0.1)

            self._labels.append(label)