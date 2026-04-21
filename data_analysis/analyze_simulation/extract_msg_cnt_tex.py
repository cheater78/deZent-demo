import pandas as pd
import matplotlib
import matplotlib.pyplot as plt



input_path = "./data_analysis/simulation_stats/"
output_path = "./data_analysis/simulation_stats/"

l_sce_label = ["centralized", "deZent", "fully_decentralized"]

# load message counting stats
df_cnt = pd.read_csv((input_path + "msg_cnt_analysis.csv"), sep = ",", header=0)

### GW - CE ###
# extract specific count data
gwce_cnt = df_cnt.loc[:, ["n_gw", "msg_cnt_gw_ce", "z", "scenario"]]

# average message count across runs, all z, all runs included
gwce_avg = gwce_cnt.groupby(["n_gw", "scenario"])[["msg_cnt_gw_ce"]].mean().reset_index()
gwce_std = gwce_cnt.groupby(["n_gw", "scenario"])[["msg_cnt_gw_ce"]].std().reset_index().rename(columns={"msg_cnt_gw_ce":"std"})
gwce_cnt_stats = pd.merge(gwce_avg,gwce_std,how="left")
gwce_cnt_stats.to_csv((output_path + "avg_msg_cnt_gw_ce.dat"), sep = " ", index = False)

for sce in l_sce_label:
    # msg count per scenario
    tmp_gwce = gwce_cnt.loc[gwce_cnt["scenario"] == sce]
    tmp_gwce.to_csv((output_path + "msg_cnt_gw_ce_" + sce + ".dat"), sep = " ", index = False)

    # average message count across runs
    tmp_gwce_avg = tmp_gwce.groupby(["n_gw", "scenario"]).mean().reset_index()
    tmp_gwce_avg.to_csv((output_path + "avg_msg_cnt_gw_ce_" + sce + ".dat"), sep = " ", index = False)

    # get mean value per z across scenario
    tmp_gwce_z = tmp_gwce.groupby(["n_gw", "z", "scenario"])[["msg_cnt_gw_ce"]].mean().reset_index()
    tmp_gwce_z_std = tmp_gwce.groupby(["n_gw", "z", "scenario"])[["msg_cnt_gw_ce"]].std().reset_index().rename(columns={"msg_cnt_gw_ce":"std"})
    print(tmp_gwce_z.head())
    cnt_gwce_z_stats = pd.merge(tmp_gwce_z,tmp_gwce_z_std,how="left")
    print(cnt_gwce_z_stats.head())
    cnt_gwce_z_stats.to_csv((output_path + "msg_cnt_gw_ce_" + sce + "avg_per_z.dat"), sep = " ", index = False)


### GW - GW ###
# extract specific count data
gwgw_cnt = df_cnt.loc[:, ["n_gw", "msg_cnt_gw_gw", "z", "scenario"]]

# average message count across runs, all z, all runs included
gwgw_avg = gwgw_cnt.groupby(["n_gw", "scenario"]).mean().reset_index()
gwgw_std = gwgw_cnt.groupby(["n_gw", "scenario"])[["msg_cnt_gw_gw"]].std().reset_index().rename(columns={"msg_cnt_gw_gw":"std"})
gwgw_cnt_stats = pd.merge(gwgw_avg,gwgw_std,how="left")
gwgw_cnt_stats.to_csv((output_path + "avg_msg_cnt_gw_gw.dat"), sep = " ", index = False)

for sce in l_sce_label:

    tmp_gwgw = gwgw_cnt.loc[gwgw_cnt["scenario"] == sce]
    tmp_gwgw.to_csv((output_path + "msg_cnt_gw_gw_" + sce + ".dat"), sep = " ", index = False)

