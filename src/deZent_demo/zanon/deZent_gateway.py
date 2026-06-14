import random
from datetime import datetime, timedelta

from deZent_demo.ami.gateway import Gateway, GWID
from deZent_demo.ami.smart_meter_profile_distribution import SmartMeterProfileDistributionType
from deZent_demo.ami.smart_meter_measurement import RecordLog, PubLog
from deZent_demo.ami.gateway_profile import GatewayProfileType
from deZent_demo.ami.central_entity import CEID

from deZent_demo.network.deZent_node import deZentNetworkNode

from deZent_demo.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent_demo.zanon.counting_data_structure.counting_bloom_filter import CBloomFilter


class deZentGateway(Gateway):
    
    def __init__(self,
                 ce_id: CEID,
                 gw_id: GWID,
                 dt_minutes: int,
                 z: int,
                 gw_profile_type: GatewayProfileType = GatewayProfileType.STANDARD,
                 n_sm_conn: int = 0,
                 sm_profile_distribution_type: SmartMeterProfileDistributionType = SmartMeterProfileDistributionType.TK) -> None:
        Gateway.__init__(
            self,
            ce_id,
            gw_id,
            gw_profile_type,
            n_sm_conn,
            sm_profile_distribution_type
        )
        
        self.coord: bool = False
        self.coord_noise: int = 0

        self.delta_t: timedelta = timedelta(minutes=dt_minutes)
        self.z: int = z
        self.measurement_frequency = timedelta(minutes=15)
        self.n_cycles_for_anon: int = int(max(1, self.delta_t.seconds/self.measurement_frequency.seconds))

    def promote_coord(self) -> None:
        self.coord = True
    
    '''
        coordinating gw prepares and starts collection round
        create cbf and add initial noise for protecting measurement entries
    '''
    def coord_begin_collection_round(self) -> None:
        cnt_struct: CntDataStructure = CBloomFilter.create(self.n_sm_conn, self.n_cycles_for_anon)
        cnt_struct = self.__coord_add_initial_noise_to_cnt_struct__(cnt_struct)
        self.send_collection_to_next(cnt_struct)

    '''
        coordinating gw ends the collection round
        remove initial noise, start first publication round
    '''
    def coord_end_collection_round(self, cnt_struct: CntDataStructure) -> None:
        cnt_struct = self.__coord_remove_initial_noise_from_cnt_struct__(cnt_struct)
        cnt_struct.ensure_min_cnt_z(self.z) # NOTE: dangerzone! what abt byzantine CCCs, not ensuring z exposes non-anon. data
        self.coord_begin_first_publication_round(cnt_struct)

    '''
        coordinating gw starts first publication round
        sample publication probability
    '''
    def coord_begin_first_publication_round(self, cnt_struct: CntDataStructure) -> None:
        p_pub: int = self.__sample_publication_probability__()
        self.send_publication_to_next(cnt_struct, p_pub)

    '''
        coordinating gw starts second publication round
        ensure publication now
    '''
    def coord_begin_second_publication_round(self, cnt_struct: CntDataStructure) -> None:
        p_pub: int = 100
        self.send_publication_to_next(cnt_struct, p_pub)

    '''
        collection round with count structure passed on from predecessor
    '''
    def deZent_collection_round(self, cnt_struct: CntDataStructure, curr_round_time: datetime) -> None:
        self.record_log.remove_records_older_dt(curr_round_time, self.delta_t)
        
        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_round_time)
        cnt_struct.add_records(self.record_log)

        self.send_collection_to_next(cnt_struct)

    def deZent_publication_round(self, cnt_struct: CntDataStructure, p_pub: int, curr_round_time: datetime) -> tuple[CntDataStructure, int]:
        if cnt_struct.is_empty():
            return cnt_struct, p_pub
        
        # trigger publication process at GW
        cnt_struct = self.publish_anonyimzed_tuples(cnt_struct, p_pub, curr_round_time)

        # if the ID of the upcoming GW equals the coordinating GW ID we have completed the ring
        if self.coord:
            # if cnt_struct is already empty so we have definitely found all potential tuples for publishing we can stop
            if cnt_struct.is_empty():
                return cnt_struct, p_pub

            # if we already completed the second round or had p_pub == 100 before we already published as many tupe as possible
            if p_pub == 100:
                return cnt_struct, p_pub

            # prepare for the second publication round
            p_pub = 100
        # endif curr.gw == coordinator

        return cnt_struct, p_pub

    '''
        publish tuples that have been successfully anonymized with z
        the publication probability can be changed to provide certain deniability and provide more privacy
    '''
    def publish_anonyimzed_tuples(self, cnt_struct: CntDataStructure, p_pub: int, curr_time: datetime) -> CntDataStructure:
        # find records in my local log are in cnt_struct
        # meaning they occurred at more than z individuals
        existing_records: RecordLog = cnt_struct.filter_records_existing(self.record_log)

        print(f"__check__: existing records: {existing_records}")

        # find those entries that have been recorded in current clock cycle
        # and aren't published yet
        recs2pub: PubLog = existing_records.get_current_unpublished_records(curr_time)
        
        #print("__check__: potential current pub records at GW: ", self.id)#, recs2pub)
        #logger.print_pub_log(recs2pub)
        
        # no records for publishing found
        if not recs2pub:
            return cnt_struct

        # key hashes of some of GW's records were found in cnt_struct
        for rec2pub in recs2pub:
            # take publication responsibility with probability p_pub 
            if self.__sample_publish__(p_pub) and cnt_struct.check(rec2pub.key):

                # to publish: forward PubLogEntry to CE with value, timepoint, and sm_id for collection and further processing
                self.publish_record(rec2pub)
                
                # update flag in record_log to indicate that the corresponding tuple has been published (rec2pub == PubLogEntry)
                self.record_log.update_record_published(rec2pub)

                # remove element's hash from cnt_struct
                cnt_struct.remove(rec2pub.key)

                # count structure is empty after publication -> not often the case due to older measurements within dt that are also counted
                if(cnt_struct.is_empty()):
                    break
        return cnt_struct

    def __coord_sample_initial_noise__(self) -> int:
        return random.randint(20,30)

    def __coord_add_initial_noise_to_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        self.coord_noise = self.__coord_sample_initial_noise__()
        cnt_struct.add(self.coord_noise)
        return cnt_struct
    
    def __coord_remove_initial_noise_from_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        cnt_struct.remove(self.coord_noise)
        return cnt_struct

    @staticmethod
    def __sample_publication_probability__(allow_zero: bool = False) -> int:
        return random.randint((0 if allow_zero else 1),100) # allow 0%/1% - 100%
    
    @staticmethod
    def __sample_publish__(p_pub: int) -> bool:
        return random.randint(0,99) < p_pub # 0%: 0 !< 0, 100%: 99 < 100

    def __get_current_time__(self) -> datetime:
        return datetime.now()
