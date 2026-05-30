from datetime import datetime
from deZent.src.ami.smart_meter_measurement import RecordLog

from deZent.src.node import NodeID
from counting_data_structure import CntDataStructure

from deZent.src.ami.smart_meter import SMID, SmartMeter, MeasurementKey
from deZent.src.ami.smart_meter_profile_distribution import SmartMeterProfileDistributionType, SmartMeterProfileDistribution
from deZent.src.ami.gateway_profile import GatewayProfileType
from deZent.src.ami.central_entity import CEID

# TODO: possibly move to network, since SMs could be a separate instance
def gw_create_sms(gw_id: GWID, sm_profile_type: SmartMeterProfileDistributionType, n_sm_conn: int) -> dict[SMID, SmartMeter]:
    sm_dict: dict[SMID, SmartMeter] = {}
    sm_profile_distribution = SmartMeterProfileDistribution.create_sm_profile_distribution(sm_profile_type)

    for sm_id in range(n_sm_conn):
        sm_dict[sm_id] = SmartMeter.create_sample_sm_from_profile_distribution(gw_id, sm_id, sm_profile_distribution)
    return sm_dict

GWID = NodeID
class Gateway():

    def __init__(self,
                 ce: CEID,
                 gw_id: GWID,
                 gw_profile_type: GatewayProfileType = GatewayProfileType.STANDARD,
                 n_sm_conn: int = 0,
                 sm_profile_distribution_type: SmartMeterProfileDistributionType = SmartMeterProfileDistributionType.TK):
        self.ce: CEID = ce
        self.gw_profile_type: GatewayProfileType = gw_profile_type
        self.record_log = RecordLog()

        # TODO: possibly move to network, since SMs could be a separate instance
        self.n_sm_conn: int = n_sm_conn
        self.sm_profile_type: SmartMeterProfileDistributionType = sm_profile_distribution_type
        self.l_sms: dict[SMID, SmartMeter] = gw_create_sms(gw_id, sm_profile_distribution_type, n_sm_conn)

##########################
##### COLLECTION ROUND #####
##########################
    
    '''
        when coordinating gw prepares and starts collection round
        create cbf and add initial noise for protecting measurement entries
    '''

    '''
        remove initial noise before preoceeding to data publication
    '''

    '''
        collection round with count structure passed on from predecessor
    '''
    def add_curr_measurement(self, cnt_struct: CntDataStructure, curr_time: datetime) -> CntDataStructure:
        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_time)

        # add valid measurements (wihtin delta t) of all SMs connected to this GW to count structure
        cnt_struct.add_measurements(self.record_log.log)
        return cnt_struct

    '''
        get new measurement for the current time point from sm and add to list
            save values in dictionary for smart meters with measurements and time point
    '''
    def collect_curr_measurement_from_sms(self, curr_time: datetime):
        for sm_id in self.l_sms.keys():
            # get sm instance to request current measurement
            sm = self.l_sms[sm_id]
            curr_measurement = sm.measure_data(curr_time)

            # add measurement to log at GW
            self.record_log.add_measurement(sm_id, sm.type, curr_time, curr_measurement)


##########################
##### PUBLICATION ROUND #####
##########################

    '''
        get list of PubLogEntry Entries that have been counted more than z times for publishing
            only publish those entries that have been recorded in current clock cycle
    '''
    def get_curr_records_for_publishing(self, cnt_struct: CntDataStructure, curr_time: datetime) -> list[PubLogEntry]:
        # find out which of the records in my local log are in cnt_struc t, meaning they occurred at more than z individuals
        existing_record_keys = cnt_struct.existing_records(list(self.record_log.log.keys()))
        pub_records: list[PubLogEntry] = []
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
    def get_entries_w_current_timestamp(self, m_key: MeasurementKey, curr_time: datetime.time) -> list[PubLogEntry]:
        curr_records: list[PubLogEntry] = []
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
    
