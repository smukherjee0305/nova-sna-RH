#    Created on 2017
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI

"""Codes to generate simulated network of developers using Monte Carlo sampling technique."""
"""

Provides:

 - null_model_shuffle_edge_weights()
 - gen_null_network_from_raw_data()
 - spatio_temporal_network_neighbor_ego_effect()

References:
 - networkx:     https://networkx.github.io/
 - Monte Carlo Hypothesis: https://en.wikipedia.org/wiki/Monte_Carlo_method

 Publications where the script is being used:
 - Temporal and spatial distance and knowledge contribution
	(Under Preparation)
"""

import numpy as np
import itertools
import sys
from operator import itemgetter
import itertools as it
from collections import defaultdict, Counter
import glob, copy
import scipy as sp
import scipy.stats
from random import choice, shuffle, sample, random
import networkx as nx
import old_gml as nx_old
from itertools import combinations, product, permutations
from datetime import datetime
import time
from sets import Set



def null_model_shuffle_edge_weights(gml1, year, nsim) :
	
	## Here we shuffle the weight of edges (temporal and spatial). Thus two edge-pairs (u1,v1) of weight w1 
	## and (u2, v2) of weight w2 shuffled and resultant weighted edge-pairs are (u1, v1, w1) and (u2, v2, w2)
	## Then we get the strength of the nodes as per the weighted spatial and temporal edges 


	##create the destination folder ##

	destdir = '../../Idea03_06/Data/Null/networks_from_edge_val_shuffle/'+str(year)+'/'
	for i in range(0, int(nsim)+1, 1) :
		G = nx_old.read_gml(gml1)

	## generate a null network and add the links from the observed network
		G_null = nx.Graph()
		
		spatial_list_edge = []; temporal_list_edge = []; edge_list = []
		committer_names_list_with_attr = []

		for (u, v, d) in G.edges(data=True) :
			spatial_list_edge.append(d['mean_spatial_inter']) 
			temporal_list_edge.append(d['wt_mu_inter_commit_time'])
			edge_list.append((G.node[u]['label'], G.node[v]['label']))

		shuffle(spatial_list_edge, random)
		shuffle(temporal_list_edge, random)


		#shuffle_spatial = sample(spatial_list_edge, len(spatial_list_edge))
		#shuffle_temporal = sample(temporal_list_edge, len(temporal_list_edge))

		z = zip(edge_list, spatial_list_edge, temporal_list_edge)

		G_null.add_weighted_edges_from([(z1[0], z1[1], z2) for (z1, z2, z3) in z],weight="mean_spatial_inter")
		G_null.add_weighted_edges_from([(z1[0], z1[1], z3) for (z1, z2, z3) in z],weight="wt_mu_inter_commit_time")

		weightlists = ["mean_spatial_inter", "wt_mu_inter_commit_time"]
		
		for wtl in weightlists :
			for u,v in nx.degree(G_null,weight=str(wtl)).items() :
				G_null.node[u]['s'+'_'+str(wtl)] = float(v)

		dict_id_name = defaultdict(list)

		for n in G.nodes() :

			committer_name = str(G.node[n]['label'])
			lines_of_code_added_sum = str(G.node[n]['lines_of_code_added_sum'])
			tenure_committer = str(G.node[n]['tenure_committer'])
			avg_MI_committer = str(G.node[n]['avg_MI_committer'])

			dict_id_name[committer_name] = lines_of_code_added_sum+'|'+tenure_committer+'|'+avg_MI_committer

		for n in G_null.nodes() :
			if str(n) in dict_id_name :
				vals = dict_id_name[str(n)]

				G_null.node[n]['label'] = str(n)
				G_null.node[n]['lines_of_code_added_sum'] = float(vals.split('|')[0])
				G_null.node[n]['tenure_committer'] = float(vals.split('|')[1])
				G_null.node[n]['avg_MI_committer'] = float(vals.split('|')[2])		

		gmlw = destdir+'sim__'+str(i)+'.gml'
		
		G_null = nx_old.write_gml(G_null, str(gmlw))



def gen_null_network_from_raw_data(f1, destdir, n0, n1, n2, n3, nsim, yearstr, gml1) :

	data1 = open(f1, 'r') 

	dict_id_name = defaultdict(list)

	G = nx_old.read_gml(gml1)

	for n in G.nodes() :
		try:

			committer_name = str(G.node[n]['label'])
			lines_of_code_added_sum = str(G.node[n]['lines_of_code_added_sum'])
			tenure_committer = str(G.node[n]['tenure_committer'])
			avg_MI_committer = str(G.node[n]['avg_MI_committer'])

			dict_id_name[committer_name] = lines_of_code_added_sum+'|'+tenure_committer+'|'+avg_MI_committer

		except KeyError,e :
			continue
			
	committernameslist = []
	commit_id_code_list = []
	commit_time_list = []
	lines_list = []

	for line in data1.readlines()[1:] :	
			line = line.strip().split('|')

			c0 = int(n0); c1 = int(n1); c2 = int(n2); c3 = int(n3)

			committer_name = str(line[c1].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0]); 
			committer_id = committer_name 	
			commit_id_code = str(line[c0])

			if " -" in str(line[c2]) : 
				time_of_commit = str(line[c2].split(', ')[1].split(' -')[0])

			if " +" in str(line[c2]) : 
				time_of_commit = str(line[c2].split(', ')[1].split(' +')[0])
 
			new_line = line[c3].split('+')[1].split(',')
			if len(new_line) > 1:
				start_line = int(new_line[0]); end_line = start_line+int(new_line[1])
				year = int(line[9])

				if year == int(yearstr):

					committernameslist.append(committer_id)
					lines_list.append(commit_id_code+'|'+str(start_line)+'|'+str(end_line))
					commit_time_list.append(time_of_commit)

	#print len(committernameslist), len(lines_list), len(commit_time_list)

	for isim in range(0, int(nsim)+1, 1) :
		
		shuffle(lines_list, random)
		shuffle(commit_time_list, random)

		zip_info = zip(committernameslist, lines_list, commit_time_list)
		
		#print isim, len(zip_info)

		dict_committer_codes = defaultdict(list); dict_committer_codes_complexity = defaultdict(list)
		
		dict_gen_network = defaultdict(list); dict_committer_codes_lines = defaultdict(list)
		
		dict_code_time_of_commit = defaultdict(list)
		
		dict_code_commiter_time_of_commit = defaultdict(list)

		for z1, z2, z3 in zip_info :
					committer_id = z1
					commit_id_code = z2.split('|')[0]
					start_line = int(z2.split('|')[1])
					end_line = int(z2.split('|')[2])
					time_of_commit = z3

					#print commit_id_code, committer_id, start_line, end_line, time_of_commit

					## spatial
					dict_committer_codes[commit_id_code].append(committer_id)
					dict_committer_codes_lines['/'.join(commit_id_code.split('/')[1:])+'|'+committer_id].append((start_line, end_line))

					## temporal
					dict_code_time_of_commit[commit_id_code+'|'+committer_id] = time_of_commit


		for keys, values in dict_code_time_of_commit.items() :
			codes = '/'.join(keys.split('|')[0].split('/')[1:])
			dict_code_commiter_time_of_commit[codes+'|'+keys.split('|')[1]].append(values)

		for keys, values in dict_committer_codes.items() :

			codes = keys.split('/')[1:]; setval = list(set(values))
			codes = '/'.join(codes)
			for v in setval :
				dict_gen_network[str(codes)].append(str(v))



		keylist = []; edgelist = []; G_null = nx.Graph(); G1 = G_null
	
		edgelist_mu = []
		edgelist_del_time_mu = []
	
		dict_mu_edges = defaultdict(list); 
		dict_inter_commit_time = defaultdict(list)
	

		### shuffle the spatial componentes 
		#keys_sp = dict_committer_codes_lines.keys()
		#shuffle(keys_sp, random)
		#dict_spatial_separation = dict(zip(keys_sp, dict_committer_codes_lines.values()))

		### shuffle the temporal componentes 
		#keys_tp = dict_code_commiter_time_of_commit.keys()
		#shuffle(keys_tp, random)
		#dict_temporal_separation = dict(zip(keys_tp, dict_code_commiter_time_of_commit.values()))

		#print dict_gen_network

		for k in dict_gen_network :
			vals = dict_gen_network[str(k)]

			combo = combinations(vals, 2)

			for (u,v) in combo :
				if str(u) != str(v) :

					### Now check for overlap of lines in same code by the co-developers ###
					lu = k+'|'+u ; lv = k+'|'+v
					nu = dict_committer_codes_lines[lu]; nv = dict_committer_codes_lines[lv]

					#print lu, dict_committer_codes_lines[lu], lv, dict_committer_codes_lines[lv]

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

							mean_line_diff = np.mean(inter_line_dist)

							dict_mu_edges[(str(u), str(v))].append(float(mean_line_diff))

							### temporal weights generation

							if len(dict_code_commiter_time_of_commit[k+'|'+u]) > 0 and len(dict_code_commiter_time_of_commit[k+'|'+v]) > 0 :


								list_commit_time_i = [datetime.strptime(x,'%d %b %Y %H:%M:%S') for x in dict_code_commiter_time_of_commit[k+'|'+u]]; list_commit_time_j = [datetime.strptime(x,'%d %b %Y %H:%M:%S') for x in dict_code_commiter_time_of_commit[k+'|'+u]]
								list_commit_time = list_commit_time_i + list_commit_time_j ; list_commit_time.sort(); 

								inter_commit_time = [time.mktime(x.timetuple()) - time.mktime(list_commit_time[i - 1].timetuple()) for i, x in enumerate(list_commit_time)][1:]; 
								del_time_commit = [x*1.0/(60*60*24) for x in inter_commit_time]; 
								dict_inter_commit_time[(str(u), str(v))].append(float(np.mean(del_time_commit))); 


		for keys, values in dict_mu_edges.items() :
			u = keys[0]; v = keys[1]
			if str(u) != str(v) :

				##spatial 
				edgelist_mu.append((str(u), str(v), float(np.mean(values))))
		
				##call temporal
				k1_node = keys[0]; k2_node = keys[1]; 
				del_time = [x for x in dict_inter_commit_time[(k1_node, k2_node)]]
				edgelist_del_time_mu.append((k1_node, k2_node, np.mean(del_time)))

		### Spatial weights and Temporal weights ####

		G1.add_weighted_edges_from(edgelist_mu,weight="mean_spatial_inter")
	
		G1.add_weighted_edges_from(edgelist_del_time_mu, weight="wt_mu_inter_commit_time")

		weightlists = ['mean_spatial_inter', 'wt_mu_inter_commit_time']

		for wtl in weightlists :
			for u,v in nx.degree(G1,weight=str(wtl)).items() :
				G1.node[u]['s'+'_'+str(wtl)] = float(v)


		for n in G1.nodes() :
			if str(n) in dict_id_name :
				vals = dict_id_name[str(n)]

				try :

					G1.node[n]['label'] = str(n)
					G1.node[n]['lines_of_code_added_sum'] = float(vals.split('|')[0])
					G1.node[n]['tenure_committer'] = float(vals.split('|')[1])
					G1.node[n]['avg_MI_committer'] = float(vals.split('|')[2])		
					G1.node[n]['neigh_lines_of_code_added_sum'] = np.mean([G1.node[k][str(x)] for k in G1.neighbors(n)])
					G1.node[n]['ego_lines_of_code_added_sum'] = np.mean([G1.node[k][str(x)] for k in nx.ego_graph(G1, n)])

				except KeyError, e:
					continue

		gmlw = destdir+'sim__'+str(isim)+'.gml'

		G1 = nx_old.write_gml(G1, str(gmlw))

def spatio_temporal_network_neighbor_ego_effect(sourcedir, destdir) :
				
	globgml = glob.glob(sourcedir+'*.gml')

	for gml_file in globgml :
		
		outname = gml_file.split('/')[-1]

		G = nx_old.read_gml(gml_file)
		list_attr_dv = ['lines_of_code_added_sum']

	### neighbors and Ego of a committer
		for x in list_attr_dv :

			for n in G.nodes() :
	
				try :
					G.node[n]['neigh'+'_'+str(x)] = np.mean([G.node[k][str(x)] for k in G.neighbors(n)])
					G.node[n]['ego'+'_'+str(x)] = np.mean([G.node[k][str(x)] for k in nx.ego_graph(G, n)])
				except KeyError,e :
					print gml_file, n, G.neighbors(n), len(G.neighbors(n))

		G = nx_old.write_gml(G, destdir+str(outname))




if __name__ == '__main__':

	f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]; f5 = sys.argv[5]; f6 = sys.argv[6]; f7 = sys.argv[7]; f8 = sys.argv[8]; f9 = sys.argv[9]
	#null_model_shuffle_edge_weights(f1, f2, f3)
	gen_null_network_from_raw_data(f1, f2, f3, f4, f5, f6, f7, f8, f9)
	#spatio_temporal_network_neighbor_ego_effect(f1, f2)