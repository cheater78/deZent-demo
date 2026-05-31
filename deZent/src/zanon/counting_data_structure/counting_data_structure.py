from __future__ import annotations
from abc import ABC, abstractmethod

from deZent.src.ami.smart_meter_measurement import MeasurementKey, RecordLog

# abstract class to force sub classes to implement methods
class CntDataStructure(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def add(self, item: MeasurementKey) -> None:
        pass

    @abstractmethod
    def check(self, item: MeasurementKey) -> bool:
        pass

    @abstractmethod
    def remove(self, item: MeasurementKey) -> None:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass
    
    @abstractmethod
    def subtract_constant(self, z_min: int) -> None:
        pass

    @abstractmethod
    def print_cnt_struct(self) -> None:
        pass
    
    '''
        to ensure z-anonymity ensure that only entries remain that have occurred at least z times
        for that subtract the constant value z from each count entry in cnt_struct
    '''
    def ensure_min_cnt_z(self, z: int) -> None:
        self.subtract_constant(z-1)

    def add_records(self, log: RecordLog) -> None:
        for m_key, m_dict in log:
            n_m = len(m_dict)
            # add m multiple times
            for _ in range(n_m):
                self.add(m_key)

    def existing_records(self, log: RecordLog) -> RecordLog:
        found_records: RecordLog = RecordLog()
        for m_key, records in log:
            if(self.check(m_key)):
                found_records.add_records_for_key(m_key, records)
        return found_records


    
