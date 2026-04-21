from collections import defaultdict
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator

MAX_GENERALIZATION = 20
stepsize = np.array([3000, 5000, 10000, 30000, 500000])

numeric_category = False

with open('output.json',"r") as f:
    data = json.load(f)
    labels = []   
    labels.append("Anonymized")
    details = [x for x in data["all_details"] if not all(v == 0 for v in x)]
    if numeric_category:
        for i in reversed(stepsize):
            labels.append(str(int(i/1000))+" km")
    else:
        for i in range(len(details)):
            labels.append(str(i + 1) + "-detail")       
    to_plot =  np.vstack((data["tot_anon"], details))
    color = 'tab:red'
    fig, ax_left = plt.subplots(figsize=(20, 10))
    ax_right = ax_left.twinx()
    ax_third = ax_left.twinx()
    ax_third.spines["right"].set_position(("axes", 1.1))
    ax_left.plot(data["time"],data["z"], color=color, linewidth="5")
    ax_right.plot(data["time"], data["kanon"], color='black', linewidth="5")
    ax_third.stackplot(data["time"], to_plot, 
                        labels = labels ,alpha=0.4)
    ax_third.legend(loc='upper left', prop={"size":20})
    ax_left.set_xlabel('time', fontsize=20)
    ax_left.set_ylabel('z', color=color, fontsize=20)
    ax_left.autoscale()
    ax_third.autoscale()
    ax_third.set_ylabel('Tuple traffic', color = "blue", fontsize=20)
    ax_third.tick_params(axis='y', labelcolor="blue", labelsize=20.0)
    ax_right.set_ylim(bottom = 0.0, top = 1.0)
    ax_left.tick_params(axis='y', labelcolor=color, labelsize=20.0)
    ax_right.set_ylabel('pkanon', color='black', fontsize= 20)
    ax_right.tick_params(axis='y', labelcolor='black', labelsize = 20.0)
    ax_left.get_xaxis().set_major_locator(LinearLocator(numticks=20))
    ax_left.tick_params(labelsize=20)        
    fig.autofmt_xdate(rotation = 45)
    fig.tight_layout()
    fig.savefig('z_tuning.pdf')

with open('simu_trace.txt') as f:
    rows =  sum(1 for _ in f)
    
final_dataset = defaultdict(set)
file = open('output.txt','r')
gen = [0]*MAX_GENERALIZATION
tot = 0
for line in file:
    tot += 1
    t,u,a = line.split("\t")
    t = float(t)
    a.strip()          
    final_dataset[u].add(a)
    cat = a.split("*")
    gen[len(cat)] += 1

final_dataset_inv = defaultdict(list)
for k,v in final_dataset.items():
    final_dataset_inv[str(v)].append(k)
ks = np.array([len(v) for v in final_dataset_inv.values()])
for k in range(2,5):
    print("Final " + str(k) + "-anonymization: " + str(sum(ks[ks >= k])/sum(ks)))
    
for index,i in enumerate(gen):
    if(i == 0 and index == 0):
        continue
    elif(i == 0):
        break
    print("Tuple passed with " + str(index ) + "-details level: " + str(i))
print("Tuple anonymized: " + str(rows - tot))
    
