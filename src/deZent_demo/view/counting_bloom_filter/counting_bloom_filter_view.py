from .counting_bloom_filter_plot import CBFPlot, CBloomFilter

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsScene,
)

class CountingBloomFilterView(QGraphicsView):

    def __init__(self,
                 /,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._scene: QGraphicsScene = QGraphicsScene(parent=self)

        cbf_dummy: CBloomFilter = CBloomFilter.create(3, 2) # TODO: dummy
        for _ in range(78):
            cbf_dummy.add(78)

        self._cbf_plot: CBFPlot = CBFPlot(cbf_dummy, cbf_dummy.inspect_item_indices(78)) 
        
        self._scene.addItem(self._cbf_plot)
        
        self.setScene(self._scene)