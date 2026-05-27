import random
import datetime
from counting_data_structure import CntDataStructure
from gateway import Gateway
import zanon_utils as z_utils

class zAnonNode:
    
    def __init__(self, gw: Gateway, dt_minutes: int, z: int) -> None:
        self.gw: Gateway = gw
        self.coord: bool = False

        self.delta_t: datetime.timedelta = datetime.timedelta(minutes=dt_minutes) # timedelta 
        self.z: int = z
        self.measurement_frequency = datetime.timedelta(minutes=15)
        self.n_cycles_for_anon: int = int(max(1, self.delta_t.seconds/self.measurement_frequency.seconds))
        self.cnt_struct_type: str = "bloom"

        self.msg_cnt_gwgw: int = 0
        self.msg_cnt_gw_ce: int = 0

    def promote_coord(self) -> None:
        self.coord = True
    
    def coord_create_cnt_struct(self) -> CntDataStructure:
        cnt_struct: CntDataStructure = z_utils.create_cnt_structure(self.gw.n_sm_conn, self.n_cycles_for_anon, self.cnt_struct_type)
        cnt_struct = self.gw.add_initial_noise_to_cnt_struct(cnt_struct)
        return cnt_struct

    def coord_end_collection_start_publication(self, cnt_struct: CntDataStructure) -> tuple[CntDataStructure, int]:
        cnt_struct = self.gw.remove_initial_noise_from_cnt_struct(cnt_struct)
        cnt_struct = z_utils.ensure_min_cnt_z(cnt_struct, self.z)

        p_pub = random.randint(0, 100)
        return cnt_struct, p_pub

    def collect(self, cnt_struct: CntDataStructure) -> CntDataStructure:
        curr_time: datetime.datetime = self.__get_current_time__()
        cnt_struct = self.gw.add_curr_measurement(cnt_struct, curr_time)
        return cnt_struct


    def deZent_publication_round(self, cnt_struct: CntDataStructure, p_pub: int, first_pub_round: bool) -> tuple[CntDataStructure, int]:
        if cnt_struct.is_empty():
            return cnt_struct, p_pub
        
        curr_time: datetime.datetime = self.__get_current_time__()
        
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


    def __get_current_time__(self) -> datetime.datetime:
        return datetime.datetime.now()
