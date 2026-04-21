import sys
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
MAX_GENERALIZATION = 20

def evaluate(z):
    categories = {}
    count_attr = [0]*MAX_GENERALIZATION #count number of records passed per level of generalization
    count_cat = {} #count distinct categories/attributes passed per level of generalization
    j = 0
    for line in open("simulation_output.txt","r"):
        items = line.split("\t")
        for i,count in enumerate(items[3::][::-1]):         
            if (int(count) >= z):
                if (i == 0):
                    lev = items[2]
                else: 
                    lev = '*'.join(items[2].split('*')[:-i])
                j += 1
                count_attr[i] += 1              
                if i not in count_cat:
                    count_cat[i] = [lev]
                else: 
                    if lev not in count_cat[i]:
                        count_cat[i].append(lev)                
                if(lev not in categories):
                    categories[lev] = 1
                else: categories[lev] += 1 
                break
    dict = {k: v for k, v in sorted(categories.items(), key=lambda item: item[1], reverse = True)}
    f = open("categories_zanon.txt", "w")  #store top categories 
    for i in dict:
        f.write(i + ": " + str(dict[i]) + "\n")
    f.close()
    
    fig = plt.figure(figsize=(8,8))
    plt.barh(list(dict.keys())[:40],list(dict.values())[:40])
    plt.gca().invert_yaxis() 
    plt.title("Top 40 attributes/categories over threshold with z = " + str(z))
    plt.tight_layout()
    plt.savefig('categories.pdf')
    
    print("Outputs over threshold with z = " + str(z) + ": " + str(j))
    for index,i in enumerate(count_attr):
        if((i) == 0):
            break
        print("With " + str(index) + "-generalization: " + str(i) + ". Distinct: " + str(len(count_cat[index])))
    print("Number of distinct outputs over threshold: " + str(len(categories)))
    
def evaluate_cat(zeta):
    evaluate(zeta)
    
