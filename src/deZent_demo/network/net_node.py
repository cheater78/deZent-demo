from __future__ import annotations
from abc import ABC, abstractmethod
import asyncio
from typing import cast, Callable

from deZent_demo.utils import cbor_codec

from deZent_demo.network.address import *
from deZent_demo.network.net_stack import NetworkStack, NetworkMessage
from deZent_demo.network.protocol import *
from deZent_demo.utils.async_thread import QueueWorkerThread

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


default_node_port: int = 9000

class NetworkNode(AbstractNetworkNode):
    """
    NetworkNode abstracts a NetworkStack to use NetworkNodeIDs as communication handles,
    as well as provides NetworkNodeMessage communication
    """

    def __init__(self,
                 net_if: str,
                 certificate_name: str,
                 port: int = default_node_port,
                 node_id: NetworkNodeID | None = None,
                 msg_cb: NetworkNodeMessageCB | None = None,):

        self.net_stack = NetworkStack(
            net_if = net_if,
            port = port,
            msg_cb = self.__net_stack_msg_cb__,
            connection_opened_cb = self.__net_stack_connection_opened_cb__,
            connection_closed_cb = self.__net_stack_connection_closed_cb__,
            certificate_name = certificate_name
        )

        self._known_peers_: dict[NetworkNodeID, NetAddr] = { }

        super().__init__(
            msg_cb = msg_cb,
            node_id = node_id
        )

    def known_peers(self) -> list[NetworkNodeID]:
        return list(self._known_peers_.keys())
    
    def write(self, receiver: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        if receiver not in self.known_peers():
            raise RuntimeError(f"Receiver {receiver} was unknown!")
        addr: NetAddr = cast(NetAddr, self._known_peers_.get(receiver))
        self.__write_msg_raw__(addr, msg)

    def __write_msg_raw__(self, addr: NetAddr, msg: NetworkNodeMessage) -> None:
        msg_bytes: bytes = cbor_codec.encode(msg)
        self.net_stack.write(addr, msg_bytes)

    def __net_stack_connection_opened_cb__(self, addr: NetAddr) -> None:
        self.__write_msg_raw__(addr, MessageConnect(self._node_id_))

    def __net_stack_connection_closed_cb__(self, addr: NetAddr) -> None:
        node_id: NetworkNodeID | None = self.__get_node_id_from_addr__(addr)
        if not node_id:
            return
        del self._known_peers_[node_id]

    def __net_stack_msg_cb__(self, addr: NetAddr, msg: NetworkMessage) -> None:
        msg_obj: NetworkNodeMessage = cbor_codec.decode(NetworkNodeMessage, msg)
        match msg_obj:
            case MessageConnect() as con:
                self._known_peers_[con.id] = addr
            case MessageNodeIDResponse() as ns:
                self._known_peers_[ns.id_addr.id] = ns.id_addr.addr
            case _:
                pass
        node_id: NetworkNodeID | None = self.__get_node_id_from_addr__(addr)
        if not node_id:
            print(f"[NetworkNode] received message from unknown sender ({addr})!")
            return
        self._node_msg_cb_(node_id, msg_obj)
    
    def __get_node_id_from_addr__(self, addr: NetAddr) -> NetworkNodeID | None:
        for node_id, net_addr in self._known_peers_.items():
            if net_addr == addr:
                return node_id
        return None

@dataclass(frozen=True)
class VirtualNetworkMessageTask:
    sender: NetworkNodeID
    receiver: NetworkNodeID
    msg: NetworkNodeMessage

class VirtualNetwork(QueueWorkerThread[VirtualNetworkMessageTask]):

    def __init__(self,
                 start_immediately: bool = True) -> None:
        self.nodes: dict[NetworkNodeID, VirtualNetworkNode] = { }
        super().__init__(start_immediately)
    
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
                 network: VirtualNetwork,
                 node_id: NetworkNodeID | None = None,
                 msg_cb: NetworkNodeMessageCB | None = None,):
        
        super().__init__(
            msg_cb = msg_cb,
            node_id = node_id
        )

        self.network: VirtualNetwork = network
        self.network.add_node(self)

    def known_peers(self) -> list[NetworkNodeID]:
        return list(self.network.nodes.keys())
    
    def write(self, receiver: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        self.network.write_message(self.id(), receiver, msg)
        print(f"VirtualNetworkNode: {self.id()}>{receiver}: {msg}", flush=True)

    def emit_net_node_msg(self, sender: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        self._node_msg_cb_(sender, msg)
    