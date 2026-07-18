from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
)

from .graph import *
from deZent_demo.network.net_node import NetworkNodeID
from .cbf_histogram import *

class GWNode(Node):

    def __init__(self,
                 id: NetworkNodeID,
                 position: QPointF = QPointF(0, 0),
                 size: QSizeF = QSizeF(1, 1),
                 socket_position_relative: QPointF = QPointF(0.0, 0.0), # upper right corner
                 socket_size_relative: QSizeF = QSizeF(0.1, 0.1),
                 cbf_position_relative: QPointF = QPointF(0.05, 0.15), # indented upper left corner
                 cbf_size_relative: QSizeF = QSizeF(0.9, 0.85),
                 border_color: QColor = QColor(90, 255, 10),
                 border_width: float = 0.1,
                 bg_color: QColor = QColor(10, 12, 15),
                 parent: QGraphicsItem | None = None):
        super().__init__(
            position,
            size,
            socket_position_relative,
            socket_size_relative,
            border_color,
            border_width,
            bg_color,
            parent=parent
        )

        self.id: NetworkNodeID = id

        node_cbf_size: QSizeF = QSizeF(
            size.width() * cbf_size_relative.width(),
            size.height() * cbf_size_relative.height()
        )
        max_node_socket_offset: QSizeF = size - node_cbf_size
        node_cbf_position: QPointF = clamp(
            QPointF(
                size.width() * cbf_position_relative.x(),
                size.height() * cbf_position_relative.y()
            ),
            QPointF(0.0, 0.0),
            QPointF(max_node_socket_offset.width(), max_node_socket_offset.height())
        )
        
        self.cbf_plot = CBFHistogram(
            node_cbf_position,
            node_cbf_size,
            0.08,
            parent=self)
        
        self.gw_label = QGraphicsSimpleTextItem(f"GW-{id}", parent=self)
        font = self.gw_label.font()
        font.setPointSizeF(1)
        self.gw_label.setFont(font)
        label_pen: QPen = QPen(Qt.GlobalColor.white)
        label_pen.setWidthF(0.1)
        label_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.gw_label.setPen(label_pen)
        self.gw_label.setScale(0.3)
        l_rect = self.gw_label.mapRectToParent(self.gw_label.boundingRect())
        self.gw_label.setPos(QPointF(size.width() - (size.width() * 0.1) - l_rect.width(), (size.height() * 0.1)))

    def update_cbf(self, cbf: CBloomFilter) -> None:
        self.cbf_plot.update_cbf(cbf)
        


