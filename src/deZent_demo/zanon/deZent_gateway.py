import random
from datetime import datetime, timedelta

from deZent_demo.ami.gateway import Gateway
from deZent_demo.ami.smart_meter_profile_distribution import SmartMeterProfileDistributionType
from deZent_demo.ami.measurement_log import RecordLog, PubLog
from deZent_demo.ami.gateway_profile import GatewayProfileType
from deZent_demo.network import *
from deZent_demo.utils.data.counting_structure import *
from deZent_demo.utils.time_env import *

from deZent_demo.instrument.deZent_gateway_instrumentor import *

class deZentGateway(Gateway, deZentNode):
    
    def __init__(
        self,
        env: AbstractTimeEnv,
        dt: timedelta,
        z: int,
        node: AbstractNetworkNode,
        ce_id: NetworkNodeID | None = None,
        next_id: NetworkNodeID | None = None,
        gw_profile_type: GatewayProfileType = GatewayProfileType.STANDARD,
        n_sm_conn: int = 1,
        sm_profile_distribution_type: SmartMeterProfileDistributionType = SmartMeterProfileDistributionType.TK,
        instrumentor: Instrumentor = Instrumentor(),
        **kwargs: Any,
    ) -> None:
        super().__init__(
            node=node,
            ce_id=ce_id,
            next_id=next_id,
            gw_profile_type=gw_profile_type,
            n_sm_conn=n_sm_conn,
            sm_profile_distribution_type=sm_profile_distribution_type,
            instrumentor=instrumentor,
            **kwargs
        )
        self.env: AbstractTimeEnv = env

        self._network_node.register_msg_cb(self._node_msg_cb_)

        self.coord: bool = False
        self.coord_noise: int = 0

        self.delta_t: timedelta = dt
        self.z: int = z
        self.measurement_interval = timedelta(minutes=15)
        self.n_cycles_for_anon: int = int(max(1, self.delta_t.seconds/self.measurement_interval.seconds))
    
    def on_coord_round_begin(self, curr_round_time: datetime) -> None:
        if not self.on_coord_wait_for_round_begin(curr_round_time):
            return # waiting was cancelled

        self._instrument(dZGWInstrumentEvent.CCC_ROUND_BEGIN,
            curr_round_time)

        self.coord = True
        self.on_coord_collection_round_begin(curr_round_time)

    '''
        coordinating gw prepares and starts collection round
        create cbf and add initial noise for protecting measurement entries
    '''
    def on_coord_collection_round_begin(self, curr_round_time: datetime) -> None:
        self._instrument(dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN,
            curr_round_time)
        
        cnt_struct: CntDataStructure = CBloomFilter.create(self.n_sm_conn, self.n_cycles_for_anon)
        self._instrument(dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_CREATED,
            curr_round_time, cnt_struct)
        
        cnt_struct = self.__coord_add_initial_noise_to_cnt_struct__(cnt_struct)
        self._instrument(dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED,
            curr_round_time, cnt_struct, self.coord_noise)
        
        self.send_collection_to_next(cnt_struct, curr_round_time)

    '''
        coordinating gw ends the collection round
        remove initial noise, start first publication round
    '''
    def on_coord_collection_round_end(self, cnt_struct: CntDataStructure, curr_round_time: datetime) -> None:
        self._instrument(dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END,
            curr_round_time, cnt_struct)
        
        cnt_struct = self.__coord_remove_initial_noise_from_cnt_struct__(cnt_struct)
        self._instrument(dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_NOISE_REMOVED,
            curr_round_time, cnt_struct, self.coord_noise)

        # NOTE: dangerzone! what abt byzantine CCCs, not ensuring z exposes non-anon. data        
        cnt_struct.ensure_min_cnt_z(self.z)
        self._instrument(dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_Z_ENSURED,
            curr_round_time, cnt_struct, self.z)

        # start publication round with random 0.0 <= p_pub < 1.0
        p_pub: float = random.random()
        self.on_coord_publication_round_begin(cnt_struct, p_pub, curr_round_time)

    '''
        coordinating gw starts a publication round (could be first with 0 < p_pub < 1.0, or second with p_pub = 1.0)
    '''
    def on_coord_publication_round_begin(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        self._instrument(dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_BEGIN,
            curr_round_time, cnt_struct, p_pub)
        
        self.send_publication_to_next(cnt_struct, p_pub, curr_round_time)        

    def on_coord_publication_round_end(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        publication_fully_finished: bool = (cnt_struct.is_empty() or p_pub == 1)
        
        self._instrument(dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_END,
            curr_round_time, cnt_struct, p_pub, publication_fully_finished)
        
        if publication_fully_finished:
            self.on_coord_round_end(curr_round_time)
        else:
            # start another publication round with p_pub = 1.0
            p_pub = 1.0
            self.on_coord_publication_round_begin(cnt_struct, p_pub, curr_round_time)

    
    def on_coord_round_end(self, curr_round_time: datetime) -> None:
        self._instrument(dZGWInstrumentEvent.CCC_ROUND_END,
            curr_round_time)
        
        self.coord = False
        self.send_coord_round_begin_to_next(curr_round_time)

    '''
        collection round with count structure passed on by predecessor
    '''
    def on_collection_round(self, cnt_struct: CntDataStructure, curr_round_time: datetime) -> None:
        self._instrument(dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND,
            curr_round_time, cnt_struct)
        
        self.record_log.remove_records_older_dt(curr_round_time, self.delta_t)
        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_round_time)
        self._instrument(dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_SM_MEASUREMENTS_COLLECTED,
            curr_round_time, self.record_log)

        cnt_struct.add_records(self.record_log)
        self._instrument(dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_RECORDS_ADDED,
            curr_round_time, cnt_struct)

        if self.coord: # collection round returned to the CCC
            self.on_coord_collection_round_end(cnt_struct, curr_round_time)
        else:
            self.send_collection_to_next(cnt_struct, curr_round_time)
    
    '''
        publish tuples that have been successfully anonymized with z
        the publication probability can be changed to provide certain deniability and provide more privacy
    '''
    def on_publication_round(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        self._instrument(dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND,
            curr_round_time, cnt_struct, p_pub)

        # find records in my local log are in cnt_struct
        # meaning they occurred at more than z individuals
        existing_records: RecordLog = cnt_struct.filter_records_existing(self.record_log)
        # find those entries that have been recorded in current clock cycle
        # and aren't published yet
        recs2pub: PubLog = existing_records.get_current_unpublished_records(curr_round_time)
        self._instrument(dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_RECORDS_TO_PUBLISH,
            curr_round_time, cnt_struct, self.record_log, recs2pub, p_pub)
        
        published_records: PubLog = PubLog() # collect published records first, then send them all at once
        # key hashes of some of GW's records were found in cnt_struct
        for rec2pub in recs2pub:
            # take publication responsibility with probability p_pub
            sampled_p_pub: float = random.random()
            should_publish: bool = sampled_p_pub < p_pub
            self._instrument(dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_SHOULD_RECORD_BE_PUBLISHED,
                curr_round_time, cnt_struct, self.record_log, recs2pub, p_pub, rec2pub, sampled_p_pub, should_publish)

            if should_publish and cnt_struct.check(rec2pub.key):

                # to publish: forward PubLogEntry to CE with value, timepoint, and sm_id for collection and further processing
                published_records.add_record(rec2pub)
                
                # update flag in record_log to indicate that the corresponding tuple has been published (rec2pub == PubLogEntry)
                self.record_log.update_record_published(rec2pub)

                # remove element's hash from cnt_struct
                cnt_struct.remove(rec2pub.key)
                self._instrument(dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_CBF_REMOVED_PUBLISHED_RECORD,
                    curr_round_time, cnt_struct, self.record_log, recs2pub, p_pub, rec2pub)

                # count structure is empty after publication -> not often the case due to older measurements within dt that are also counted
                if(cnt_struct.is_empty()):
                    break
        
        if published_records: 
            # publish all records at once
            self.send_publication_to_ce(published_records)
        
        if self.coord:
            self.on_coord_publication_round_end(cnt_struct, p_pub, curr_round_time)
        else:
            self.send_publication_to_next(cnt_struct, p_pub, curr_round_time)

    '''
        coord waits for the current round time stamp to be reached before starting the round
    '''
    def on_coord_wait_for_round_begin(self, curr_round_time: datetime) -> bool:
        return self.env.wait_until(curr_round_time)

    def _node_msg_cb_(self, sender: NetworkNodeID, msg: Message) -> None:
        match msg:
            case MessageDeZentRoundBegin() as m:
                self.on_coord_round_begin(m.round_time_stamp)
            case MessageRoundCollect() as m:
                self.on_collection_round(m.cnt_struct, m.round_time_stamp)
            case MessageRoundPublish() as m:
                self.on_publication_round(m.cnt_struct, m.p_pub, m.round_time_stamp)
            case _:
                pass

    def send_collection_to_next(self, cnt_struct: CntDataStructure, curr_round_time: datetime) -> None:
        msg: MessageRoundCollect = MessageRoundCollect(
            curr_round_time,
            cnt_struct
        )
        self._instrument(dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT,
            self.get_next(), msg)
        self.write_next(msg)

    def send_publication_to_next(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        msg: MessageRoundPublish = MessageRoundPublish(
            curr_round_time,
            cnt_struct,
            p_pub
        )
        self._instrument(dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_NEXT,
            self.get_next(), msg)
        self.write_next(msg)

    def send_publication_to_ce(self, records: PubLog) -> None:
        msg: MessagePublishRecord = MessagePublishRecord(
            records
        )
        self._instrument(dZGWInstrumentEvent.GW_SEND_PUBLICATION_TO_CE,
            self.get_ce(), msg)
        self.write_ce(msg)

    def send_coord_round_begin_to_next(self, curr_round_time: datetime) -> None:
        # NOTE: CCC promotion is currently cyclic
        # TODO: proper CCC election
        msg: MessageDeZentRoundBegin = MessageDeZentRoundBegin(
            curr_round_time + self.measurement_interval
        )
        self._instrument(dZGWInstrumentEvent.CCC_SEND_COORD_ROUND_BEGIN_TO_NEXT,
            self.get_next(), msg)
        self.write_next(msg)

    def __coord_sample_initial_noise__(self) -> int:
        return random.randint(20,30)

    def __coord_add_initial_noise_to_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        self.coord_noise = self.__coord_sample_initial_noise__()
        cnt_struct.add(self.coord_noise)
        return cnt_struct
    
    def __coord_remove_initial_noise_from_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        cnt_struct.remove(self.coord_noise)
        return cnt_struct
