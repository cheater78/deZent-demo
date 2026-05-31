from __future__ import annotations
import random
import pandas as pd
from datetime import datetime, time
from enum import StrEnum
from abc import ABC, abstractmethod
from typing import Any, ClassVar, cast

from smart_meter_measurement import MeasurementValue

profile_data_path: str = "../../data/consumption_data/"
comsumption_p_a_scale_factor: float = (1 / 1000)

class SmartMeterProfileType(StrEnum):
    Household1P = "1p_household"
    Household2P = "2p_household"
    Household3P = "3p_household"
    Household4P = "4p_household"
    Bakery      = "bakery"
    Workshop    = "workshop"
    Restaurant  = "restaurant"
    Store       = "store"
    HairDresser = "hair_dresser"

    @classmethod
    def all_sm_profile_types(cls) -> list[SmartMeterProfileType]:
        return list(cls)
    
    @classmethod
    def all_sm_profile_names(cls) -> list[str]:
        return [ profile.value for profile in cls ]

class SmartMeterProfile(ABC):
    _cls_type: ClassVar[SmartMeterProfileType]
    _cls_registry: ClassVar[dict[SmartMeterProfileType, type[SmartMeterProfile]]] = {}

    @staticmethod
    def create_sm_profile(profile_type: SmartMeterProfileType) -> SmartMeterProfile:
        if not profile_type in SmartMeterProfile._cls_registry.keys():
            raise KeyError(f"SmartMeterProfileType {profile_type} was not found in registry!")
        # retrieve class type from registry
        cls_by_type: type[SmartMeterProfile] = SmartMeterProfile._cls_registry[profile_type]
        # instantiate by derived constructor 
        obj: SmartMeterProfile = cls_by_type() # type: ignore[call-arg] (pylance assumes SmartMeterProfile as a valid construction type, which it is not by ABC)
        return obj

    '''
    creation of subclasses, i.e. profile implementaions, register in the SmartMeterProfile class registry,
    this allows for automatic instatiation given their corresponding type as enum
    '''
    def __init_subclass__(
        cls,
        *,
        type: SmartMeterProfileType | None,
        **kwargs: Any
    ):
        super().__init_subclass__(**kwargs)

        # only final classes are registered
        # meaning type has to be a unique SmartMeterProfileType
        if type:
            cls._cls_type = type
            SmartMeterProfile._cls_registry[type] = cls

    def __init__(self) -> None:
        pass
    
    def get_type(self) -> SmartMeterProfileType:
        return self.__class__._cls_type

    @abstractmethod
    def acquire_measurement(self, curr_time: datetime) -> MeasurementValue:
        pass

class SmartMeterTemplateProfile(SmartMeterProfile, type=None):
    # NOTE: This could be any other base type of SM profiles
    # e.g. serving a continuous data function or even taking real measurements
    # if more of these base types are added, you may consider specifying SmartMeterProfileType with some subdivison into those
    pass

class SmartMeterRecordedDataProfile(SmartMeterProfile, type=None):

    """
        map iso timestamp to columns in standard load profiles, e.g. define winter months
    """
    @staticmethod
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

    def __init__(self,
                 consumption_p_a: float,
                 sla_file: str,
                 measurement_noise: float = 0.1) -> None:
        self.consumption_p_a: float = consumption_p_a
        self.scaling_sla: float = self.consumption_p_a * comsumption_p_a_scale_factor
        self.sla_file: str = sla_file
        self.measurement_noise: float = measurement_noise
        self.data: pd.DataFrame = self.__load_data__()

    def acquire_measurement(self, curr_time: datetime) -> MeasurementValue:
        # get normalized consumption value, scaled by building factor
        consumption: MeasurementValue = self.__query_data__(curr_time)
        
        consumption = self.__apply_measurement_noise__(consumption)

        return consumption

    """
        define consumption function based on building type that is measured
        TODO: define SLA functions for each sm type to get measurement based on x (==time)
        currently, chosen from csv table
        NOTE: somewhat prepared using inheritance -> implement your desired SmartMeter<Template>Profile
    """
    def __load_data__(self) -> pd.DataFrame:
        profile_data_file_path: str = profile_data_path + self.sla_file
        data: pd.DataFrame = \
            pd.read_csv(
                profile_data_file_path,
                sep = ",", skiprows=[0,1, 2, -1], 
                names = ["time", "w_5", "w_6", "w_0-4","s_5", "s_6", "s_0-4", "i_5", "i_6", "i_0-4"],
                index_col=0
            )[:-1]
        time_idx: list[time] = [datetime.strptime(x, "%H:%M").time() for x in data.index]
        data.set_index(pd.Index(time_idx), inplace=True)
        return data
    
    def __query_data__(self, curr_time: datetime) -> MeasurementValue:
        col_idx = self.__choose_col_by_isotimestamp__(curr_time)
        t_idx: time = curr_time.time()
        # get normalized consumption value and scale by building factor
        measurement_data: float = cast(float, self.data.loc[t_idx, col_idx]) # type: ignore (pd.Dataframe structure unknown)
        return MeasurementValue(measurement_data * self.scaling_sla)
    
    def __apply_measurement_noise__(self, measurement: MeasurementValue) -> MeasurementValue:
        rnd_noise = random.randint(0, MeasurementValue(measurement / self.measurement_noise))
        return measurement + rnd_noise

# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class SmartMeterProfileHousehold1P(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.Household1P):
    def __init__(self):
        super().__init__(
            consumption_p_a = 2105,
            sla_file = "SLA_h0_Haushalt.csv"
        )

# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class SmartMeterProfileHousehold2P(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.Household2P):
    def __init__(self):
        super().__init__(
            consumption_p_a = 3470,
            sla_file = "SLA_h0_Haushalt.csv"
        )

# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class SmartMeterProfileHousehold3PAndMore(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.Household3P):
    def __init__(self):
        super().__init__(
            consumption_p_a = 5047,
            sla_file = "SLA_h0_Haushalt.csv"
        )

# https://www.wattline.de/energiewissen/energiekosten-baeckerei/ TODO: project partner??!!
# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileBakery(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.Bakery):
    def __init__(self):
        super().__init__(
            consumption_p_a = 25000, # 50 qm
            sla_file = "SLA_g5_bakery.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileBureauWorkshop(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.Workshop):
    def __init__(self):
        super().__init__(
            consumption_p_a = 6000, # 100 qm
            sla_file = "SLA_g1_bureaus_workshops.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileRestaurant(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.Restaurant):
    def __init__(self):
        super().__init__(
            consumption_p_a = 20000, # 100 qm
            sla_file = "SLA_g2_restaurants.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileStore(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.HairDresser):
    def __init__(self):
        super().__init__(
            consumption_p_a = 17000, # 100 qm
            sla_file = "SLA_g4_store_hairdresser.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileHairDresser(SmartMeterRecordedDataProfile, type=SmartMeterProfileType.Store):
    def __init__(self):
        super().__init__(
            consumption_p_a = 7500, # 50 qm
            sla_file = "SLA_g4_store_hairdresser.csv"
        )

# TODO: ggf erwartbarer Verbrauch pro Tga und dann ranges fürs runden definieren