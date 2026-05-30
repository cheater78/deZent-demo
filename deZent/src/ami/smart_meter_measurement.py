from datetime import datetime
from smart_meter import SMID, SmartMeterProfileType

MeasurementKey=int
MeasurementValue=int

RecordLogDict = dict[MeasurementKey, dict[SMID, "RecordLogEntry"]]
class RecordLog():
    def __init__(self):
        self.log: RecordLogDict = {}

    def add_measurement(self, sm_id: SMID, sm_type: SmartMeterProfileType, t: datetime, m: MeasurementValue) -> MeasurementKey:
        key: MeasurementKey = RecordLog.map_measurement_to_key(m)
        self.add_new_m_to_record_log(sm_id, sm_type, t, key, m)
        return key
    
    # TODO: explicitly needed like this?
    def add_new_m_to_record_log(self, sm_id: SMID, sm_type: SmartMeterProfileType, t: datetime, m_key: MeasurementKey, curr_measurement: MeasurementValue):
        # new measurement -> cannot have been published yet
        is_published = False
        # measurement value was already observed at some SM before -> either add (sm: t) newly or update t for this observation at this SM
        if(m_key in self.log):
            self.log[m_key][sm_id] = RecordLogEntry(curr_measurement, sm_type, t, is_published)

        # measurement value has never been seen before -> add to dictionary
        else:
            self.log[m_key] = {sm_id: RecordLogEntry(curr_measurement, sm_type, t, is_published)}
        return self.log

    '''
        update record that has been published and set flag to avoid publishing multiple times
            pub_tuple == PubLogEntry
    '''
    def update_local_record_log(self, pub_tuple):
        is_published = True
        self.log[pub_tuple.key][pub_tuple.id] = RecordLogEntry(pub_tuple.measurement, pub_tuple.sm_type, pub_tuple.time, is_published)
        return self.log
    
    '''
        print record log for debugging
    '''
    def print_record_log(self):
        for i in self.log.keys():
            for sm, log_entry in self.log[i].items():
                print("__record log__: measurement_key: ", i, ", SM: ", sm, log_entry)

    '''
        numerical values are mapped to key values, basically value bins are used for measurement values
    '''
    # TODO: possibly private? - MeasurementValue does alr uniquely id the key
    @staticmethod
    def map_measurement_to_key(m: MeasurementValue) -> MeasurementKey:
        group_base: int = 25 # buckets in group_base*2^ceil_ld(m/group_base)
        n_buckets: int = 20

        if(m < 0):
            raise ValueError("Only consumption values > 0 allowed")
        group_max: int = RecordLog.__find_m_group__(m, group_base)

        group_interval = int(group_max / n_buckets)
        r = m % group_interval
        if(r < group_interval/2):
            key: MeasurementKey = m - r
        else:
            key: MeasurementKey = m + (group_interval-r)
        return key
    
    @staticmethod
    def __find_m_group__(m: int, tmp_max: int):
        # while(m > tmp_max):
        #     tmp_max *= 2
        # return tmp_max

        # faster upper pow2 with bit shift
        if m <= tmp_max:
            return tmp_max
        return tmp_max << ((m - 1) // tmp_max).bit_length()

class RecordLogEntry():
    def __init__(self, m: MeasurementValue, sm_type: str, time: datetime, is_pub: bool):
        self.orig_measurement: MeasurementValue = m
        self.sm_type: str = sm_type
        self.time: datetime = time
        self.is_published: bool = is_pub
        
    def __str__(self):
        return ("orig value: " + str(self.orig_measurement) + " time: " + str(self.time) + 
                ", is_published " + str(self.is_published) )