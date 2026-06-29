from __future__ import annotations
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QWidget
)

class GatewayWidget(QWidget):

    def __init__(self):
        self.cbf_plot: CBFPlot = CBFPlot()

class CBFPlot(FigureCanvasQTAgg):
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