import pandas as pd


path_deZ = "./data/anonymized_data/deZent/"
path_jha = "./data/anonymized_data/jha/"
input_log_path = "./data/log_data/deZent/" 
plotdata_path = "model_validation/data/"

l_n_gw = [5]#, 25, 50, 75, 100, 125, 150] 
#l_n_max_sm = [20, 100] # n_gw(5, 25) -> 100; n_gw(150) -> 20
l_z = [1]#, 5, 10, 25, 50, 100]
d_t = 121 * 60 # minutes
l_seed=[1, 2, 3, 4, 5]#, 6, 7, 8, 9, 10]

dez_scenario = "cent_w_comm_zanon_z_"



pub_diff_log= {"n_gw": [],
        "z": [],
        "n_pub_dez": [],
        "n_pub_jha": [],
        "n_total":[],
        "pub_rat_dez":[],
        "pub_rat_jha":[],
        "d_t":[],
        "seed": []
        }


for n_gw in l_n_gw:
    scenario_params = "_dt_" + str(d_t) + "_nGw_" + str(n_gw) + "_distSm_normal_maxSm_20"  
    for z_val in l_z:
        #for n_max_sm in l_n_max_sm:

        for seed in l_seed:
            scenario = dez_scenario + str(z_val) + scenario_params + "_seed_" + str(seed)

            print("################################")
            input_deZent = scenario + ".csv"
            df_anon_deZ = pd.read_csv((path_deZ + input_deZent),  sep = ",", header=2)
            n_pub_dez = len(df_anon_deZ)
            print("deZent: ", n_pub_dez)

            print("#############################")
            simu_log_file = "simu_log_" + input_deZent
            df_simu_log = pd.read_csv((input_log_path + simu_log_file),  sep = ",", header=0)
            n_total = len(df_simu_log)
            pub_ratio_deZ = n_pub_dez/n_total
            print("deZent: ", pub_ratio_deZ)

            
            print("################################")
            input_jha = "output_jha_simu_log_" + scenario + ".csv.txt"
            df_jha = pd.read_csv( (path_jha + input_jha), sep ="\t", header = None, names = ["time", "ID", "value"])
            n_pub_jha = len(df_jha)
            print(df_jha.head())
            print("Jha: ", n_pub_jha)
            pub_ratio_jha = n_pub_jha/n_total
            print("deZent: ", pub_ratio_jha)

            pub_diff_log["n_gw"].append(n_gw)
            pub_diff_log["z"].append(z_val)
            pub_diff_log["n_pub_dez"].append(n_pub_dez)
            pub_diff_log["n_pub_jha"].append(n_pub_jha)
            pub_diff_log["n_total"].append(n_total)
            pub_diff_log["pub_rat_dez"].append(pub_ratio_deZ)
            pub_diff_log["pub_rat_jha"].append(pub_ratio_jha)
            pub_diff_log["d_t"].append(d_t)
            pub_diff_log["seed"].append(seed)
df_diff = pd.DataFrame(pub_diff_log)

df_diff["npub_diff"] =  df_diff["n_pub_jha"] -df_diff["n_pub_dez"]
df_diff["pub_rat_diff"] = df_diff["pub_rat_jha"] - df_diff["pub_rat_dez"]
print(df_diff.head())


df_diff.to_csv((plotdata_path + "npub_diff.csv"), sep = ',', index=False)
