from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable

from .address import NetworkNodeID, create_network_node_id
from .protocol import Message

NetworkNodeMessage = Message
NetworkNodeMessageCB = Callable[[NetworkNodeID, NetworkNodeMessage], None]

class AbstractNetworkNode(ABC):
    """
    AbstractNetworkNode that ensures writing and reading via cb of NetworkNodeMessages
    """

    def __init__(self,
                 node_id: NetworkNodeID | None = None,
                 msg_cb: NetworkNodeMessageCB | None = None,) -> None:
        self._node_id_: NetworkNodeID = node_id if node_id is not None else create_network_node_id()
        self._msg_cb_: NetworkNodeMessageCB | None = msg_cb

    @abstractmethod
    def known_peers(self) -> list[NetworkNodeID]:
        pass

    @abstractmethod
    def write(self, receiver: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        pass
    
    def _node_msg_cb_(self, sender: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        if self._msg_cb_:
            self._msg_cb_(sender, msg)

    def id(self) -> NetworkNodeID:
        return self._node_id_
    
    def register_msg_cb(self, msg_cb: NetworkNodeMessageCB) -> None:
        self._msg_cb_ = msg_cb

__all__ = [
    "NetworkNodeID",
    "NetworkNodeMessage",
    "NetworkNodeMessageCB",
    "AbstractNetworkNode"
]