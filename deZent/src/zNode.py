import random
import datetime
from counting_data_structure import CntDataStructure
from node import NodeID
from deZent.src.legacy.gateway import Gateway
import zanon_utils as z_utils

class deZentGateway(Gateway):
    
    def __init__(self,
                 ce: NodeID,
                 peer_prev: NodeID,
                 peer_next: NodeID,
                 dt_minutes: int,
                 z: int) -> None:
        

        self.coord: bool = False
        self.coord_noise: int = 0

        self.delta_t: datetime.timedelta = datetime.timedelta(minutes=dt_minutes) # timedelta 
        self.z: int = z
        self.measurement_frequency = datetime.timedelta(minutes=15)
        self.n_cycles_for_anon: int = int(max(1, self.delta_t.seconds/self.measurement_frequency.seconds))
        self.cnt_struct_type: str = "bloom"

    def promote_coord(self) -> None:
        self.coord = True
    
    def coord_begin_collection_round(self) -> None:
        cnt_struct: CntDataStructure = z_utils.create_cnt_structure(self.gw.n_sm_conn, self.n_cycles_for_anon, self.cnt_struct_type)
        cnt_struct = self.__coord_add_initial_noise_to_cnt_struct__(cnt_struct)
        # TODO: Send cnt_struct to GW+1

    def coord_end_collection_round(self, cnt_struct: CntDataStructure) -> None:
        cnt_struct = self.__coord_remove_initial_noise_from_cnt_struct__(cnt_struct)
        cnt_struct.ensure_min_cnt_z(self.z)
        # TODO: Start publication round

    def coord_begin_publication_round(self, cnt_struct: CntDataStructure) -> None:
        p_pub = self.__coord_sample_publication_probability__()
        # TODO: Send cnt_struct to GW+1

    def deZent_collection_round(self, cnt_struct: CntDataStructure) -> None:
        curr_time: datetime.time = self.__get_current_time__()
        cnt_struct = self.gw.add_curr_measurement(cnt_struct, curr_time)
        # TODO: Send cnt_struct to GW+1

    def deZent_publication_round(self, cnt_struct: CntDataStructure, p_pub: int, first_pub_round: bool) -> tuple[CntDataStructure, int]:
        if cnt_struct.is_empty():
            return cnt_struct, p_pub
        
        curr_time: datetime.time = self.__get_current_time__()
        
        # trigger publication process at GW
        cnt_struct = z_utils.publish_anonyimzed_tuples(self.gw, cnt_struct, p_pub, curr_time)

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
    def publish_anonyimzed_tuples(data_origin, cnt_struct: CntDataStructure, p_pub: int, curr_time: datetime.datetime) -> CntDataStructure:
        l_curr_records = []
        l_curr_records = data_origin.get_curr_records_for_publishing(cnt_struct, curr_time)

        # key hashes of some of GW's records were found in cnt_struct
        if(l_curr_records):
            for rec2pub in l_curr_records:
                # take publication responsibility with probability p_pub 
                rnd = random.randint(0,100)
                if(rnd <= p_pub):
                    rec_in_cnt_struct = check_cnt_struct(data_origin, cnt_struct, rec2pub)
                    if(rec_in_cnt_struct):
                        # to publish: forward PubLogEntry to CE with value, timepoint, and sm_id for collection and further processing
                        data_origin.publish_tuple(rec2pub)
                        

                        # update flag in record_log to indicate that the corresponding tuple has been published (rec2pub == PubLogEntry)
                        data_origin.record_log.update_local_record_log(rec2pub)

                        # central cnt_struct at CE
                        if(data_origin.id == "CE"):
                            cnt_struct = remove_rec_cnt(cnt_struct, rec2pub.key) 
                        
                        # stochastic cnt_struct at GW
                        else:
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

    def __coord_sample_publication_probability__(self) -> int:
        return random.randint(0,100)

    def __get_current_time__(self) -> datetime.time:
        return datetime.datetime.now().time()
