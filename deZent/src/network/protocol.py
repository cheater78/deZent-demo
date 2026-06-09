from deZent.src.network.net_node import NetworkNodeIDAddr
from deZent.src.zanon.counting_data_structure.counting_data_structure import CntDataStructure

from c78_pytils.types.pkgable_struct import PkgableTaggedStruct
from c78_pytils.types.smart_struct import StructTag

class MessageType(StructTag):
    NETOP_REGISTRATION = "NetOP_registration"
    DZ_ROUND_COLLECT = "deZent_collection_round"
    DZ_ROUND_PUBLISH = "deZent_publication_round"
    DZ_PUBLISH_RECORD = "deZent_record_publication"

class Message(PkgableTaggedStruct[MessageType]):
    pass

class MessageNetworkOPRegistration(Message, tag=MessageType.NETOP_REGISTRATION):
    id: NetworkNodeIDAddr
    ce: NetworkNodeIDAddr
    prev: NetworkNodeIDAddr
    next: NetworkNodeIDAddr


class MessageRoundCollect(Message):
    cnt_struct: CntDataStructure

class MessageRoundPublish(Message):
    cnt_struct: CntDataStructure
    first_round: bool
    p_pub: int

class MessagePublishRecord(Message):
    pass

__all__ = [
    "MessageType",
    "Message",
    "MessageNetworkOPRegistration",
    "MessageRoundCollect",
    "MessageRoundPublish",
    "MessagePublishRecord",
]