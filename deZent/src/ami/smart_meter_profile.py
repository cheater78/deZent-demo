from __future__ import annotations
import pandas as pd
from datetime import datetime, time
from enum import StrEnum
from abc import ABC
from typing import Any, ClassVar

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
        type: SmartMeterProfileType,
        **kwargs: Any
    ):
        super().__init_subclass__(**kwargs)

        cls._cls_type = type
        SmartMeterProfile._cls_registry[type] = cls

    def __init__(self,
                 consumption_p_a: float,
                 sla_file: str) -> None:
        self.consumption_p_a: float = consumption_p_a
        self.scaling_sla = self.consumption_p_a * comsumption_p_a_scale_factor
        self.sla_file = sla_file

    """
        # define consumption function based on building type that is measured
        # TODO: define SLA functions for each sm type to get measurement based on x (==time)
        # currently, chosen from csv table
    """
    def load_data(self) -> pd.DataFrame:
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

    def scale_to_measurement_value(self, consumption_data: float) -> MeasurementValue:
        return MeasurementValue(consumption_data * self.scaling_sla)


# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class SmartMeterProfileHousehold1P(SmartMeterProfile, type=SmartMeterProfileType.Household1P):
    def __init__(self):
        super().__init__(
            consumption_p_a = 2105,
            sla_file = "SLA_h0_Haushalt.csv"
        )

# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class SmartMeterProfileHousehold2P(SmartMeterProfile, type=SmartMeterProfileType.Household2P):
    def __init__(self):
        super().__init__(
            consumption_p_a = 3470,
            sla_file = "SLA_h0_Haushalt.csv"
        )

# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class SmartMeterProfileHousehold3PAndMore(SmartMeterProfile, type=SmartMeterProfileType.Household3P):
    def __init__(self):
        super().__init__(
            consumption_p_a = 5047,
            sla_file = "SLA_h0_Haushalt.csv"
        )

# https://www.wattline.de/energiewissen/energiekosten-baeckerei/ TODO: project partner??!!
# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileBakery(SmartMeterProfile, type=SmartMeterProfileType.Bakery):
    def __init__(self):
        super().__init__(
            consumption_p_a = 25000, # 50 qm
            sla_file = "SLA_g5_bakery.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileBureauWorkshop(SmartMeterProfile, type=SmartMeterProfileType.Workshop):
    def __init__(self):
        super().__init__(
            consumption_p_a = 6000, # 100 qm
            sla_file = "SLA_g1_bureaus_workshops.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileRestaurant(SmartMeterProfile, type=SmartMeterProfileType.Restaurant):
    def __init__(self):
        super().__init__(
            consumption_p_a = 20000, # 100 qm
            sla_file = "SLA_g2_restaurants.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileStore(SmartMeterProfile, type=SmartMeterProfileType.HairDresser):
    def __init__(self):
        super().__init__(
            consumption_p_a = 17000, # 100 qm
            sla_file = "SLA_g4_store_hairdresser.csv"
        )

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class SmartMeterProfileHairDresser(SmartMeterProfile, type=SmartMeterProfileType.Store):
    def __init__(self):
        super().__init__(
            consumption_p_a = 7500, # 50 qm
            sla_file = "SLA_g4_store_hairdresser.csv"
        )

# TODO: ggf erwartbarer Verbrauch pro Tga und dann ranges fürs runden definieren