import pandas as pd

class RecordLog():
    def __init__(self):
        self.log = {}
        
    def add_new_m_to_record_log(self, curr_measurement, m_key, sm_id, sm_type, t):
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



class RecordLogEntry():
    def __init__(self, m, sm_type, time, is_pub):
        self.orig_measurement = m
        self.sm_type = sm_type
        self.time = time
        self.is_published = is_pub
        
    def __str__(self):
        return ("orig value: " + str(self.orig_measurement) + " time: " + str(self.time) + 
                ", is_published " + str(self.is_published) )


    
class PubLog():
    def __init__(self):
        self.log = pd.DataFrame(columns = ["value", "time", "ID", "orig_measurement", "type"])

    def add_new_tuple(self, pub_tuple):
        new_record = pd.DataFrame({"value": [pub_tuple.key], "time": [pub_tuple.time], "ID": [pub_tuple.id], "orig_measurement": [pub_tuple.measurement], "type": [pub_tuple.sm_type]})
        self.log = pd.concat([self.log, new_record], ignore_index = True) # Appending new rows using concat()

                

class PubLogEntry():
    def __init__(self, key, orig_measurement, time, sm_id, sm_type):
        self.key = key
        self.time = time
        self.id = sm_id
        self.measurement = orig_measurement
        self.sm_type = sm_type

    def __str__(self):
        return ("key: " + str(self.key) + ", value: " + str(self.measurement) + ", timepoint: " 
                + str(self.time) + ", SM: " + str(self.id) + ", type: " + str(self.sm_type) )
    

class SimuLog():
    def __init__(self):
        self.log = pd.DataFrame(columns = ["value", "time", "ID", "orig_measurement", "type"])

    def add_new_tuple(self, t):
        new_record = pd.DataFrame({"value": [t.key], "time": [t.time], "ID": [t.id], "orig_measurement": [t.measurement], "type": [t.sm_type]})
        self.log = pd.concat([self.log, new_record], ignore_index = True)

class SimuLogEntry():
    def __init__(self, key, orig_measurement, time, sm_id, sm_type):
        self.key = key
        self.measurement = orig_measurement
        self.time = time
        self.id = sm_id
        self.sm_type = sm_type
    
    def __str__(self):
        return ("key: " + str(self.key) + ", value: " + str(self.measurement) + ", timepoint: " 
                + str(self.time) + ", SM: " + str(self.id) + ", type: " + str(self.sm_type) )


'''
    print publication log for debugging
'''
def print_pub_log(pub_log_list):
    for log in pub_log_list:
        print("__pub log__: ", log)

