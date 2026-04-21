import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

"""
get count statistics of siumulation data -> generate stat csv files
    - general message count file
    - average GW-GW msg count per scenario (all z, all #SM, all runs)
    - average GW-CE msg count per scenario (all z, all #SM, all runs)
"""
def analyze_cnt_data(prefix_scenario, l_n_gw, d_t, l_z, l_seed, input_anon_path, output_path):

    distribution_num_sms = "normal"

    cnt_joint= {"n_gw": [],
                "n_max_sm": [],
                "z": [],
                "msg_cnt_gw_gw": [],
                "msg_cnt_gw_ce": [],
                "d_t":[],
                "scenario": [],
                "dist_sm": [],
                "seed": []
                }
    
    for prefix in prefix_scenario: 
        match prefix:
            case "cent_w_comm_zanon_z_":
                sce_label = "centralized"
            case "decent_w_comm_zanon_z_":
                sce_label = "deZent"
            case "fully_decent_wo_coord_zanon_z_":
                sce_label = "fully_decentralized"

        for n_gw in l_n_gw:
            match n_gw:
                case 50 | 75 | 100 | 125 | 150:
                    l_n_max_sm = [20]
                case 5 | 25:
                    l_n_max_sm = [20]#, 100]

            for n_max_sm in l_n_max_sm:  
                for z in l_z:

                    for seed in l_seed:

                        input_file = prefix + str(z) + "_dt_" + str(d_t) + "_nGw_" + str(n_gw) + "_distSm_" + distribution_num_sms + "_maxSm_" + str(n_max_sm) + "_seed_" + str(seed) + ".csv"
                        df_tmp = pd.read_csv((input_anon_path + input_file),  sep = ",", nrows=2, header=None, index_col=0,usecols=[0,1], names=["label", "cnt"])
                        
                        cnt_joint["n_gw"].append(n_gw)
                        cnt_joint["n_max_sm"].append(n_max_sm)
                        cnt_joint["z"].append(z)
                        cnt_joint["msg_cnt_gw_gw"].append(df_tmp.loc["msg_count_gwgw", "cnt"])
                        cnt_joint["msg_cnt_gw_ce"].append(df_tmp.loc["msg_cnt_gw_ce", "cnt"])
                        cnt_joint["d_t"].append(d_t)
                        cnt_joint["scenario"].append(sce_label)
                        cnt_joint["dist_sm"].append(distribution_num_sms)
                        cnt_joint["seed"].append(seed)

    ### GENERAL SIMULATION MSG CNT ###
    df_cnt_joint = pd.DataFrame(cnt_joint)
    print(df_cnt_joint.head())
    df_cnt_joint.to_csv((output_path + "msg_cnt_analysis.csv"), sep = ',', index=False)

    ### MSG CNT GW - CE ###
    # extract msg count between GWs - CE
    df_cnt_gw_ce = df_cnt_joint.loc[:, ["n_gw", "msg_cnt_gw_ce", "scenario"]]
    # get average cnt across runs per n_gw & scenario
    df_cnt_gw_ce = df_cnt_gw_ce.groupby(["n_gw", "scenario"]).mean().reset_index().rename(columns={0:'avg_msg_count'})
    print(df_cnt_gw_ce.head())
    df_cnt_gw_ce.to_csv(output_path + "avg_msgcnt_gw_ce_per_scenario.csv", sep = ',', index=False)

    ### MSG CNT GW - GW ###
    # extract msg count between GWs - GWs
    df_cnt_gw_gw = df_cnt_joint.loc[:, ["n_gw", "msg_cnt_gw_gw", "scenario"]]
    df_cnt_gw_gw = df_cnt_gw_gw.groupby(["n_gw", "scenario"]).mean().reset_index().rename(columns={0:'avg_msg_count'})
    print(df_cnt_gw_gw.head())
    df_cnt_gw_gw.to_csv(output_path + "avg_msgcnt_gw_gw_per_scenario.csv", sep = ',', index=False)


def analyze_pub_ratio(prefix_scenario, l_n_gw, d_t, l_z, l_seed, input_anon_path, output_path):

    input_log_path = "./data/log_data/deZent/" 
    
    distribution_num_sms = "normal"

    pub_ratio_log= {"n_gw": [],
            "n_max_sm": [],
            "z": [],
            "n_pub": [],
            "n_total": [],
            "pub_ratio":[],
            "d_t":[],
            "scenario": [],
            "dist_sm": [],
            "seed": []
            }
    
    for prefix in prefix_scenario: 
        match prefix:
            case "cent_w_comm_zanon_z_":
                sce_label = "centralized"
            case "decent_w_comm_zanon_z_":
                sce_label = "deZent"
            case "fully_decent_wo_coord_zanon_z_":
                sce_label = "fully_decentralized"
        for n_gw in l_n_gw:
            match n_gw:
                case 50 | 75 | 100 | 125 | 150:
                    l_n_max_sm = [20]
                case 5 | 25:
                    l_n_max_sm = [20, 100]
                
            for z in l_z:
                for n_max_sm in l_n_max_sm:

                    for seed in l_seed:

                        input_anon_file = prefix + str(z) + "_dt_" + str(d_t) + "_nGw_" + str(n_gw) + "_distSm_" + distribution_num_sms + "_maxSm_" + str(n_max_sm) + "_seed_" + str(seed) + ".csv"
                        df_anon_log = pd.read_csv((input_anon_path + input_anon_file),  sep = ",", header=2)
                        n_pub = len(df_anon_log)

                        simu_log_file = "simu_log_" + input_anon_file
                        df_simu_log = pd.read_csv((input_log_path + simu_log_file),  sep = ",", header=0)
                        n_total = len(df_simu_log)

                        pub_ratio = n_pub/n_total

                        pub_ratio_log["n_gw"].append(n_gw)
                        pub_ratio_log["n_max_sm"].append(n_max_sm)
                        pub_ratio_log["z"].append(z)
                        pub_ratio_log["n_pub"].append(n_pub)
                        pub_ratio_log["n_total"].append(n_total)
                        pub_ratio_log["pub_ratio"].append(pub_ratio)
                        pub_ratio_log["d_t"].append(d_t)
                        pub_ratio_log["scenario"].append(sce_label)
                        pub_ratio_log["dist_sm"].append(distribution_num_sms)
                        pub_ratio_log["seed"].append(seed)
    df_pub_ratio = pd.DataFrame(pub_ratio_log)
    print(df_pub_ratio.head())
    df_pub_ratio.to_csv((output_path + "pub_ratio_analysis" + ".csv"), sep = ',', index=False)
    #return df_pub_ratio



def analyze_pub_ratio_p_smtype(prefix_scenario, l_z, l_n_gw, d_t, l_seed, input_anon_path, output_path):

    input_log_path = "./data/log_data/deZent/" 

    distribution_num_sms = "normal"
    n_max_sm = 20

    type_pub_ratio = {"n_gw": [],
            "n_max_sm": [],
            "z": [],
            "type": [],
            "n_pub": [],
            "n_total": [],
            "pub_ratio":[],
            "d_t":[],
            "scenario": [],
            "dist_sm": [],
            "seed": []
            }
    
    for prefix in prefix_scenario: 
        match prefix:
            case "cent_w_comm_zanon_z_":
                sce_label = "centralized"
            case "decent_w_comm_zanon_z_":
                sce_label = "deZent"
            case "fully_decent_wo_coord_zanon_z_":
                sce_label = "fully decentralized"
        for n_gw in l_n_gw:
            for z in l_z:
                for seed in l_seed:
                    input_anon_file = prefix + str(z) + "_dt_" + str(d_t) + "_nGw_" + str(n_gw) + "_distSm_normal_maxSm_" + str(n_max_sm) + "_seed_" + str(seed) + ".csv"
                    df_anon_log = pd.read_csv((input_anon_path + input_anon_file),  sep = ",", header=2)

                    simu_log_file = "simu_log_" + input_anon_file
                    df_simu_log = pd.read_csv((input_log_path + simu_log_file),  sep = ",", header=0)

                    uni_sm_types = df_anon_log["type"].unique()

                    for t in uni_sm_types:
                        df_pub = df_anon_log.loc[df_anon_log["type"] == t]
                        n_pub = len(df_pub)
                        df_tot = df_simu_log.loc[df_simu_log["type"] == t]
                        n_total = len(df_tot)
                        pub_ratio = n_pub/n_total


                        type_pub_ratio["n_gw"].append(n_gw)
                        type_pub_ratio["n_max_sm"].append(n_max_sm)
                        type_pub_ratio["type"].append(t)
                        type_pub_ratio["z"].append(z)
                        type_pub_ratio["n_pub"].append(n_pub)
                        type_pub_ratio["n_total"].append(n_total)
                        type_pub_ratio["pub_ratio"].append(pub_ratio)
                        type_pub_ratio["d_t"].append(d_t)
                        type_pub_ratio["scenario"].append(sce_label)
                        type_pub_ratio["dist_sm"].append(distribution_num_sms)
                        type_pub_ratio["seed"].append(seed)

    df_pub_ratio = pd.DataFrame(type_pub_ratio)
    print(df_pub_ratio.head())
    df_pub_ratio.to_csv((output_path + "smtype_pub_ratio_analysis.csv"), sep = ',', index=False)




#################################
#################################
'''
main 
'''
def main():
    input_anon_path = "./data/anonymized_data/deZent/"
    output_path = "./data_analysis/simulation_stats/"

    l_n_gw = [5, 25, 50, 75, 100, 125, 150] 
    #l_n_max_sm = [20, 100] # n_gw(5, 25) -> 100; n_gw(150) -> 20
    l_z = [1,5, 10, 25, 50, 100]
    d_t = 121 * 60 # minutes
    l_seed=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    prefix_scenario = ["cent_w_comm_zanon_z_", "decent_w_comm_zanon_z_", "fully_decent_wo_coord_zanon_z_"]

    analyze_cnt_data(prefix_scenario, l_n_gw, d_t, l_z, l_seed, input_anon_path, output_path)
    analyze_pub_ratio(prefix_scenario, l_n_gw, d_t, l_z, l_seed, input_anon_path, output_path)
    analyze_pub_ratio_p_smtype(prefix_scenario, l_z, l_n_gw, d_t, l_seed, input_anon_path, output_path)


if __name__ == "__main__":
    main()