# Source Generated with Decompyle++
# File: presentation_sandbox.cpython-314.pyc (Python 3.14)

from typing import override, cast
from deZent_demo.network import *
from .sandbox import *
from deZent_demo.view.control_overlay.control_overlay import *
from deZent_demo.view.counting_bloom_filter.counting_bloom_filter_view import *
from deZent_demo.view.network_graph.network_graph_view import *
from PySide6.QtCore import QSizeF

class PresentationSandbox(Sandbox):

    def __init__(
        self,
        ctrl_overlay: ControlOverlay,
        cbf_view: CountingBloomFilterView,
        network_graph_view: NetworkGraphView,
    ) -> None:
        super().__init__()
        
        self._ctrl_overlay: ControlOverlay = ctrl_overlay
        self._cbf_view: CountingBloomFilterView = cbf_view
        self._network_graph_view: NetworkGraphView = network_graph_view

        self._network_graph_central_entity: NetworkGraphNode | None = None
        self._network_graph_gateways: dict[NetworkNodeID, NetworkGraphNode] = { }
        
        self.create()
        NetworkGraph.arrange_ring(
            list[NetworkGraphNode](self._network_graph_gateways.values()),
            cast(NetworkGraphNode, self._network_graph_central_entity).center(),
            QSizeF(300, 300)
        )
        self._network_graph_view.refit_view()
        self._cbf_view.hide()

    @override
    def create_central_entity(self, ce_id: NetworkNodeID):
        if self._network_graph_central_entity is not None:
            raise RuntimeError('create_gateway: ce already exists!')
        
        Sandbox.create_central_entity(self, ce_id)
        self._network_graph_central_entity = self._network_graph_view.create_node()
    
    @override
    def create_gateway(
        self,
        id: NetworkNodeID,
        ce_id: NetworkNodeID | None = None,
        next_id: NetworkNodeID | None = None,
    ) -> None:
        if self._network_graph_gateways.get(id) is not None:
            raise RuntimeError(f"create_gateway: id={id} already exists!")
        
        Sandbox.create_gateway(self, id, ce_id, next_id)
        network_graph_node = self._network_graph_view.create_node()
        self._network_graph_gateways[id] = network_graph_node
    
    @override
    def link_gateway_to_central_entity(self, gw_id: NetworkNodeID):
        if self._network_graph_gateways.get(gw_id) is None \
            or self._network_graph_central_entity is None:
            raise RuntimeError(f"link_gateway_to_central_entity: id={gw_id},ce do not exists!")
        
        Sandbox.link_gateway_to_central_entity(self, gw_id)
        self._network_graph_gateways[gw_id].link_to(self._network_graph_central_entity)

    @override
    def link_gateway_to_gateway(self, from_id: NetworkNodeID, to_id: NetworkNodeID):
        if self._network_graph_gateways.get(from_id) is None \
            or self._network_graph_gateways.get(to_id) is None:
            raise RuntimeError(f"link_gateway_to_gateway: id={from_id},{to_id} do not exists!")
        
        Sandbox.link_gateway_to_gateway(self, from_id, to_id)
        self._network_graph_gateways[from_id].link_to(self._network_graph_gateways[to_id])