import pandas as pd


plotdata_path = "model_validation/data/"

# average publication ratio difference
tmp_df = pd.read_csv((plotdata_path + "npub_diff.csv"), sep = ',')

avg_pr_diff = tmp_df.groupby(["n_gw", "z"])["pub_rat_diff"].mean().reset_index()
std_pr_diff = tmp_df.groupby(["n_gw", "z"])[["pub_rat_diff"]].std().reset_index().rename(columns={"pub_rat_diff":"std"})
df_pub_ratio_diff_stats = pd.merge(avg_pr_diff, std_pr_diff, how="left")
df_pub_ratio_diff_stats.to_csv((plotdata_path + "avg_pub_ratio_diff.dat"), sep = " ", index = False)

avg_npub_diff = tmp_df.groupby(["n_gw", "z"])["npub_diff"].mean().reset_index()
std_npub_diff = tmp_df.groupby(["n_gw", "z"])[["npub_diff"]].std().reset_index().rename(columns={"npub_diff":"std"})
df_npub_diff_stats = pd.merge(avg_npub_diff, std_npub_diff, how="left")
df_npub_diff_stats.to_csv((plotdata_path + "avg_npub_diff.dat"), sep = " ", index = False)