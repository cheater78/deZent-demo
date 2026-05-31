from enum import Enum

from deZent.src.zanon.counting_data_structure.counting_data_structure import CntDataStructure

class MessageType(Enum):
    ROUND_COLLECT = 1
    ROUND_PUBLISH = 2
    PUBLISH_RECORD = 3

class Message:
    pass

class MessageRoundCollect(Message):
    cnt_struct: CntDataStructure

class MessageRoundPublish(Message):
    cnt_struct: CntDataStructure
    first_round: bool
    p_pub: int

class MessagePublishRecord(Message):
    pass