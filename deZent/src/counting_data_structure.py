from abc import ABC, abstractmethod

from logging_utils import RecordLogType
from smartmeter import MeasurementKey

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


    
