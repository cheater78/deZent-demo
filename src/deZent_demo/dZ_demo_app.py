from __future__ import annotations
import sys
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
)

from deZent_demo.network.net_node import VirtualNetwork, VirtualNetworkNode
from deZent_demo.zanon.deZent_central_entity import *
from deZent_demo.zanon.deZent_gateway import *
from deZent_demo.utils.time_env import *
from deZent_demo.dZ_demo_app import *

from .ui.window import Window
from .ui.scene import dZGraphScene
from .ui.view import PanningView
from .ui.graph_node_gw import GWNode
from .ui.deZent_gateway_widget import deZentGatewayWidget

from .ui.cbf_vis.cbf_vis import CBFPlot

from deZent_demo.instrument.gateway_instrumentor import *
from deZent_demo.instrument.deZent_gateway_instrumentor import *

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

        self.scene: dZGraphScene = dZGraphScene()
        self.view: PanningView = PanningView(self.scene)
        self.window: Window = Window(
            "deZent Demonstration",
            self.view
        )

        self.__setup_default_gws__()

        self.scene.setSceneRect(-8.0, -8.0, 1500, 800)

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

        self.scene.update()
        self.view.reset_view()

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

            self.gws.append(dz_gw)
            self.gw_wgs.append(dz_gw_wg)