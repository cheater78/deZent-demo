from dataclasses import dataclass
from typing import cast, Callable

from deZent_demo.utils import cbor_codec

from deZent_demo.network.net_stack import NetworkStack, NetAddr, NetworkMessage
from deZent_demo.network.protocol import *

NetworkNodeMessage = Message
NetworkNodeID = int
NetworkNodeMessageCB = Callable[[NetworkNodeID, NetworkNodeMessage], None]

@dataclass(frozen=True)
class NetworkNodeIDAddr:
    id: NetworkNodeID
    addr: NetAddr

default_node_port: int = 9000

class NetworkNode():
    """
    NetworkNode abstracts a NetworkStack to use NetworkNodeIDs as communication handles,
    as well as provides NetworkNodeMessage communication
    """

    def __init__(self,
                 net_if: str,
                 msg_cb: NetworkNodeMessageCB,
                 certificate_name: str,
                 port: int = default_node_port):

        self.net_stack = NetworkStack(
            net_if = net_if,
            port = port,
            msg_cb = self.__net_stack_msg_cb__,
            connection_opened_cb = self.__net_stack_connection_opened_cb__,
            connection_closed_cb = self.__net_stack_connection_closed_cb__,
            certificate_name = certificate_name
        )

        self.node_id: NetworkNodeID
        self.msg_cb: NetworkNodeMessageCB = msg_cb
        self._known_peers_: dict[NetworkNodeID, NetAddr] = { }

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
        self.__write_msg_raw__(addr, MessageConnect(self.node_id))

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
            case _:
                pass
        node_id: NetworkNodeID | None = self.__get_node_id_from_addr__(addr)
        if not node_id:
            print(f"[NetworkNode] received message from unknown sender ({addr})!")
            return
        self.__net_node_msg_cb__(node_id, msg_obj)

    def __net_node_msg_cb__(self, node_id: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        self.msg_cb(node_id, msg)
    
    def __get_node_id_from_addr__(self, addr: NetAddr) -> NetworkNodeID | None:
        for node_id, net_addr in self._known_peers_.items():
            if net_addr == addr:
                return node_id
        return None