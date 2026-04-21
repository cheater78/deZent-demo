import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator
import statistics
import numpy as np
import json
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict
import math
from scipy.stats import entropy

MAX_GENERALIZATION = 20


def fill_json_stats():
    with open('output.json',"r") as f: 
        data = json.load(f)
        z = data['z']
        z = np.array(z)
        pk = data['kanon']
        pk = np.array(pk)
        cpu = data['cpu']
        cpu = np.array(cpu)
        ram = data['ram']
        ram = np.array(ram)
        ent = entropy_fun()
        
    with open('max_mean.json', 'r') as f:
        data = json.load(f)
        data['zmedian'].append(float(np.median(z)))
        data['zmax'].append(float(np.max(z)))
        data["zmin"].append(float(np.min(z)))
        data['zmean'].append(float(np.mean(z)))
        data['pkmedian'].append(float(np.median(pk)))
        data['pkmax'].append(float(np.max(pk)))
        data['pkmin'].append(float(np.min(pk)))
        data['pkmean'].append(float(np.mean(pk)))
        data['cpumedian'].append(float(np.median(cpu)))
        data['cpumax'].append(float(np.max(cpu)))
        data['cpumin'].append(float(np.min(cpu)))
        data['rammedian'].append(float(np.median(ram)))
        data['rammax'].append(float(np.max(ram)))
        data['rammin'].append(float(np.min(ram)))
        data['entropy'].append(ent)
        with open("max_mean.json", "w") as fi:
            json.dump(data, fi)
            
def generate_empty_json():
    data = {}
    data['zmedian'] = []
    data['zmax'] = []
    data["zmin"] = []
    data['zmean'] = []
    data['pkmedian'] = []
    data['pkmax'] = []
    data['pkmin'] = []
    data['pkmean'] = []
    data['cpumax'] = []
    data['cpumin'] = []
    data['cpumedian'] = []
    data['rammedian'] = []
    data['rammax'] = []
    data['rammin'] = []
    data['entropy'] = []
    with open("max_mean.json", "w") as fi:
        json.dump(data, fi)     

def plot_z(k):
    if (k < 1):
        kanon = [2,3,4,5,6,7,8,9] 
        k_pk = "k"
        pk_k = "pk"
    else:
        kanon = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        k_pk = "pk"
        pk_k = "k"
    with open("max_mean.json", "r") as f:
        data = json.load(f)

    fig, ax_left = plt.subplots(figsize=(15, 8))
    str_title = "Considering "+pk_k+" goal of " + str(k)
    ax_left.set_title(str_title, fontdict={'fontsize': 15.0, 'fontweight': 'medium'})   
    #ax_right = ax_left.twinx()
    ax_left.plot(kanon,data['zmedian'], color="#EF1717", linewidth="3", label="z median")
    ax_left.plot(kanon,data['zmin'], color="#FF3333", linewidth="3", label="z min/max", linestyle="dashed")
    ax_left.plot(kanon,data['zmax'], color="#FF3333", linewidth="3",linestyle="dashed")
    #ax_right.plot(kanon,data['pkmedian'], color='#000000', linewidth="3", label = "pk median")
    #ax_right.plot(kanon,data['pkmin'], color='#808080', linewidth="3", label="pk min/max",linestyle="dashed")
    #ax_right.plot(kanon,data['pkmax'], color='#808080', linewidth="3",linestyle="dashed")
    ax_left.fill_between(kanon, data['zmin'],data['zmax'], color='#FF3333', alpha=0.5)
    #ax_right.fill_between(kanon, data['pkmin'],data['pkmax'], color='#808080', alpha=0.5)   
    ax_left.set_xlabel(k_pk+' goal', fontsize=30)
    ax_left.set_ylabel('z', color="red", fontsize=30)
    #ax_right.set_ylabel('pk', color='black', fontsize=30)
    ax_left.autoscale()
    #ax_right.set_ylim(bottom = 0.0, top = 1.0)
    ax_left.tick_params(axis='y', labelcolor="red", labelsize=20.0)
    #ax_right.tick_params(axis='y', labelcolor='black', labelsize = 20.0)
    #ax_left.get_xaxis().set_major_locator(LinearLocator(numticks=20))
    ax_left.tick_params(labelsize=20)
    h1, l1 = ax_left.get_legend_handles_labels()
    #h2, l2 = ax_right.get_legend_handles_labels()
    ax_left.legend(h1,l1,bbox_to_anchor=(1.5, 1), prop={"size":20})
    #ax_right.legend(loc='upper right', prop={"size":20})
    fig.autofmt_xdate(rotation = 45)
    fig.tight_layout()   
    stringa = "z with "+pk_k+"="+str(k)+".pdf"
    fig.savefig(stringa)
    
def plot_pk(k):
    if (k < 1):
        kanon = [2,3,4,5,6,7,8,9] 
        k_pk = "k"
        pk_k = "pk"
    else:
        kanon = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        k_pk = "pk"
        pk_k = "k"
    with open("max_mean.json", "r") as f:
        data = json.load(f)

    fig, ax_left = plt.subplots(figsize=(15, 8))
    str_title = "Considering "+pk_k+" goal of " + str(k)
    ax_left.set_title(str_title, fontdict={'fontsize': 15.0, 'fontweight': 'medium'})   
    ax_left.plot(kanon,data['pkmedian'], color="black", linewidth="3", label="pk median")
    ax_left.plot(kanon,data['pkmin'], color="gray", linewidth="3", label="pk min/max", linestyle="dashed")
    ax_left.plot(kanon,data['pkmax'], color="gray", linewidth="3",linestyle="dashed")
    ax_left.fill_between(kanon, data['pkmin'],data['pkmax'], color='gray', alpha=0.4)
    ax_left.set_xlabel(k_pk+' goal', fontsize=30)
    #ax_left.set_ylabel('pk', color="red", fontsize=30)
    ax_left.autoscale()
    #ax_left.tick_params(axis='y', labelcolor="red", labelsize=20.0)
    ax_left.tick_params(labelsize=20)
    h1, l1 = ax_left.get_legend_handles_labels()
    ax_left.legend(h1,l1,bbox_to_anchor=(1.5, 1), prop={"size":20})
    fig.autofmt_xdate(rotation = 45)
    fig.tight_layout()   
    stringa = pk_k+"="+str(k)+".pdf"
    fig.savefig(stringa)
    
    
def plot_comp_time(k):
    if (k < 1):
        kanon = [2,3,4,5,6,7,8,9] 
        k_pk = "k"
        pk_k = "pk"
    else:
        kanon = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        k_pk = "pk"
        pk_k = "k"
    with open("time.json", "r") as f:
        data = json.load(f)
    fig, ax = plt.subplots(figsize=(10, 8))
    str_title = "Considering "+pk_k+" goal of " + str(k)
    ax.set_title(str_title, fontdict={'fontsize': 15.0, 'fontweight': 'medium'}) 
    ax.plot(kanon, data['time'])
    ax.set_xlabel(k_pk+' goal', fontsize=20)
    ax.set_ylabel('Seconds to compute', fontsize=20)
    ax.autoscale()
    ax.tick_params(axis='y',  labelsize=12.0)
    ax.tick_params(labelsize = 12.0)
    fig.tight_layout()   
    stringa = "Time " + pk_k+"="+str(k)+".pdf"
    fig.savefig(stringa)
    
def plot_cpu(k):
    if (k < 1):
        kanon = [2,3,4,5,6,7,8,9] 
        k_pk = "k"
        pk_k = "pk"
    else:
        kanon = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        k_pk = "pk"
        pk_k = "k"
    with open("max_mean.json", "r") as f:
        data = json.load(f)

    fig, ax_left = plt.subplots(figsize=(15, 8))
    str_title = "Considering "+pk_k+" goal of " + str(k)
    ax_left.set_title(str_title, fontdict={'fontsize': 15.0, 'fontweight': 'medium'})   
    ax_left.plot(kanon,data['cpumedian'],  linewidth="3", label="z median")
    ax_left.plot(kanon,data['cpumin'], linewidth="3", label="z min/max", linestyle="dashed", color = "lightblue")
    ax_left.plot(kanon,data['cpumax'], linewidth="3",linestyle="dashed", color = "lightblue")
    ax_left.fill_between(kanon, data['cpumin'],data['cpumax'], color='blue', alpha=0.1)
    ax_left.set_xlabel(k_pk+' goal', fontsize=30)
    ax_left.set_ylabel('cpu %',  fontsize=30)
    ax_left.autoscale()
    ax_left.tick_params(axis='y',  labelsize=20.0)
    #ax_left.get_xaxis().set_major_locator(LinearLocator(numticks=20))
    ax_left.tick_params(labelsize=20)
    ax_left.legend(bbox_to_anchor=(1.5, 1), prop={"size":20})
    #ax_right.legend(loc='upper right', prop={"size":20})
    #fig.autofmt_xdate(rotation = 45)
    fig.tight_layout()   
    stringa = "cpu with "+pk_k+"="+str(k)+".pdf"
    fig.savefig(stringa)
    
def plot_entropy():
    if (k < 1):
        kanon = [2,3,4,5,6,7,8,9] 
        k_pk = "k"
        pk_k = "pk"
    else:
        kanon = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        k_pk = "pk"
        pk_k = "k"
    with open("max_mean.json", "r") as f:
        data = json.load(f)

    fig, ax_left = plt.subplots(figsize=(15, 8))
    str_title = "Considering "+pk_k+" goal of " + str(k)
    ax_left.set_title(str_title, fontdict={'fontsize': 15.0, 'fontweight': 'medium'})   
    ax_left.plot(kanon,data['entropy'],  linewidth="3", label="Entropy")
    ax_left.set_xlabel(k_pk+' goal', fontsize=30)
    ax_left.set_ylabel('Entropy',  fontsize=30)
    ax_left.autoscale()
    ax_left.tick_params(axis='y',  labelsize=20.0)
    #ax_left.get_xaxis().set_major_locator(LinearLocator(numticks=20))
    ax_left.tick_params(labelsize=20)
    #ax_left.legend(bbox_to_anchor=(1.5, 1), prop={"size":20})
    #ax_right.legend(loc='upper right', prop={"size":20})
    #fig.autofmt_xdate(rotation = 45)
    fig.tight_layout()   
    stringa = "Entropy with "+pk_k+"="+str(k)+".pdf"
    fig.savefig(stringa)

def entropy_fun():
    final_dataset = defaultdict(set)
    file = open('output.txt','r')

    for line in file:
        t,u,a = line.split("\t")
        t = float(t)
        a.strip()          
        final_dataset[u].add(a)
    tot_user = len(final_dataset)

    #print("distinct users: " + str(len(final_dataset)))
    final_dataset_inv = defaultdict(list)
    for k,v in final_dataset.items():
        final_dataset_inv[frozenset(v)].append(k)
    ks = np.array([len(v) for v in final_dataset_inv.values()])
    #for k in range(1,5):
      #  print("Final " + str(k) + "-anonymization: " + str(sum(ks[ks >= k])/sum(ks)))
    groups = {}

    for i in range(1,10000):
        if(sum(ks[ks == i]) != 0):
            groups[i] = sum(ks[ks == i])
    print(groups)
    #print(tot_user)

    pk_list = []
    for G,U in groups.items():
        for x in range(int(U/G)):
            pk_list.append(G/tot_user)
    e = entropy(pk_list)
    return e