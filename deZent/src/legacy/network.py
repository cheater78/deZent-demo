import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

from deZent.src.legacy.central_entity import CentralEntity
from deZent.src.legacy.gateway import Gateway
from deZent.src.ami.smart_meter import SmartMeter
from deZent.src.legacy.zanon import zAnon
import zanon_utils as z_utils

class Network():
    def __init__(self,  n_gws):
        self.clock = 0

        # Network Parameters
        self.ce = None
        self.n_gws = n_gws # number of Gws in network
        
        self.l_gws = [] # keep track of all GWs in network
        self.l_free_gw_ids = set(np.arange(0, 3*n_gws)) # list of available IDs for GWs within network

        
    '''
        initialize network: 
            open GWs with random ID
            connect GWs in a ring architecture
            add smart meters to GWs
    '''
    def init_network(self, dist_num_sms, max_n_sms_at_gw):
        print("__init nw__: start init")
        # init CE that collects published data stream
        self.ce = CentralEntity() #CentralEntity(self.env, self.zanon_instance)

        # init GW instances with number of open connections [0, max_n]
        self.open_gws( dist_num_sms, max_n_sms_at_gw)

        # set up connection between GWs to have a complete ring for further communication
        self.create_gw_ring()
        print("__init nw__: created GW ring structure")
        #for gw in self.l_gws:
        #    print("GW no. ", gw.id, " with pred GW: ", gw.gw_pred.id, " and suc GW: ", gw.gw_suc.id)

        # add SM instances to GWs
        self.add_sms_to_gw()
        

    '''
        open Gateways with random ID and add to network
        initialize number of connections for SMs following a predefined distribution with parameter maximum number of SM per GW
    '''
    def open_gws(self,  dist_num_sms, max_n_sms):
        # generate random ID for every GW and initialize GW with it
        for i in range(self.n_gws):
            gw_id = self.get_gw_id()
            n_sms = self.get_n_sm(dist_num_sms, max_n_sms)

            # create GW with specified parameters ID and no. of SM
            gw = Gateway( self.ce, gw_id, n_sms)#Gateway(self.env, self.zanon_instance, self.ce, gw_id, n_sms)
            self.l_gws.append(gw)
            #print("__open gw__: generated GW no. ", i, " with ID: ", gw.id, " and n of open connections: ", gw.n_sm_conn)


    '''
        determine number of SMs at respective GW
            draw this number from a predefined distribution
    '''
    def get_n_sm(self, distribution, max_n_sms):
        n_sm = 0
        if(distribution == "uniform"):
            n_sm = int(np.random.uniform(1,max_n_sms))

        elif(distribution == "normal"):
            tmp_mean = max(1, (max_n_sms/2))
            print(z_utils.get_truncated_normal(mean=(max_n_sms/2), sd=2, low=0, upp=max_n_sms))
            print(z_utils.get_truncated_normal(mean=(max_n_sms/2), sd=2, low=0, upp=max_n_sms).rvs(1)[0])
            n_sm = int(z_utils.get_truncated_normal(mean=(max_n_sms/2), sd=2, low=0, upp=max_n_sms).rvs(1)[0])
            # ensure at least 1 SM per GW
            if(n_sm) < 1:
                n_sm = 1

        #elif(distribution == "poisson"):
        #    n_sm = int(np.random.poisson(1,max_n_sms))

        else:
            raise ValueError("Please choose a valid distribution for generating SMs: [uniform, normal, poisson]")

        return n_sm

                    
    '''
        get random ID for GW
    '''
    def get_gw_id(self):
         # extract random ID
        gw_id = random.sample(list(self.l_free_gw_ids), 1)[0]
        # delete ID from set with available IDs
        self.l_free_gw_ids.remove(gw_id)
        return gw_id 
   

    '''
        connect all GWs in the network in a ring
            determine predecessor and succesor per GW
    '''
    def create_gw_ring(self):

        entry_gw = None

        # find fitting predecessor and succesor for every GW
        for gw in self.l_gws:

            # add first element to ring
            if(entry_gw == None):
                gw.gw_pred = gw
                gw.gw_suc = gw
                entry_gw = gw
                continue
            
            # determine direction of search for neighbouring GW
            if(gw.id > entry_gw.id):
                self.increasing_search(entry_gw, gw)
            else:
                self.decreasing_search(entry_gw, gw)


    '''
        search for insertion point for gw in increasing order ("clockwise")
    '''
    def increasing_search(self, entry_gw, gw):
        # enter ring at entry_gw
        tmp_gw = entry_gw
        while True:
            if( tmp_gw.id >= tmp_gw.gw_suc.id ):  
                # edge case overflow
                gw.gw_pred = tmp_gw
                tmp_suc = tmp_gw.gw_suc
                tmp_gw.gw_suc = gw
                gw.gw_suc = tmp_suc
                gw.gw_suc.gw_pred = gw
                break

            elif( gw.id < tmp_gw.gw_suc.id ):
                # found gw whose succesor is larger than own id
                gw.gw_pred = tmp_gw
                gw.gw_suc = tmp_gw.gw_suc
                gw.gw_suc.gw_pred = gw
                tmp_gw.gw_suc = gw
                break

            # insertion point not found yet -> continue increasing search
            tmp_gw = tmp_gw.gw_suc

    '''
        search for insertion point for gw in decreasing order ("counter clockwise")
    '''
    def decreasing_search(self, entry_gw, gw):
        # enter ring at entry_gw
        tmp_gw = entry_gw
        while True:
            if( tmp_gw.id <= tmp_gw.gw_pred.id ):
                # edge case overflow
                tmp_pred = tmp_gw.gw_pred
                tmp_gw.gw_pred = gw
                gw.gw_pred = tmp_pred
                gw.gw_suc = tmp_gw
                gw.gw_pred.gw_suc = gw
                break
            
            elif( gw.id > tmp_gw.gw_pred.id ):
                # found gw whose preccesor is smaller than own id
                gw.gw_pred = tmp_gw.gw_pred
                gw.gw_suc = tmp_gw
                tmp_gw.gw_pred = gw
                gw.gw_pred.gw_suc = gw
                break

            # insertion point not found yet -> continue decreasing search
            tmp_gw = tmp_gw.gw_pred


    '''
        add smart meters to GWs
    '''      
    def add_sms_to_gw(self):
        for gw in self.l_gws:
            gw.connect_gw_to_sm()


