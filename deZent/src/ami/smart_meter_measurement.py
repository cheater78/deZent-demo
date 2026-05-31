import pandas as pd
from datetime import datetime
from typing import Iterator

from smart_meter_profile import SmartMeterProfileType
from smart_meter import SMID

MeasurementKey=int
MeasurementValue=int

class RecordLogEntry():
    def __init__(self, m: MeasurementValue, sm_type: SmartMeterProfileType, time: datetime, is_pub: bool):
        self.orig_measurement: MeasurementValue = m
        self.sm_type: SmartMeterProfileType = sm_type
        self.time: datetime = time
        self.is_published: bool = is_pub
        
    def __str__(self):
        return ("orig value: " + str(self.orig_measurement) + " time: " + str(self.time) + 
                ", is_published " + str(self.is_published) )

RecordLogDictEntry = dict[SMID, RecordLogEntry]
RecordLogDict = dict[MeasurementKey, RecordLogDictEntry]
class RecordLog():
    def __init__(self):
        self.log: RecordLogDict = {}

    def add_record(self, sm_id: SMID, record: RecordLogEntry) -> None:
        m_key: MeasurementKey = RecordLog.map_measurement_to_key(record.orig_measurement)

        # measurement value has never been seen before -> create dictionary
        if not m_key in self.log.keys():
            self.log[m_key] = {}

        self.log[m_key][sm_id] = record

    def add_records_for_key(self, m_key: MeasurementKey, records: RecordLogDictEntry) -> None:
        if not m_key in self.log.keys():
            self.log[m_key] = {}
        self.log[m_key] |= records

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

    def __iter__(self) -> Iterator[tuple[MeasurementKey, RecordLogDictEntry]]:
        return iter(self.log.items())

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
    

class PubLogEntry():
    def __init__(self, key: MeasurementKey, orig_measurement: MeasurementValue, time: datetime, sm_id: SMID, sm_type: SmartMeterProfileType):
        self.key = key
        self.time = time
        self.id = sm_id
        self.measurement = orig_measurement
        self.sm_type = sm_type

    def __str__(self):
        return ("key: " + str(self.key) + ", value: " + str(self.measurement) + ", timepoint: " 
                + str(self.time) + ", SM: " + str(self.id) + ", type: " + str(self.sm_type) )

class PubLog():
    def __init__(self):
        self.log = pd.DataFrame(columns = ["value", "time", "ID", "orig_measurement", "type"])

    def add_new_tuple(self, pub_tuple: PubLogEntry):
        new_record = pd.DataFrame({"value": [pub_tuple.key], "time": [pub_tuple.time], "ID": [pub_tuple.id], "orig_measurement": [pub_tuple.measurement], "type": [pub_tuple.sm_type]})
        self.log = pd.concat([self.log, new_record], ignore_index = True) # Appending new rows using concat()

