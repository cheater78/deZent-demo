from deZent_demo.utils import utils
from deZent_demo.network.net_node import *

default_p2p_bootstrap_node: NetworkNodeIDAddr = NetworkNodeIDAddr(
    NetworkNodeID(0),
    NetAddr("10.0.0.1", default_node_port)
)

class P2PNode(NetworkNode):
    
    def __init__(self,
                 net_if: str,
                 certificate_name: str,
                 port: int = default_node_port,
                 bootstrap: NetworkNodeIDAddr = default_p2p_bootstrap_node):
        
        self.k_nodes: int = 2

        NetworkNode.__init__(self, net_if, self.__p2p_node_msg_cb__, certificate_name)

    def write(self, receiver: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        if receiver not in self.known_peers():
            if not self.discover_node(receiver):
                raise RuntimeError(f"Receiver {receiver} was unknown and failed to be discovered!")
        NetworkNode.write(self, receiver, msg)

    def discover_node(self, requested_peer: NetworkNodeID) -> bool:
        request: MessageP2PResquest = MessageP2PResquest(requested_peer)
        def peer_found():
            return requested_peer in self.known_peers()
        if peer_found():
            return True
        for known_peer in self.known_peers():
            self.write(known_peer, request)
        return utils.wait_sync(peer_found, timeout_s=5)
    
    def __p2p_node_msg_cb__(self, node_id: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        match msg:
            case MessageP2PResquest() as p2p_req:
                if p2p_req.requested_peer in self.known_peers():
                    response: MessageP2PShare = MessageP2PShare([
                        NetworkNodeIDAddr(p2p_req.requested_peer, self._known_peers_[p2p_req.requested_peer])
                    ])
                    self.write(node_id, response)
                else:
                    self.discover_node(p2p_req.requested_peer)
            case _:
                pass
        self.msg_cb(node_id, msg)