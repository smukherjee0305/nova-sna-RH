
#    Created on 2017
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI


"""Codes to detect motifs in file dependency networks and count the number of motifs."""
"""

Provides:

 - subgraph_pattern()
 - check_cycles()
 - check_Motifs()
 - write_network_attr_gml()
 - gen_visibility_matrix_dsm_adjacency()

References:
 - networkx:     https://networkx.github.io/
 - motif algorithms: https://doi.org/10.1016/j.physa.2007.02.102
 					 http://science.sciencemag.org/content/298/5594/824
 					 http://science.sciencemag.org/content/353/6295/163

 - DSM: http://www.sciencedirect.com/science/article/pii/S0048733314001012
 		http://pubsonline.informs.org/doi/abs/10.1287/mnsc.1060.0552

Publication/Manuscript:
 - Motifs and modularity in complex systems
   Satyam Mukherjee and Sabine Brunswicker (Under Preparation)
"""


import networkx as nx
import numpy as np
import itertools
import old_gml as nx_old
import sys
from operator import itemgetter
import itertools as it
from collections import defaultdict, Counter
import glob, copy
import scipy as sp
import scipy.stats
from random import choice



def subgraph_pattern(graph,pattern,sign_sensitive = True):

	"""
	Motif detection algorithm:
	1. Count all k-subgraphs in the network
	2. Which of those subgraphs are isomorphic (i.e. topologically equivalent) and count only once every such isomorphic groups
	"""

	if sign_sensitive:

		edge_match = lambda e1,e2 : (e1['sign']==e2['sign'])
	else:
		edge_match = None
	matcher = nx.algorithms.isomorphism.DiGraphMatcher(graph,pattern,edge_match=edge_match)
	return list(matcher.subgraph_isomorphisms_iter())

def check_cycles(H) :
	cycles = {'Cycle_2': [(1,2),(2,1)], 'Cycle_3': [(1,2),(2,3),(3,1)], 'Cycle_4': [(1,2),(2,3),(3,4),(4,1)], 'Cycle_5': [(1,2),(2,3),(3,4),(4,5),(5,1)], 'Cycle_6': [(1,2),(2,3),(3,4),(4,5),(5,6),(6,1)], 'Cycle_7': [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,1)]}
	
	## match the pattern and count the cycles
	G = H

	ccount = dict(zip(cycles.keys(), list(map(int, np.zeros(len(cycles))))))

	dict_edges = defaultdict(list); dict_nodes = defaultdict(list)
	for key in cycles :
	
			pattern = cycles[key]
		
			gcycle = nx.DiGraph()
			gcycle.add_edges_from(pattern)

			cycle_pattern_obs = subgraph_pattern(G, gcycle, sign_sensitive=False)

			s = []
		#if len(cycle_pattern_obs) > 0 :
			for subgraph in cycle_pattern_obs :
				tup = tuple(subgraph.keys())

				#k1 = subgraph.keys()[0]; k2 = subgraph.keys()[1]; k3 = subgraph.keys()[2]
				s.append(tup)

			uniqs = list(set(s))

			if len(uniqs) > 0 :
				maplist = map(list, uniqs)

			### label the edges as per the cycle labels
				ccount[str(key)] = len(maplist)

				for nplets in maplist :
					subgraph = G.subgraph(nplets)
					edgeLists = [e for e in subgraph.edges() if G.has_edge(*e)]

				## an edge is part of multiple cycles
				## lets count the number of cycles an edge is part of 
					for u, v in edgeLists :
						dict_edges[(u, v)].append(str(key))

				## A node is also part of multiple cycles. 
				## We count the total number of cycle a node is part of
				## We count the frequency of occurence each cycle the node is part of
					nodelists = subgraph.nodes()
					for n in nodelists :
						dict_nodes[str(n)].append(str(key))

		### Let's mark the edge with cycle type and count. We count the number of types
		### of cycle an edge is a part of. An edge could appear in M1: M1x times and in M2: M2x times and so on

	for u,v in G.edges() :
			if (u,v) in dict_edges :
				G[u][v]['num_cycle_edge'] = len(list(set(dict_edges[(u,v)])))

	### Let's mark the node with cycle type and count. We count the number of types of cycle a node is a part of. 

	for n in G.nodes() :
		cyclecountnode = dict(zip(ccount.keys(), list(map(int, np.zeros(len(ccount))))))

		if str(n) in dict_nodes :
			subgraphnodeslist = dict_nodes[str(n)]

			for key in subgraphnodeslist:
				cyclecountnode[str(key)] +=1

		for cycle, count  in cyclecountnode.items() :
			G.node[n][str(cycle)] = int(count)
	
	### Let's mark the edge with cycle type and count. We count the number of types
	### of cycle an edge is a part of. 

	for u,v in G.edges() :
		cyclecountedge = dict(zip(ccount.keys(), list(map(int, np.zeros(len(ccount))))))

		if (u,v) in dict_edges :
			subgraphedgeslist = dict_edges[(u,v)]

			for key in subgraphedgeslist :
				cyclecountedge[key] += 1

		for cycle, count in cyclecountedge.items() :
			G[u][v][str(cycle)] = int(count)


	return G

def check_Motifs(H, m):
	"""
	Basic simple motif counter for networkx takes 2 arguments
	a Graph and the size of the motif. Motif sizes supported 3 and 4.

	This function is actually rather simple. It will extract all 3-grams from
	the original graph, and look for isomorphisms in the motifs contained
	in a dictionary. The returned object is a ``dict`` with the number of
	times each motif was found.::

	m :: motif type. Currently this is for 3-node. I am working on "bifan" and 4-node

	"""
	#This function will take each possible subgraphs of gr of size 3, then
	#compare them to the mo dict using .subgraph() and is_isomorphic
	
	#This line simply creates a dictionary with 0 for all values, and the
	#motif names as keys

	##paper source "Higher-order organization ofcomplex networks" (2016) Benson et al, Science
	## I choose only the unidirection ones : M1, M5, M8, M9, M10


	s = int(m)

	if (s==3):
		#motifs = {'M1': nx.DiGraph([(1,2),(2,3),(3,1)]), 'M5': nx.DiGraph([(1,2),(2,3),(1,3)]), 'M8': nx.DiGraph([(2, 1),(2,3)]), 'M9': nx.DiGraph([(2, 1),(3, 2)]), 'M10': nx.DiGraph([(1,2),(3,2)])}
		motifs = {'M1': [(1,2),(2,3),(3,1)], 'M5': [(1,2),(2,3),(1,3)], 'M8': [(2, 1),(2,3)], 'M9': [(2, 1),(3, 2)], 'M10': [(1,2),(3,2)],
					'M2': [(1,2),(2,3),(3,2),(3,1)], 'M3': [(1,2),(2,3),(3,2),(1,3),(3,1)], 'M4': [(1,2),(2,1),(2,3),(3,2),(1,3),(3,1)], 'M6': [(2, 1),(2,3),(1,3),(3,1)], 'M7': [(1,2),(3,2),(1,3),(3,1)],
					'M11': [(1,2),(2,1),(2,3)], 'M12': [(1,2),(2,1),(3,2)], 'M13': [(1,2),(2,1),(2,3),(3,2)]}

	elif (s==4): ## under development
		motifs = {'bifan': [(1,2),(1,3),(4,2),(4,3)]}

		#edgeLists=[[[1,2],[1,3],[1,4]]]
		#edgeLists.append([[1,2],[1,3],[1,4],[2,3]])
		#edgeLists.append([[1,2],[1,3],[1,4],[2,3],[3,4]])
		#edgeLists.append([[1,2],[1,3],[1,4],[2,3],[3,4],[2,4]])
	else:
		raise nx.NetworkXNotImplemented('Size of motif must be 3 or 4')

	#outf = open(f2, 'w')
	#print >> outf, 'commitid|motiflabel|count'

	G = H

	mcount = dict(zip(motifs.keys(), list(map(int, np.zeros(len(motifs))))))

	## match the pattern and count the motifs 
	dict_edges = defaultdict(list); dict_nodes = defaultdict(list)
	for key in motifs :
	
			pattern = motifs[key]
		
			gmoti = nx.DiGraph()
			gmoti.add_edges_from(pattern)

			motif_pattern_obs = subgraph_pattern(G, gmoti, sign_sensitive=False)

			s = []
			for subgraph in motif_pattern_obs :
				tup = tuple(subgraph.keys())
				s.append(tup)

			uniqs = list(set(s))

			if len(uniqs) > 0 :
				maplist = map(list, uniqs)

			### label the edges as per the motif labels
				mcount[str(key)] = len(maplist)

				for triplets in maplist :
					subgraph = G.subgraph(triplets)
					edgeLists = [e for e in subgraph.edges() if G.has_edge(*e)]

				## an edge is part of multiple motifs
				## lets count the number of motifs an edge is part of 
					for u, v in edgeLists :
						dict_edges[(u, v)].append(str(key))
	

				## A node is also part of multiple motifs. 
				## We count the total number of motifs a node is part of
				## We count the frequency of occurence each motif the node is part of
					nodelists = subgraph.nodes()
					for n in nodelists :
						dict_nodes[str(n)].append(str(key))



		#for keys, values in mcount.items() :
		#	print >> outf, '%s|%s|%s' %(outname, keys, values) 

	### Let's mark the edge with motif type and count. We count the number of types
	### of motif an edge is a part of. An edge could appear in M1: M1x times and in M2: M2x times and so on

	for u,v in G.edges() :
			if (u,v) in dict_edges :
				G[u][v]['num_motif_edge'] = len(list(set(dict_edges[(u,v)])))

	### Let's mark the node with motif type and count. We count the number of types of motif a node is a part of. 

	for n in G.nodes() :
		motficountnode = dict(zip(motifs.keys(), list(map(int, np.zeros(len(motifs))))))

		if str(n) in dict_nodes :
			subgraphnodeslist = dict_nodes[str(n)]

			for key in subgraphnodeslist:
				motficountnode[str(key)] +=1

		for motif, count  in motficountnode.items() :
			G.node[n][str(motif)] = int(count)

	### Let's mark the edge with motif type and count. We count the number of types
	### of motif an edge is a part of. An edge could appear in M1: M1x times and in M2: M2x times and so on

	for u,v in G.edges() :
		motficountedge = dict(zip(motifs.keys(), list(map(int, np.zeros(len(motifs))))))

		if (u,v) in dict_edges :
			subgraphedgeslist = dict_edges[(u,v)]

			for key in subgraphedgeslist:
				motficountedge[str(key)] +=1

		for motif, count  in motficountedge.items() :
			G[u][v][str(motif)] = int(count)


	return G

def write_network_attr_gml(sourcedir, destdir, n1, n2) :

	"""
	Usage:
	1. Sourcedir : directory where the gml file (of directed graph of file dependencies are located)
	2. destdir : destination directory
	3. n1, n2: range of files we want to read and write

	We add node and edge attribute. Node attributes include:
	- roles and cartographic measures from community detection
	- number of motifs a node is part of
	- frequency of motif types a node is part of

	Edge attribute includes:
	- frequency of motif types an edge is part of

	"""
	globgml = glob.glob(sourcedir+'*.gml')

	for gml_file in globgml[int(n1):int(n2)] :
		print gml_file
		
		outname = gml_file.split('/')[-1]

		G = nx_old.read_gml(gml_file)
		G = nx_code_complexity.directed_network_measures(G)
		G = check_cycles(G)
		G = check_Motifs(G, 3)
		G = nx_comm_carto.communityroledetectionInfomap(G, 'Infomap')

		G = nx_old.write_gml(G, destdir+str(outname))

def gen_visibility_matrix_dsm_adjacency(sourcedir, destdir, n1, n2) :

	"""
	generate the visibility matrix of DSM and evaluate the 
	propagation cost as defined by Baldwin
	"""

	globgml = glob.glob(sourcedir+'nova-*.gml')

	outfile = open(destdir+'commitID_propagation_costs__2012'+'__'+str(n1)+'__'+str(n2)+'.txt','w')

	for gml_file in globgml[int(n1):int(n2)] :
		#print gml_file
		commitid = gml_file.split('/')[-1][:-4].split('-')[1]

		G = nx_old.read_gml(gml_file)

		#### get the visibility matrix from DSM ###

		nodelist = G.nodes(); path_to_descedants = []

		for n in nodelist :

			## Get the list of descendants of a node. 
			desc = nx.descendants(G, n)

			path_to_descedants.append(len(list(desc)))

		power = max(path_to_descedants)

		adjacency_matrix = nx.to_numpy_matrix(G, weight=None) ## Adjacency matrix of directed graph
		adjacency_matrix_wt = nx.to_numpy_matrix(G, weight='weight') ## Weighted Adjacency matrix of directed graph

		M1 = adjacency_matrix

		## Visibility matrix
		visibilityM = 0; visibilityM_w = 0
		for k in range(power) :

			visibilityM += M1**int(k)
			visibilityM_w += adjacency_matrix_wt**int(k)

		## Propagation cost
		column_sums = [sum([row[i] for row in visibilityM]) for i in range(0,len(visibilityM[0]))]
		propagation_cost_dsm = np.sum(column_sums)*1.0/(int(len(G.nodes()))**2)

		wcolumn_sums = [sum([row[i] for row in visibilityM_w]) for i in range(0,len(visibilityM_w[0]))]
		propagation_cost_dsm_wc = np.sum(wcolumn_sums)*1.0/(int(len(G.nodes()))**2)


		print >> outfile, '%s|%s|%s|%s|%s|%s|%s' % (commitid, propagation_cost_dsm, propagation_cost_M1_col, propagation_cost_M5_col, propagation_cost_M8_col, propagation_cost_M9_col, propagation_cost_M10_col)


if __name__ == '__main__':

	f1 = sys.argv[1]; f2 = sys.argv[2] ;f3 = sys.argv[3]; f4 = sys.argv[4] #; f5 = sys.argv[5]; f6 = sys.argv[6]
	gen_visibility_matrix_dsm_motif_adjacency(f1, f2, f3, f4)
	#role_performance_commit_status(f1, f2, f3, f4, f5, f6)

	#motif_performance_complexity_codes(f1, f2, f3, f4, f5)
	#motif_performance_code_contribution(f1, f2, f3, f4, f5)
	#write_network_attr_gml(f1, f2, f3, f4)
	#count_cycle_motif(f1, f2, f3, f4, f5)

	#f1 = sys.argv[1]
	#checkmark_nodelist_motif_time(f1)
	