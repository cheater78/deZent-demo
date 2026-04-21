import pandas as pd

input_path = "./data_analysis/simulation_stats/"
output_path = "./data_analysis/simulation_stats/"

l_sce_label = ["centralized", "deZent", "fully_decentralized"]

# load message counting stats
df_pub_ratio = pd.read_csv((input_path + "pub_ratio_analysis.csv"), sep = ",", header=0)
df_pub_ratio = df_pub_ratio.loc[:, ["z", "n_gw", "n_max_sm", "pub_ratio", "scenario"]]

### n_sm == 20
for sce in l_sce_label:
    tmp_df = df_pub_ratio.loc[df_pub_ratio["scenario"] == sce]
    tmp_df = tmp_df.loc[tmp_df["n_max_sm"] == 20]
    tmp_df = tmp_df.loc[:, ["z", "pub_ratio", "n_gw"]]
    tmp_df.to_csv((output_path + "pub_ratio_" + sce + "_nsm20.dat"), sep = " ", index = False)

    # average publication ratio
    tmp_df_avg = tmp_df.groupby(["z", "n_gw"])["pub_ratio"].mean().reset_index()
    tmp_df_std = tmp_df.groupby(["z", "n_gw"])[["pub_ratio"]].std().reset_index().rename(columns={"pub_ratio":"std"})
    df_pub_ratio_stats = pd.merge(tmp_df_avg,tmp_df_std,how="left")
    df_pub_ratio_stats.to_csv((output_path + "avg_pub_ratio_" + sce + "_nsm20.dat"), sep = " ", index = False)


### n_sm == 100
for sce in l_sce_label:
    tmp_df = df_pub_ratio.loc[df_pub_ratio["scenario"] == sce]
    tmp_df = tmp_df.loc[tmp_df["n_max_sm"] == 100]
    tmp_df = tmp_df.loc[:, ["z", "pub_ratio", "n_gw"]]
    tmp_df.to_csv((output_path + "pub_ratio_" + sce + "_nsm100.dat"), sep = " ", index = False)

    # average publication ratio
    tmp_df_avg = tmp_df.groupby(["z", "n_gw"])["pub_ratio"].mean().reset_index()
    tmp_df_std = tmp_df.groupby(["z", "n_gw"])[["pub_ratio"]].std().reset_index().rename(columns={"pub_ratio":"std"})
    df_pub_ratio_stats = pd.merge(tmp_df_avg,tmp_df_std,how="left")
    df_pub_ratio_stats.to_csv((output_path + "avg_pub_ratio_" + sce + "_nsm100.dat"), sep = " ", index = False)



