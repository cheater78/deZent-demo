from __future__ import annotations
from datetime import datetime

from deZent_demo.network.address import NetworkNodeID
from deZent_demo.ami.measurement import MeasurementValue
from deZent_demo.ami.measurement_log import RecordLogEntry
from deZent_demo.ami.smart_meter_profile import SmartMeterProfileType, SmartMeterProfile
from deZent_demo.ami.smart_meter_profile_distribution import SmartMeterProfileDistribution

class SmartMeter():

    @staticmethod
    def create_sample_sm_from_profile_distribution(gw_id: NetworkNodeID, sm_id: NetworkNodeID, profile_dist: SmartMeterProfileDistribution) -> SmartMeter:
        sm_profile_type: SmartMeterProfileType = profile_dist.sample_sm_profile_type()
        return SmartMeter(gw_id, sm_id, sm_profile_type)

    def __init__(
        self,
        gw_id: NetworkNodeID,
        sm_id: NetworkNodeID,
        sm_profile_type: SmartMeterProfileType
    ) -> None:
        self.gw: NetworkNodeID = gw_id
        self.id: NetworkNodeID = sm_id
        self.name: str = str(gw_id) + "-" + str(sm_id)

        self.type: SmartMeterProfileType = sm_profile_type
        self.sm_profile: SmartMeterProfile = SmartMeterProfile.create_sm_profile(sm_profile_type)
        
    
    '''
        get measurement based on current timepoint from the SM profile
        virtually receiving a measurement record from the SM
    '''
    def receive_measurement_data_record(self, curr_time: datetime) -> RecordLogEntry:
        measurement: MeasurementValue = self.sm_profile.acquire_measurement(curr_time)
        record: RecordLogEntry = RecordLogEntry(
            measurement,
            self.sm_profile.get_type(),
            curr_time,
            is_pub = False
        )
        return record
    
    