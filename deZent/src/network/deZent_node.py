from deZent.src.network.net_node import NetworkNode, NetworkNodeID, NetworkNodeMessageCB, NetAddr
from deZent.src.ami.smart_meter_measurement import PubLogEntry
from deZent.src.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent.src.network.protocol import *

class deZentNetworkNode(NetworkNode):

    def __init__(self,
                 host: NetAddr,
                 net_op: NetAddr,
                 msg_cb: NetworkNodeMessageCB,
                 cert: str = "cert.pem",
                 key: str = "key.pem") -> None:
        NetworkNode.__init__(self, host, net_op, self.__msg_cb__)
        
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