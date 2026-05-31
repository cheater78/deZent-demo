import random
from datetime import datetime, timedelta

from deZent.src.zanon.counting_data_structure.counting_data_structure import CntDataStructure

from deZent.src.ami.gateway import Gateway, GWID
from deZent.src.ami.smart_meter_profile_distribution import SmartMeterProfileDistributionType
from deZent.src.ami.smart_meter_measurement import MeasurementKey, RecordLog, PubLog, PubLogEntry
from deZent.src.ami.gateway_profile import GatewayProfileType
from deZent.src.ami.central_entity import CEID

import zanon_utils as z_utils

class deZentGateway(Gateway):
    
    def __init__(self,
                 ce_id: CEID,
                 gw_id: GWID,
                 peer_prev: GWID,
                 peer_next: GWID,
                 dt_minutes: int,
                 z: int,
                 gw_profile_type: GatewayProfileType = GatewayProfileType.STANDARD,
                 n_sm_conn: int = 0,
                 sm_profile_distribution_type: SmartMeterProfileDistributionType = SmartMeterProfileDistributionType.TK) -> None:
        
        super().__init__(
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
        self.cnt_struct_type: str = "bloom"

    def promote_coord(self) -> None:
        self.coord = True
    
    '''
        coordinating gw prepares and starts collection round
        create cbf and add initial noise for protecting measurement entries
    '''
    def coord_begin_collection_round(self) -> None:
        cnt_struct: CntDataStructure = z_utils.create_cnt_structure(self.n_sm_conn, self.n_cycles_for_anon, self.cnt_struct_type)
        cnt_struct = self.__coord_add_initial_noise_to_cnt_struct__(cnt_struct)
        # TODO: Send cnt_struct to GW+1

    '''
        remove initial noise before preoceeding to data publication
    '''
    def coord_end_collection_round(self, cnt_struct: CntDataStructure) -> None:
        cnt_struct = self.__coord_remove_initial_noise_from_cnt_struct__(cnt_struct)
        cnt_struct.ensure_min_cnt_z(self.z) # TODO: move to GWs -> they schould decide whether their Records appear >z-1 times
        # TODO: Start publication round

    def coord_begin_publication_round(self, cnt_struct: CntDataStructure) -> None:
        p_pub = self.__coord_sample_publication_probability__()
        # TODO: Send cnt_struct to GW+1

    '''
        collection round with count structure passed on from predecessor
    '''
    def deZent_collection_round(self, cnt_struct: CntDataStructure) -> None:
        curr_time: datetime = self.__get_current_time__()
        
        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_time)

        cnt_struct.add_records(self.record_log)
        # TODO: Send cnt_struct to GW+1

##########################
##### PUBLICATION ROUND #####
##########################

    def deZent_publication_round(self, cnt_struct: CntDataStructure, p_pub: int, first_pub_round: bool) -> tuple[CntDataStructure, int]:
        if cnt_struct.is_empty():
            return cnt_struct, p_pub
        
        curr_time: datetime = self.__get_current_time__()
        
        # trigger publication process at GW
        cnt_struct = self.publish_anonyimzed_tuples(cnt_struct, p_pub, curr_time)

        # if the ID of the upcoming GW equals the coordinating GW ID we have completed the ring
        if self.coord:
            # if cnt_struct is already empty so we have definitely found all potential tuples for publishing we can stop
            if cnt_struct.is_empty():
                return cnt_struct, p_pub

            # if we already completed the second round or had p_pub == 100 before we already published as many tupe as possible
            if(not first_pub_round or (p_pub == 100)):
                return cnt_struct, p_pub

            # prepare for the second publication round
            first_pub_round = False
            p_pub = 100
        # endif curr.gw == coordinator

        return cnt_struct, p_pub

    '''
        publish tuples that have been successfully anonymized with z
        the data_origin is either the central entity or a decentralized GW
        the publication probability can be changed to provide certain deniability and provide more privacy
        if the function is called on the central entity p_pub is always 100 
    '''
    def publish_anonyimzed_tuples(self, cnt_struct: CntDataStructure, p_pub: int, curr_time: datetime) -> CntDataStructure:
        l_curr_records: PubLog = self.get_curr_records_for_publishing(cnt_struct, curr_time)

        # key hashes of some of GW's records were found in cnt_struct
        if(l_curr_records):
            for rec2pub in l_curr_records:
                # take publication responsibility with probability p_pub 
                rnd = random.randint(0,100)
                if(rnd <= p_pub):
                    rec_in_cnt_struct = cnt_struct.check(rec2pub.key)
                    if(rec_in_cnt_struct):
                        # to publish: forward PubLogEntry to CE with value, timepoint, and sm_id for collection and further processing
                        data_origin.publish_tuple(rec2pub)
                        

                        # update flag in record_log to indicate that the corresponding tuple has been published (rec2pub == PubLogEntry)
                        data_origin.record_log.update_local_record_log(rec2pub)

                        # remove element's hash from cnt_struct
                        cnt_struct.remove(rec2pub.key) 

                        # count structure is empty after publication -> not often the case due to older measurements within dt that are also counted
                        if(cnt_struct.is_empty()):
                            break
        return cnt_struct



    '''
        get list of PubLogEntry Entries that have been counted more than z times for publishing
            only publish those entries that have been recorded in current clock cycle
    '''
    def get_curr_records_for_publishing(self, cnt_struct: CntDataStructure, curr_time: datetime) -> PubLog:
        # find out which of the records in my local log are in cnt_struct, meaning they occurred at more than z individuals
        existing_records: RecordLog = cnt_struct.existing_records(self.record_log)
        
        print("__check__: existing records: ", existing_records)

        pub_records: PubLog = PubLog()
        # get those entries that are from the current round (timepoint) and could get published
        for m_key, m_dict in existing_records:

            curr_entry = self.get_entries_w_current_timestamp(m_key, curr_time)
            if(curr_entry):
                pub_records.extend(curr_entry)
        #print("__check__: potential current pub records at GW: ", self.id)#, pub_records)
        #logger.print_pub_log(pub_records)
        return pub_records
    
    
    '''
        return PubLogEntries with current timestamp
    '''
    def get_entries_w_current_timestamp(self, m_key: MeasurementKey, curr_time: datetime) -> PubLog:
        curr_records: PubLog = PubLog()
        for sm_id, log_entry in self.record_log.log[m_key].items():
            if( (log_entry.time == curr_time) and (not log_entry.is_published) ):
                new_pub_log = PubLogEntry(m_key, log_entry.orig_measurement, log_entry.time, sm_id, log_entry.sm_type)
                curr_records.append(new_pub_log)
        return curr_records
    

    def __coord_sample_initial_noise__(self) -> int:
        return random.randint(20,30)

    def __coord_add_initial_noise_to_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        self.coord_noise = self.__coord_sample_initial_noise__()
        cnt_struct.add(self.coord_noise)
        return cnt_struct
    
    def __coord_remove_initial_noise_from_cnt_struct__(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        cnt_struct.remove(self.coord_noise)
        return cnt_struct

    def __coord_sample_publication_probability__(self) -> int:
        return random.randint(0,100)

    def __get_current_time__(self) -> datetime:
        return datetime.now()
