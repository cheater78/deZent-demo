import random
import datetime
import zanon_utils as z_utils
import deZent.src.legacy.logging_utils as logging_utils

class zAnon():
    def __init__(self, env, dt_minutes, z):
        self.env = env
        self.delta_t = datetime.timedelta(minutes=dt_minutes) # timedelta 
        self.z = z
        self.clock = None
        self.measurement_frequency = datetime.timedelta(minutes=15)
        self.n_cycles_for_anon = max(1, self.delta_t.seconds/self.measurement_frequency.seconds)
        self.cnt_struct_type = "bloom"
        self.msg_cnt_gwgw= 0
        self.msg_cnt_gw_ce = 0

    ################################
    ######## DECENT W COMM ########
    ################################
    '''
        z-anonymize data in decentralized scenario with communication
            the whole process takes place between the GWs 
            the CE only receives the anonymized data points in the end and collects them for further processing
    '''
    def decent_zanon_w_comm(self, network, t_start_offset):
        print("__decent_wc_zanonymize__: start run")
        # coordinating GW in first round
        gw_coord = network.l_gws[0]
        
        while True:
            # every clock cycle: call for measurement
            time_change = datetime.timedelta(minutes = self.env.now) # add current simulation time to global simulation offsset
            self.clock = t_start_offset + time_change
            measurement_time = self.clock

            # create a stochastic data structure to store measurement hashes for data exchange
            cnt_struct = z_utils.create_cnt_structure(gw_coord.n_sm_conn, self.n_cycles_for_anon, self.cnt_struct_type)
            
            # decentralized collection round between GWs
            # MSG: transmission to address coordinating GW to trigger collection procedure
            self.msg_cnt_gw_ce += 1 
            cnt_struct = gw_coord.add_initial_noise_to_cnt_struct(cnt_struct)
            cnt_struct = self.decent_collection_round(gw_coord.gw_suc, gw_coord.id, cnt_struct, measurement_time) # start collection round at successor
            cnt_struct = gw_coord.remove_initial_noise_from_cnt_struct(cnt_struct)

            # on gw_coord: ensure minimum count z to guarantee z-anonymity protection
            cnt_struct = z_utils.ensure_min_cnt_z(cnt_struct, self.z)

            # decentrally publish anonymized data stream
            self.decent_publication_round(gw_coord.gw_suc, gw_coord.id, cnt_struct, measurement_time) # start publication round at successor

            # determine coordinating GW for next round
            #   draw random GW or traverse the ring
            gw_coord = gw_coord.gw_suc

            # wait 15 minutes until next round
            yield self.env.timeout(self.measurement_frequency.seconds/60)

    '''
        collect data decentrally between GWs
            without involving any central coordinator or revealing clear data of coordinated SMs
    '''
    # TODO: start with successor first
    def decent_collection_round(self, curr_gw, coord_id, cnt_struct, curr_time):
        while True:
            # at each GW clean current record log from entries that are too old
            curr_gw.record_log = z_utils.apply_deltat_to_records(curr_gw.record_log, curr_time, self.delta_t)

            # get new measurements of curr_gw and update cnt_struct
            #   NOTE: local record_log of curr_gw is also updated
            cnt_struct = curr_gw.add_curr_measurement(cnt_struct, curr_time)
            # MSG: transmission from GW - SM - GW to trigger and receive new measurements from SMs
            self.msg_cnt_gwgw += (curr_gw.n_sm_conn * 2) 
            
            # if the ID belongs to the coordinating GW ID we have completed the ring
            if(curr_gw.id == coord_id):
                break
            # otherwise, continue the collection round at suceeding gateway
            else:
                # "forward" updated cnt_struct to suceeding GW
                #   NOTE: that no central entitiy is needed for this 
                curr_gw = curr_gw.gw_suc
                self.msg_cnt_gwgw += 1 # MSG to forward cnt_struct to next GW for decentralized counting

        # collection throughout ring has been completed: back at coordinating GW
        return cnt_struct

    '''
        delegate publication responsibility decentrally between GWs 
            without involving any central coordinator or revealing clear data of coordinated SMs
    '''
    def decent_publication_round(self, curr_gw, coord_id, cnt_struct, curr_time):
        first_pub_round = True
        p_pub = random.randint(0, 100)
        while True:
            # stop publication round earlier if everything has been published already
            #   NOTE: this will seldom be the case since older entries within dt are counted in cnt_struct as well 
            #   but only measurements from this round can be potentially published
            if(cnt_struct.is_empty()):
                break
            
            # trigger publication process at GW
            cnt_struct = z_utils.publish_anonyimzed_tuples(curr_gw, cnt_struct, p_pub, curr_time)
            # MSG: transmissions from GW to CE for tuple publishing
            self.msg_cnt_gw_ce += curr_gw.get_gw_ce_msg_cnt()

            # if the ID of the upcoming GW equals the coordinating GW ID we have completed the ring
            if(curr_gw.id == coord_id):
                # if cnt_struct is already empty so we have definitely found all potential tuples for publishing we can stop
                if(cnt_struct.is_empty()):
                    break

                # if we already completed the second round or had p_pub == 100 before we already published as many tupe as possible
                if(not first_pub_round or (p_pub == 100)):
                    break

                # prepare for the second publication round
                first_pub_round = False
                p_pub = 100
            # endif curr.gw == coordinator

            # proceed to next GW and forward updated cnt_struct to suceeding GW
            #   NOTE: that no central entitiy is needed for this 
            curr_gw = curr_gw.gw_suc
            # MSG: transmission to forward cnt_struct to next GW in decentralized publishing
            self.msg_cnt_gwgw += 1 
        return
                

    ################################
    ######## CENTRAL W CNT ########
    ################################
    '''
        z-anonymize data in a distributed setting with the help of a central entity
            it collects data from distributed data sources (e.g. GWs)
            and combines them for anonymization and further processing
        this implementation uses a cnt_struct just as the GWs in a decentralized setting to validate its use
    '''
    def central_zanon_w_cnt_struct(self, network, t_start_offset):
        print("__central_zanonymize w cnt_struct__: start run")
        central_entity = network.ce

        while True:
            # every clock cycle: call for measurement
            time_change = datetime.timedelta(minutes = self.env.now) # add current simulation time to global simulation offsset
            self.clock = t_start_offset + time_change
            measurement_time = self.clock

            # get new measurements from all GWs and update cnt_struct
            ce_cnt_struct = self.central_collection_round(central_entity, network.l_gws, measurement_time)
            
            # ensure minimum count z to guarantee z-anonymity protection
            ce_cnt_struct = z_utils.central_ensure_min_cnt_z(ce_cnt_struct, self.z)

            # centrally publish anonymized data stream
            self.central_publication_round(central_entity, ce_cnt_struct, measurement_time)

            # wait 15 minutes until next round
            yield self.env.timeout(self.measurement_frequency.seconds/60)

    '''
        collect data centrally at CE
            trigger data collection at each GW connected to the CE
            add it to a central record log
    '''
    def central_collection_round(self, ce, l_gws, curr_time): #(self, ce, cnt_struct, l_gws, curr_time):
        # at CE: clean global record log from entries that are too old
        ce.record_log = z_utils.apply_deltat_to_records(ce.record_log, curr_time, self.delta_t)

        # trigger new measurements at all GWs in network
        for gw in l_gws:
            # MSG: transmission from CE - GW to address current GW to trigger data collection
            self.msg_cnt_gw_ce += 1 

            # get new measurements of curr_gw and update cnt_struct
            #   NOTE: local record_log of gw is also updated
            gw.collect_curr_measurement_from_sms(curr_time)
            # MSG: transmission from GW - SM - GW to trigger and receive new measurements from SMs
            self.msg_cnt_gwgw += (gw.n_sm_conn * 2)

            # add new data points reported by GW to global record log at CE
            n_added_m = ce.update_central_record_log(gw.record_log.log, curr_time) # FIX
            # MSG: transmission of all of GW's CURRENT data tuples to CE
            self.msg_cnt_gw_ce += int(n_added_m) # FIX

        current_cnt_log = ce.cnt_curr_values()
        return current_cnt_log
    

    '''
        publish all tuples within central record log that have occurred more than z times
    '''
    def central_publication_round(self, ce, cnt_struct, curr_time):
        p_pub = 100
        
        z_utils.publish_anonyimzed_tuples(ce, cnt_struct, p_pub, curr_time)



    ################################
    ######## FULLY DECENT WO COORD ########
    ################################
    '''
        z-anonymize data in decentralized scenario without any coordination between the GWs
            the whole process takes place at each GWs respectively
            the CE only receives the anonymized data points in the end and collects them for further processing
    '''
    def fully_decent_zanon_wo_coord(self, network, t_start_offset):
        print("__decent_wc_zanonymize__: start run")

        while True:
            # every clock cycle: call for measurement
            time_change = datetime.timedelta(minutes = self.env.now) # add current simulation time to global simulation offsset
            self.clock = t_start_offset + time_change
            measurement_time = self.clock
            
            # each GW in the network performs the same steps
            #   NOTE: this is done rather simultaneously than sequentially like the for-loop implies
            #   actually, it can be assumed that each GW receives the trigger at the same time and processes it parallely
            for gw in network.l_gws:
                # MSG: transmission from CE - GW to address current GW to trigger data collection
                self.msg_cnt_gw_ce += 1

                # create a stochastic data structure to store measurement hashes for data exchange
                cnt_struct = z_utils.create_cnt_structure(gw.n_sm_conn, self.n_cycles_for_anon, self.cnt_struct_type)
            
                # decentralized collection round between GWs
                cnt_struct = self.fully_decent_collection_round(gw, cnt_struct, measurement_time)

                # on each GW: ensure minimum count z to guarantee z-anonymity protection
                cnt_struct = z_utils.ensure_min_cnt_z(cnt_struct, self.z)

                # decentrally publish anonymized data stream
                self.fully_decent_publication_round(gw, cnt_struct, measurement_time)

            # wait 15 minutes until next round
            yield self.env.timeout(self.measurement_frequency.seconds/60)

    '''
        collect data decentrally at current GW
            without involving any central coordinator or other GWs or revealing clear data of coordinated SMs
    '''
    def fully_decent_collection_round(self, curr_gw, cnt_struct, curr_time):
        # at each GW clean current record log from entries that are too old
        curr_gw.record_log = z_utils.apply_deltat_to_records(curr_gw.record_log, curr_time, self.delta_t)

        # get new measurements of curr_gw and update cnt_struct
        #   NOTE: local record_log of curr_gw is also updated
        cnt_struct = curr_gw.add_curr_measurement(cnt_struct, curr_time)
        # MSG: transmission from GW - SM - GW to trigger and receive new measurements from SMs
        self.msg_cnt_gwgw+= (curr_gw.n_sm_conn * 2)
        
        # collection at SMs has been completed
        return cnt_struct
    
    '''
        publish tuples within local GW's record log that have occurred more than z times
    '''
    def fully_decent_publication_round(self, curr_gw, cnt_struct, curr_time):
        p_pub = 100
        z_utils.publish_anonyimzed_tuples(curr_gw, cnt_struct, p_pub, curr_time)
        # MSG: transmissions from GW to CE for tuple publishing
        self.msg_cnt_gw_ce += curr_gw.get_gw_ce_msg_cnt()
