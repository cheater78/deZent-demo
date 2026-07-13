import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Callable

from deZent_demo.ami.gateway import Gateway, GatewayInstrumentInfo
from deZent_demo.ami.smart_meter_profile_distribution import SmartMeterProfileDistributionType
from deZent_demo.ami.measurement_log import RecordLog, PubLog
from deZent_demo.ami.gateway_profile import GatewayProfileType
from deZent_demo.network.address import NetworkNodeID
from deZent_demo.network.net_node import AbstractNetworkNode
from deZent_demo.network.protocol import *
from deZent_demo.zanon.counting_data_structure import *
from deZent_demo.utils.time_env import *

@dataclass
class deZentGatewayInstrumentInfo:
    ccc_round_begin_cb: Callable[[NetworkNodeID, datetime], None] | None = None
    ccc_round_end_cb: Callable[[NetworkNodeID, datetime], None] | None = None
    
    ccc_collection_round_begin_cb: Callable[[NetworkNodeID, datetime, CntDataStructure], None] | None = None
    ccc_collection_round_end_cb: Callable[[NetworkNodeID, datetime, CntDataStructure], None] | None = None

    ccc_publication_round_begin_cb: Callable[[NetworkNodeID, datetime, CntDataStructure, float], None] | None = None
    ccc_publication_round_end_cb: Callable[[NetworkNodeID, datetime, CntDataStructure, float], None] | None = None

    collection_round_cb: Callable[[NetworkNodeID, datetime, CntDataStructure], None] | None = None
    publication_round_cb: Callable[[NetworkNodeID, datetime, CntDataStructure, float], None] | None = None

    gateway_instrument_info: GatewayInstrumentInfo | None = None

class deZentGateway(Gateway):
    
    def __init__(self,
                 env: AbstractTimeEnv,
                 node: AbstractNetworkNode,
                 dt_minutes: int,
                 z: int,

                 ce: NetworkNodeID,
                 prev: NetworkNodeID,
                 next: NetworkNodeID,

                 gw_profile_type: GatewayProfileType = GatewayProfileType.STANDARD,
                 n_sm_conn: int = 1,
                 sm_profile_distribution_type: SmartMeterProfileDistributionType = SmartMeterProfileDistributionType.TK,
                 instrument_info: deZentGatewayInstrumentInfo | None = None) -> None:
        self.env: AbstractTimeEnv = env

        self._node_: AbstractNetworkNode = node
        self._node_.register_msg_cb(self._node_msg_cb_)
        
        # TODO: get ring and star
        self.ce: NetworkNodeID = ce
        self.prev: NetworkNodeID = prev
        self.next: NetworkNodeID = next

        self.coord: bool = False
        self.coord_noise: int = 0

        self.delta_t: timedelta = timedelta(minutes=dt_minutes)
        self.z: int = z
        self.measurement_interval = timedelta(minutes=15)
        self.n_cycles_for_anon: int = int(max(1, self.delta_t.seconds/self.measurement_interval.seconds))
        
        Gateway.__init__(
            self,
            self.ce,
            self._node_.id(),
            gw_profile_type,
            n_sm_conn,
            sm_profile_distribution_type
        )

        self.dZgw_instrument_info: deZentGatewayInstrumentInfo | None = instrument_info

    def on_coord_round_begin(self, curr_round_time: datetime) -> None:
        self.coord = True
        self.on_coord_wait_for_round_begin(curr_round_time)
        self.on_coord_collection_round_begin(curr_round_time)

        if self.dZgw_instrument_info and self.dZgw_instrument_info.ccc_round_begin_cb:
            self.dZgw_instrument_info.ccc_round_begin_cb(self._node_.id(), curr_round_time)

    '''
        coordinating gw prepares and starts collection round
        create cbf and add initial noise for protecting measurement entries
    '''
    def on_coord_collection_round_begin(self, curr_round_time: datetime) -> None:
        cnt_struct: CntDataStructure = CBloomFilter.create(self.n_sm_conn, self.n_cycles_for_anon)
        cnt_struct = self.__coord_add_initial_noise_to_cnt_struct__(cnt_struct)

        if self.dZgw_instrument_info and self.dZgw_instrument_info.ccc_collection_round_begin_cb:
            self.dZgw_instrument_info.ccc_collection_round_begin_cb(self._node_.id(), curr_round_time, cnt_struct)
        
        self.send_collection_to_next(cnt_struct, curr_round_time)

    '''
        coordinating gw ends the collection round
        remove initial noise, start first publication round
    '''
    def on_coord_collection_round_end(self, cnt_struct: CntDataStructure, curr_round_time: datetime) -> None:
        cnt_struct = self.__coord_remove_initial_noise_from_cnt_struct__(cnt_struct)
        cnt_struct.ensure_min_cnt_z(self.z) # NOTE: dangerzone! what abt byzantine CCCs, not ensuring z exposes non-anon. data
        
        if self.dZgw_instrument_info and self.dZgw_instrument_info.ccc_collection_round_end_cb:
            self.dZgw_instrument_info.ccc_collection_round_end_cb(self._node_.id(), curr_round_time, cnt_struct)

        # start publication round with random 0 <= p_pub < 1
        p_pub: float = random.random()
        self.on_coord_publication_round_begin(cnt_struct, p_pub, curr_round_time)

    '''
        coordinating gw starts a publication round (could be first with 0 < p_pub < 100, or second with p_pub = 100)
    '''
    def on_coord_publication_round_begin(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        if self.dZgw_instrument_info and self.dZgw_instrument_info.ccc_publication_round_begin_cb:
            self.dZgw_instrument_info.ccc_publication_round_begin_cb(self._node_.id(), curr_round_time, cnt_struct, p_pub)
        
        self.send_publication_to_next(cnt_struct, p_pub, curr_round_time)        

    def on_coord_publication_round_end(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        if self.dZgw_instrument_info and self.dZgw_instrument_info.ccc_publication_round_begin_cb:
            self.dZgw_instrument_info.ccc_publication_round_begin_cb(self._node_.id(), curr_round_time, cnt_struct, p_pub)
        
        if cnt_struct.is_empty() or p_pub == 1:
            self.on_coord_round_end(curr_round_time)
        else:
            # start another publication round with p_pub = 1
            p_pub = 1
            self.on_coord_publication_round_begin(cnt_struct, p_pub, curr_round_time)

    
    def on_coord_round_end(self, curr_round_time: datetime) -> None:
        if self.dZgw_instrument_info and self.dZgw_instrument_info.ccc_round_end_cb:
            self.dZgw_instrument_info.ccc_round_end_cb(self._node_.id(), curr_round_time)
        
        self.coord = False
        self.send_coord_round_begin_to_next(curr_round_time)


    '''
        collection round with count structure passed on from predecessor
    '''
    def on_collection_round(self, cnt_struct: CntDataStructure, curr_round_time: datetime) -> None:
        self.record_log.remove_records_older_dt(curr_round_time, self.delta_t)
        
        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_round_time)
        cnt_struct.add_records(self.record_log)

        if self.dZgw_instrument_info and self.dZgw_instrument_info.collection_round_cb:
            self.dZgw_instrument_info.collection_round_cb(self._node_.id(), curr_round_time, cnt_struct)

        if self.coord: # collection round returned to the CCC
            self.on_coord_collection_round_end(cnt_struct, curr_round_time)
        else:
            self.send_collection_to_next(cnt_struct, curr_round_time)
    
    '''
        publish tuples that have been successfully anonymized with z
        the publication probability can be changed to provide certain deniability and provide more privacy
    '''
    def on_publication_round(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        # find records in my local log are in cnt_struct
        # meaning they occurred at more than z individuals
        existing_records: RecordLog = cnt_struct.filter_records_existing(self.record_log)

        # print(f"__check__: existing records: {existing_records}")

        # find those entries that have been recorded in current clock cycle
        # and aren't published yet
        recs2pub: PubLog = existing_records.get_current_unpublished_records(curr_round_time)
        
        #print("__check__: potential current pub records at GW: ", self.id)#, recs2pub)
        #logger.print_pub_log(recs2pub)
        
        published_records: PubLog = PubLog() # collect published records first, then send them all at once
        # key hashes of some of GW's records were found in cnt_struct
        for rec2pub in recs2pub:
            # take publication responsibility with probability p_pub
            sampled_p_pub: float = random.random()
            should_publish: bool = sampled_p_pub < p_pub
            if should_publish and cnt_struct.check(rec2pub.key):

                # to publish: forward PubLogEntry to CE with value, timepoint, and sm_id for collection and further processing
                published_records.add_record(rec2pub)
                
                # update flag in record_log to indicate that the corresponding tuple has been published (rec2pub == PubLogEntry)
                self.record_log.update_record_published(rec2pub)

                # remove element's hash from cnt_struct
                cnt_struct.remove(rec2pub.key)

                # count structure is empty after publication -> not often the case due to older measurements within dt that are also counted
                if(cnt_struct.is_empty()):
                    break
        
        if published_records: 
            # publish all records at once
            self.send_publication_to_ce(published_records)
        
        if self.dZgw_instrument_info and self.dZgw_instrument_info.publication_round_cb:
            self.dZgw_instrument_info.publication_round_cb(self._node_.id(), curr_round_time, cnt_struct, p_pub)
        
        if self.coord:
            self.on_coord_publication_round_end(cnt_struct, p_pub, curr_round_time)
        else:
            self.send_publication_to_next(cnt_struct, p_pub, curr_round_time)

    '''
        coord waits for the current round time stamp to be reached before starting the round
    '''
    def on_coord_wait_for_round_begin(self, curr_round_time: datetime) -> None:
        self.env.wait_until(curr_round_time)

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
        self._node_.write(self.next, msg)

    def send_publication_to_next(self, cnt_struct: CntDataStructure, p_pub: float, curr_round_time: datetime) -> None:
        msg: MessageRoundPublish = MessageRoundPublish(
            curr_round_time,
            cnt_struct,
            p_pub
        )
        self._node_.write(self.next, msg)

    def send_publication_to_ce(self, records: PubLog) -> None:
        msg: MessagePublishRecord = MessagePublishRecord(
            records
        )
        self._node_.write(self.ce, msg)

    def send_coord_round_begin_to_next(self, curr_round_time: datetime) -> None:
        msg: MessageDeZentRoundBegin = MessageDeZentRoundBegin(
            curr_round_time + self.measurement_interval
        )
        self._node_.write(self.next, msg)

    def __coord_sample_initial_noise__(self) -> int:
        return random.randint(20,30)

    def __coord_add_initial_noise_to_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        self.coord_noise = self.__coord_sample_initial_noise__()
        cnt_struct.add(self.coord_noise)
        return cnt_struct
    
    def __coord_remove_initial_noise_from_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        cnt_struct.remove(self.coord_noise)
        return cnt_struct
