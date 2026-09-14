from __future__ import annotations
import sys
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
)
from PySide6.QtGui import (
    QColor,
    QBrush,
)

from deZent_demo.legacy_resolve.network.net_node import VirtualNetwork, VirtualNetworkNode
from deZent_demo.zanon.deZent_central_entity import *
from deZent_demo.zanon.deZent_gateway import *
from deZent_demo.utils.time_env import *
from deZent_demo.delete_me.dZ_demo_app import *

from .window import Window
from .scene import dZGraphScene
from ..view.network_graph.panning_graphics_view import PanningGraphicsView
from .graph_node_gw import GWNode
from .deZent_gateway_widget import deZentGatewayWidget

from ..view.counting_bloom_filter_plot.counting_bloom_filter_plot import CBFPlot

from deZent_demo.instrument.gateway_instrumentor import *
from deZent_demo.instrument.deZent_gateway_instrumentor import *

from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsView,
    QWidget,
    QStackedLayout,

)

class App(QApplication):

    def __init__(self) -> None:
        super().__init__(sys.argv)

        self.network: VirtualNetwork = VirtualNetwork(start_immediately=False)
        self.start_time: datetime = datetime.fromisoformat("2026-01-01")
        self.env: SimTimeEnv = SimTimeEnv(self.start_time)

        self.ce: deZentCentralEntity = deZentCentralEntity(
            VirtualNetworkNode(
                self.network,
                node_id = 0 # CE's ID = 0
            )
        )
        self.gws: list[deZentGateway] = []
        self.gw_wgs: list[deZentGatewayWidget] = []

        # Scene config
        scene_aspect: float = 9 / 16
        scene_xsize: float = 2000
        scene_ysize: float = scene_xsize * scene_aspect

        self.scene: dZGraphScene = dZGraphScene()
        self.scene.setBackgroundBrush(QBrush(QColor(128,128,128)))
        self.scene.setSceneRect(0, 0, scene_xsize, scene_ysize)
        self.view: PanningGraphicsView = PanningGraphicsView(self.scene)
        self.view.refit_view()
        self.window: Window = Window(
            "deZent Demonstration",
            self.view
        )
        

        self.__setup_default_gws__()

        self.nrb = QPushButton("Next Round")
        def next_round():
            self.env.advance(by=timedelta(minutes=15))
        self.nrb.clicked.connect(next_round)
        w = self.scene.addWidget(self.nrb)
        w.setPos(self.scene.sceneRect().topLeft())
        w.setScale(0.1)

        self.cbf: CBloomFilter = CBloomFilter.create(3, 2)
        
        for _ in range(0, pow(2, 10)):
            self.cbf.add(random.randint(0,1024))

        self.cbf_plot: CBFPlot = CBFPlot(self.cbf)
        self.scene.addItem(self.cbf_plot)
        self.cbf_plot.setPos(32, 128 + self.cbf_plot.sceneBoundingRect().height())

        self.cbf_add_key: int = random.randint(0,1024)

        self.cbf_add_button: QPushButton = QPushButton(f"Add to CBF: {self.cbf_add_key}")
        abw = self.scene.addWidget(self.cbf_add_button)
        abw.setPos(32, 0)
        abw.setScale(3)
        def cbf_add():
            self.cbf.add(self.cbf_add_key)
            self.cbf_plot.update_cbf(self.cbf, focus = self.cbf.inspect_item_indices(self.cbf_add_key))
            self.cbf_plot.setPos(32, 128 + self.cbf_plot.sceneBoundingRect().height())
        self.cbf_add_button.clicked.connect(cbf_add)

        self.cbf_add_newkey_button: QPushButton = QPushButton(f"Pick new key")
        nkbw = self.scene.addWidget(self.cbf_add_newkey_button)
        nkbw.setPos(32 + abw.sceneBoundingRect().width(), 0)
        nkbw.setScale(3)
        def cbf_newkey():
            self.cbf_add_key = random.randint(0,1024)
            self.cbf_add_button.setText(f"Add to CBF: {self.cbf_add_key}")
            self.cbf_plot.update_cbf(self.cbf, focus = self.cbf.inspect_item_indices(self.cbf_add_key))

        self.cbf_add_newkey_button.clicked.connect(cbf_newkey)

    def run(self) -> int:
        self.network.start()
        
        self.ce.node.write(
            self.gws[0].gw_id,
            MessageDeZentRoundBegin(self.start_time)
        )

        self.window.show()

        exit_code: int = 1
        try:
            exit_code: int = self.exec()
        except KeyboardInterrupt:
            print("Cancelling...")
            exit_code = 0
        except:
            raise
        finally:
            self.env.stop() # release time waiters first
            self.network.stop()
            for gw_wg in self.gw_wgs: # TODO: not working
                gw_wg.instrumentor.release_gates() # TODO: into node graph, some shutdown

        return exit_code

    
    def __setup_default_gws__(self) -> None:
        n_gws: int = 3
        dt_minutes: int = 121
        z: int = 2

        self.gws = []

        for i in range(n_gws):
            gw_id: int = i + 1 # ID = 0 is CE

            gz_gw_ui_node: GWNode = self.scene.add_gw(gw_id)

            dz_gw: deZentGateway = deZentGateway(
                self.env,
                VirtualNetworkNode(
                    self.network,
                    node_id = gw_id
                ),
                dt_minutes=dt_minutes,
                z=z,
                ce=self.ce.id(),
                prev=(gw_id - 1) if gw_id > 1 else n_gws,
                next=(gw_id + 1) if gw_id < n_gws else 1,
            )

            # TODO: move GWNode, and all UI stuff into deZentGatewayWidget
            dz_gw_wg: deZentGatewayWidget = deZentGatewayWidget(dz_gw)
            dz_gw_wg_proxy = self.scene.addWidget(dz_gw_wg)
            dz_gw_wg_proxy.setScale(0.01)
            dz_gw_wg_proxy.setPos(gz_gw_ui_node.pos())

            self.gws.append(dz_gw)
            self.gw_wgs.append(dz_gw_wg)