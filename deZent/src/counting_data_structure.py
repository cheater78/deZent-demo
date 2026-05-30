from __future__ import annotations
from abc import ABC, abstractmethod

from logging_utils import RecordLogType
from deZent.src.ami.smart_meter import MeasurementKey

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

    def add_measurements(self, log: RecordLogType) -> None:
        for m in log.keys():
            n_m = len(log[m])
            # add m multiple times
            for _ in range(n_m):
                self.add(m)

    def existing_records(self, r_list: list[MeasurementKey]) -> list[MeasurementKey]:
        found_records: list[MeasurementKey] = []
        for r in r_list:
            if(self.check(r)):
                found_records.append(r)
        return found_records


    
