
"""
networkx version is 1.11 / 
"""

### Create the spatio-temporal networks of developers ###

#    Created on 2017
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI

"""Codes to create the network of developers who are spatially and temporally separated."""
""" Codes to get the average performance of developers and merge with the gml files as node attribiute."""
""" Codes to get the neighbor and ego effect

Provides:

 - countDuplicatesInList()
 - network_measures()
 - create_spatial_temporal_network_of_developers()
 - measure_developer_attributes()
 - spatio_temporal_network_neighbor_ego_effect()

References:
 - networkx: http://selenium-python.readthedocs.io/

Publication title:
 - Temporal and spatial distance and knowledge contribution
	(Under Preparation)
"""


import sys
import os, re
import networkx as nx
#from matplotlib import pyplot
import old_gml as nx_old
from itertools import combinations, product, permutations
from collections import defaultdict
import copy, difflib
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from sets import Set



def countDuplicatesInList(dupedList):
	uniqueSet = Set(item for item in dupedList)
	return [(item, dupedList.count(item)) for item in uniqueSet]

#------------------------------------------------------------------------------
# Compute the network measures
#------------------------------------------------------------------------------
def network_measures(graphname) :

	H = nx_old.read_gml(graphname)

	## Calculate the degree of nodes in the network

	for u,v in nx.degree(H).items() :
		H.node[u]['degree'] = int(v)

	## Compute betweenness centrality for nodes

	betweenness_dictionary = nx.betweenness_centrality(H)
	for u,v in betweenness_dictionary.items() :
		H.node[u]['betweenness_centrality'] = float(v)

	## Calculate the kshell-index of the network

	list_conn=[]
	for node in H.nodes():
		list_conn.append(len(H.neighbors(node)))
	max_connect=max(list_conn)

	H.remove_edges_from(H.selfloop_edges())

	for index in range (max_connect+1):
		k_core=nx.algorithms.core.k_shell(H,k=index)
		if len (k_core)>0:
			for node in k_core:
				H.node[node]['kshell_index']=int(index)


	H = nx_old.write_gml(H,str(graphname))


#------------------------------------------------------------------------------
# create the spatio-temporal network of developers from commit data
#------------------------------------------------------------------------------
def create_spatial_temporal_network_of_developers(f1, yearstr, gmlw) :
	'''
	Usage:
	f1 : read the file
	yearstr: Which year you want to generate the network
	gmlw: the gml file where we store the network with edge and node attributes

	node attributes: 
	::::

	- 'wt_n_com_code'
	Number of common files two developers commit on. The weight of the edge is count of 
	all such common files

	- 'mean_spatial_inter'
	Average of mean inter-line distance between two developers who commit on common files
	
	- 'std_spatial_inter'
	Standard deviation of inter-line distance between two developers who commit on common files

	- 'median_spatial_inter'
	Median of inter-line distance between two developers who commit on common files

	- 'diff_90_10_spatial'
	Difference of 90th and 10th percentile of lines between two developers who commit on common files

	- 'wt_hm_diff_first_commit_time' 
	Harmonic mean of difference of first commit time of two developers on common files

	- 'wt_hsum_diff_first_commit_time'
	Harmonic sum of difference of first commit time of two developers on common files

	- 'wt_hm_diff_last_commit_time' 
	Harmonic mean of difference of last commit time of two developers on common files

	- 'wt_hsum_diff_last_commit_time' 
	Harmonic sum of difference of last commit time of two developers on common files

	- 'wt_mean_joint_commit'
	Average of mean number of joint commits

	- 'wt_sum_joint_commit'
	sum of joint commits

	- 'wt_mu_inter_commit_time'
	Average of mean inter-commit time of two developers commiting on common files

	- 'wt_std_inter_commit_time'
	Standard deviation of inter-commit time of two developers commiting on common files

	- 'diff_90_10_temporal'
	Difference of 90th and 10th percentile of commit times between two developers who commit on common files

	'''

	data1 = open(f1, 'r') 
	dict_committer_codes = defaultdict(list); dict_committer_codes_complexity = defaultdict(list)
	dict_gen_network = defaultdict(list); dict_committer_codes_lines = defaultdict(list)
	dict_code_time_of_commit = defaultdict(list)

	for line in data1.readlines()[1:] :	
		line = line.strip().split('|')
		committer_name = str(line[4].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0]); 
		committer_id = committer_name 	
		commit_id_code = str(line[0])

		if " -" in str(line[6]) : 
			time_of_commit = str(line[6].split(', ')[1].split(' -')[0])

		if " +" in str(line[6]) : 
			time_of_commit = str(line[6].split(', ')[1].split(' +')[0])
 
		new_line = line[8].split('+')[1].split(',')
		if len(new_line) > 1:
			start_line = int(new_line[0]); end_line = start_line+int(new_line[1])

			year = int(line[9])

			if year == int(yearstr) :
				## spatial
				dict_committer_codes[commit_id_code].append(committer_id)
				dict_committer_codes_lines['/'.join(commit_id_code.split('/')[1:])+'|'+committer_id].append((start_line, end_line))

				## temporal
				dict_code_time_of_commit[commit_id_code+'|'+committer_id] = time_of_commit

	dict_code_commiter_time_of_commit = defaultdict(list)

	for keys, values in dict_code_time_of_commit.items() :
		codes = '/'.join(keys.split('|')[0].split('/')[1:])
		dict_code_commiter_time_of_commit[codes+'|'+keys.split('|')[1]].append(values)

	for keys, values in dict_committer_codes.items() :

		codes = keys.split('/')[1:]; setval = list(set(values))
		codes = '/'.join(codes)
		for v in setval :
			dict_gen_network[str(codes)].append(str(v))

	keylist = []; edgelist = []; G1 = nx.Graph()
	
	edgelist_mu = []; edgelist_median = []; edgelist_diff_90_10 = []; edgelist_std = []; edgelist_diff_90_10_temporal = []
	
	dict_mu_edges = defaultdict(list); dict_median_edges = defaultdict(list); dict_diff9010_edges = defaultdict(list); dict_diff9010_temporal = defaultdict(list)
	dict_inter_commit_time = defaultdict(list); dict_edge_list_first_time = defaultdict(list); dict_edge_list_last_time = defaultdict(list)
	
	dict_edge_list_joint_commit = defaultdict(list)

	edgelist_first_time_hm = []; edgelist_first_time_hsum = []; edgelist_last_time_hm = []; edgelist_last_time_hsum = []; edgelist_joint_commit_mean = []; edgelist_joint_commit_sum = []
	edgelist_del_time_mu = []; edgelist_del_time_std = []
	
	for k in dict_gen_network :
		vals = dict_gen_network[str(k)]

		combo = combinations(vals, 2)

		for (u,v) in combo :
			if str(u) != str(v) :

				### Now check for overlap of lines in same code by the co-developers ###
				lu = k+'|'+u ; lv = k+'|'+v
				nu = dict_committer_codes_lines[lu]; nv = dict_committer_codes_lines[lv]

				product_lines = product(nu, nv)

				for k1, k2 in product_lines :
					i1 = int(k1[0]); i2 = int(k1[1])
					j1 = int(k2[0]); j2 = int(k2[1])

					rangek1 = range(i1, i2)
					rangek2 = range(j1, j2)

					if len(list(set(rangek1)&set(rangek2))) > 0 :
					### Spatial weights generation 

						keylist.append((str(u), str(v), k))

						list_lines_codes = [i1, i2, j1, j2]; list_lines_codes.sort()
						inter_line_dist = [x - list_lines_codes[i-1] for i, x in enumerate(list_lines_codes)][1:]
						tenth_perc_line =  scipy.stats.scoreatpercentile(list_lines_codes, 10)
						ninetieth_perc_line =  scipy.stats.scoreatpercentile(list_lines_codes, 90)

						median_line_diff = np.median(inter_line_dist)
						mean_line_diff = np.mean(inter_line_dist)

						diff_90_10 = ninetieth_perc_line - tenth_perc_line

						dict_mu_edges[(str(u), str(v))].append(float(mean_line_diff))
						dict_median_edges[(str(u), str(v))].append(float(median_line_diff))
						dict_diff9010_edges[(str(u), str(v))].append(float(diff_90_10))

						### temporal weights generation

						if len(dict_code_commiter_time_of_commit[k+'|'+u]) > 0 and len(dict_code_commiter_time_of_commit[k+'|'+v]) > 0 :
							#print dict_code_commiter_time_of_commit[k+'|'+u], dict_code_commiter_time_of_commit[k+'|'+v]
							time_first_commit_i =  datetime.strptime(str(min([x for x in dict_code_commiter_time_of_commit[k+'|'+u]])), '%d %b %Y %H:%M:%S'); time_last_commit_i = datetime.strptime(str(max([x for x in dict_code_commiter_time_of_commit[k+'|'+u]])), '%d %b %Y %H:%M:%S')
							time_first_commit_j =  datetime.strptime(str(min([x for x in dict_code_commiter_time_of_commit[k+'|'+v]])), '%d %b %Y %H:%M:%S'); time_last_commit_j = datetime.strptime(str(max([x for x in dict_code_commiter_time_of_commit[k+'|'+v]])), '%d %b %Y %H:%M:%S')
							
							del_first_commit_ij = abs(time.mktime(time_first_commit_i.timetuple()) - time.mktime(time_first_commit_j.timetuple()))*1.0/(60*60*24)
							del_last_commit_ij = abs(time.mktime(time_last_commit_i.timetuple()) - time.mktime(time_last_commit_j.timetuple()))*1.0/(60*60*24)
							
							dict_edge_list_first_time[(str(u), str(v))].append(float(del_first_commit_ij))
							dict_edge_list_last_time[(str(u), str(v))].append(float(del_last_commit_ij))

							list_commit_time_i = [datetime.strptime(x,'%d %b %Y %H:%M:%S') for x in dict_code_commiter_time_of_commit[k+'|'+u]]; list_commit_time_j = [datetime.strptime(x,'%d %b %Y %H:%M:%S') for x in dict_code_commiter_time_of_commit[k+'|'+u]]
							list_commit_time = list_commit_time_i + list_commit_time_j ; list_commit_time.sort(); 

							inter_commit_time = [time.mktime(x.timetuple()) - time.mktime(list_commit_time[i - 1].timetuple()) for i, x in enumerate(list_commit_time)][1:]; 
							del_time_commit = [x*1.0/(60*60*24) for x in inter_commit_time]; 
							dict_inter_commit_time[(str(u), str(v))].append(float(np.mean(del_time_commit))); 
							num_commit_i = len(dict_code_commiter_time_of_commit[k+'|'+u]); num_commit_j = len(dict_code_commiter_time_of_commit[k+'|'+v]); 
							joint_commit_ij = num_commit_i + num_commit_j; 
							dict_edge_list_joint_commit[(str(u), str(v))].append(int(joint_commit_ij))

							tenth_perc_time =   scipy.stats.scoreatpercentile([time.mktime(x.timetuple()) for x in list_commit_time], 10)
							ninetieth_perc_time =  scipy.stats.scoreatpercentile([time.mktime(x.timetuple()) for x in list_commit_time], 90)

							
							diff_90_10_temporal = abs(ninetieth_perc_time - tenth_perc_time)*1.0/(60*60*24)

							dict_diff9010_temporal[(str(u), str(v))].append(float(diff_90_10_temporal))


	edgelistuniq = list(set(keylist))
	newedgesuniq = []
	for (u,v,p) in edgelistuniq :
		newedgesuniq.append((u, v))
	count_edge_weight = countDuplicatesInList(newedgesuniq)


	for (u,v), w in count_edge_weight :
		edgelist.append((u, v, w))

	for keys, values in dict_mu_edges.items() :
		u = keys[0]; v = keys[1]
		if str(u) != str(v) :
		##spatial 
			edgelist_mu.append((str(u), str(v), float(np.mean(values))))
			edgelist_std.append((str(u), str(v), float(np.std(values))))
			edgelist_median.append((str(u), str(v), float(np.median(dict_median_edges[keys]))))
			edgelist_diff_90_10.append((str(u), str(v), float(np.mean(dict_diff9010_edges[keys]))))
		
		##call temporal
			values_first_time = dict_edge_list_first_time[(str(u), str(v))]
			k1_node = keys[0]; k2_node = keys[1]; xinv_first_time = [1.0/x for x in values_first_time]

			values_last_time = dict_edge_list_last_time[(k1_node, k2_node)]; xinv_last_time = [1.0/x for x in values_last_time]; 
			values_diff9010_temp = dict_diff9010_temporal[(k1_node, k2_node)]


			weights_first_time_hm = np.mean(xinv_first_time); weights_first_time_hsum = np.sum(xinv_first_time)
			weights_last_time_hm = np.mean(xinv_last_time); weights_last_time_hsum = np.sum(xinv_last_time)
			weights_joint_commit_sum = np.sum(dict_edge_list_joint_commit[(k1_node, k2_node)])
			weights_joint_commit_avg = np.mean(dict_edge_list_joint_commit[(k1_node, k2_node)])
		
			edgelist_first_time_hm.append((k1_node, k2_node, weights_first_time_hm))
			edgelist_last_time_hm.append((k1_node, k2_node, weights_last_time_hm))
			edgelist_first_time_hsum.append((k1_node, k2_node, weights_first_time_hsum))
			edgelist_last_time_hsum.append((k1_node, k2_node, weights_last_time_hsum))
			edgelist_joint_commit_mean.append((k1_node, k2_node, weights_joint_commit_avg))
			edgelist_joint_commit_sum.append((k1_node, k2_node, weights_joint_commit_sum))
		
			del_time = [x for x in dict_inter_commit_time[(k1_node, k2_node)]]
			edgelist_del_time_mu.append((k1_node, k2_node, np.mean(del_time)))
			edgelist_del_time_std.append((k1_node, k2_node, np.std(del_time))); 
			edgelist_diff_90_10_temporal.append((k1_node, k2_node, float(np.mean(values_diff9010_temp))))

	### Spatial weights ####

	G1.add_weighted_edges_from(edgelist,weight="wt_n_com_code")
	G1.add_weighted_edges_from(edgelist_mu,weight="mean_spatial_inter")
	G1.add_weighted_edges_from(edgelist_std,weight="std_spatial_inter")	
	G1.add_weighted_edges_from(edgelist_median,weight="median_spatial_inter")
	G1.add_weighted_edges_from(edgelist_diff_90_10,weight="diff_90_10_spatial")
	
	G1.add_weighted_edges_from(edgelist_first_time_hm, weight="wt_hm_diff_first_commit_time") ## form the network of committers using the harmonic mean of difference of commit time
	G1.add_weighted_edges_from(edgelist_first_time_hsum, weight="wt_hsum_diff_first_commit_time") ## form the network of committers using the harmonic sum of difference of commit time
	G1.add_weighted_edges_from(edgelist_last_time_hm, weight="wt_hm_diff_last_commit_time") ## form the network of committers
	G1.add_weighted_edges_from(edgelist_last_time_hsum, weight="wt_hsum_diff_last_commit_time") ## form the network of committers using the harmonic mean of difference of commit time
	G1.add_weighted_edges_from(edgelist_joint_commit_mean, weight="wt_mean_joint_commit") ## form the network of committers using the harmonic sum of difference of commit time
	G1.add_weighted_edges_from(edgelist_joint_commit_sum, weight="wt_sum_joint_commit") ## form the network of committers using the harmonic sum of difference of commit time
	G1.add_weighted_edges_from(edgelist_del_time_mu, weight="wt_mu_inter_commit_time")
	G1.add_weighted_edges_from(edgelist_del_time_std, weight="wt_std_inter_commit_time")
	G1.add_weighted_edges_from(edgelist_diff_90_10_temporal, weight="diff_90_10_temporal")

	weightlists = ['wt_n_com_code', 'mean_spatial_inter', 'std_spatial_inter', 'median_spatial_inter', 'diff_90_10_spatial', 'wt_hm_diff_first_commit_time', 'wt_hsum_diff_first_commit_time', 'wt_hm_diff_last_commit_time', 'wt_hsum_diff_last_commit_time', 'wt_mean_joint_commit', 'wt_sum_joint_commit', 'wt_mu_inter_commit_time', 'wt_std_inter_commit_time','diff_90_10_temporal']

	## Compute weighted degree (strength) for nodes
	for wtl in weightlists :
		for u,v in nx.degree(G1,weight=str(wtl)).items() :
			G1.node[u]['s'+'_'+str(wtl)] = float(v)

	## Compute weighted betweenness centrality for nodes
	for wtl in weightlists :
		betweenness_dictionary = nx.betweenness_centrality(G1,weight=str(wtl),normalized=True)
		for u,v in betweenness_dictionary.items() :
			G1.node[u]['nbc'+'_'+str(wtl)] = float(v)

	H = G1

	list_conn=[]
	for node in H.nodes():
		list_conn.append(len(H.neighbors(node)))
	max_connect=max(list_conn)
	H.remove_edges_from(H.selfloop_edges())
	for index in range (max_connect+1):
		k_core=nx.algorithms.core.k_shell(H,k=index)
		if len (k_core)>0:
			for node in k_core:
				H.node[node]['kshell_index']=int(index)

	H = nx_old.write_gml(H, str(gmlw))

def measure_developer_attributes(fadd, frem, fcompl, yearstr, gml1) :

	'''
	Usage:

	fadd : The file containing lines of code added by developers
	frem: The file containing lines of code removed by developers
	fcompl: The file containing code complexity
	yearstr: Which year you want to generate the network
	gml1: the gml file where we store the network with edge and node attributes

	'''

	from datetime import datetime
	import time
	data_add = open(fadd, 'r'); data_rem = open(frem, 'r'); G = nx_old.read_gml(gml1); data_compl = open(fcompl, 'r')

	dict_committer_code_add = defaultdict(list); dict_committer_code_rem = defaultdict(list); dict_committer_code_CC = defaultdict(list); dict_committer_code_HV = defaultdict(list); dict_committer_code_MI = defaultdict(list);
	dict_committer_tenure = defaultdict(list);  dict_committer_codes_complexity = defaultdict(list)

	### file with lines of code added info
	for line in data_add.readlines()[1:] :
		line = line.strip().split('|')
		committer_name = line[6].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0]

		if " -" in str(line[8]) : 
			time_of_commit = str(line[8].split(', ')[1].split(' -')[0])
		if " +" in str(line[8]) : 
			time_of_commit = str(line[8].split(', ')[1].split(' +')[0])

		year = time_of_commit.split(' ')[2]
		if int(year) == int(yearstr) :
			dict_committer_tenure[str(committer_name)].append(time_of_commit)
			dict_committer_code_add[str(committer_name)].append(int(line[0]))

	### file with lines of code removed info
	for line in data_rem.readlines()[1:] :
		line = line.strip().split('|')
		committer_name = line[6].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0]

		if " -" in str(line[8]) : 
			time_of_commit = str(line[8].split(', ')[1].split(' -')[0])
		if " +" in str(line[8]) : 
			time_of_commit = str(line[8].split(', ')[1].split(' +')[0])

		year = time_of_commit.split(' ')[2]
		if int(year) == int(yearstr) :
			dict_committer_code_rem[str(committer_name)].append(int(line[0]))

	##get matching of above two dataset
	dict_commiter_info = defaultdict(list)
	for keys, values in dict_committer_code_add.items() :
		if str(keys) in dict_committer_code_rem :

			total_lines_of_code_added = np.sum(values)
			avg_lines_of_code_added = np.mean(values)

			total_lines_of_code_removed = np.sum(dict_committer_code_rem[str(keys)])
			avg_lines_of_code_removed = np.sum(dict_committer_code_rem[str(keys)])

			time_first_committed = datetime.strptime(str(min([x for x in dict_committer_tenure[str(keys)]])), '%d %b %Y %H:%M:%S')

			time_last_committed = datetime.strptime(str(max([x for x in dict_committer_tenure[str(keys)]])), '%d %b %Y %H:%M:%S')

			tenure_committer = abs(time.mktime(time_first_committed.timetuple()) - time.mktime(time_last_committed.timetuple()))*1.0/(60*60*24)

			total_num_committs = len(dict_committer_tenure[str(keys)])

			dict_commiter_info[str(keys)] = str(total_lines_of_code_added)+'|'+str(avg_lines_of_code_added)+'|'+str(total_lines_of_code_removed)+'|'+str(avg_lines_of_code_removed)+'|'+str(tenure_committer)+'|'+str(total_num_committs)

	for line in data_compl.readlines()[1:] :
		line = line.strip().split('|')
		committer_name = str(line[4].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0]); 
		commit_id_code = str(line[0])
		new_line = line[8].split('+')[1].split(',')
		if len(new_line) > 1:
			start_line = int(new_line[0]); end_line = start_line+int(new_line[1])
			year = int(line[9])
			if year == int(yearstr) :
				dict_committer_codes_complexity[commit_id_code+'|'+committer_name] = line[11]+'|'+line[18]+'|'+line[19]



	for keys, values in dict_committer_codes_complexity.items() :
		committer_name = keys.split('|')[1]
		MI = values.split('|')[0]; HV = values.split('|')[1]; CC = values.split('|')[2]

		dict_committer_code_MI[str(committer_name)].append(float(MI))
		dict_committer_code_HV[str(committer_name)].append(float(HV))
		dict_committer_code_CC[str(committer_name)].append(float(CC))

	dict_commiter_info_compl  = defaultdict(list)

	for keys, values in dict_committer_code_MI.items() :

		avg_MI_committer = np.mean(values)
		avg_HV_committer = np.mean(dict_committer_code_HV[str(keys)])
		avg_CC_committer = np.mean(dict_committer_code_CC[str(keys)])

		if str(keys) in dict_commiter_info :

			info = dict_commiter_info[str(keys)] 
			dict_commiter_info_compl[str(keys)] = info+'|'+str(avg_MI_committer)+'|'+str(avg_HV_committer)+'|'+str(avg_CC_committer)


	for nodes in G.nodes() :
		if str(G.node[nodes]['label']) in dict_commiter_info_compl :

			info = dict_commiter_info_compl[str(G.node[nodes]['label'])]

			lines_of_code_added_sum = info.split('|')[0]
			lines_of_code_added_avg = info.split('|')[1]
			lines_of_code_removed_sum = info.split('|')[2]
			lines_of_code_removed_mean = info.split('|')[3]
			tenure_committer = info.split('|')[4]
			total_num_committs = info.split('|')[5]

			MI = info.split('|')[6]
			HV = info.split('|')[7]
			CC = info.split('|')[8]

			G.node[nodes]['lines_of_code_added_sum'] = float(lines_of_code_added_sum)
			G.node[nodes]['lines_of_code_added_avg'] = float(lines_of_code_added_avg)
			G.node[nodes]['lines_of_code_removed_sum'] = float(lines_of_code_removed_sum)
			G.node[nodes]['lines_of_code_removed_mean'] = float(lines_of_code_removed_mean)
			G.node[nodes]['tenure_committer'] = float(tenure_committer)
			G.node[nodes]['total_num_committs'] = float(total_num_committs)
			G.node[nodes]['avg_MI_committer'] = float(MI)
			G.node[nodes]['avg_HV_committer'] = float(HV)
			G.node[nodes]['avg_CC_committer'] = float(CC)
	### triangles ###

	for node, val in nx.triangles(G).items() :
		G.node[node]['triangle'] = float(val)

	### local clustering coefficient ###
	weightlists = ['wt_n_com_code', 'mean_spatial_inter', 'std_spatial_inter', 'median_spatial_inter', 'diff_90_10_spatial', 'wt_hm_diff_first_commit_time', 'wt_hsum_diff_first_commit_time', 'wt_hm_diff_last_commit_time', 'wt_hsum_diff_last_commit_time', 'wt_mean_joint_commit', 'wt_sum_joint_commit', 'wt_mu_inter_commit_time', 'wt_std_inter_commit_time']
	for wtl in weightlists :
		for node, val in nx.clustering(G, weight=str(wtl)).items() :
			G.node[node]['LCC'+'_'+str(wtl)] = float(val)

	list_attr_dv = ['lines_of_code_added_sum', 'lines_of_code_added_avg', 'lines_of_code_removed_sum', 'lines_of_code_removed_mean', 'total_num_committs']

	G = nx_old.write_gml(G, str(gml1))

def spatio_temporal_network_neighbor_ego_effect(gml_file) :

	'''
	Here we generate the data of neighbor's contribution and Ego network's contribution
	in terms of lines of code added, lines of code removed, total number of commits
	'''

	G = nx_old.read_gml(str(gml_file))
	list_attr_dv = ['lines_of_code_added_sum', 'lines_of_code_added_avg', 'lines_of_code_removed_sum', 'lines_of_code_removed_mean', 'total_num_committs']

	### neighbors and Ego of a committer
	for x in list_attr_dv :
		print x
		for n in G.nodes() :
	
			try :
				G.node[n]['neigh'+'_'+str(x)] = np.mean([G.node[k][str(x)] for k in G.neighbors(n)])
				G.node[n]['ego'+'_'+str(x)] = np.mean([G.node[k][str(x)] for k in nx.ego_graph(G, n)])
			except KeyError,e :
				print n, G.neighbors(n), len(G.neighbors(n))
					
	G = nx_old.write_gml(G, str(gml_file))

if __name__ == '__main__':
	

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3];
	#create_spatial_temporal_network_of_developers(f1, f2, f3)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]; f5 = sys.argv[5]
	#measure_developer_attributes(f1, f2, f3, f4, f5)

	f1 = sys.argv[1]
	spatio_temporal_network_neighbor_ego_effect(f1)
