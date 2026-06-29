from datetime import datetime, timedelta

from deZent_demo.network.net_node import NetworkNodeID, NetworkNodeIDAddr
from deZent_demo.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent_demo.ami.measurement_log import PubLog

from deZent_demo.utils.pkgable_struct import *


class MessageType(StructTag):
    NETOP_REGISTRATION = "NetOP_registration"
    NETOP_PROMOTE_CCC = "NetOP_promote_ccc"

    CONNECT = "connect"

    RING_UPDATE = "ring_update"

    NODE_ID_REQUEST = "ns_request"
    NODE_ID_RESPONSE = "ns_response"

    CTL_START = "ctl_start"
    CTL_RESET = "ctl_rst"

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

@smartdataclass
class MessageRingViewLike(Message):
    view_id: int

@smartdataclass
class MessageRingUpdate(MessageRingViewLike, tag=MessageType.RING_UPDATE):
    prev: NetworkNodeID
    next: NetworkNodeID

@smartdataclass
class MessageNodeIDRequest(Message, tag=MessageType.NODE_ID_REQUEST):
    id: NetworkNodeID

@smartdataclass
class MessageNodeIDResponse(Message, tag=MessageType.NODE_ID_RESPONSE):
    id: NetworkNodeIDAddr


#### control Messages ############################################

@smartdataclass
class MessageCTLStart(Message, tag=MessageType.CTL_START):
    start_time: datetime
    run_time: timedelta
    speed: float

@smartdataclass
class MessageCTLReset(Message, tag=MessageType.CTL_RESET):
    pass


#### deZent Messages ############################################

@smartdataclass
class MessageDeZentRound(MessageRingViewLike):
    round_id: int

@smartdataclass
class MessageRoundCollect(MessageDeZentRound, tag=MessageType.DZ_ROUND_COLLECT):
    cnt_struct: CntDataStructure

@smartdataclass
class MessageRoundPublish(MessageDeZentRound, tag=MessageType.DZ_ROUND_PUBLISH):
    cnt_struct: CntDataStructure
    first_round: bool
    p_pub: int

@smartdataclass
class MessagePublishRecord(MessageDeZentRound, tag=MessageType.DZ_PUBLISH_RECORD):
    pub_log: PubLog


__all__ = [
    "MessageType",
    "Message",

    "MessageConnect",

    "MessageRoundCollect",
    "MessageRoundPublish",
    "MessagePublishRecord",
]