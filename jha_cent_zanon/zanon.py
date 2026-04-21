from utils import *
#from .utils import *
from evaluate_category import *
from evaluate_output import *
import matplotlib.pyplot as plt
import collections
import json


class zanon(object):

    #def __init__(self, deltat, pk, k, z, fn): 
    def __init__(self, deltat, z, fn_path, fn): 
        super(zanon, self).__init__()
        self.deltat = deltat
        #self.rate = 1800
        self.z = z #0
        self.H = {}
        self.c = {}
        #self.pk = pk
        #self.k = k
        self.t_start = 0
        self.t_stop = 0
        self.last_update = 0
        self.test = []
        self.time = []
        self.kanon = []
        self.queue = collections.deque()
        self.out_tuple = []
        self.all_tuple = collections.deque()
        self.f_out = open((fn_path + 'output_' + fn +'.txt'), 'w+')
        self.f_count = open( (fn_path + 'counters_' + fn + '.txt'), 'w+')
        self.tot_data = []
        self.details = [0]*20
        self.all_details = [[] for i in range(20)]
        self.anonymized  = collections.deque()
        self.tot_anon = []
        self.stepsize = np.array([3000, 5000, 10000, 30000, 500000])
        self.numeric_category = False

	
    def anonymize(self, tupla):
        
        t = float(tupla[0])
        u = tupla[1]  
       
        #if(len(tupla) == 4):
        #    lat = tupla[2]
        #    lon = tupla[3]
        #    a = "*".join(str(x) for x in reversed(get_cell(self,lat,lon)))
        #    self.numeric_category = True
        if(len(tupla)==3):
            a = tupla[2].strip() 
        else: raise ValueError("Arguments can be either 3 or 4, not " + str(len(tupla)))
            
              
        if self.t_start == 0:
            self.t_start = t
            output = {}
            output['all_details']=[[] for i in range(20)]
            output['tot_anon']=[]
            output['time'] = []
            output['z']=[]
            output['kanon']=[]
            with open("output.json","w+") as f:
                json.dump(output,f)
             
        sep = '*'
        cat = a.split(sep)  # cat = consumption in our case
        for level in range(len(cat)):    
            att = '*'.join(cat[:level + 1]) # nothing to join so att is consumption value
            if att in self.H:
                evict(self, t, att)
                  
        clean_queue(self,t)        
        #z_change(self, t)          
        self.t_stop = t                
        manage_data_structure(self, t, u, a)       
        check_and_output(self, t, u, a)
               
    def duration(self):
        print('End of simulation (simulated time: {})'.format(str(timedelta(seconds = int(self.t_stop - self.t_start)))))

    def evaluate_output(self):
        evaluate_output()
        
    def evaluate_category(self,z):
        evaluate_cat(z)
        
    def final_kanon(self):
        final_kanon()

    def plot_z(self):
        plot_z(self)
        
    def endFiles(self):
        self.f_out.close()
        self.f_count.close()
		
