from PySide6.QtWidgets import (
    QWidget,
    QPushButton
)

from deZent_demo.zanon.deZent_gateway import *
from deZent_demo.instrument.deZent_gateway_instrumentor import *

class deZentGatewayWidget(QWidget):

    def __init__(self, deZent_gateway: deZentGateway) -> None:
        super().__init__()

        self.dZgw: deZentGateway = deZent_gateway
        
        self.instrumentor: dZGWInstrumentor = dZGWInstrumentor()
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_ROUND_BEGIN,
            self.on_ccc_round_begin
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN,
            self.on_ccc_collection_round_begin
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_CREATED,
            self.on_ccc_collection_round_begin_cbf_created
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED,
            self.on_ccc_collection_round_begin_cbf_noise_added
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END,
            self.on_ccc_collection_round_end
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_NOISE_REMOVED,
            self.on_ccc_collection_round_end_cbf_noise_removed
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_Z_ENSURED,
            self.on_ccc_collection_round_end_cbf_z_ensured
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_BEGIN,
            self.on_ccc_publication_round_begin
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_END,
            self.on_ccc_publication_round_end
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_ROUND_END,
            self.on_ccc_round_end
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND,
            self.on_gw_on_collection_round
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_SM_MEASUREMENTS_COLLECTED,
            self.on_gw_on_collection_round_sm_measurements_collected
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_RECORDS_ADDED,
            self.on_gw_on_collection_round_records_added
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND,
            self.on_gw_on_publication_round
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_RECORDS_TO_PUBLISH,
            self.on_gw_on_publication_round_records_to_publish
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_SHOULD_RECORD_BE_PUBLISHED,
            self.on_gw_on_publication_round_should_record_be_published
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_CBF_REMOVED_PUBLISHED_RECORD,
            self.on_gw_on_publication_round_cbf_removed_published_record
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT,
            self.on_gw_send_collection_to_next
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_NEXT,
            self.on_gw_send_publication_to_next
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_CE,
            self.on_gw_send_publication_to_ce
        )
        self.instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_SEND_COORD_ROUND_BEGIN_TO_NEXT,
            self.on_ccc_send_coord_round_begin_to_next
        )

        # TODO: build and integrate UI

        self.next_b: QPushButton = QPushButton("next", parent=self)
        self.next_gate: QtInstrumentorGate = QtInstrumentorGate(parent=self)
        self.next_b.clicked.connect(self.next_gate.release)

        for event in dZGWInstrumentEvent:
            self.instrumentor.set_instrument_gate(event, self.next_gate)

        # TODO: build and integrate UI

        self.dZgw.set_instrumentor(self.instrumentor)

    def on_ccc_round_begin(self, curr_time: datetime) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_round_begin {curr_time}")

    def on_ccc_collection_round_begin(self, curr_time: datetime) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_collection_round_begin {curr_time}")

    def on_ccc_collection_round_begin_cbf_created(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_collection_round_begin_cbf_created {curr_time} {cbf}")
    
    def on_ccc_collection_round_begin_cbf_noise_added(self, curr_time: datetime, cbf: CBloomFilter, noise: int) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_collection_round_begin_cbf_noise_added {curr_time} {cbf} {noise}")

    def on_ccc_collection_round_end(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_collection_round_end {curr_time} {cbf}")

    def on_ccc_collection_round_end_cbf_noise_removed(self, curr_time: datetime, cbf: CBloomFilter, noise: int) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_collection_round_end_cbf_noise_removed {curr_time} {cbf} {noise}")

    def on_ccc_collection_round_end_cbf_z_ensured(self, curr_time: datetime, cbf: CBloomFilter, z: int) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_collection_round_end_cbf_z_ensured {curr_time} {cbf} {z}")

    def on_ccc_publication_round_begin(self, curr_time: datetime, cbf: CBloomFilter, p_pub: float) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_publication_round_begin {curr_time} {cbf} {p_pub}")

    def on_ccc_publication_round_end(self, curr_time: datetime, cbf: CBloomFilter, p_pub: float, published: bool) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_publication_round_end {curr_time} {cbf} {p_pub} {published}")

    def on_ccc_round_end(self, curr_time: datetime) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_round_end {curr_time}")

    def on_gw_on_collection_round(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_on_collection_round {curr_time} {cbf}")

    def on_gw_on_collection_round_sm_measurements_collected(self, curr_time: datetime, record_log: RecordLog) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_on_collection_round_sm_measurements_collected {curr_time} {record_log}")

    def on_gw_on_collection_round_records_added(self, curr_time: datetime, cbf: CBloomFilter) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_on_collection_round_records_added {curr_time} {cbf}")

    def on_gw_on_publication_round(self, curr_time: datetime, cbf: CBloomFilter, p_pub: float) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_on_publication_round {curr_time} {cbf} {p_pub}")

    def on_gw_on_publication_round_records_to_publish(
        self,
        curr_time: datetime,
        cbf: CBloomFilter,
        record_log: RecordLog,
        pub_log: PubLog,
        p_pub: float,
    ) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_on_publication_round_records_to_publish {curr_time} {cbf} {record_log} {pub_log} {p_pub}")

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
        print(f"GW-{self.dZgw.gw_id}: on_gw_on_publication_round_should_record_be_published {curr_time} {cbf} {record_log} {pub_log} {p_pub} {pub_log_entry} {sampled_p_pub} {should_publish}")

    def on_gw_on_publication_round_cbf_removed_published_record(
        self,
        curr_time: datetime,
        cbf: CBloomFilter,
        record_log: RecordLog,
        pub_log: PubLog,
        p_pub: float,
        pub_log_entry: PubLogEntry,
    ) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_on_publication_round_cbf_removed_published_record {curr_time} {cbf} {record_log} {pub_log} {p_pub} {pub_log_entry} ")

    def on_gw_send_collection_to_next(self, node_id: NetworkNodeID, message: MessageRoundCollect) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_send_collection_to_next {node_id} {message}")

    def on_gw_send_publication_to_next(self, node_id: NetworkNodeID, message: MessageRoundPublish) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_send_publication_to_next {node_id} {message}")

    def on_gw_send_publication_to_ce(self, node_id: NetworkNodeID, message: MessagePublishRecord) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_gw_send_publication_to_ce {node_id} {message}")

    def on_ccc_send_coord_round_begin_to_next(
        self,
        node_id: NetworkNodeID,
        message: MessageDeZentRoundBegin,
    ) -> None:
        print(f"GW-{self.dZgw.gw_id}: on_ccc_send_coord_round_begin_to_next {node_id} {message}")