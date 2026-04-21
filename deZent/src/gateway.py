import random

from logging_utils import RecordLog, PubLogEntry, SimuLogEntry

#from counting_bloom_filter import CBloomFilter
from smartmeter import SmartMeter
from profile_distribution import ProfileDistribution



class Gateway():
    def __init__(self, ce, id=None,n_sm_conn=0):
        self.ce = ce

        self.id = id
        self.gw_pred = None
        self.gw_suc = None
        
        self.n_sm_conn = n_sm_conn
        self.gw_type = "standard" # mieter # industry
        self.profile_type = "tk" # "berlin", "ger"

        self.l_sms = {} # TODO: remember sm id and instance
        self.record_log = RecordLog()

        self.coord_noise = 0
        self.gw_ce_msg_cnt = 0

##########################
##### SETUP #####
##########################
    '''
        connect GW with smart meters
            for now this is done for all connections that are available
    '''
    def connect_gw_to_sm(self):
        sm_distribution = ProfileDistribution()
        sm_distribution.generate_sm_weighted_distribution(self.profile_type, self.gw_type)

        for conn in range(self.n_sm_conn):
            sm = SmartMeter( sm_distribution, sm_id=conn, gw_id=self.id)#SmartMeter(self.env, sm_distribution, sm_id=conn, gw_id=self.id)
            if sm.id not in self.l_sms.keys():
                self.l_sms[sm.id] = sm # list with sms connected to GW


##########################
##### COLLECTION ROUND #####
##########################
    '''
        coordinating gw prepares and starts collection round
            create cbf and add initial noise for protecting measurement entries
    '''
    def add_initial_noise_to_cnt_struct(self, cnt_struct):
        self.coord_noise = random.randint(20,30)
        cnt_struct.add(self.coord_noise)
        return cnt_struct
    
    
    '''
        remove initial noise before preoceeding to data publication
    '''
    def remove_initial_noise_from_cnt_struct(self, cnt_struct):
        cnt_struct.remove(self.coord_noise)
        return cnt_struct


    '''
        collection round with count structure passed on from predecessor
    '''
    def add_curr_measurement(self, cnt_struct, curr_time):
        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_time)

        # add valid measurements (wihtin delta t) of all SMs connected to this GW to count structure
        cnt_struct.add_measurements(self.record_log.log)
        return cnt_struct


    '''
        get new measurement for the current time point from sm and add to list
            save values in dictionary for smart meters with measurements and time point
    '''
    def collect_curr_measurement_from_sms(self, curr_time):

        for sm_id in self.l_sms.keys():
            # get sm instance to request current measurement
            sm = self.l_sms[sm_id]
            curr_measurement, m_key = sm.measure_data(curr_time)

            # add measurement to log at GW
            self.record_log.add_new_m_to_record_log(curr_measurement, m_key, sm_id, sm.type, curr_time)

            # record all occurred tuple for simulation analysis
            #   NOTE: this would not be done for "real" z-anonymity
            log_tuple = SimuLogEntry(m_key, curr_measurement, curr_time, sm_id, sm.type)
            self.ce.store_tuple_in_simu_log(log_tuple)


##########################
##### PUBLICATION ROUND #####
##########################

    '''
        get list of PubLogEntry Entries that have been counted more than z times for publishing
            only publish those entries that have been recorded in current clock cycle
    '''
    def get_curr_records_for_publishing(self, cnt_struct, curr_time):
        # find out which of the records in my local log are in cnt_struc t, meaning they occurred at more than z individuals
        existing_record_keys = cnt_struct.existing_records(self.record_log.log.keys())
        pub_records = []
        #print("__check__: existing records: ", existing_record_keys)
        # get those entries that are from the current round (timepoint) and could get published
        for m_key in existing_record_keys:
            curr_entry = self.get_entries_w_current_timestamp(m_key, curr_time)
            if(curr_entry):
                pub_records.extend(curr_entry)
        #print("__check__: potential current pub records at GW: ", self.id)#, pub_records)
        #logger.print_pub_log(pub_records)
        return pub_records
    
    
    '''
        return PubLogEntries with current timestamp
    '''
    def get_entries_w_current_timestamp(self, m_key, curr_time):
        curr_records = []
        for sm_id, log_entry in self.record_log.log[m_key].items():
            if( (log_entry.time == curr_time) and (not log_entry.is_published) ):
                new_pub_log = PubLogEntry(m_key, log_entry.orig_measurement, log_entry.time, sm_id, log_entry.sm_type)
                curr_records.append(new_pub_log)
        return curr_records
    
    
    
    def publish_tuple(self, tuple):
        self.ce.publish_tuple(tuple)
        self.gw_ce_msg_cnt += 1



    def get_gw_ce_msg_cnt(self):
        tmp_cnt = self.gw_ce_msg_cnt
        self.gw_ce_msg_cnt = 0
        return tmp_cnt
    
