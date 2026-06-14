from deZent_demo.network.net_node import NetworkNodeID, NetworkNodeIDAddr
from deZent_demo.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent_demo.ami.smart_meter_measurement import PubLog

from deZent_demo.utils.pkgable_struct import *

class MessageType(StructTag):
    NETOP_REGISTRATION = "NetOP_registration"
    NETOP_PROMOTE_CCC = "NetOP_promote_ccc"

    CONNECT = "connect"

    P2P_PEER_REQUEST = "p2p_peer_request"
    P2P_PEER_SHARE = "p2p_peer_share"

    DZ_ROUND_COLLECT = "deZent_collection_round"
    DZ_ROUND_PUBLISH = "deZent_publication_round"
    DZ_PUBLISH_RECORD = "deZent_record_publication"

@smartdataclass
class Message(PkgableTaggedStruct[MessageType]):
    pass

@smartdataclass
class MessageConnect(Message, tag=MessageType.CONNECT):
    id: NetworkNodeID

#### p2p network Messages ############################################


@smartdataclass
class MessageP2PResquest(Message, tag=MessageType.P2P_PEER_REQUEST):
    requested_peer: NetworkNodeID

@smartdataclass
class MessageP2PShare(Message, tag=MessageType.P2P_PEER_SHARE):
    known_peers: list[NetworkNodeIDAddr]

#### deZent Messages ############################################
@smartdataclass
class MessageRoundCollect(Message, tag=MessageType.DZ_ROUND_COLLECT):
    cnt_struct: CntDataStructure

@smartdataclass
class MessageRoundPublish(Message, tag=MessageType.DZ_ROUND_PUBLISH):
    cnt_struct: CntDataStructure
    first_round: bool
    p_pub: int

@smartdataclass
class MessagePublishRecord(Message, tag=MessageType.DZ_PUBLISH_RECORD):
    pub_log: PubLog


__all__ = [
    "MessageType",
    "Message",

    "MessageConnect",

    "MessageP2PResquest",
    "MessageP2PShare",

    "MessageRoundCollect",
    "MessageRoundPublish",
    "MessagePublishRecord",
]