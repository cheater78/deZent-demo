import pandas as pd

from logging_utils import RecordLog, PubLog, PubLogEntry, SimuLog


class CentralEntity():
    def __init__(self):
        self.clock = 0
        self.id = "CE"

        self.record_log = RecordLog() 
        self.pub_records = PubLog()
        self.simu_log = SimuLog()

    '''
        update central record log with data reported by GW
    '''
    def update_central_record_log(self, gw_record_log, curr_time):
        n_added_m = 0 # FIX
        for m_key in gw_record_log:
            for sm_id, log_entry in gw_record_log[m_key].items():
                if(log_entry.time == curr_time):
                    self.record_log.add_new_m_to_record_log(log_entry.orig_measurement, m_key, sm_id, log_entry.sm_type, log_entry.time )
                    n_added_m = n_added_m + 1 # FIX 
        return n_added_m # FIX
            

    def cnt_curr_values(self):
        # NOTE: only logs that might be counted (== within dt) in record log
        df_record = pd.DataFrame.from_records(
            [
                (m_key, sm_id, l_entry.orig_measurement, l_entry.time, l_entry.is_published)
                for m_key, level2_dict in self.record_log.log.items()
                for sm_id, l_entry in level2_dict.items()
             ],
             columns = ["measurement", "SM", "orig_val", "time", "is_published"])
        # TODO: only measurement bucket and sm_id is needed
        current_cnt_log = df_record.groupby("measurement").size().reset_index().rename(columns={0:'tuple_count'})
        #print(df_cnt.head())
        return current_cnt_log

    '''
        get list of PubLogEntry Entries that have been counted more than z times for publishing
            only publish those entries that have been recorded in current clock cycle
    '''
    def get_curr_records_for_publishing(self, cnt_struct, curr_time):
        # find out which of the records in my local log are in cnt_struct, meaning they occurred at more than z individuals
        # existing_record_keys = cnt_struct.existing_records(self.record_log.log.keys())
        existing_record_keys = [x for x in cnt_struct["measurement"]] #cnt_struct.keys()
        
        l_pub_records = []

        # get those entries that are from the current round (timepoint) and could get published
        for m_key in existing_record_keys:
            curr_entry = self.get_entries_w_current_timestamp(m_key, curr_time)
            if(curr_entry):
                l_pub_records.extend(curr_entry)
        # publish newest tuples first
        l_pub_records.reverse()
        return l_pub_records

    '''
        return PubLogEntry Entry with current timestamp
    '''
    def get_entries_w_current_timestamp(self, m_key, curr_time):
        curr_records = []
        for sm_id, log_entry in self.record_log.log[m_key].items():
            if( (log_entry.time == curr_time) and (not log_entry.is_published) ):
                new_pub_log = PubLogEntry(m_key, log_entry.orig_measurement, log_entry.time, sm_id, log_entry.sm_type)
                curr_records.append(new_pub_log)
        return curr_records
    

    def publish_tuple(self, pub_log):
        self.pub_records.add_new_tuple(pub_log)

    def store_tuple_in_simu_log(self, tuple):
        self.simu_log.add_new_tuple(tuple)


