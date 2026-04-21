import random
from numpy.random import choice
import pandas as pd
from datetime import datetime

from profile_distribution import household_1p, household_2p, household_3p_more, bureau_workshop, restaurant, store, hair_dresser, bakery



class SmartMeter():
    def __init__(self,  type_dist, sm_id, gw_id):
        #self.env = env
        self.id = str(gw_id) + "-" + str(sm_id)
        self.gw = gw_id
        self.type = random.choices(type_dist.sm_sampleList, weights=type_dist.sm_dist_weights).pop()
        self.type_class = self.choose_type_class_by_name(self.type)
        self.data = None
        self.load_consumption_data()

    def define_sm_type(self, type_dist):
        self.type = random.choices(type_dist.sm_sampleList, weights=type_dist.sm_dist_weights).pop()
        self.type_class = self.choose_type_class_by_name(self.type)

    def choose_type_class_by_name(self, type):
        type_class = None
        match type:
            case "1p_household":
                type_class = household_1p()
            case "2p_household":
                type_class = household_2p()
            case "3p_household":
                type_class = household_3p_more()
            case "4p_household":
                type_class = household_3p_more()
            case "workshop":
                type_class = bureau_workshop()
            case "bakery":
                type_class = bakery()
            case "restaurant":
                type_class = restaurant()
            case "store":
                type_class = store()
            case "hair_dresser":
                type_class = hair_dresser()

        if (type_class==None):
            raise ValueError
        
        return type_class
    
    """
        # define consumption function based on biulding type that is measured
        # TODO: define SLA functions for each sm type to get measurement based on x (==time)
        # currently, chosen from csv table
    """
    def load_consumption_data(self):
        data_dir = "../../data/consumption_data/"
        self.data = pd.read_csv((data_dir + self.type_class.sla_file), sep = ",", skiprows=[0,1, 2, -1], 
                                names = ["time", "w_5", "w_6", "w_0-4","s_5", "s_6", "s_0-4", "i_5", "i_6", "i_0-4"], index_col=0 )[:-1]
        time_idx = [datetime.strptime(x, "%H:%M").time() for x in self.data.index]
        self.data.set_index(pd.Index(time_idx), inplace=True)


    '''
        get measurement based on current timepoint
            * curr_time = datetime format
    '''
    def measure_data(self, curr_time):
        col_idx = self.choose_col_by_isotimestamp(curr_time)
        t_idx = curr_time.time()

        # get normalized consumption value and scale with building factor
        consumption = self.data.loc[t_idx, col_idx]
        consumption = int(consumption * self.type_class.scaling_sla)

        # add up to 10 percent of measurement as noise
        rnd_noise = random.randint(0, int(consumption/10))
        consumption = consumption + rnd_noise

        key_value = self.map_measurement_to_key(consumption)

        return consumption, key_value
    

    '''
        numerical values are mapped to key values, basically value bins are used for measurement values
    '''
    def map_measurement_to_key(self, m):
        if(m < 0):
            raise ValueError("Only consumption values > 0 allowed")
        group_max = 25
        group_interval = 2
        if(m > group_max):
            group_max = self.find_m_group(m, group_max)

        n_interval_sections = 20
        group_interval = int(group_max/n_interval_sections)
        r = m % group_interval
        if(r < group_interval/2):
            key = m - r
        else:
            key = m + (group_interval-r)
        return key
    

    def find_m_group(self, x, tmp_max):
        while(x > tmp_max):
            tmp_max = tmp_max * 2
        return tmp_max
    

    '''
        map iso timestamp to columns in standard load profiles, e.g. define winter months
    '''
    def choose_col_by_isotimestamp(self, ct):
        # month
        winter_month = [12,1,2]
        summer_month = [6,7,8]
        interim_month = [3,4,5,9,10,11]
        # weekday
        weekend = [5, 6]
        week = [0, 1, 2, 3, 4]

        tmp_m = ""
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
        tmp_d = ""
        if(ct.weekday() in weekend):
            tmp_d = str(ct.weekday())
        elif(ct.weekday() in week):
            tmp_d = "0-4"
        else:
            raise ValueError("Not a valid weekday")

        col_idx = tmp_m + "_" + tmp_d
        return col_idx
        

        