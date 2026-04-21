import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import csv
import numpy as np

complete_deZent = pd.DataFrame()
complete_orig = pd.DataFrame()

path_deZ = "./data/anonymized_data/deZent/"
path_jha = "./data/anonymized_data/jha/"
plotdata_path = "model_validation/data/"

z_val = 50 #((1 5 10 25 50 100))
deltat = 7260 #in seconds
n_gw = 50

prefix = "simu_log_"
dez_scenario = "cent_w_comm_zanon_z_"
scenario_params = "_dt_" + str(deltat) + "_nGw_" + str(n_gw) + "_distSm_normal_maxSm_20"

# join data of 10 simulation runs
for seed in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    scenario = dez_scenario + str(z_val) + scenario_params + "_seed_" + str(seed)

    ### input deZent
    print("################################")
    print("dezent")
    input_deZent = scenario + ".csv"
    tmp = pd.read_csv( (path_deZ+input_deZent), sep =",", header = 2)
    tmp["seed"] = [seed] * len(tmp)
    tmp["cat"] = ["cent_deZent"] * len(tmp)
    df_deZent = tmp[["time", "ID", "value", "seed", "cat"]]
    #df_deZent = df_deZent#.iloc[0:181]
    #print(df_deZent.head())
    l_time = [(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")).timestamp() for t in df_deZent["time"] ]
    print(l_time[0:5])
    df_deZent.loc[:, "time"] = l_time
    print(df_deZent.head())

    complete_deZent = pd.concat([complete_deZent, df_deZent])

    ### input Jha
    print("################################")
    print("Jha")
    input_orig = "output_jha_simu_log_" + scenario + ".csv.txt"
    df_orig = pd.read_csv( (path_jha + input_orig), sep ="\t", header = None, names = ["time", "ID", "value"])
    df_orig["seed"] = [seed] * len(df_orig)
    df_orig["cat"] = ["Jha"] * len(df_orig)
    df_orig = df_orig#.iloc[0:300]
    print(df_orig.head())

    complete_orig = pd.concat([complete_orig, df_orig])

### Jha simulation data ###
print(complete_orig["value"].unique())
jha_complete_cnt = complete_orig["value"].value_counts()
jha_complete_cnt = jha_complete_cnt.sort_index()
jha_complete_cnt.to_csv(plotdata_path + "Jha_value_cnt_z" + str(z_val) + scenario_params + ".dat", index=True, sep = " ")

value_avg = []
count_sum = []
orig_values = complete_orig["value"]    # get measurement values
orig_cnt = orig_values.value_counts()   # get count statistics, Value = index
orig_cnt = orig_cnt.sort_index()        # sort values to average neighbouring values
orig_cnt = orig_cnt.reset_index()       # use value as column
# average 3 neighbouring values for better visibility in histogram
for x in range(0, len(orig_cnt), 3):
    value_avg.append(orig_cnt.loc[x:x+2, "value"].mean())
    count_sum.append(orig_cnt.loc[x:x+2, "count"].sum())

orig_cnt_data = pd.DataFrame({"Value":value_avg, "Count":count_sum})
orig_cnt_data.to_csv(plotdata_path + "Jha_cnt_avg_value_z" + str(z_val) + scenario_params + ".dat", sep = ' ', index= False)

### deZent simulation data ###
print(complete_deZent["value"].unique())
deZ_complete_cnt = complete_deZent["value"].value_counts()
deZ_complete_cnt = deZ_complete_cnt.sort_index()
deZ_complete_cnt.to_csv(plotdata_path + "deZ_value_cnt_z" + str(z_val) + scenario_params + ".dat", index=True, sep = " ")

value_avg = []
count_sum = []
deZ_values = complete_deZent["value"] # get measurement values
deZ_cnt = deZ_values.value_counts() # get count statistics, Value = index
deZ_cnt = deZ_cnt.sort_index()      # sort values to average neighbouring values
deZ_cnt = deZ_cnt.reset_index()     # use value as column
# average 3 neighbouring values for better visibility in histogram
for x in range(0, len(deZ_cnt), 3):
    value_avg.append(deZ_cnt.loc[x:x+2, "value"].mean())
    count_sum.append(deZ_cnt.loc[x:x+2, "count"].sum())

deZ_cnt_data = pd.DataFrame({"Value":value_avg, "Count":count_sum})
deZ_cnt_data.to_csv(plotdata_path + "deZ_cnt_avg_value_z" + str(z_val) + scenario_params + ".dat", sep = ' ', index= False)

