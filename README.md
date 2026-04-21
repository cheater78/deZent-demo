### deZent - Local z-anonymity with minimal coordination ###
The repository contains the implementation and simulation details for deZent that is published on arXiv (https://arxiv.org/abs/2603.08854).
deZent realizes z-anonymity in a decentralized system, e.g., in sensor networks that are used for smart metering. 
The work is based on centralized z-anonymity that was published by Jha et al. (DOI: 10.1109/BigData50022.2020.9378422, https://github.com/nikhiljha95/zanonymity).
By introducing minimal coordination between middle nodes, e.g. gateways, deZent generates output that is similar to centralized z-anonymity while increasing privacy protection.

This repository facilitates the complete reproduction of the results published on arXiv. 
The data base, model validation, and simulation details are made available and should be fully reproducible.
In case of any doubts, please do not hesitate to contact the authors.

For the simulation of deZent, a virtual network is generated with gateways (GW) that are connected in a ring, each GW knowing its predecessor and successor.
Each GW is managing several smart meters (SM) that report consumption values in regular intervals. The GWs forward measurement values to a central entity for publication.
Regular consumption measurement can reveal sensitive personal information, e.g., daily schedules and socio-economic status based on electricity consumption. Therefore, privacy-preserving technologies are needed.
z-anonymity prevents re-identification we implement z-anonymity at GW level such that only anonymized data points are published towards the central entity.

Simulation parameters that can be changed are: value of z, number of GWs in the network, average number of SMs per GW, random seed
Consumption measurements are simulated based on user profiles and standard load profiles. The distribution of user profiles is chosen based on real statistical distributions to represent a district in Berlin. The parameters and statistics are documented in /deZent/profile_distribution.py

## Enable virtual environment
	python3 -m venv .venv
	..venv\Scripts\activate (Windows)
	source .venv/bin/activate (Linux)
    
## Install packages
	pip3 install -r requirements.txt
	
## Run deZent simulation
	Command line:
		* navigate to deZent/src/
		* python3 main.py <n_gw> <n_max_sm> <z> <seed>
	Bash script
		* exemplary bash script in /scripts/
		* adapt paths to own system path
		* chmod +x run_zanon_simu.sh
		* ./run_zanon_simu.h
		* !Simulating all parameter combinations at once takes a long while! You can split the parameters to several bash files and execute them simultaneously
		
## Run Jha simulation
	* !deZent needs to be executed first!
	* to compare the output that is generated with z-anonymity by Jha et al., the simulation with Jha uses the simulation log files that are written during the deZent simulation (log_data)
	* navigate to jha_cent_zanon
	* change simulation parameters in test_zanon.py (e.g., l_n_gw, z_val)
	* run test_zanon.py
	
## Model validation
	* to verify that we implement z-anonymity, we compare the results of centralized deZent and the implementation with Jha et al.
	* analyze_pub_diff.py analyzes the difference of number of published data points and publication ratio for chosen scenarios
	* the programs *_tex*.py can be used to generate ouput for Latex pfg-plots
	
## Data analysis
	* the programs in /data_analysis/analyze_simulation/ are used to evaluate the results reported in the evaluation of the deZent paper
	* analyze_simu_stats.py calculates simulation statistics that are saved in csv files
	* extract_*_tex.py can be used to extract the corresponding data for pgf plots
	
	
	
	
