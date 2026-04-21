#!/bin/bash
#!/change/home/path/to/python/ python3

echo "set parameters"

l_n_gw=(5 25 50 100 250 500 1000 1500)
l_n_max_sm=(20)
l_z=(0 5 10 25 50 100)
l_seed=(1 2 3 4 5 6 7 8 9 10)
cd /change/path/to/deZent/src/

echo "start bash script now"

### all users simulation for centralized scenario
for z in "${l_z[@]}"
do
    for n_gw in "${l_n_gw[@]}"
    do
    	for n_max_sm in "${l_n_max_sm[@]}"
    	do
    		for seed in "${l_seed[@]}"
    		do
        		echo $z
        		echo $n_gw
        		echo $n_max_sm
        		echo $seed
        		python3 main.py $n_gw $n_max_sm $z $seed
        	done
        done
    done
done

echo "finished successfully"
