from __future__ import annotations
import random
import pandas as pd
from datetime import datetime, time
from typing import cast

from deZent.src.node import NodeID
from deZent.src.ami.smart_meter_measurement import MeasurementKey, MeasurementValue
from deZent.src.ami.smart_meter_profile import SmartMeterProfileType, SmartMeterProfile
from deZent.src.ami.smart_meter_profile_distribution import SmartMeterProfileDistribution
from gateway import GWID

'''
    map iso timestamp to columns in standard load profiles, e.g. define winter months
'''
def __choose_col_by_isotimestamp__(ct: datetime) -> str:
    # month
    winter_month: list[int] = [12,1,2]
    summer_month: list[int] = [6,7,8]
    interim_month: list[int] = [3,4,5,9,10,11]
    # weekday
    weekend: list[int] = [5, 6]
    week: list[int] = [0, 1, 2, 3, 4]

    tmp_m: str = ""
    if(ct.month in winter_month):
        tmp_m = "w"
    elif(ct.month in summer_month):
        tmp_m = "s"
    elif(ct.month in interim_month):
        tmp_m = "i"
    else: 
        raise ValueError("Not a valid month")
    
    if(int(ct.weekday()) != ct.weekday()):
        raise TypeError("Not a valid weekday: only integers allowed")
    if((ct.weekday() < 0) or (ct.weekday() > 6)):
        raise ValueError("Not a valid weekday: only values between 0-6 allowed")
    tmp_d: str = ""
    if(ct.weekday() in weekend):
        tmp_d = str(ct.weekday())
    elif(ct.weekday() in week):
        tmp_d = "0-4"
    else:
        raise ValueError("Not a valid weekday")

    col_idx: str = tmp_m + "_" + tmp_d
    return col_idx

SMID = NodeID # NOTE: SMs could become nodes in the future
class SmartMeter():

    @staticmethod
    def create_sample_sm_from_profile_distribution(gw_id: GWID, sm_id: SMID, profile_dist: SmartMeterProfileDistribution) -> SmartMeter:
        sm_profile_type: SmartMeterProfileType = profile_dist.sample_sm_profile_type()
        return SmartMeter(gw_id, sm_id, sm_profile_type)

    def __init__(self,
                 gw_id: GWID,
                 sm_id: SMID,
                 sm_profile_type: SmartMeterProfileType):
        self.gw: GWID = gw_id
        self.id: SMID = sm_id
        self.name: str = str(gw_id) + "-" + str(sm_id)

        self.type: SmartMeterProfileType = sm_profile_type
        self.sm_profile: SmartMeterProfile = SmartMeterProfile.create_sm_profile(sm_profile_type)
        self.data: pd.DataFrame = self.sm_profile.load_data()
    
    '''
        get measurement based on current timepoint
            * curr_time = datetime format
    '''
    # TODO: maybe move contents and data to profile, since csv data and pd.Dataframe is part of that system
    def measure_data(self, curr_time: datetime) -> MeasurementValue:
        col_idx = __choose_col_by_isotimestamp__(curr_time)
        t_idx: time = curr_time.time()

        # get normalized consumption value and scale with building factor
        consumption_data: float = cast(float, self.data.loc[t_idx, col_idx]) # type: ignore (pd.Dataframe structure unknown to pylance)
        consumption: MeasurementValue = self.sm_profile.scale_to_measurement_value(consumption_data)
        
        # add up to 10 percent of measurement as noise
        rnd_noise = random.randint(0, MeasurementValue(consumption/10))
        consumption = consumption + rnd_noise

        return consumption
    
    