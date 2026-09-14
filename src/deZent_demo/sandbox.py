from __future__ import annotations

from deZent_demo.network.virtual import VirtualNetworkThread, VirtualNetworkNode
from deZent_demo.zanon.deZent_central_entity import *
from deZent_demo.zanon.deZent_gateway import *
from deZent_demo.utils.time_env import *

from deZent_demo.instrument.gateway_instrumentor import *
from deZent_demo.instrument.deZent_gateway_instrumentor import *


from PySide6.QtWidgets import (
    QWidget,
)

class Sandbox(QWidget):
    # deZent defaults
    dZ_z: ClassVar[int] = 2
    dZ_dt: ClassVar[timedelta] = timedelta(minutes=121)
    # sim defaults
    sim_start_time: ClassVar[datetime] = datetime.fromisoformat("2026-01-01")

    def __init__(self,
                 /,
                 dZ_z: int = dZ_z,
                 dZ_dt: timedelta = dZ_dt,
                 sim_start_time: datetime = sim_start_time) -> None:
        # TODO: config
        self._dZ_z: int = dZ_z
        self._dZ_dt: timedelta = dZ_dt
        n_gws: int = 7 # TODO

        # Sim network
        self._network: VirtualNetworkThread = VirtualNetworkThread(start_immediately=False)
        self._sim_start_time = sim_start_time
        self._sim_time_env: SimTimeEnv = SimTimeEnv(self._sim_start_time)

        self._dZ_central_entity: deZentCentralEntity = deZentCentralEntity(
            self._network.create_node(0) # TODO: CE_ID = 0 -> random IDs
        )
        self._dZ_gws: list[deZentGateway] = []

        # UI elements
        # TODO: as args - DO NOT CREATE THEM HERE
        
        for i in range(n_gws):
            gw_id: int = i + 1 # ID = 0 is CE

            # the actual gateway
            self.create_gateway(
                gw_id,
                0,
                (gw_id - 1) if gw_id > 1 else n_gws,
                (gw_id + 1) if gw_id < n_gws else 1
            )

            # the UI representation
            # TODO: link to an ID for order? - implicit rn
            # self._network_graph.create_node()

    def create_gateway(self,
                       id: NetworkNodeID,
                       ce: NetworkNodeID,
                       prev: NetworkNodeID,
                       next: NetworkNodeID) -> deZentGateway:
        network_node: AbstractNetworkNode = VirtualNetworkNode(
            self._network,
            node_id = id
        )
        dz_gw: deZentGateway = deZentGateway(
            self._sim_time_env,
            network_node,
            dt=self._dZ_dt,
            z=self._dZ_z,
            ce=ce,
            prev=prev,
            next=next,
        )
        self._dZ_gws.append(dz_gw)
        return dz_gw


    def sim_init(self) -> None:
        #self._network.start()
        pass
    
    def sim_start(self) -> None:
        self._dZ_central_entity.node.write(
            self._dZ_gws[0].gw_id, # TODO: First CCC ID
            MessageDeZentRoundBegin(self._sim_start_time)
        )

    def sim_stop(self) -> None:
        pass