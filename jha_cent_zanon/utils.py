import numpy as np
from collections import defaultdict
import subprocess
import sys
import collections
from datetime import datetime, timedelta
import json


def get_cell(self, lat, lon):
    
    nw = self.from_ll_to_mt.transform(47.5, 5.5)
    se = self.from_ll_to_mt.transform(35, 20)
    point = self.from_ll_to_mt.transform(lat, lon)
    distx = point[0] - nw[0]
    disty = nw[1] - point[1]
    cellx = (distx / self.stepsize).astype(int)
    celly = (disty / self.stepsize).astype(int)
    maxx = (np.ceil((se[0] - nw[0]) / self.stepsize)).astype(int)
    cell = celly * maxx + cellx
    return cell.tolist()


def kanon_for_binary(self, z):
    final_dataset = defaultdict(set)
    for i in self.all_tuple:      #coda di tuple(t,u,a,contatori di a)     
        u = i[1]
        a = i[2]
        counters = i[3]
        cat = a.split("*")
        att = None
        for i,c in enumerate(counters):
            if int(c) >= z:
                att = '*'.join(cat[:i + 1]) 
        if att != None:
            final_dataset[u].add(att) 
            
    if len(final_dataset) != 0:  
        final_dataset_inv = defaultdict(list)
        for k,v in final_dataset.items():
            final_dataset_inv[str(v)].append(k)    
        ks = np.array([len(v) for v in final_dataset_inv.values()])
        #print(sum(ks[ks >= 2])/sum(ks))
        return sum(ks[ks >= self.k])/sum(ks)
    else: return 2
                

def binary_search(self, pk, z_start, z_end): 
    if z_start > z_end:
        return -1

    z_mid = (z_start + z_end) // 2 
    r = kanon_for_binary(self, int(z_mid))
    if r >= pk and r <= pk + 0.01:
        return z_mid

    if r > pk:
        return binary_search(self, pk, z_start, z_mid-1)
    else:
        return binary_search(self, pk, z_mid+1, z_end)
    

"""
def z_change(self, t):
    if(t - self.t_start >= self.deltat and t-self.last_update >= self.rate):
        self.last_update = t
        result = binary_search(self, self.pk, 0, 1800)
        '''
        self.kanon.append(result)
        if(result < 0.80):
            self.z += 1
        if(result > 0.81 and self.z > 5):
            self.z -=1
        #print("Value of z: " + str(self.z))
        '''
        with open("output.json", "r") as fi:
            data = json.load(fi)
            if(result != -1):
                self.z = result
            i = 0
            for  detail in self.details:
                #self.all_details[i].append(detail)
                data['all_details'][i].append(detail)
                i += 1
            data['tot_anon'].append(len(self.anonymized))
            data['time'].append(str(datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')))
            data['z'].append(self.z)
            data['kanon'].append(compute_kanon(self))
        with open("output.json", "w") as fi:
            json.dump(data, fi)
"""

def compute_kanon(self):   
    
    final_dataset = defaultdict(set)
    for i in self.queue:
        final_dataset[i[1]].add(i[2])       
    final_dataset_inv = defaultdict(list)
    for k,v in final_dataset.items():
        final_dataset_inv[str(v)].append(k)
    
    ks = np.array([len(v) for v in final_dataset_inv.values()])
    if(sum(ks) != 0):
        return sum(ks[ks >= 2])/sum(ks)
    else: return 1.0
    

def clean_queue(self,t):
    
    if self.all_tuple:
        while True:
            if self.all_tuple:
                temp = self.all_tuple.popleft()          
                if(t - temp[0] <= self.deltat): 
                #if(t - temp[0] < self.deltat): # TODO: fix in deZent implementation
                    self.all_tuple.appendleft(temp)
                    break
            else: break
    
    if self.queue:            
        while True:
            if self.queue:
                temp = self.queue.popleft()     
                detail = len(temp[2].split("*"))
                self.details[detail - 1] -= 1
                if(t - temp[0] <= self.deltat):
                    self.queue.appendleft(temp)
                    self.details[detail - 1] += 1
                    break
            else: break
         
    if self.anonymized:            
        while True:
            if self.anonymized:
                temp = self.anonymized.popleft()
                if(t - temp[0] <= self.deltat): 
                #if(t - temp[0] < self.deltat): # TODO: fix in deZent implementation
                    self.anonymized.appendleft(temp)
                    break
            else: break
    

def read_next_visit(line):
    t, u, a = line.split(',')
    t = float(t)
    a = a.strip()
    return t, u, a
    
def a_not_present(self, t, u, a):
    self.H[a] = collections.OrderedDict()
    self.H[a][u] = t
    self.c[a] = 1
    


def a_present(self, t, u, a):
    if u not in self.H[a]:
        u_not_present(self, t, u, a)
    else:
        u_present(self, t, u, a)

def u_not_present(self, t, u, a):
    self.H[a][u] = t
    self.c[a] += 1

    
def u_present(self, t, u, a):
    self.H[a][u] = t
    self.H[a].move_to_end(u)
    
def evict(self, t, a):
    to_remove = []
    for u,time in self.H[a].items():
        #if (t - self.deltat > time): # TODO: works with deZent implementation
        if (t - time > self.deltat):
            to_remove.append(u)
        else:break
    for u in to_remove:
        self.H[a].pop(u, None)
        self.c[a] -= 1
        if len(self.H[a]) == 0:          
            self.H.pop(a, None)
            break


def manage_data_structure(self, t, u, a):
    sep = '*'
    cat = a.split(sep)
    for level in range(len(cat)):
        i = '*'.join(cat[:level + 1])
        if i not in self.H:
            a_not_present(self, t, u, i)
        else:
            a_present(self, t, u, i)
            

        
def check_and_output(self, t, u, a):
    sep = '*'
    cat = a.split(sep)
    counters = []
    output = None
    for level in range(len(cat)):
        attr = '*'.join(cat[:level + 1])
        counters.append(self.c[attr])
        if self.c[attr] >= self.z: ### TODO: > works with deZent comparison
            output = (t,u,attr) 
            
    if(output != None):
        self.queue.append(output)
        detail = len(output[2].split("*"))
        self.details[detail - 1] += 1
        self.f_out.write("\t".join(str(x) for x in output) + "\n")
    else: self.anonymized.append((t,u,a))
    self.f_count.write("\t".join(str(x) for x in [t,u,a])+ "\t" +
                       "\t".join(str(x) for x in counters) + '\n')
    self.all_tuple.append((t,u,a,counters))
    self.out_tuple.append((t,u,a,counters))
    
