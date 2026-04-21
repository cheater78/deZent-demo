import matplotlib.pyplot as plt
import numpy as np
import json
from collections import defaultdict
import pathlib

def plot_ca():
    params = json.loads(open('output_params.json', 'r').read())
    start = params['start']
    c_oa = params['c_oa']
    t_oa = params['t_oa']
    observed_attributes = params['observed_attributes']
    plt.figure(figsize = (10,6))
    plt.xlabel('s')
    plt.ylabel('c_a')
    #plt.plot([0, stop-start], [z, z], '--', label = 'z')
    for oa in observed_attributes:
        plt.plot([(x - start) for x in t_oa[oa]], c_oa[oa], label = oa)

    #plt.xticks()
    plt.grid()
    plt.legend()
    plt.show()

def get_pkanon_with_cat(output, z):
    pathlib.Path('./output/').mkdir(parents=True, exist_ok=True) 
    f = open('output/out_{:02d}.txt'.format(z), 'w+')
    attribute_set = set()
    final_dataset = defaultdict(set)
    for o in output:
        record = o[0] #tuple in the form (timestamp, user, attribute)
        c_a = o[1] #list of counters per category, most general to the left
        for i, level in enumerate(reversed(c_a)): #read the counters from the one reffering to the most specific category
            level = int(level)
            if level >= z: #if the counter satisfy the threshold, select the appropriate level of generalization
                if i == 0:
                    a = record[2] #if the most specific category satisfies the threshold, output the whole attribute
                else:
                    a = '*'.join(record[2].split('*')[:-i]) #else, remove the z-private specifications
                final_dataset[record[1]].add(a)
                if a not in attribute_set:
                    attribute_set.add(a)
                    f.write(a + '\n')
                break
    f.close()
    final_dataset_inv = defaultdict(list)
    for k,v in final_dataset.items():
            final_dataset_inv[str(v)].append(k)

    #ks = np.array([len(v) for v in final_dataset_inv.values()])
    return final_dataset_inv

def get_pkanon_without_cat(output, z):
    final_dataset = defaultdict(set)
    for o in output:
        record = o[0]
        c_a = int(o[1][-1])
        if c_a >= z:
            final_dataset[record[1]].add(record[2])

    final_dataset_inv = defaultdict(list)
    for k,v in final_dataset.items():
            final_dataset_inv[str(v)].append(k)

    #ks = np.array([len(v) for v in final_dataset_inv.values()])
    return final_dataset_inv

        
def pkanon_vs_z():
    output = []
    for line in open('simulation_output.txt', 'r'):
        items = line.split('\t')
        output.append(((float(items[0]), items[1], items[2]), [x for x in items[3:]]))
    
    z_range = range(1, 51)
    #k1 = []
    k2 = []
    k3 = []
    k4 = []
    k2_nocat = []
    for z in z_range:
        ks = np.array([len(v) for v in get_pkanon_with_cat(output, z).values()])
        k2.append(sum(ks[ks >= 2])/sum(ks))
        k3.append(sum(ks[ks >= 3])/sum(ks))
        k4.append(sum(ks[ks >= 4])/sum(ks))
        ks_nocat = np.array([len(v) for v in get_pkanon_without_cat(output, z).values()])
        if (sum(ks_nocat) == 0):
            break
        k2_nocat.append(sum(ks_nocat[ks_nocat >= 2])/sum(ks_nocat))
    
    plt.figure()
    plt.xlabel('z')
    plt.ylabel('p_kanon')
    plt.plot(z_range, k2, label = 'w/ categories')
    plt.plot(z_range, k2_nocat, label = 'w/o categories')
    plt.ylim(bottom = 0., top = 1.)
    plt.legend()
    plt.savefig('pkanon_cat_nocat.pdf')
    plt.show()
    
    plt.figure()
    plt.xlabel('z')
    plt.ylabel('p_kanon')
    plt.plot(z_range, k2, label = 'k = 2')
    plt.plot(z_range, k3, label = 'k = 3')
    plt.plot(z_range, k4, label = 'k = 4')
    plt.ylim(bottom = 0., top = 1.)
    plt.legend()
    plt.savefig('pkanon_vs_k.pdf')
    plt.show()
    
def evaluate_output():
    #plot_ca()
    pkanon_vs_z()
    
    
    