
from deZent.src.zanon.counting_data_structure.counting_data_structure import CntDataStructure

NodeID = int
class deZentNetworkNode:

    def __init__(self,
                 id: NodeID,
                 ce: NodeID,
                 peer_prev: NodeID,
                 peer_next: NodeID) -> None:
        self.id: NodeID = id
        self.ce: NodeID = ce
        self.prev: NodeID = peer_prev
        self.next: NodeID = peer_next

    def send_collection_to_next(self, cnt_struct: CntDataStructure) -> None:
        pass

    def send_publication_to_next(self, cnt_struct: CntDataStructure, p_pub: int) -> None:
        pass

    def send_publication_to_ce(self, record) -> None:
        pass