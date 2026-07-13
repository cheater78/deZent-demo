from __future__ import annotations
import sys
from PySide6.QtWidgets import (
    QApplication,
)

from deZent_demo.network.net_node import VirtualNetwork, VirtualNetworkNode
from deZent_demo.zanon.deZent_central_entity import *
from deZent_demo.zanon.deZent_gateway import *
from deZent_demo.utils.time_env import *
from deZent_demo.dZ_demo_app import *

from .ui.window import Window
from .ui.scene import dZGraphScene
from .ui.view import PanningView

import inspect

def print_values(*args: Any) -> None:
    line: str = ""

    stack_frame = inspect.currentframe()
    if stack_frame is not None:
        caller = inspect.currentframe().f_back
        line += f"{caller.f_code.co_name}"
    else:
        line += f"unkwnf"

    for value in args:
        if line:
            line += ", "
        if isinstance(value, CBloomFilter):
            # line += f"\n\r{value.draw_ascii()}"
            line += "CBF"
        else:
            line += f"{value}"
    print(line, flush=True)

instrumentor = deZentGatewayInstrumentInfo(
    ccc_round_begin_cb = print_values,
    ccc_round_end_cb = print_values,
    ccc_collection_round_begin_cb = print_values,
    ccc_collection_round_end_cb = print_values,
    ccc_publication_round_begin_cb = print_values,
    ccc_publication_round_end_cb = print_values,
    collection_round_cb = print_values,
    publication_round_cb = print_values,

    gateway_instrument_info=GatewayInstrumentInfo(
        sm_measurement_cb=print_values
    )
)

class App(QApplication):

    def __init__(self) -> None:
        super().__init__(sys.argv)
        
        self.network: VirtualNetwork = VirtualNetwork(auto_start=False)
        self.start_time: datetime = datetime.fromisoformat("2026-01-01")
        self.env: AbstractTimeEnv = SimTimeEnv(self.start_time)

        self.ce: deZentCentralEntity = deZentCentralEntity(
            VirtualNetworkNode(
                self.network,
                node_id = 0 # CE's ID = 0
            )
        )
        self.gws: list[deZentGateway] = []

        self.__setup_default_gws__()

        self.scene: dZGraphScene = dZGraphScene()
        self.view: PanningView = PanningView(self.scene)
        self.window: Window = Window(
            "deZent Demonstration",
            self.view
        )

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
            self.network.stop()

        return exit_code

    
    def __setup_default_gws__(self) -> None:
        n_gws: int = 3
        dt_minutes: int = 121
        z: int = 2

        self.gws = []

        for i in range(n_gws):
            gw_id: int = i + 1 # ID = 0 is CE

            gw_net_node = VirtualNetworkNode(
                self.network,
                node_id = gw_id
            )

            dz_gw: deZentGateway = deZentGateway(
                self.env,
                gw_net_node,
                dt_minutes=dt_minutes,
                z=z,
                ce=self.ce.id(),
                prev=(gw_id - 1) if gw_id > 1 else n_gws,
                next=(gw_id + 1) if gw_id < n_gws else 1,
                instrument_info=instrumentor
            )

            self.gws.append(dz_gw)