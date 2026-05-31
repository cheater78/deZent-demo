from deZent.src.ami.smart_meter_measurement import MeasurementKey
from deZent.src.zanon.counting_data_structure.counting_data_structure import CntDataStructure

# TODO: not implemented
class CDict(CntDataStructure):
    
    def __init__(self):
        raise RuntimeError(f"Class {self.__class__.__name__} is not implemented!")

    def add(self, item: MeasurementKey):
        pass

    def check(self, item: MeasurementKey) -> bool:
        return False

    def remove(self, item: MeasurementKey) -> None:
        pass

    def is_empty(self) -> bool:
        return False
    
    def print_cnt_struct(self) -> None:
        pass

