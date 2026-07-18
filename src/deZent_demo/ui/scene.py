import random
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import QRectF

from deZent_demo.zanon.deZent_central_entity import *
from deZent_demo.zanon.deZent_gateway import *

from .graph import *
from .graph_node_gw import *
from .graph_node_ce import *

def add_random_mesurements(cbf: CBloomFilter, key_add_count: int = 5, max_key: int = 10, max_count: int = 3) -> CBloomFilter:
    for _ in range(key_add_count):
        random_key = random.randint(0,10)
        random_count = random.randint(int(max_count / 2),max_count)
        for _ in range(random_count):
            cbf.add(random_key)
    return cbf

class dZGraphScene(QGraphicsScene):

    def __init__(self) -> None:
        super().__init__()
        self.setSceneRect(QRectF(0, 0, 0, 0))

        self.nodes: list[GWNode] = []

        center: QPointF = QPointF(0.0, 0.0)
        node_size: QSizeF = QSizeF(2.0, 2.0)
        self.ce = CENode(
            center - QPointF(node_size.width() / 2, node_size.height() / 2),
            node_size,
            QPointF(0.45, 0.45),
            bg_color=QColor(255, 80, 20)
        )
        self.addItem(self.ce)
    
    def add_gw(self, gw_id: NetworkNodeID) -> GWNode:
        gw = GWNode(gw_id)
        self.nodes.append(gw)
        self.update_elements()
        return gw

    def update_elements(self) -> None:
        node_count: int = len(self.nodes)

        center: QPointF = QPointF(0.0, 0.0)
        node_size: QSizeF = QSizeF(2.0, 2.0)
        size: QSizeF = node_size * (3 * node_count / math.pi)
        
        self.nodes.sort(key=lambda gw: gw.id)

        for i, gw in enumerate(self.nodes):
            node_pos: QPointF = center + QPointF(
                0.5 * size.width()  * math.cos( 2 * math.pi * (i / node_count) ),
                0.5 * size.height() * math.sin( 2 * math.pi * (i / node_count) )
            )
            gw.setPos(node_pos)
            if not gw in self.items():
                self.addItem(gw)

            if i != 0:
                self.addItem(Edge(self.nodes[i - 1], self.nodes[i]))
            if i + 1 >= node_count:
                self.addItem(Edge(self.nodes[i], self.nodes[0]))

            self.addItem(Edge(self.nodes[i], self.ce))

        self.__update_scene_rect__()



    def __update_scene_rect__(self) -> None:
        items = self.items()
        if not items:
            return

        rect: QRectF | None = None

        for item in items:
            r = item.sceneBoundingRect()
            rect = r if rect is None else rect.united(r)

        if rect is None or rect.isNull():
            return
        
        w = rect.width()
        h = rect.height()

        pad_x = w * 0.6
        pad_y = h * 0.6

        padded_rect = rect.adjusted(
            -pad_x,
            -pad_y,
            pad_x,
            pad_y,
        )

        self.setSceneRect(padded_rect)
