from abc import ABC, abstractmethod

class CntDataStructure(ABC):
    #def __init__(self, n):
    #    self.n = n  # no of items to add # TODO: estimate number of items that occur within delta_t at all the gateways


    # abstract class to force sub classes to implement methods
    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def check(self, item):
        pass

    @abstractmethod
    def remove(self, item):
        pass

    @abstractmethod
    def is_empty(self):
        pass


    def add_measurements(self, log):
        for m in log.keys():
            n_m = len(log[m])
            # add m multiple times
            for i in range(n_m):
                self.add(m)


    def existing_records(self, r_list):
        found_records = []
        for r in r_list:
            if(self.check(r)):
                found_records.append(r)
        return found_records
    
    '''
        print counting structure at GW for debugging
    '''
    def print_cnt_struct(self):
        line_cnt = 0
        bit_str = ''
        for b in self.bit_array:
            bit_str = bit_str + b.to01() + ' '
            line_cnt += 1
            if(line_cnt == 4):
                line_cnt = 0
                print(bit_str)
                bit_str = ''
        print(bit_str)

    



    
