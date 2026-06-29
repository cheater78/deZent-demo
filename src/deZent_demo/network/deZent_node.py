from deZent_demo.network.net_node import NetworkNodeID, NetworkNodeMessageCB, NetAddr
from deZent_demo.ami.measurement_log import PubLogEntry
from deZent_demo.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent_demo.network.protocol import *

class deZentNetworkNode():

    def __init__(self) -> None:
        
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

