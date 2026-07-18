from enum import auto
from datetime import datetime

from deZent_demo.network.address import NetworkNodeID
from deZent_demo.network.protocol import *
from deZent_demo.zanon.counting_data_structure import CBloomFilter
from deZent_demo.ami.measurement_log import RecordLog, PubLog, PubLogEntry

from .gateway_instrumentor import *

class dZGWInstrumentEvent(InstrumentEvent):
    CCC_ROUND_BEGIN = auto()

    CCC_COLLECTION_ROUND_BEGIN = auto()
    CCC_COLLECTION_ROUND_BEGIN_CBF_CREATED = auto()
    CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED = auto()

    CCC_COLLECTION_ROUND_END = auto()
    CCC_COLLECTION_ROUND_END_CBF_NOISE_REMOVED = auto()
    CCC_COLLECTION_ROUND_END_CBF_Z_ENSURED = auto()

    CCC_PUBLICATION_ROUND_BEGIN = auto()
    CCC_PUBLICATION_ROUND_END = auto()

    CCC_ROUND_END = auto()

    GW_ON_COLLECTION_ROUND = auto()
    GW_ON_COLLECTION_ROUND_SM_MEASUREMENTS_COLLECTED = auto()
    GW_ON_COLLECTION_ROUND_RECORDS_ADDED = auto()

    GW_ON_PUBLICATION_ROUND = auto()
    GW_ON_PUBLICATION_ROUND_RECORDS_TO_PUBLISH = auto()
    GW_ON_PUBLICATION_ROUND_SHOULD_RECORD_BE_PUBLISHED = auto()
    GW_ON_PUBLICATION_ROUND_CBF_REMOVED_PUBLISHED_RECORD = auto()

    GW_SEND_COLLECTION_TO_NEXT = auto()
    GW_SEND_PUBLICATION_TO_NEXT = auto()
    GW_SEND_PUBLICATION_TO_CE = auto()

    # NOTE: CCC promotion is currently cyclic
    # TODO: proper CCC election
    CCC_SEND_COORD_ROUND_BEGIN_TO_NEXT = auto()

class dZGWInstrumentor(GWInstrumentor):
    event_type = dZGWInstrumentEvent
    event_cb_signatures = {
        dZGWInstrumentEvent.CCC_ROUND_BEGIN: [datetime],

        dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN: [datetime],
        dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_CREATED: [datetime, CBloomFilter],
        dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED: [datetime, CBloomFilter, int],

        dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END: [datetime, CBloomFilter],
        dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_NOISE_REMOVED: [datetime, CBloomFilter, int],
        dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_Z_ENSURED: [datetime, CBloomFilter, int],

        dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_BEGIN: [datetime, CBloomFilter, float],
        dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_END: [datetime, CBloomFilter, float, bool],

        dZGWInstrumentEvent.CCC_ROUND_END: [datetime],

        dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND: [datetime, CBloomFilter],
        dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_SM_MEASUREMENTS_COLLECTED: [datetime, RecordLog],
        dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_RECORDS_ADDED: [datetime, CBloomFilter],

        dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND: [datetime, CBloomFilter, float],
        dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_RECORDS_TO_PUBLISH: [datetime, CBloomFilter, RecordLog, PubLog, float],
        dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_SHOULD_RECORD_BE_PUBLISHED: [datetime, CBloomFilter, RecordLog, PubLog, float, PubLogEntry, float, bool],
        dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_CBF_REMOVED_PUBLISHED_RECORD: [datetime, CBloomFilter, RecordLog, PubLog, float, PubLogEntry],

        dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT: [NetworkNodeID, MessageRoundCollect],
        dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_NEXT: [NetworkNodeID, MessageRoundPublish],
        dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_CE: [NetworkNodeID, MessagePublishRecord],

        dZGWInstrumentEvent.CCC_SEND_COORD_ROUND_BEGIN_TO_NEXT: [NetworkNodeID, MessageDeZentRoundBegin],
    }