from deZent_demo.network.net_node import NetworkNodeID, NetworkNodeMessageCB, NetAddr
from deZent_demo.network.p2p_node import P2PNode
from deZent_demo.ami.smart_meter_measurement import PubLogEntry
from deZent_demo.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent_demo.network.protocol import *

class deZentNetworkNode(P2PNode):

    def __init__(self,
                 host: NetAddr,
                 net_op: NetAddr,
                 msg_cb: NetworkNodeMessageCB,
                 cert: str = "cert.pem",
                 key: str = "key.pem") -> None:
        P2PNode.__init__(self, host, net_op, self.__msg_cb__)
        
        self.ce: NetworkNodeID
        self.prev: NetworkNodeID
        self.next: NetworkNodeID

    def send_collection_to_next(self, cnt_struct: CntDataStructure) -> None:
        pass

    def send_publication_to_next(self, cnt_struct: CntDataStructure, p_pub: int) -> None:
        pass

    def send_publication_to_ce(self, record: PubLogEntry) -> None:
        pass

    def __msg_cb__(self, node_id: NetworkNodeID, msg: Message) -> None:
        match msg:
            case MessageNetworkOPRegistration() as reg:
                self.ce = reg.ce.id
                self.prev = reg.prev.id
                self.next = reg.next.id
                # TODO: some system to register NetAddr as well
            case _:
                pass
        self.msg_cb(node_id, msg)


    # state: {SEARCHING, CONNECTED} = SEARCHING
    # link to self & assume existing ring
    # for curr_peer = known_peer
    #   ask curr_peer for prev and next
    #   if self.id < prev:
    #       curr_peer = prev
    #   if self.id > next:
    #       curr_peer = next
    #   if is next keep seaching next, else prev

