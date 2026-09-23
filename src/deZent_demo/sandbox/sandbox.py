from __future__ import annotations
from datetime import datetime, timedelta

from deZent_demo.network import *
from deZent_demo.zanon.deZent_central_entity import *
from deZent_demo.zanon.deZent_gateway import *
from deZent_demo.utils.time_env import *
from deZent_demo.instrument.gateway_instrumentor import *
from deZent_demo.instrument.deZent_gateway_instrumentor import *
from deZent_demo.utils.config.config import *

@dataclass
class SimConfig(Config):
    start_time: datetime = datetime.fromisoformat("2026-01-01")
    measurement_interval: timedelta = timedelta(minutes=15)
    n_gws: int = 5
    n_sms: int = 3

class Sandbox:
    
    def __init__(
        self,
        deZent_config: deZentConfig = deZentConfig(),
        sim_config: SimConfig = SimConfig(),
        **kwargs: Any,
    ) -> None:
        self._deZent_config = deZent_config
        self._sim_config: SimConfig = sim_config

        self._network = VirtualNetworkThread(start_immediately = False)
        self._sim_start_time: datetime = self._sim_config.start_time
        self._sim_time_env = SimTimeEnv(self._sim_start_time)

        self._dZ_ce_id: NetworkNodeID = 0
        self._dZ_init_ccc_id: NetworkNodeID = 1
        self._dZ_central_entity: deZentCentralEntity | None = None
        self._dZ_gws: dict[NetworkNodeID, deZentGateway] = { }
        
        super().__init__(**kwargs)

    def create_sandbox(self) -> None:
        self.create_central_entity(self._dZ_ce_id)
        n_gws = self._sim_config.n_gws
        for i in range(n_gws):
            gw_id = i + 1
            self.create_gateway(gw_id)
            self.link_gateway_to_central_entity(gw_id)
            if i == 0:
                self._dZ_init_ccc_id = gw_id
                continue
            prev_id = i
            if gw_id == n_gws:
                self.link_gateway_to_gateway(gw_id, 1)
            self.link_gateway_to_gateway(prev_id, gw_id)
    
    def create_central_entity(self, ce_id: NetworkNodeID):
        if self._dZ_central_entity is not None:
            return
        network_node = self._network.create_node(ce_id)
        self._dZ_central_entity = deZentCentralEntity(network_node)
    
    def create_gateway(
        self,
        id: NetworkNodeID,
        ce_id: NetworkNodeID | None = None,
        next_id: NetworkNodeID | None = None,
    ) -> None:
        if self._dZ_gws.get(id) is not None:
            raise RuntimeError(f"create_gateway: id={id} already exists!")
        network_node = self._network.create_node(id)
        dz_gw = deZentGateway(
            self._sim_time_env,
            self._deZent_config,
            network_node,
            ce_id = ce_id,
            next_id = next_id,
            measurement_interval=self._sim_config.measurement_interval,
            n_sm_conn = self._sim_config.n_sms,
        )
        self._dZ_gws[id] = dz_gw
    
    def link_gateway_to_central_entity(self, gw_id: NetworkNodeID):
        if self._dZ_gws.get(gw_id) is None:
            raise RuntimeError(f"link_gateway_to_central_entity: id={gw_id} doesn\'t exists!")
        self._dZ_gws[gw_id].set_ce(self._dZ_ce_id)

    def link_gateway_to_gateway(self, from_id: NetworkNodeID, to_id: NetworkNodeID):
        if self._dZ_gws.get(from_id) is None \
            or self._dZ_gws.get(to_id) is None:
            raise RuntimeError(f"link_gateway_to_gateway: id={from_id},{to_id} do not exists!")
        self._dZ_gws[from_id].set_next(to_id)

    def sim_start(self):
        if self._dZ_central_entity is None:
            raise RuntimeError('central_entity was unset!')
        self._network.start()
        self._dZ_central_entity.node.write(self._dZ_init_ccc_id, MessageDeZentRoundBegin(self._sim_start_time))

    def sim_stop(self):
        self._sim_time_env.stop()
        self._network.stop()

