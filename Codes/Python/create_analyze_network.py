#!/usr/bin/env python
# encoding: utf-8
"""
networkx version is 1.11 / 
all attributes have changed x-()
Satyam Mukherjee
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

#from pymnet import * ### multiplex package in python

#sys.path.insert(0, '../../Idea01_Static/Community_Structure/Infomap/examples/python/infomap/')
#import infomap ### Let's get the community structure using infomap algorithm

def countDuplicatesInList(dupedList):
	uniqueSet = Set(item for item in dupedList)
	return [(item, dupedList.count(item)) for item in uniqueSet]

def transform_labels_to_nx(G):
	'''
	Needed only if the labels and id in gml files get interchanged
	'''
	H = nx.Graph()
	label_mapping={}
		#add the nodes by label from G to H
	for node in G.nodes(data=True):
		H.add_node(node[1]['label'])
		label_mapping[node[0]] = node[1]['label']   
		
		if len(node[1]) > 2:
			for key in node[1]:
				H.node[node[1]['label']][key] = node[1][key]
	#add the appropriate edges
	for edge in G.edges(data=True):
		H.add_edge(label_mapping[edge[0]], label_mapping[edge[1]])
		if len(edge[2]) > 0:
			for key in edge[2]:
				H[label_mapping[edge[0]]][label_mapping[edge[1]]][key] = edge[2][key]            
	return H

def create_edge_list(file_name, outfile_name, n, m):
	##n, m : column ids to be used from commit file

	f1 = open(file_name,'r') ## input file from raw data/processed data

	list_feature_author = []
	for line in f1.readlines()[1:] :
		line = line.strip().split("\t")
		list_feature_author.append((str(line[int(n)]),str(line[int(m)])))

	dict_feature_key_authors_vals = defaultdict(list)

	for u, v in list(set(list_feature_author)) :
		dict_feature_key_authors_vals[str(u)].append(str(v)) ## for each feature get the authors

	return dict_feature_key_authors_vals

def network_create_gml(graph_name) :
	
	G = nx.Graph() ### The network. for directed graph use G = nx.DiGraph() and for undirected graph use G=nx.Graph()
	edgelist = graph_name
	G.add_edges_from(edgelist)
	list_edges = G.edges() #entire network
	return list_edges


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
# Add network attributes from Data_commit.csv file
#------------------------------------------------------------------------------
def network_attribute_node_type(files_csv, gml_file, col_id) : 
	### Here I introduce the attribute of the node, if it is an independent user, firm or distributor
	##col_id : column G for author id and column I for committer id

	H = nx_old.read_gml(gml_file)

	f1 = open(files_csv,'r') ## input file from raw data/processed data

	dict_feature_type_authorid = defaultdict(list); color_feature = defaultdict(list)

	for line in f1.readlines()[1:] :
		line = line.strip().split("\t")
		dict_feature_type_authorid[str(line[int(col_id)])] = str(line[5].replace('"',''))

	for n in H.nodes() :
				
				H.node[n]['node_type'] = dict_feature_type_authorid[str(H.node[n]['label'])]

				if dict_feature_type_authorid[str(H.node[n]['label'])] == "firm" : H.node[n]['node_color_id'] = 1
				if dict_feature_type_authorid[str(H.node[n]['label'])] == "independent" : H.node[n]['node_color_id'] = 2
				if dict_feature_type_authorid[str(H.node[n]['label'])] == "distributor" : H.node[n]['node_color_id'] = 3

				#print n, H.node[n]['label'], dict_feature_type_authorid[str(H.node[n]['label'])], H.node[n]['node_color_id'], H.node[n]['node_type']

	H = nx_old.write_gml(H,str(gml_file))


#------------------------------------------------------------------------------
# Compute the empirical CDF from the data
#------------------------------------------------------------------------------
def empirical_cdf_from_data(_data,both=True,increasing=False,zero=False):
	"""Generate empirical CDF from data
	"""
	data = copy.deepcopy(_data)
	data.sort()
	n = float(len(data))

	# determine whether cdf is increasing or decreasing
	if increasing:
		f = lambda i: float(i+1)/n
	else:
		f = lambda i: 1.0-float(i)/n
		
	# make cdf
	cdf = []
	if zero and increasing:
		cdf.append( (data[0], 0.0) )
	for i,datum in enumerate(data):
		cdf.append( (datum, f(i)) )
		if both and i+1<int(n):
			cdf.append( (datum, f(i+1)) )
	if zero and not increasing:
		cdf.append( (data[-1], 0.0) )
	return cdf

#------------------------------------------------------------------------------
# Extract the empirical cdf of network
#------------------------------------------------------------------------------
def read_gml_for_distr(input_gml_file, param_net, outfile_name) : 
	#param net = "degree", "betweenness_centrality"

	H = nx_old.read_gml(input_gml_file)
	values = []
	for n in H.nodes() :
		values.append(H.node[n][str(param_net)])
	values.sort()

	cdf_degree = empirical_cdf_from_data(values)


	clean_cdf_degree = []
	clean_cdf_degree.append(cdf_degree[0])
	last = cdf_degree[0][0]

	for i in range(1, len(cdf_degree)):
		if cdf_degree[i][0] != last:
			clean_cdf_degree.append(cdf_degree[i])
			last = cdf_degree[i][0]
	clean_cdf_degree.append(cdf_degree[-1])

	return clean_cdf_degree


#------------------------------------------------------------------------------------------------------
#######                    Network of committers in three principles                          #########
### 1. Two committers are connected if the committed on the same code. This creates a weighted network
### 2. Two committers are commenting on different lines of the same code. They are linked 
####   with weights proportional to the difference in line numbers. We take average and sum as weights
### 3. Take the difference of time of last commit and use it as a weight of a link
#------------------------------------------------------------------------------------------------------



def create_text_matching_developer_network(f1, gml_file, yearstr, f2) :

	data1 = open(f1, 'r'); outf = open(f2, 'w')
	dict_committer_codes_text = defaultdict(list); dict_committer_text_tag = defaultdict(list)

	for line in data1.readlines()[1:]:
		line = line.strip().split('|')
		try :
			committer_name = str(line[6].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0])
			committer_email = re.sub('[!#$IV()<>]','',str(line[7])).encode('ascii','ignore')
			if "Gerrit" not in committer_name and "Bot" not in committer_name: 
		
				committer_id = committer_name #+'__'+committer_email
				codes = str(line[2].split(';')[2])
				codeline = str(line[2].split(';')[4].split('#')[1])
				code_text = str(line[0])

				if " -" in str(line[8]) : 
					time_of_commit = str(line[8].split(', ')[1].split(' -')[0])
				if " +" in str(line[8]) : 
					time_of_commit = str(line[8].split(', ')[1].split(' +')[0])
		
				year = time_of_commit.split(' ')[2]

				if int(year) == int(yearstr) :
					dict_committer_codes_text[committer_id].append(codes+'|'+code_text)
					dict_committer_text_tag[committer_id+'|'+codes].append(code_text)
		except IndexError,e :
			continue

	keylist = []; dict_edge_list_code_stringmatch = defaultdict(list); 

	for keys, values in dict_committer_text_tag.items() :
		keylist.append(keys)
	keypairs = combinations(keylist, 2)
	
	for k1, k2 in keypairs :
		if str(k1.split('|')[1]) == str(k2.split('|')[1]) :
			committer_i = k1.split('|')[0]; committer_j = k2.split('|')[0]; code = str(k1.split('|')[1])
			u = dict_committer_text_tag[k1]; v = dict_committer_text_tag[k2]

			#join_u = " ".join(u); join_v = " ".join(v)
			product_codes = product(u, v)
			for p, q in product_codes :
				#if str(join_u) != "+" or str(join_v) !="+" :
					stringmatch_score = difflib.SequenceMatcher(None, str(p), str(q)).ratio()
					
					#if int(outnum) == 1 :
					print >> outf, '%s|%s|%s|%s' % ( k1.split('|')[0], k2.split('|')[0], k1.split('|')[1], stringmatch_score) 
					
					#if int(outnum) == 0 :
					if float(stringmatch_score) >= 0.9 :

							dict_edge_list_code_stringmatch[(committer_i, committer_j, code)].append(float(stringmatch_score))

	G = nx.Graph(); dict_edge_list_stringmatch = defaultdict(list)

	edgelist_wt_count = []; edgelist_wt_mu = []; edgelist_wt_std = []

	for keys, values in dict_edge_list_code_stringmatch.items() :

		k1 = keys[0]; k2 = keys[1]; k3 = keys[2]
		wt_string_edit_avg = np.mean(values)
		wt_string_edit_med = np.median(values)

		dict_edge_list_stringmatch[(k1, k2)].append(float(wt_string_edit_avg))

	for k, v in dict_edge_list_stringmatch.items() :

		edgelist_wt_count.append((k[0], k[1], len(v)))
		edgelist_wt_mu.append((k[0], k[1], np.mean(v)))
		edgelist_wt_std.append((k[0], k[1],  np.std(v)))
	
	G.add_weighted_edges_from(edgelist_wt_count, weight="string_edit_code_count") 
	G.add_weighted_edges_from(edgelist_wt_mu, weight="string_edit_code_mean") 
	G.add_weighted_edges_from(edgelist_wt_std, weight="string_edit_code_std") 

	H = G
	
	weightlists = ['string_edit_code_count', 'string_edit_code_mean', 'string_edit_code_std']
	for wtl in weightlists :
		for u,v in nx.degree(H,weight=str(wtl)).items() :
			H.node[u]['s'+'_'+str(wtl)] = float(v)

	## Compute weighted betweenness centrality for nodes
	for wtl in weightlists :
		betweenness_dictionary = nx.betweenness_centrality(H,weight=str(wtl),normalized=True)
		for u,v in betweenness_dictionary.items() :
			H.node[u]['nbc'+'_'+str(wtl)] = float(v)

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

	H = nx_old.write_gml(H, str(gml_file))

def create_cross_code_text_matching(f1, gml_file, yearstr) :

	data1 = open(f1, 'r'); #outf = open(f2, 'w')
	dict_committer_codes_text = defaultdict(list); dict_committer_text_tag = defaultdict(list)

	for line in data1.readlines()[1:]:
		line = line.strip().split('|')
		try :
			committer_name = str(line[6].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0])
			committer_email = re.sub('[!#$IV()<>]','',str(line[7])).encode('ascii','ignore')
			if "Gerrit" not in committer_name and "Bot" not in committer_name: 
		
				committer_id = committer_name #+'__'+committer_email
				codes = str(line[2].split(';')[2])
				codeline = str(line[2].split(';')[4].split('#')[1])
				code_text = str(line[0])

				if " -" in str(line[8]) : 
					time_of_commit = str(line[8].split(', ')[1].split(' -')[0])
				if " +" in str(line[8]) : 
					time_of_commit = str(line[8].split(', ')[1].split(' +')[0])
		
				year = time_of_commit.split(' ')[2]

				if int(year) == int(yearstr) :
					#dict_committer_codes_text[committer_id].append(codes+'|'+code_text)
					dict_committer_text_tag[codes].append(code_text+'|'+committer_id)
		except IndexError,e :
			continue

	keylist = []; dict_edge_list_code_stringmatch = defaultdict(list); 

	for keys, values in dict_committer_text_tag.items() :
		keylist.append(keys)
	keypairs = combinations(keylist, 2)
	
	for k1, k2 in keypairs :
		code_k1_dev_text = dict_committer_text_tag[k1]
		code_k2_dev_text = dict_committer_text_tag[k2]

		if len(code_k1_dev_text) > 0 and len(code_k2_dev_text) > 0 :
			developers_text_pairs = product(code_k1_dev_text, code_k2_dev_text)

			for kd1, kd2 in developers_text_pairs :
				if str(kd1.split('|')[1]) != str(kd2.split('|')[1]) :
					k1_code_text = str(kd1.split('|')[0])
					k2_code_text = str(kd2.split('|')[0])
					stringmatch_score = difflib.SequenceMatcher(None, k1_code_text, k2_code_text).ratio()
					
					committer_i = str(kd1.split('|')[1]); committer_j = str(kd2.split('|')[1])

					#print >> outf, '%s|%s|%s' % ( committer_i, committer_j, stringmatch_score) 
					
					if float(stringmatch_score) >= 0.0 :

							dict_edge_list_code_stringmatch[(committer_i, committer_j)].append(float(stringmatch_score))

	G = nx.Graph(); 

	edgelist_wt_count = []; edgelist_wt_mu = []; edgelist_wt_std = []

	for keys, values in dict_edge_list_code_stringmatch.items() :

		k1 = keys[0]; k2 = keys[1];

		wt_string_edit_avg = np.mean(values)
		wt_string_edit_std = np.std(values)
		wt_string_edit_sum = len(values)

		edgelist_wt_count.append((k1, k2, wt_string_edit_sum))
		edgelist_wt_mu.append((k1, k2, wt_string_edit_avg))
		edgelist_wt_std.append((k1, k2, wt_string_edit_std))
	
	G.add_weighted_edges_from(edgelist_wt_count, weight="string_edit_crosscode_count") 
	G.add_weighted_edges_from(edgelist_wt_mu, weight="string_edit_crosscode_mean") 
	G.add_weighted_edges_from(edgelist_wt_std, weight="string_edit_crosscode_std") 

	H = G
	
	weightlists = ['string_edit_crosscode_count', 'string_edit_crosscode_mean', 'string_edit_crosscode_std']
	for wtl in weightlists :
		for u,v in nx.degree(H,weight=str(wtl)).items() :
			H.node[u]['s'+'_'+str(wtl)] = float(v)

	## Compute weighted betweenness centrality for nodes
	for wtl in weightlists :
		betweenness_dictionary = nx.betweenness_centrality(H,weight=str(wtl),normalized=True)
		for u,v in betweenness_dictionary.items() :
			H.node[u]['nbc'+'_'+str(wtl)] = float(v)

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

	H = nx_old.write_gml(H, str(gml_file))




def get_core_community_classf(gml_file, networktype, g2) :
	"""
	Partition network with the Infomap algorithm.
	Annotates nodes with 'community' id and return number of communities found.
	"""
	import roles_classifications as nx_cart_role

	G = nx_old.read_gml(gml_file)
	infomapWrapper = infomap.Infomap("-N 10 --directed --two-level --clu --map")

	if str(networktype) == "reuse" :
		weightlists = ['wt_reuse_mean', 'wt_reuse_sum', 'wt_reuse_median', 'wt_reuse_std']

	if str(networktype) == "gitweb" :
		weightlists = ['wt_n_com_code', 'wt_hm_diff_first_commit_time', 'wt_hsum_diff_first_commit_time', 'wt_hm_diff_last_commit_time', 'wt_hsumm_diff_last_commit_time', 'wt_mean_joint_commit', 'wt_sum_joint_commit']


	for wtl in weightlists :
		print wtl
		for e in G.edges_iter(data=True):
			infomapWrapper.addLink(e[0], e[1], e[2][str(wtl)])
		infomapWrapper.run();
		tree = infomapWrapper.tree

		communities = {}
		for node in tree.leafIter():
			communities[node.originalLeafIndex] = node.moduleIndex()

	#nx.set_node_attributes(G, 'community', communities)
		print communities
		for n in G.nodes() :
			if n in communities:
				#print str(communities[n])+'_'+str(n), G.node[n], str(wtl)

				G.node[n]['infomap_'+str(wtl)] = str(communities[n])+'_'+str(n)
	#	print G.nodes(data=True)
	#	Groles = nx_cart_role.main(G, str(wtl))
	#	G = nx_old.write_gml(Groles, g2)

#    g1 = gx.Graph(len(H2), zip(*zip(*nx.to_edgelist(H2))[:2]))

#    for u,v,d in H2.edges(data=True) :
#        g1.es['weight'] = 1.0
#        g1[u, v] = d['wt_n_com_code']
	
#    for n in H2.nodes() :
#        g1.vs["name"] = n
#        g1.vs["weight"] = H2.node[n]['strengthn_com_code']

#    print g1.is_weighted()

#    weighted_kcores = wkcore.core_dec(g1, weighted = True)

#    weighted_kcores = s_core.s_core_number(H, weight=None)
#    listkcore = weighted_kcores.values(); listkcore.sort()
#    print listkcore
	#print nx.k_core(H)


def plot_network_nx(graphname, iter1, sizeres, edgewidth):
	from networkx.drawing.nx_agraph import graphviz_layout
	G = nx_old.read_gml(graphname)
	
	fig = plt.figure()
	ax = fig.add_subplot(111)    

	pos2 = nx.spring_layout(G,iterations=int(iter1))
	#pos2 = graphviz_layout(G, prog='neato')

	nodelist_firm = []; nodelist_ind = []; nodelist_distr = []
	nodelist_firm_clr = []; nodelist_ind_clr = []; nodelist_distr_clr = []
	nodelist_firm_sz = []; nodelist_ind_sz = []; nodelist_distr_sz = []
	nodekshell = []; nodesize = []; nodelist = []; nodesattr = []; colorf = []; colord = []; colori = []

	for n in G.nodes() :
		nodekshell.append(int(G.node[n]['kshell_index']))
		nodesize.append(100*(1+np.log(float(G.node[n]['degree']))))
		nodelist.append(int(G.node[n]['id']))
		nodesattr.append((G.node[n]['id'], int(sizeres)*(np.log10(1+float(G.node[n]['degree']))), G.node[n]['kshell_index'], G.node[n]['node_type']))

	print min(nodekshell), max(nodekshell), nodekshell


	for (ind, sz, clr, type1) in nodesattr :
		if str(type1) == "distributor" :
			nodelist_distr.append(ind)
			nodelist_distr_sz.append(sz)
			nodelist_distr_clr.append(float(clr-min(nodekshell))*1.0/float(max(nodekshell) - min(nodekshell)))

		if str(type1) == "independent" :
			nodelist_ind.append(ind)
			nodelist_ind_sz.append(sz)
			nodelist_ind_clr.append(float(clr-min(nodekshell))*1.0/float(max(nodekshell) - min(nodekshell)))

		if str(type1) == "firm" :
			nodelist_firm.append(ind)
			nodelist_firm_sz.append(sz)
			nodelist_firm_clr.append(float(clr-min(nodekshell))*1.0/float(max(nodekshell) - min(nodekshell)))
	for colors in nodelist_firm_clr :
		colorf.append(plt.cm.jet(colors))
	for colors in nodelist_distr_clr :
		colord.append(plt.cm.jet(colors))
	for colors in nodelist_ind_clr :
		colori.append(plt.cm.jet(colors))

	#cax = ax.imshow([nodekshell],cmap=plt.cm.jet,interpolation="nearest")
	#cbar = plt.colorbar(cax)
	#cbar.set_label('k', size=10)

	# define the colormap
	#cmap = plt.cm.jet
	# extract all colors from the map
	#cmaplist = [cmap(i) for i in range(cmap.N)]
	# force the first color entry to be grey
	#cmaplist[0] = (.5,.5,.5,1.0)
	# create the new map
	#cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

# define the bins and normalize
	#bounds = list(set(nodekshell))
	#bounds.sort()
	#norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

	#cb = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, spacing='proportional', ticks=bounds, boundaries=bounds, format='%1i')

	#cmap = plt.cm.get_cmap('jet', len(list(set(nodekshell)))) 
	#cax = ax.imshow([nodekshell],cmap=cmap,interpolation="bilinear")
	
	#cbar = plt.colorbar(cax)
	#cbar.set_ticks([])

	nx.draw_networkx_nodes(G,pos2,nodelist=nodelist_firm, node_size = nodelist_firm_sz, node_shape = 'o', node_color=colorf, cmap=plt.cm.jet, linewidths=None)
	nx.draw_networkx_nodes(G,pos2,nodelist=nodelist_ind, node_size = nodelist_ind_sz, node_shape = 'o', node_color=colori, cmap=plt.cm.jet, linewidths=None)
	nx.draw_networkx_nodes(G,pos2,nodelist=nodelist_distr, node_size = nodelist_distr_sz, node_shape = 'o', node_color=colord, cmap=plt.cm.jet, linewidths=None)

	nx.draw_networkx_edges(G,pos2,edgelist=None,width=int(edgewidth), edge_color='k',style='solid',alpha=0.35)
	
	plt.axis('off')
	plt.show()

def plot_network_paper2(graphname, iter1, edgewidth, nodesz):
	from networkx.drawing.nx_agraph import graphviz_layout
	G = nx_old.read_gml(graphname)
	
	fig = plt.figure()
	ax = fig.add_subplot(111)    

	pos2 = nx.spring_layout(G,iterations=int(iter1))
	#pos2 = graphviz_layout(G, prog='neato')

	nodelist_firm = []; nodelist_ind = []; nodelist_distr = []
	nodelist_firm_clr = []; nodelist_ind_clr = []; nodelist_distr_clr = []
	nodescolor = []; nodelist = []; nodesattr = []; colord = []

	for n in G.nodes() :
		nodescolor.append(int(G.node[n]['node_color_id']))
		nodelist.append(int(G.node[n]['id']))
		nodesattr.append((G.node[n]['id'], G.node[n]['node_color_id'], G.node[n]['node_type']))

	print min(nodescolor), max(nodescolor), nodescolor


	for (ind, clr, type1) in nodesattr :
			nodelist_distr_clr.append(float(clr-min(nodescolor))*1.0/float(max(nodescolor) - min(nodescolor)))


	for colors in nodelist_distr_clr :
		colord.append(plt.cm.jet(colors))

	#cmap = plt.cm.get_cmap('jet', len(list(set(nodescolor)))) 
	#cax = ax.imshow([nodescolor],cmap=cmap,interpolation="bilinear")
	
	#cbar = plt.colorbar(cax)
	#cbar.set_ticks([])

	nx.draw_networkx_nodes(G, pos2, nodelist=nodelist, node_size = int(nodesz), node_shape = 'o', node_color=colord, cmap=plt.cm.jet, linewidths=None)

	nx.draw_networkx_edges(G, pos2, edgelist=None,width=int(edgewidth), edge_color='k',style='solid',alpha=0.35)
	
	plt.axis('off')
	plt.show()



def distributions_cdf(f1, f2, num) :

	data1 = open(f1, 'r'); outf2 = open(str(f2), 'w')
	values = []
	for line in data1.readlines()[1:]:
		line = line.strip().split('|')
		values.append(float(line[int(num)]))

	cdf_val = empirical_cdf_from_data(values)
	clean_cdf_degree = []
	clean_cdf_degree.append(cdf_val[0])
	last = cdf_val[0][0]
	for i in range(1, len(cdf_val)):
		if cdf_val[i][0] != last:
			clean_cdf_degree.append(cdf_val[i])
			last = cdf_val[i][0]

	clean_cdf_degree.append(cdf_val[-1])

	for u, v in clean_cdf_degree :
		print >> outf2, u, v

def create_spatial_temporal_network_of_developers(f1, yearstr, gmlw) :

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

	### neighbors and Ego of a committer
	#for x in list_attr_dv :
	#    print x
	#    for n in G.nodes() :
	#        try :
			   # print n, G.neighbors(n), len(G.neighbors(n))

	#            G.node[n]['neigh'+'_'+str(x)] = np.mean([G.node[k][str(x)] for k in G.neighbors(n)])
	#            G.node[n]['ego'+'_'+str(x)] = np.mean([G.node[k][str(x)] for k in nx.ego_graph(G, n)])            
	#        except KeyError,e :
	#            print n, G.neighbors(n), len(G.neighbors(n))

	G = nx_old.write_gml(G, str(gml1))

def spatio_temporal_network_neighbor_ego_effect(gml_file) :

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
	
	#graph_filename = sys.argv[1] #; outf = sys.argv[2]; col1 = sys.argv[3]; col2 = sys.argv[4]

### This part is to create the network and save in gml format. you have to uncomment the lines and run the code
	#edges_items = create_edge_list(graph_filename, outf, col1, col2)
	#list_link = []; dict_links = defaultdict(list)
	
	#for key in edges_items :
		
	#    for n in range(1,len(edges_items[str(key)])) :
	#        dict_links[str(key)].append((edges_items[str(key)][n-1], edges_items[str(key)][n]))

	#for k, vals in dict_links.items():
	#    for u,v in vals :
	#        list_link.append((str(u), str(v)))

	#edges = list(set(list_link)) ## exclude duplicate links to avoid multigraph. Other option could be to convert to a weighted graph

	#H = nx.Graph()
	#H.add_edges_from(edges)

	#H = nx.write_gml(H, str(outf))

	#G = nx.Graph(); G.add_edges_from(list_link)
	#print len(G.nodes()), len(list(max(nx.connected_components(G), key=len))) ## Giant component of network
	
	#plot_network(graph_filename) ## import the gml file and plot the network
	
	#network_measures(graph_filename) ## write the network attributes in the gml file
	
	#graph_filename = sys.argv[1] ; outgml = sys.argv[2]; col1 = sys.argv[3]
	#network_attribute_node_type(graph_filename, outgml, col1) # Feature type information

	#------------------------------------------------------------------------------
	## Distributions
	#------------------------------------------------------------------------------

	#gml_file = sys.argv[1] ; networkparam = sys.argv[2]; outfile = sys.argv[3]
	#list_val = read_gml_for_distr(gml_file, networkparam, outfile)
	#outw = open(str(outfile), 'w')
	#for u,v in list_val :
	#    print >> outw, u, v

	#------------------------------------------------------------------------------
	## Multiplex data nodes and edges and labeling of layers
	#------------------------------------------------------------------------------

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]; f5 = sys.argv[5]; f6 = sys.argv[6]; f7 = sys.argv[7]
	#get_net = gen_open_source_multilayer(f1, f2, f3, f4, f5, f6, f7)

	#outfile = open('../Static/multiplex/author_edges_no_self_layer2layer__nova_02_processed.txt','w')
	#list_rem_nodes = []

	#for n in get_net.nodes() :
	#    try :
	#        print n, get_net.node[n]['layer_name']
	#    except KeyError,e :
	#        list_rem_nodes.append(n)

	#get_net.remove_nodes_from(list_rem_nodes)

	#for u, v in get_net.edges() :
	#    print >> outfile, get_net.node[u]['label'], get_net.node[u]['layer_name'], get_net.node[v]['label'], get_net.node[v]['layer_name']

### netio.write_edge_files(net,outputfiles,columnSeparator="\t",rowSeparator="\n",weights=True,masterFile=True,numericNodes=False)
### netio.read_edge_files(edgeinput,layerinput=None,nodeinput=None,couplings='categorical',fullyInterconnected=True,directed=False,ignoreSelfLink=True):

	#------------------------------------------------------------------------------
	## Multiplex visualize
	#------------------------------------------------------------------------------
	
	#f1 = sys.argv[1]
	#visualize_multiplex_network_simple(f1)

	#------------------------------------------------------------------------------
	## Community structure infomap
	#------------------------------------------------------------------------------

	#f1 = sys.argv[1]
	#findCommunities(f1)


	#------------------------------------------------------------------------------
	## Network formation with common code overlap in gitweb links
	#------------------------------------------------------------------------------

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	#create_temporal_network_from_gitweb_codes(f1, f2, f3)

	#------------------------------------------------------------------------------
	## Network formation with reuse codes
	#------------------------------------------------------------------------------

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	#create_directed_weighted_network_no_restr(f1, f2, f3)

	#------------------------------------------------------------------------------
	## Network formation with reuse codes
	#------------------------------------------------------------------------------
	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	#get_core_community_classf(f1, f2, f3)


	#------------------------------------------------------------------------------
	## Network formation spatial difference of lines
	#------------------------------------------------------------------------------
	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	#create_spatial_network_from_gitweb_pages(f1, f2, f3)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
	#create_text_matching_developer_network(f1, f2, f3, f4)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]#; f4 = sys.argv[4]
	#create_cross_code_text_matching(f1, f2, f3)

	#------------------------------------------------------------------------------
	## Network plot
	#------------------------------------------------------------------------------
	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3];  f4 = sys.argv[4]
	#plot_network_nx(f1, f2, f3, f4)


	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
	#convert_gml_to_table_for_analysis(f1, f2, f3, f4)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
	#plot_network_paper2(f1, f2, f3, f4)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3];
	#distributions_cdf(f1, f2, f3)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3];
	#create_spatial_temporal_network_of_developers(f1, f2, f3)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]; f5 = sys.argv[5]
	#measure_developer_attributes(f1, f2, f3, f4, f5)

	f1 = sys.argv[1]
	spatio_temporal_network_neighbor_ego_effect(f1)
