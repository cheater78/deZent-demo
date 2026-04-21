from scipy.stats import truncnorm
import numpy as np
import random

from counting_bloom_filter import CBloomFilter

# https://stackoverflow.com/questions/36894191/how-to-get-a-normal-distribution-within-a-range-in-numpy
def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    tn = truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
    return tn


'''
    create count structure (e.g. CBF) for data collection
'''
def create_cnt_structure(n_sm_conn, anon_cycles, struct_type):
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

    return cnt_struct

"""
def create_central_cnt():
    cs = {"value_cnt":[]}
    return cs
"""


'''
    delete measurements from timepoints older than delta_t 
        update local record list to keep only valid data points 
'''
def apply_deltat_to_records(record_log, curr_time, dt):
    t_limit = curr_time - dt # t_limit = datetime <= curr_time = datetime delta_t = time_delta

    l_del_rec = []

    # for each record get log entries
    for record_val in record_log.log.keys():
        l_del_sm = []
        for sm_id, log_entry in record_log.log[record_val].items():
            if(log_entry.time < t_limit):
                l_del_sm.append(sm_id)

        # delete observations of SMs that are too old
        for del_sm in l_del_sm:
            del record_log.log[record_val][del_sm]
            # no entries left for this record value
            if(not record_log.log[record_val]):
                l_del_rec.append(record_val)
                
    for del_rec in l_del_rec:           
        del record_log.log[del_rec]

    return record_log


'''
    to ensure z-anonymity ensure that only entries remain that have occurred at least z times
        for that subtract the constant value z from each count entry in cnt_struct
'''
def ensure_min_cnt_z(cnt_struct, z):
    cnt_struct.subtract_constant((z-1))
    return cnt_struct

def central_ensure_min_cnt_z(cnt_struct, z):
    cnt_struct["tuple_count"] = cnt_struct["tuple_count"] - (z-1)
    valid_cnt_struct = cnt_struct.loc[cnt_struct["tuple_count"] > 0]
    return valid_cnt_struct

'''
    publish tuples that have been successfully anonymized with z
        the data_origin is either the central entity or a decentralized GW
        the publication probability can be changed to provide certain deniability and provide more privacy
        if the function is called on the central entity p_pub is always 100 
'''
def publish_anonyimzed_tuples(data_origin, cnt_struct, p_pub, curr_time):
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


def check_cnt_struct(data_origin, cs, rec):
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

def remove_rec_cnt(cnt_struct, val):
    new_cnt = cnt_struct.loc[cnt_struct["measurement"] == val]["tuple_count"] - 1
    cnt_struct.loc[cnt_struct["measurement"] == val, "tuple_count"] = new_cnt
    return cnt_struct