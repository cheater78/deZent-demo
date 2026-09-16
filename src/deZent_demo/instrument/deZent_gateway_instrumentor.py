from enum import auto
from datetime import datetime

from deZent_demo.network.address import NetworkNodeID
from deZent_demo.network.protocol import *
from deZent_demo.utils.data.counting_structure.counting_bloom_filter import CBloomFilter
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

class dZGWLoggingDebugInstrumentor(dZGWInstrumentor):

    def __init__(self, tag: str = "unnamed") -> None:
        super().__init__()
        self._tag = tag

        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_ROUND_BEGIN,
            self.on_ccc_round_begin
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN,
            self.on_ccc_collection_round_begin
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_CREATED,
            self.on_ccc_collection_round_begin_cbf_created
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED,
            self.on_ccc_collection_round_begin_cbf_noise_added
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END,
            self.on_ccc_collection_round_end
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_NOISE_REMOVED,
            self.on_ccc_collection_round_end_cbf_noise_removed
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_Z_ENSURED,
            self.on_ccc_collection_round_end_cbf_z_ensured
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_BEGIN,
            self.on_ccc_publication_round_begin
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_END,
            self.on_ccc_publication_round_end
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_ROUND_END,
            self.on_ccc_round_end
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND,
            self.on_gw_on_collection_round
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_SM_MEASUREMENTS_COLLECTED,
            self.on_gw_on_collection_round_sm_measurements_collected
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_RECORDS_ADDED,
            self.on_gw_on_collection_round_records_added
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND,
            self.on_gw_on_publication_round
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_RECORDS_TO_PUBLISH,
            self.on_gw_on_publication_round_records_to_publish
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_SHOULD_RECORD_BE_PUBLISHED,
            self.on_gw_on_publication_round_should_record_be_published
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_CBF_REMOVED_PUBLISHED_RECORD,
            self.on_gw_on_publication_round_cbf_removed_published_record
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT,
            self.on_gw_send_collection_to_next
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_NEXT,
            self.on_gw_send_publication_to_next
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_CE,
            self.on_gw_send_publication_to_ce
        )
        self.set_instrument_callback(
            dZGWInstrumentEvent.CCC_SEND_COORD_ROUND_BEGIN_TO_NEXT,
            self.on_ccc_send_coord_round_begin_to_next
        )

        # NOTE: no gates for debug
        # for event in dZGWInstrumentEvent:
        #     self.set_instrument_gate(event, None)

    def on_ccc_round_begin(self, curr_time: datetime) -> None:
        print(f"GW-{self._tag}: on_ccc_round_begin {curr_time}")

    def on_ccc_collection_round_begin(self, curr_time: datetime) -> None:
        print(f"GW-{self._tag}: on_ccc_collection_round_begin {curr_time}")

    def on_ccc_collection_round_begin_cbf_created(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self._tag}: on_ccc_collection_round_begin_cbf_created {curr_time} {cbf}")
    
    def on_ccc_collection_round_begin_cbf_noise_added(self, curr_time: datetime, cbf: CBloomFilter, noise: int) -> None:
        print(f"GW-{self._tag}: on_ccc_collection_round_begin_cbf_noise_added {curr_time} {cbf} {noise}")

    def on_ccc_collection_round_end(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self._tag}: on_ccc_collection_round_end {curr_time} {cbf}")

    def on_ccc_collection_round_end_cbf_noise_removed(self, curr_time: datetime, cbf: CBloomFilter, noise: int) -> None:
        print(f"GW-{self._tag}: on_ccc_collection_round_end_cbf_noise_removed {curr_time} {cbf} {noise}")

    def on_ccc_collection_round_end_cbf_z_ensured(self, curr_time: datetime, cbf: CBloomFilter, z: int) -> None:
        print(f"GW-{self._tag}: on_ccc_collection_round_end_cbf_z_ensured {curr_time} {cbf} {z}")

    def on_ccc_publication_round_begin(self, curr_time: datetime, cbf: CBloomFilter, p_pub: float) -> None:
        print(f"GW-{self._tag}: on_ccc_publication_round_begin {curr_time} {cbf} {p_pub}")

    def on_ccc_publication_round_end(self, curr_time: datetime, cbf: CBloomFilter, p_pub: float, published: bool) -> None:
        print(f"GW-{self._tag}: on_ccc_publication_round_end {curr_time} {cbf} {p_pub} {published}")

    def on_ccc_round_end(self, curr_time: datetime) -> None:
        print(f"GW-{self._tag}: on_ccc_round_end {curr_time}")

    def on_gw_on_collection_round(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self._tag}: on_gw_on_collection_round {curr_time} {cbf}")

    def on_gw_on_collection_round_sm_measurements_collected(self, curr_time: datetime, record_log: RecordLog) -> None:
        print(f"GW-{self._tag}: on_gw_on_collection_round_sm_measurements_collected {curr_time} {record_log}")

    def on_gw_on_collection_round_records_added(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self._tag}: on_gw_on_collection_round_records_added {curr_time} {cbf}")

    def on_gw_on_publication_round(self, curr_time: datetime, cbf: CBloomFilter, p_pub: float) -> None:
        print(f"GW-{self._tag}: on_gw_on_publication_round {curr_time} {cbf} {p_pub}")

    def on_gw_on_publication_round_records_to_publish(
        self,
        curr_time: datetime,
        cbf: CBloomFilter,
        record_log: RecordLog,
        pub_log: PubLog,
        p_pub: float,
    ) -> None:
        print(f"GW-{self._tag}: on_gw_on_publication_round_records_to_publish {curr_time} {cbf} {record_log} {pub_log} {p_pub}")

    def on_gw_on_publication_round_should_record_be_published(
        self,
        curr_time: datetime,
        cbf: CBloomFilter,
        record_log: RecordLog,
        pub_log: PubLog,
        p_pub: float,
        pub_log_entry: PubLogEntry,
        sampled_p_pub: float,
        should_publish: bool,
    ) -> None:
        print(f"GW-{self._tag}: on_gw_on_publication_round_should_record_be_published {curr_time} {cbf} {record_log} {pub_log} {p_pub} {pub_log_entry} {sampled_p_pub} {should_publish}")

    def on_gw_on_publication_round_cbf_removed_published_record(
        self,
        curr_time: datetime,
        cbf: CBloomFilter,
        record_log: RecordLog,
        pub_log: PubLog,
        p_pub: float,
        pub_log_entry: PubLogEntry,
    ) -> None:
        print(f"GW-{self._tag}: on_gw_on_publication_round_cbf_removed_published_record {curr_time} {cbf} {record_log} {pub_log} {p_pub} {pub_log_entry} ")

    def on_gw_send_collection_to_next(self, node_id: NetworkNodeID, message: MessageRoundCollect) -> None:
        print(f"GW-{self._tag}: on_gw_send_collection_to_next {node_id} {message}")

    def on_gw_send_publication_to_next(self, node_id: NetworkNodeID, message: MessageRoundPublish) -> None:
        print(f"GW-{self._tag}: on_gw_send_publication_to_next {node_id} {message}")

    def on_gw_send_publication_to_ce(self, node_id: NetworkNodeID, message: MessagePublishRecord) -> None:
        print(f"GW-{self._tag}: on_gw_send_publication_to_ce {node_id} {message}")

    def on_ccc_send_coord_round_begin_to_next(
        self,
        node_id: NetworkNodeID,
        message: MessageDeZentRoundBegin,
    ) -> None:
        print(f"GW-{self._tag}: on_ccc_send_coord_round_begin_to_next {node_id} {message}")