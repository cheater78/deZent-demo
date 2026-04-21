from abc import ABC, abstractmethod

# # https://www.bdew.de/energie/standardlastprofile-strom/
# # https://www.bayernwerk-netz.de/de/energie-anschliessen/netznutzung-strom/lastprofilverfahren.html


# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Haushalte-Familien/Tabellen/1-2-privathaushalte-bundeslaender.html
# https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Landwirtschaftliche-Betriebe/Tabellen/betriebsgroessenstruktur-landwirtschaftliche-betriebe.html
# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
# https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf
# https://www.hwk-berlin.de/artikel/handwerk-und-food-91,0,685.html
# https://www.dehoga-bundesverband.de/zahlen-fakten/anzahl-der-unternehmen/



"""
"""
class ProfileDistribution():
    def __init__(self):
        self.sm_sampleList = []
        self.sm_dist_weights = []
    
    def generate_sm_weighted_distribution(self, profile_type, gw_type):
        gw_profile = self.choose_profile_by_name(profile_type)
        self.sm_sampleList, self.sm_dist_weights = gw_profile.get_weighted_distribution(gw_type)

    def choose_profile_by_name(self, type):
        profile = None
        match type:
            case "tk":
                profile = ProfileDistribution_tk()
            case "bln":
                profile = ProfileDistribution_bln()
            # TODO: else: Error
        if (profile==None):
            raise ValueError
        return profile


"""
"""
class ProfileDistribution_mask(ABC):
    # TODO abstractvariable or @abstractmethod: ensure that all have the same attributes
    def __init__(self):
        pass

    def get_weighted_distribution(self, gw_type):
        ' TODO extract relevant parameters'
        match gw_type:
            case "standard":
                # use all entity types
                sample_list = ["1p_household", "2p_household", "3p_household", "4p_household", "workshop", "bakery", "restaurant", "store", "hair_dresser"]
                weighted_list = [self.ratio_1p, self.ratio_2p, self.ratio_3p, self.ratio_4p, self.ratio_workshops, self.ratio_bakery, self.ratio_restaurants, self.ratio_store, self.ratio_hair]
        # TODO: for key in sample_list:
        return sample_list, weighted_list


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
    smart meter generator will call the profile along with a max number of smart meters (=entities that shall be modeled)
    creates according ratio of profile type
    and accesses data about maximum consumption and corresponding scaling factor (SLAs are normed to 1000 KWh/a)
"""
class ProfileDistribution_tk(ProfileDistribution_mask):
    def __init__(self):
        self.tot_n_entities = 146611 # households + industry + bakery + restaurants + store + hair dresser
        # https://www.berlin.de/ba-treptow-koepenick/ueber-den-bezirk/zahlen-und-fakten/artikel.9422.php
        # Profiles in Treptow-Köpenick (close to average numbers of berlin)
        self.tot_n_households = 144600
        self.ratio_households = self.tot_n_households / self.tot_n_entities
        # TODO: add ratio for householöds in overall profile
        self.relative_1p_household = 0.479 # 69300
        self.ratio_1p = self.relative_1p_household * self.ratio_households

        self.relative_2p_household = 0.304 # 4390
        self.ratio_2p = self.relative_2p_household * self.ratio_households

        self.relative_3p_household = 0.127 # 18300
        self.ratio_3p = self.relative_3p_household * self.ratio_households

        self.relative_4p_household = 0.091 # 13100
        self.ratio_4p = self.relative_4p_household * self.ratio_households

        self.n_farms = 0 # https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Landwirtschaftliche-Betriebe/Tabellen/betriebsgroessenstruktur-landwirtschaftliche-betriebe.html
        
        self.n_industry = 93 # https://www.statistik-berlin-brandenburg.de/verarbeitendes-gewerbe
        self.n_workshops = 481 # https://www.berlin.de/ba-treptow-koepenick/politik-und-verwaltung/service-und-organisationseinheiten/wirtschaftsfoerderung/wirtschaftsstandort/artikel.116737.php
        self.ratio_workshops = (self.n_industry + self.n_workshops) / self.tot_n_entities

        #total_n_shops = 1141 # p. 27 in https://www.berlin.de/ba-treptow-koepenick/politik-und-verwaltung/aemter/stadtentwicklungsamt/stadtplanung/zentren-und-einzelhandelskonzept-284328.php
        self.n_bakery = 18 # assume even distribution between 12 districts from  https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf
        self.ratio_bakery = self.n_bakery / self.tot_n_entities

        self.n_restaurants = 750 #  assume even dist btw 12 districts # https://de.statista.com/statistik/daten/studie/412061/umfrage/anzahl-der-gastronomiebetriebe-in-berlin-nach-betriebsart/
        self.ratio_restaurants = self.n_restaurants / self.tot_n_entities

        self.n_store = 1000 #  assume slightly lower number than in other districts # https://gl.berlin-brandenburg.de/wp-content/uploads/2024-01-15_EH_Endfassung.pdf
        self.ratio_store = self.n_restaurants / self.tot_n_entities

        self.n_hair_dresser = 150 # assume even distribution between 12 districts from  https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BBHeft_derivate_00033138/SB_E05-01-00_2021j01_BE.pdf
        self.ratio_hair = self.n_hair_dresser / self.tot_n_entities


# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class household_1p():
    def __init__(self):
        self.consumption_p_a = 2105
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_h0_Haushalt.csv"

# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class household_2p():
    def __init__(self):
        self.consumption_p_a = 3470
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_h0_Haushalt.csv"

# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/private-haushalte/Tabellen/stromverbrauch-haushalte.html
class household_3p_more():
    def __init__(self):
        self.consumption_p_a = 5047
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_h0_Haushalt.csv"

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class bureau_workshop():
    def __init__(self):
        self.consumption_p_a = 6000 # 100 qm
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_g1_bureaus_workshops.csv"

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class restaurant():
    def __init__(self):
        self.consumption_p_a = 20000 # 100 qm
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_g2_restaurants.csv"

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class store():
    def __init__(self):
        self.consumption_p_a = 17000 # 100 qm
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_g4_store_hairdresser.csv"

# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class hair_dresser():
    def __init__(self):
        self.consumption_p_a = 7500 # 50 qm
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_g4_store_hairdresser.csv"

# https://www.wattline.de/energiewissen/energiekosten-baeckerei/ TODO: project partner??!!
# https://www.gasag.de/magazin/energiesparen/stromverbrauch-unternehmen/
class bakery():
    def __init__(self):
        self.consumption_p_a = 25000 # 50 qm
        self.scaling_sla = self.consumption_p_a / 1000
        self.sla_file = "SLA_g5_bakery.csv"

# TODO: ggf erwartbarer Verbrauch pro Tga und dann ranges fürs runden definieren

