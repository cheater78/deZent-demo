from __future__ import annotations
from dataclasses import dataclass

from .abstract_node import *
from deZent_demo.utils.thread.queue_thread import QueueWorkerThread

@dataclass(frozen=True)
class VirtualNetworkMessageTask:
    sender: NetworkNodeID
    receiver: NetworkNodeID
    msg: NetworkNodeMessage

class VirtualNetworkThread(QueueWorkerThread[VirtualNetworkMessageTask]):

    def __init__(self,
                 start_immediately: bool = True) -> None:
        self.nodes: dict[NetworkNodeID, VirtualNetworkNode] = { }
        super().__init__(start_immediately)

    def create_node(self, node_id: NetworkNodeID | None = None) -> VirtualNetworkNode:
        return VirtualNetworkNode(self, node_id)
    
    def add_node(self, node: VirtualNetworkNode) -> None:
        self.nodes[node.id()] = node

    def write_message(self, sender: NetworkNodeID, receiver: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        task = VirtualNetworkMessageTask(sender, receiver, msg)
        self.dispatch(task)

    def _handle_element(self, element: VirtualNetworkMessageTask) -> None:
        receiver = self.nodes.get(element.receiver)
        if not receiver:
            raise RuntimeError(f"VirtualNetwork: Task receiver: {element.receiver} is unknown!")
        receiver.emit_net_node_msg(element.sender, element.msg)

class VirtualNetworkNode(AbstractNetworkNode):

    def __init__(self,
                 network: VirtualNetworkThread,
                 node_id: NetworkNodeID | None = None,
                 msg_cb: NetworkNodeMessageCB | None = None,):
        
        super().__init__(
            msg_cb = msg_cb,
            node_id = node_id
        )

        self.network: VirtualNetworkThread = network
        self.network.add_node(self)

    def known_peers(self) -> list[NetworkNodeID]:
        return list(self.network.nodes.keys())
    
    def write(self, receiver: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        self.network.write_message(self.id(), receiver, msg)

    def emit_net_node_msg(self, sender: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        self._node_msg_cb_(sender, msg)

__all__ = [
    "NetworkNodeID",
    "AbstractNetworkNode",
    "NetworkNodeMessageCB",
    "VirtualNetworkThread",
    "VirtualNetworkNode"
]