import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime


path_deZ = "./data/anonymized_data/deZent/"
path_jha = "./data/anonymized_data/jha/"
path_plots = "./plots/model_validation_plots/"

z_val = 1 #((1 5 10 25 50 100))
deltat = 7260 #in seconds
n_gw = 5 #, 25, 50, 75, 100, 125, 150] 

prefix = "simu_log_"
dez_scenario = "cent_w_comm_zanon_z_"
scenario_params = "_dt_" + str(deltat) + "_nGw_" + str(n_gw) + "_distSm_normal_maxSm_20"

complete_deZent = pd.DataFrame()
complete_orig = pd.DataFrame()


for seed in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    # input filename
    scenario = dez_scenario + str(z_val) + scenario_params + "_seed_" + str(seed)

    ### input deZent ###
    print("################################")
    print("deZent")
    input_deZent = scenario + ".csv"
    tmp = pd.read_csv( (path_deZ+input_deZent), sep =",", header = 2)
    tmp["seed"] = [seed] * len(tmp)
    tmp["cat"] = ["deZent"] * len(tmp)
    df_deZent = tmp[["time", "ID", "value", "seed", "cat"]]

    l_time = [(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")).timestamp() for t in df_deZent["time"] ]
    print(l_time[0:5])
    df_deZent.loc[:, "time"] = l_time
    print(df_deZent.head())

    complete_deZent = pd.concat([complete_deZent, df_deZent])

    ### input Jha ###
    print("################################")
    print("Jha")
    input_orig = "output_jha_simu_log_" + scenario + ".csv.txt"
    df_orig = pd.read_csv( (path_jha + input_orig), sep ="\t", header = None, names = ["time", "ID", "value"])
    df_orig["seed"] = [seed] * len(df_orig)
    df_orig["cat"] = ["original"] * len(df_orig)
    df_orig = df_orig
    print(df_orig.head())

    complete_orig = pd.concat([complete_orig, df_orig])

plotdata_path = "model_validation/data/"
plotdata_file = "npub_over_time_" + scenario + ".dat"

### deZent ###
deZ_pub_over_time = complete_deZent.groupby(["time", "cat", "seed"]).size().reset_index().rename(columns={0:'tuple_count'}) # count number of IDs that published somthing during this timepoint and save as tuples_count
print(deZ_pub_over_time.head())
deZ_pub_over_time.to_csv(plotdata_path + "deZ_" + plotdata_file, index=False, sep = " ")

tmp = deZ_pub_over_time.iloc[:300,:]
deZ_avg_pub_over_time = tmp.groupby(["time", "cat"])[[ "tuple_count"]].mean().reset_index().rename(columns={0:'avg_tuple_count'})
deZ_avg_pub_over_time["time"] = range(len(deZ_avg_pub_over_time["time"]))
deZ_avg_pub_over_time.to_csv(plotdata_path + "avg_deZ_" + plotdata_file, index=False, sep = " ")


orig_pub_over_time = complete_orig.groupby(["time", "cat", "seed"]).size().reset_index().rename(columns={0:'tuple_count'})
print(orig_pub_over_time.head())
orig_pub_over_time.to_csv(plotdata_path + "jha_" + plotdata_file, index=False, sep = " ")

tmp = orig_pub_over_time.iloc[:300,:]
jha_avg_pub_over_time = tmp.groupby(["time", "cat"])[[ "tuple_count"]].mean().reset_index().rename(columns={0:'avg_tuple_count'})
jha_avg_pub_over_time["time"] = range(len(jha_avg_pub_over_time["time"]))
jha_avg_pub_over_time.to_csv(plotdata_path + "avg_jha_" + plotdata_file, index=False, sep = " ")

"""
df_pub_over_time = pd.concat([deZ_pub_over_time, orig_pub_over_time])
print(df_pub_over_time.head())

plot_name = str(z_val) + def_scenario

sns.set_theme(style = "white", palette = "colorblind")#, font_scale = 9)

sns.set_context("paper",rc={"font.size": 15, "axes.titlesize": 'medium', 'axes.labelsize': 'medium', 
                    'xtick.labelsize': 'medium', 'ytick.labelsize': 'medium',
                    "legend.fontsize": 'medium', 'legend.title_fontsize': 'medium',
                    'lines.markersize': 9.0, 'lines.linewidth': 2.8,"figure.figsize": (30,15)})


g = sns.relplot(data = df_pub_over_time, x = "time", y = "tuple_count", kind = "line", hue = "cat", style = "cat")
#plt.xticks(rotation=30)
for ax in g.axes.flat:
    ax.set_xticklabels(labels=range(0,len(df_pub_over_time["time"].unique())))
#plt.show()
sns.move_legend(g, bbox_to_anchor=(.8,.15), loc="lower right", frameon=True, title= "Scenario")
#g._legend.set_title("Scenario")
g.set(xlabel = "Time", ylabel = "Number of published tuples")
plt.savefig(("pub_over_time_" + plot_name + ".pdf"), bbox_inches = "tight")
plt.close()


df_hist = pd.concat([df_deZent, df_orig])
print(df_hist.head())
g = sns.displot(data = df_hist, x = "value", hue = "cat", kind = "hist", multiple = "dodge", binwidth=35)
#g = sns.histplot(data = df_hist, x = "value", hue = "cat", multiple="dodge")
#g.set_xlim(0,500)
#sns.despine()
g.set(xlabel = "Value", ylabel = "Count")
sns.move_legend(g,  loc="upper right", frameon=True, title="Scenario", bbox_to_anchor=(.8,.95),)
#plt.show()
plt.savefig(("hist_pub_values_" + plot_name + ".pdf"), bbox_inches = "tight")
plt.close()

#https://www.geeksforgeeks.org/how-to-change-seaborn-legends-font-size-location-and-color/
"""