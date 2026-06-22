
from __future__ import annotations
import sys
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
)
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

class PlotWidget(FigureCanvasQTAgg):
    def __init__(self):
        fig = Figure(figsize=(5, 4))
        self.ax = fig.add_subplot(111)

        super().__init__(fig)

        self.draw_plot()

    def draw_plot(self):
        df = pd.DataFrame({
            "name": ["A", "B", "C", "D"],
            "value": [10, 25, 15, 40],
        })

        plot = sns.barplot(
            data=df,
            x="name",
            y="value",
            ax=self.ax,
        )

        self.draw()

class DemoWindow(QWidget):

    @staticmethod
    def run() -> DemoWindow:
        app = QApplication(sys.argv)

        window = DemoWindow()
        window.show()

        sys.exit(app.exec())

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Qt Demo")
        self.resize(1280, 720)

        self.button = QPushButton("Click me")
        self.button.clicked.connect(self.on_button_clicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addStretch()
        layout.addWidget(PlotWidget())

        self.click_count = 0

    def on_button_clicked(self):
        self.click_count += 1
        self.button.setText(f"Clicked {self.click_count} times")

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.drawText(
            20,
            100,
            "Hello from QPainter!"
        )

        pen = QPen(QColor("green"))
        pen.setWidth(6)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        nodes: list[tuple[float, float]] = [
            (50, 50),
            (50, 150),
            (150, 200),
            (150, 100),
            (175, 100),
        ]
        path = QPainterPath()
        

        for i, node in enumerate(nodes):
            if i == 0:
                path.moveTo(*node)
            if len(nodes) > i + 1:
                path.lineTo(*nodes[i + 1])

        painter.drawPath(path)




from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QMainWindow
)
from PySide6.QtGui import QPen, QPainterPath, QColor
from PySide6.QtCore import Qt, QPointF


class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, radius=20, color="orange"):
        super().__init__(-radius, -radius, radius * 2, radius * 2)

        self.edges = []

        self.setBrush(QColor(color))
        self.setPen(QPen(Qt.black, 2))
        self.setFlags(
            QGraphicsEllipseItem.ItemIsMovable |
            QGraphicsEllipseItem.ItemIsSelectable |
            QGraphicsEllipseItem.ItemSendsGeometryChanges
        )

        self.setPos(x, y)

    def add_edge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_path()
        return super().itemChange(change, value)


class Edge(QGraphicsPathItem):
    def __init__(self, a: Node, b: Node):
        super().__init__()

        self.a = a
        self.b = b

        pen = QPen(QColor("green"))
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        self.setPen(pen)

        a.add_edge(self)
        b.add_edge(self)

        self.update_path()

    def update_path(self):
        pa = self.a.scenePos()
        pb = self.b.scenePos()

        path = QPainterPath(pa)

        mid_x = (pa.x() + pb.x()) / 2

        path.cubicTo(QPointF(mid_x, pa.y()), QPointF(mid_x, pb.y()),pb)

        self.setPath(path)


class View(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setScene(scene)

        self.setRenderHint(self.renderHints())
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)


class MainWindow(QMainWindow):

    @staticmethod
    def run() -> DemoWindow:
        app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    def __init__(self):
        super().__init__()

        scene = QGraphicsScene()
        scene.setSceneRect(-350, -350, 700, 700)

        ce = Node(0, -250, color="red")
        n1 = Node(-250, 250, color="orange")
        n2 = Node(0, 300, color="skyblue")
        n3 = Node(250, 250, color="lightgreen")

        scene.addItem(ce)
        scene.addItem(n1)
        scene.addItem(n2)
        scene.addItem(n3)

        scene.addItem(Edge(n1, ce))
        scene.addItem(Edge(n2, ce))
        scene.addItem(Edge(n3, ce))

        wg = scene.addWidget(PlotWidget())
        wg.setPos(250, 250)
        wg.setPreferredSize(100, 100)

        view = View(scene)
        view.fitInView(scene.sceneRect())
        self.setCentralWidget(view)

        self.setWindowTitle("QGraphicsView Demo")