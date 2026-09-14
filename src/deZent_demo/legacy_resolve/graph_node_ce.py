from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
)

from .graph import *

class CENode(Node):

    def __init__(self,
                 position: QPointF,
                 size: QSizeF = QSizeF(1, 1),
                 socket_position_relative: QPointF = QPointF(0.0, 0.0), # upper right corner
                 socket_size_relative: QSizeF = QSizeF(0.1, 0.1),
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
        
        self.gw_label = QGraphicsSimpleTextItem(f"CE", parent=self)
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