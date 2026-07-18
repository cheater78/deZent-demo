from datetime import datetime

from deZent_demo.network.address import NetworkNodeID, NetworkNodeIDAddr
from deZent_demo.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent_demo.ami.measurement_log import PubLog

from deZent_demo.utils.pkgable_struct import *

class MessageType(StructTag):
    NETOP_REGISTRATION = "NetOP_registration"
    NETOP_PROMOTE_CCC = "NetOP_promote_ccc"

    CONNECT = "connect"
    
    NODE_ID_REQUEST = "ns_request"
    NODE_ID_RESPONSE = "ns_response"

    DZ_ROUND_BEGIN = "deZent_round_begin"
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
class MessageNodeIDRequest(Message, tag=MessageType.NODE_ID_REQUEST):
    id: NetworkNodeID

@smartdataclass
class MessageNodeIDResponse(Message, tag=MessageType.NODE_ID_RESPONSE):
    id_addr: NetworkNodeIDAddr

#### deZent Messages ############################################

@smartdataclass
class MessageDeZentRound(Message):
    round_time_stamp: datetime

@smartdataclass
class MessageDeZentRoundBegin(MessageDeZentRound, tag=MessageType.DZ_ROUND_BEGIN):
    # NOTE: CCC promotion is currently cyclic
    # TODO: proper CCC election
    pass

@smartdataclass
class MessageRoundCollect(MessageDeZentRound, tag=MessageType.DZ_ROUND_COLLECT):
    cnt_struct: CntDataStructure

@smartdataclass
class MessageRoundPublish(MessageDeZentRound, tag=MessageType.DZ_ROUND_PUBLISH):
    cnt_struct: CntDataStructure
    p_pub: float

@smartdataclass
class MessagePublishRecord(Message, tag=MessageType.DZ_PUBLISH_RECORD):
    pub_log: PubLog
