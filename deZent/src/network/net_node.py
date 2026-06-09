from dataclasses import dataclass
from typing import cast, Callable

from c78_pytils.codec import cbor_codec

from deZent.src.network.net_stack import NetworkStack, NetAddr, NetworkMessage
from protocol import *

NetworkNodeMessage = Message
NetworkNodeID = int
NetworkNodeMessageCB = Callable[[NetworkNodeID, NetworkNodeMessage], None]

@dataclass(frozen=True)
class NetworkNodeIDAddr:
    id: NetworkNodeID
    addr: NetAddr

class NetworkNode():
    def __init__(self,
                 host: NetAddr,
                 net_op: NetAddr,
                 msg_cb: NetworkNodeMessageCB,
                 cert: str = "cert.pem",
                 key: str = "key.pem"):
        self.net_op = net_op
        self.net_stack = NetworkStack(
            host = host,
            msg_cb = self.__net_stack_msg_cb__,
            connection_closed_cb = self.__net_stack_connection_closed_cb__,
            cert = cert,
            key = key
        )

        self.node_id: NetworkNodeID
        self.msg_cb: NetworkNodeMessageCB = msg_cb
        self._known_peers_: dict[NetworkNodeID, NetAddr] = { 0: net_op } # add the network operator at id=0 immediately

    def known_peers(self) -> list[NetworkNodeID]:
        return list(self._known_peers_.keys())
    
    def write(self, receiver: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        if receiver not in self.known_peers():
            print("unknown receiver")
            return
        addr: NetAddr = cast(NetAddr, self._known_peers_.get(receiver))
        msg_bytes: bytes = cbor_codec.encode(msg)
        self.net_stack.write(addr, msg_bytes)

    def __net_stack_msg_cb__(self, addr: NetAddr, msg: NetworkMessage) -> None:
        node_id: NetworkNodeID | None = self.__get_node_id_from_addr__(addr)
        if not node_id:
            return
        msg_obj: NetworkNodeMessage = cbor_codec.decode(NetworkNodeMessage, msg)
        self.__net_node_msg_cb__(node_id, msg_obj)

    def __net_node_msg_cb__(self, node_id: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        match msg:
            case MessageNetworkOPRegistration() as reg:
                self.node_id = reg.id.id
            case _:
                pass
        self.msg_cb(node_id, msg)

    def __net_stack_connection_closed_cb__(self, addr: NetAddr) -> None:
        node_id: NetworkNodeID | None = self.__get_node_id_from_addr__(addr)
        if not node_id:
            return
        del self._known_peers_[node_id]

    def __get_node_id_from_addr__(self, addr: NetAddr) -> NetworkNodeID | None:
        for node_id, net_addr in self._known_peers_.items():
            if net_addr == addr:
                return node_id
        return None