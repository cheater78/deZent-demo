import pandas as pd
from datetime import datetime, timedelta
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
        m_key: MeasurementKey = RecordLog.__map_measurement_to_key__(record.orig_measurement)

        # measurement value has never been seen before -> create dictionary
        if not m_key in self.log.keys():
            self.log[m_key] = {}

        self.log[m_key][sm_id] = record

    def add_records_for_key(self, m_key: MeasurementKey, records: RecordLogDictEntry) -> None:
        if not m_key in self.log.keys():
            self.log[m_key] = {}
        self.log[m_key] |= records

    def remove_records_older_dt(self, curr_time: datetime, dt: timedelta) -> None:
        t_limit: datetime = curr_time - dt

        l_del_rec: list[MeasurementKey] = []
        for m_key, m_dict in self:
            l_del_sm: list[SMID] = []
            for sm_id, record in m_dict.items():
                if(record.time < t_limit):
                    l_del_sm.append(sm_id)

            # delete observations of SMs that are too old
            for del_sm in l_del_sm:
                del m_dict[del_sm]
                # no entries left for this record value
                if not m_dict:
                    l_del_rec.append(m_key)
                    
        for del_rec in l_del_rec:           
            del self.log[del_rec]

    def get_current_unpublished_records(self, curr_time: datetime) -> PubLog:
        curr_recs2pub: PubLog = PubLog()
        for m_key, m_dict in self: # self.log.items(), but we have __iter__ alr
            for sm_id, record in m_dict.items():
                if record.time == curr_time and not record.is_published:
                    pub_record = PubLogEntry(m_key, record.orig_measurement, record.time, sm_id, record.sm_type)
                    curr_recs2pub.add_record(pub_record)
        return curr_recs2pub

    '''
        update record that has been published and set flag to avoid publishing multiple times
    '''
    def update_record_published(self, pub_record: PubLogEntry) -> None:
        self.log[pub_record.key][pub_record.id] = RecordLogEntry(pub_record.measurement, pub_record.sm_type, pub_record.time, is_pub = True)

    def __bool__(self) -> bool:
        return bool(self.log) # defined by "not empty"

    def __iter__(self) -> Iterator[tuple[MeasurementKey, RecordLogDictEntry]]:
        return iter(self.log.items())

    def __str__(self) -> str:
        debug_str: str = ""
        for key, m_dict in self:
            for sm_id, record in m_dict.items():
                if debug_str:
                    debug_str += "\n"
                debug_str +=  f"__record_log__: measurement_key: {key}, SM: {sm_id}, {record}"
        return debug_str

    '''
        numerical values are mapped to key values, basically value bins are used for measurement values
    '''
    @staticmethod
    def __map_measurement_to_key__(m: MeasurementValue) -> MeasurementKey:
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

    def add_record(self, pub_tuple: PubLogEntry):
        new_record = pd.DataFrame({"value": [pub_tuple.key], "time": [pub_tuple.time], "ID": [pub_tuple.id], "orig_measurement": [pub_tuple.measurement], "type": [pub_tuple.sm_type]})
        self.log = pd.concat([self.log, new_record], ignore_index = True) # Appending new rows using concat()

    def extend(self, pub_log: PubLog) -> None:
        self.log = pd.concat([self.log, pub_log.log], ignore_index = True)

    def __bool__(self) -> bool:
        return not self.log.empty

    def __iter__(self) -> Iterator[PubLogEntry]:
        # NOTE: DataFrame / .csv has to have the exact same attribute order as PubLogEntry, 
        # if not construct with explicit assignment!
        return (PubLogEntry(*row) for row in self.log.itertuples(index=False, name=None))
    
    def __str__(self) -> str:
        debug_str: str = ""
        for pub_record in self:
            if debug_str:
                debug_str += "\n"
            debug_str +=  f"__pub_log__: {pub_record}"
        return debug_str

