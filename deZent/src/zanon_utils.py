import numpy as np

from deZent.src.zanon.counting_data_structure.counting_data_structure import CntDataStructure
from deZent.src.zanon.counting_data_structure.counting_bloom_filter import CBloomFilter

'''
    create count structure (e.g. CBF) for data collection
'''
def create_cnt_structure(n_sm_conn: int, anon_cycles: int, struct_type: str) -> CntDataStructure:
    match struct_type:
        case "bloom":
            # n: number of expected items -> estimate number of items that occur within delta_t at all the gateways
            # n = no. of items = #(GWs) * #(SM p. GW) * (dt/f)
            # NOTE: this creates a varying n depending on the current round coordinator since n_sm_conn vaires btw GWs
            # This is deliberately accepted in the expectation that collisions with underestimated n 
            #   will balance out over time due to overestimated Bloom filters with other round coordinating GWs
            n = 10 * n_sm_conn * anon_cycles  

            # N: size of each counter in the bucket
            # 2^N occurrences can be counted
            N = 20 #10  

            # m: total number of the buckets in the filter
            # this can be estimated by setting desired false positive rate P
            # m = (-n*ln(P))/(ln(2)^2)
            P = 0.05
            m_est = int( (-n*np.log(P)) / (np.log(2)**2) )
            m = m_est #min(m_est, 1000) # cut max number of buckets # TODO

            # k: number of hash functions
            # K = (m/n) * ln(2)
            k_est = int( (m/n) * np.log(2) )
            k = max(1, k_est)
            k = min(k, 6) # use between 1 and 6 hash functions
            cnt_struct = CBloomFilter(n, N, m, k)
        case _:
            raise RuntimeError(f"CntDataStructure type {struct_type} is not supported!")
    return cnt_struct

def check_cnt_struct(data_origin, cs, rec) -> bool:
    valid_rec = False
    # central cnt_struct at CE
    if(data_origin.id == "CE"):
        curr_cnt = cs.loc[cs["measurement"] == rec.key]["tuple_count"]
        if(curr_cnt.values[0] > 0 ):
            valid_rec = True
    # stochastic cnt_struct at GW
    else:
        valid_rec = cs.check(rec.key)

    return valid_rec

def remove_rec_cnt(cnt_struct: CntDataStructure, val) -> CntDataStructure:
    new_cnt = cnt_struct.loc[cnt_struct["measurement"] == val]["tuple_count"] - 1
    cnt_struct.loc[cnt_struct["measurement"] == val, "tuple_count"] = new_cnt
    return cnt_struct