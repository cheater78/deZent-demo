from __future__ import annotations
import random
from enum import StrEnum
from abc import ABC
from typing import Any, ClassVar

from smart_meter_profile import SmartMeterProfileType

class SmartMeterProfileDistributionType(StrEnum):
    TK = "tk"
    BERLIN = "bln"
    GERMANY = "ger"
    NRW = "nrw"


SmartMeterProfileWeightDistribution = dict[SmartMeterProfileType, float]
SmartMeterProfileRatioDistribution = dict[SmartMeterProfileType, float]
class SmartMeterProfileDistribution(ABC):
    _cls_type: ClassVar[SmartMeterProfileDistributionType]
    _cls_registry: ClassVar[dict[SmartMeterProfileDistributionType, type[SmartMeterProfileDistribution]]] = {}

    @staticmethod
    def create_sm_profile_distribution(dist_type: SmartMeterProfileDistributionType) -> SmartMeterProfileDistribution:
        if not dist_type in SmartMeterProfileDistribution._cls_registry.keys():
            raise KeyError(f"SmartMeterProfileDistributionType {dist_type} was not found in registry!")
        # retrieve class type from registry
        cls_by_type: type[SmartMeterProfileDistribution] = SmartMeterProfileDistribution._cls_registry[dist_type]
        # instantiate by derived constructor 
        obj: SmartMeterProfileDistribution = cls_by_type() # type: ignore[call-arg] (pylance assumes SmartMeterProfileDistribution as a valid construction type, which it is not by ABC)
        return obj

    '''
    creation of subclasses, i.e. profile implementaions, register in the SmartMeterProfile class registry,
    this allows for automatic instatiation given their corresponding type as enum
    '''
    def __init_subclass__(
        cls,
        *,
        type: SmartMeterProfileDistributionType,
        **kwargs: Any
    ):
        super().__init_subclass__(**kwargs)

        cls._cls_type = type
        SmartMeterProfileDistribution._cls_registry[type] = cls
    
    def __init__(self) -> None:
        self.profile_weights: SmartMeterProfileWeightDistribution
        self.profile_ratios: SmartMeterProfileRatioDistribution

    def get_profiles(self) -> list[SmartMeterProfileType]:
        return list(self.profile_weights.keys())
    
    def get_weights(self) -> list[float]:
        return list(self.profile_weights.values())
    
    def sample_sm_profile_type(self) -> SmartMeterProfileType:
        return random.choices(self.get_profiles(), weights=self.get_weights()).pop()

    
"""
    smart meter generator will call the profile along with a max number of smart meters (=entities that shall be modeled)
    creates according ratio of profile type
    and accesses data about maximum consumption and corresponding scaling factor (SLAs are normed to 1000 KWh/a)
"""
class ProfileDistribution_tk(SmartMeterProfileDistribution, type=SmartMeterProfileDistributionType.TK):
    def __init__(self):
        super().__init__()

        self.tot_n_entities = 146611 # households + industry + bakery + restaurants + store + hair dresser
        # https://www.berlin.de/ba-treptow-koepenick/ueber-den-bezirk/zahlen-und-fakten/artikel.9422.php
        # Profiles in Treptow-Köpenick (close to average numbers of berlin)
        self.tot_n_households = 144600
        self.ratio_households = self.tot_n_households / self.tot_n_entities
        # TODO: add ratio for households in overall profile
        self.relative_1p_household = 0.479 # 69300
        self.profile_ratios[SmartMeterProfileType.Household1P] = self.relative_1p_household * self.ratio_households

        self.relative_2p_household = 0.304 # 4390
        self.profile_ratios[SmartMeterProfileType.Household2P] = self.relative_2p_household * self.ratio_households

        self.relative_3p_household = 0.127 # 18300
        self.profile_ratios[SmartMeterProfileType.Household3P] = self.relative_3p_household * self.ratio_households

        self.relative_4p_household = 0.091 # 13100
        self.profile_ratios[SmartMeterProfileType.Household4P] = self.relative_4p_household * self.ratio_households

        self.n_farms = 0 # https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Landwirtschaftliche-Betriebe/Tabellen/betriebsgroessenstruktur-landwirtschaftliche-betriebe.html
        
        self.n_industry = 93 # https://www.statistik-berlin-brandenburg.de/verarbeitendes-gewerbe
        self.n_workshops = 481 # https://www.berlin.de/ba-treptow-koepenick/politik-und-verwaltung/service-und-organisationseinheiten/wirtschaftsfoerderung/wirtschaftsstandort/artikel.116737.php
        self.profile_ratios[SmartMeterProfileType.Workshop] = (self.n_industry + self.n_workshops) / self.tot_n_entities

        #total_n_shops = 1141 # p. 27 in https://www.berlin.de/ba-treptow-koepenick/politik-und-verwaltung/aemter/stadtentwicklungsamt/stadtplanung/zentren-und-einzelhandelskonzept-284328.php
        self.n_bakery = 18 # assume even distribution between 12 districts from  https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf
        self.profile_ratios[SmartMeterProfileType.Bakery] = self.n_bakery / self.tot_n_entities

        self.n_restaurants = 750 #  assume even dist btw 12 districts # https://de.statista.com/statistik/daten/studie/412061/umfrage/anzahl-der-gastronomiebetriebe-in-berlin-nach-betriebsart/
        self.profile_ratios[SmartMeterProfileType.Restaurant] = self.n_restaurants / self.tot_n_entities

        self.n_store = 1000 #  assume slightly lower number than in other districts # https://gl.berlin-brandenburg.de/wp-content/uploads/2024-01-15_EH_Endfassung.pdf
        self.profile_ratios[SmartMeterProfileType.Store] = self.n_restaurants / self.tot_n_entities

        self.n_hair_dresser = 150 # assume even distribution between 12 districts from  https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf
        self.profile_ratios[SmartMeterProfileType.HairDresser] = self.n_hair_dresser / self.tot_n_entities

"""
class ProfileDistribution_GER():
    def __init__(self):
        # https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Haushalte-Familien/Tabellen/1-2-privathaushalte-bundeslaender.html
        # Profiles in Nordrhein-Westfalen: all: 41330
        ratio_1p = 41 # 17007
        ratio_2p = 33.5 # 13845
        ratio_3p = 12 # 4937
        ratio_4p = 9.5 # 3943
        ratio_5p = 4 # 1598

        n_farms = 299 # https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Landwirtschaftliche-Betriebe/Tabellen/betriebsgroessenstruktur-landwirtschaftliche-betriebe.html
        n_shops = 1 
        n_bakery = 1
        n_industry = 1
        n_restaurants = 64032 # https://www.dehoga-bundesverband.de/zahlen-fakten/anzahl-der-unternehmen/ https://de.statista.com/statistik/daten/studie/500842/umfrage/anzahl-der-unternehmen-in-der-gastronomie-nach-bundeslaendern/
"""

"""
class ProfileDistribution_NRW():
    def __init__(self):
        # https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Haushalte-Familien/Tabellen/1-2-privathaushalte-bundeslaender.html
        # Profiles in Nordrhein-Westfalen: all: 8717
        ratio_1p = 40 # 3486
        ratio_2p = 34 # 2952
        ratio_3p = 12 # 1039
        ratio_4p = 10 # 860
        ratio_5p = 4 # 379

        n_farms = 33 # https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Landwirtschaftliche-Betriebe/Tabellen/betriebsgroessenstruktur-landwirtschaftliche-betriebe.html
        n_shops = 1 
        n_bakery = 1
        n_industry = 1
"""
"""
class ProfileDistribution_bln():
    def __init__(self):
        # https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Haushalte-Familien/Tabellen/1-2-privathaushalte-bundeslaender.html
        # Profiles in Berlin: all: 2011
        ratio_1p = 50 # 996
        ratio_2p = 29 # 585
        ratio_3p = 10 # 213
        ratio_4p = 8 # 155
        ratio_5p = 3 # 61

        n_farms = 0 # in complete bln
        n_industry = 752 # https://www.statistik-berlin-brandenburg.de/verarbeitendes-gewerbe
        n_workshops = 7167 # https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf


        n_bakery = 210 # bäcker + konditoren  https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf
        n_hair_dresser = 1799 # https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf
        # https://de.statista.com/statistik/daten/studie/1054669/umfrage/unternehmen-im-friseurhandwerk-nach-bundesland-in-deutschland/
        n_store = 19200 # https://gl.berlin-brandenburg.de/wp-content/uploads/2024-01-15_EH_Endfassung.pdf
        n_restaurants = 9050 # https://de.statista.com/statistik/daten/studie/500842/umfrage/anzahl-der-unternehmen-in-der-gastronomie-nach-bundeslaendern/
"""