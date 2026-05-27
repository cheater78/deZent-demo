from counting_data_structure import CntDataStructure, MeasurementKey

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

