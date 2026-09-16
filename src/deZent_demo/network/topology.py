# Source Generated with Decompyle++
# File: topology.cpython-314.pyc (Python 3.14)

from typing import Any
from .address import NetworkNodeID
from .abstract_node import AbstractNetworkNode
from .protocol import *

class NodeTopology:

    def __init__(
        self,
        node: AbstractNetworkNode,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._network_node: AbstractNetworkNode = node
    
    def set_network_node(self, node: AbstractNetworkNode):
        self._network_node = node
    
    def id(self):
        return self._network_node.id()

class CentralizedNode(NodeTopology):
    
    def __init__(
        self,
        node: AbstractNetworkNode,
        ce_id: NetworkNodeID | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            node=node,
            **kwargs
        )
        self._network_ce: NetworkNodeID | None = ce_id
    
    def get_ce(self) -> NetworkNodeID:
        if self._network_ce is None:
            raise RuntimeError('CE was unset!')
        return self._network_ce

    def set_ce(self, ce_id: NetworkNodeID | None) -> None:
        self._network_ce = ce_id
    
    def write_ce(self, message: Message) -> None:
        if self._network_ce is None:
            return
        self._network_node.write(self._network_ce, message)

class deZentNode(CentralizedNode):
    
    def __init__(
        self,
        node: AbstractNetworkNode,
        ce_id: NetworkNodeID | None = None,
        next_id: NetworkNodeID | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            node=node,
            ce_id=ce_id,
            **kwargs
        )
        self._network_next: NetworkNodeID | None = next_id
    
    def get_next(self):
        if self._network_next is None:
            raise RuntimeError('Next was unset!')
        return self._network_next

    def set_next(self, next_id: NetworkNodeID | None) -> None:
        self._network_next = next_id

    def write_next(self, message: Message) -> None:
        if self._network_next is None:
            return None
        self._network_node.write(self._network_next, message)

__all__ = [
    "NetworkNodeID",
    "AbstractNetworkNode",
    "NodeTopology",
    "CentralizedNode",
    "deZentNode",
]
