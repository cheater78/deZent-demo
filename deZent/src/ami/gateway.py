from datetime import datetime

from deZent.src.network.net_node import NetworkNodeID

from deZent.src.ami.smart_meter_measurement import RecordLogEntry, RecordLog, PubLogEntry
from deZent.src.ami.smart_meter import SMID, SmartMeter
from deZent.src.ami.smart_meter_profile_distribution import SmartMeterProfileDistributionType, SmartMeterProfileDistribution
from deZent.src.ami.gateway_profile import GatewayProfileType
from deZent.src.ami.central_entity import CEID

# TODO: possibly move to network, since SMs could be a separate instance
def gw_create_sms(gw_id: GWID, sm_profile_type: SmartMeterProfileDistributionType, n_sm_conn: int) -> dict[SMID, SmartMeter]:
    sm_dict: dict[SMID, SmartMeter] = {}
    sm_profile_distribution = SmartMeterProfileDistribution.create_sm_profile_distribution(sm_profile_type)

    for sm_id in range(n_sm_conn):
        # TODO: make sm_id random UUID - incr. for dev
        sm_dict[sm_id] = SmartMeter.create_sample_sm_from_profile_distribution(gw_id, sm_id, sm_profile_distribution)
    return sm_dict

GWID = NetworkNodeID
class Gateway():

    def __init__(self,
                 ce_id: CEID,
                 gw_id: GWID,
                 gw_profile_type: GatewayProfileType = GatewayProfileType.STANDARD,
                 n_sm_conn: int = 0,
                 sm_profile_distribution_type: SmartMeterProfileDistributionType = SmartMeterProfileDistributionType.TK):
        self.ce_id: CEID = ce_id
        self.gw_id: GWID = gw_id
        self.gw_profile_type: GatewayProfileType = gw_profile_type
        self.record_log = RecordLog()

        # TODO: possibly move to network, since SMs could be a separate instance
        self.n_sm_conn: int = n_sm_conn
        self.sm_profile_type: SmartMeterProfileDistributionType = sm_profile_distribution_type
        self.l_sms: dict[SMID, SmartMeter] = gw_create_sms(gw_id, sm_profile_distribution_type, n_sm_conn)

    '''
        get new measurement for the current time point from sm and add to list
        save values in dictionary for smart meters with measurements and time point
    '''
    def collect_curr_measurement_from_sms(self, curr_time: datetime):
        for sm_id in self.l_sms.keys():
            # get sm instance to request current measurement
            sm: SmartMeter = self.l_sms[sm_id]
            # emulate receiving a measurement record from the sm
            # NOTE: would be a async received and buffered record in the wild, that is now queried and handled
            record: RecordLogEntry = sm.receive_measurement_data_record(curr_time)

            # add measurement to log at GW
            self.record_log.add_record(sm_id, record)

    def publish_record(self, pub_record: PubLogEntry) -> None:
        pass # TODO
    
