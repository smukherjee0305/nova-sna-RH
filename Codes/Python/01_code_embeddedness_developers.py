
"""
networkx version is 1.11 / 
"""

#    Created on Nov 2016
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI
#	 Previous Red Hat Fellow : Albert Armisen

""" Original data files are from Albert Armisen."""
""" Code creates a network of developers. If two developers work on same feature, they are connected. """
"""

Provides:

 - create_edge_list()
 - network_create_gml()
 - network_measures()
 - network_attribute_node_type()
 - plot_network_nx()
 - create_blueprint_bug_feauture_committer()
 - neighbor_attribute_node_type()
 - tenure_committer()
 - create_output_from_gml()

References:
 - networkx: https://networkx.github.io/

Publication title:
 - Central or in a Nucleus? Joint Problem Solving Relationships and Individual Knowledge Creation in Open Collaboration
 Satyam Mukherjee and Sabine Brunswicker
 Under Review (2017)

"""
import sys
import os, re
import networkx as nx
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
# Extract data Raw Data and create a file for the exploration/exploitation idea
#------------------------------------------------------------------------------

def create_blueprint_bug_feauture_committer(f1, f2, f3, output_txt) : 
	
	outf = open(str(output_txt), 'w')
	#print >> outf, 'committer_id|feature_id_id|time_commit_committer|num_files|additions_code_sum|changes_code_sum|deletions_code_sum|bug_or_bluepint'
	print >> outf, 'committer_id|feature_id_id|feature_firm|time_revision|time_commit_author|time_commit_committer|num_files|num_files_added|num_files_removed|num_files_modified|num_files_comments|num_code_added|num_code_removed|num_code_modified|num_code_total|indiv_comitter_firm|indiv_comitter_firm_type|bug_or_bluepint'
	
	data1 = open(f1, 'r'); data2 = open(f2, 'r'); data3 = open(f3,'r')

	d1_bug_or_blueprint = defaultdict(list); 


	for l in data1.readlines()[1:] :
		l = l.strip().split(',')
		d1_bug_or_blueprint[str(l[1])] = "bug"
	
	for l in data2.readlines()[1:] :
		l = l.strip().split(',')
		d1_bug_or_blueprint[str(l[1])] = "blueprint"


	for l in data3.readlines()[1:] :
		l = l.strip().split(',')
		if str(l[1]) in d1_bug_or_blueprint :
			#print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s' % (l[0], l[1], l[2], l[3], l[4], l[5], l[6], d1_bug_or_blueprint[str(l[1])])
			print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % (l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], l[10], l[11], l[12], l[13], l[14], l[15], l[16], d1_bug_or_blueprint[str(l[1])])

#------------------------------------------------------------------------------
# Extract data from gml into text file for merging into Data_individual_committer
# file in Stata
#------------------------------------------------------------------------------
def create_output_from_gml(input_gml_file, output_txt) : 
	
	outf = open(str(output_txt), 'w')
	print >> outf, 'id|nrole|degree|betweenness_centrality|community_index_infm|kshell_index|eigenvector_centrality'
	
	H = nx_old.read_gml(input_gml_file)
	## Compute eigenvector centrality of nodes

	eigen_dictionary = nx.eigenvector_centrality(H)
	for u,v in eigen_dictionary.items() :
		H.node[u]['eigenvector_centrality'] = float(v)

	for n in H.nodes() :
		
		node_id = H.node[n]['label']
		node_deg = H.node[n]['degree']
		node_bc = H.node[n]['betweenness_centrality']
		node_com = H.node[n]['community_index_infm']
		node_role = H.node[n]['nrole']
		node_kshell = H.node[n]['kshell_index']
		node_ec = H.node[n]['eigenvector_centrality']

		print >> outf, '%s|%s|%s|%s|%s|%s|%s' % (node_id, node_role, node_deg, node_bc, node_com, node_kshell, node_ec)


#------------------------------------------------------------------------------
# Add neighbor, Ego network's effect 
#------------------------------------------------------------------------------
def neighbor_attribute_node_type(files_csv, gml_file, output_txt) : 

	outf = open(str(output_txt), 'w')
#    print >> outf, 'committer_id|neighbor_mean_files|neighbor_std_files|neighbor_med_files|neighbor_mean_codes|neighbor_std_codes|neighbor_med_codes|neighbor_mean_net_contr|neighbor_std_net_contr|neighbor_med_net_contr'
#    print >> outf, 'committer_id|ego_mean_files|ego_std_files|ego_med_files|ego_mean_codes|ego_std_codes|ego_med_codes|ego_mean_net_contr|ego_std_net_contr|ego_med_net_contr'
	
	#print >> outf, 'committer_id|ego_mean_files|ego_std_files|ego_med_files|ego_mean_files_added|ego_std_files_added|ego_med_files_added|ego_mean_codes_tot|ego_std_codes_tot|ego_med_codes_tot|ego_mean_codes_added|ego_std_codes_added|ego_med_codes_added|ego_mean_net_contr_total|ego_std_net_contr_total|ego_median_net_contr_total|ego_mean_net_contr_avg|ego_std_net_contr_avg|ego_median_net_contr_avg'
	print >> outf, 'committer_id|neighbor_mean_files|neighbor_std_files|neighbor_med_files|neighbor_mean_files_added|neighbor_std_files_added|neighbor_med_files_added|neighbor_mean_codes_tot|neighbor_std_codes_tot|neighbor_med_codes_tot|neighbor_mean_codes_added|neighbor_std_codes_added|neighbor_med_codes_added|neighbor_mean_net_contr_total|neighbor_std_net_contr_total|neighbor_median_net_contr_total|neighbor_mean_net_contr_avg|neighbor_std_net_contr_avg|neighbor_median_net_contr_avg'

	H = nx_old.read_gml(gml_file) ## committer network gml file

	f1 = open(files_csv,'r') ## Data individual committer file 

	dict_num_files = defaultdict(list); dict_code_added = defaultdict(list) ; dict_net_contr_total = defaultdict(list)
	dict_num_files_added = defaultdict(list); dict_code_total = defaultdict(list) ; dict_net_contr_avg = defaultdict(list)
   
	for line in f1.readlines()[1:] :

		line = line.strip().split("|")
		dict_num_files[str(line[0])] = int(line[1]) ; dict_num_files_added[str(line[0])] = int(line[2])
		dict_code_added[str(line[0])] = int(line[3]); dict_code_total[str(line[0])] = float(line[4])
		dict_net_contr_total[str(line[0])] = float(line[5]); dict_net_contr_avg[str(line[0])] = float(line[8])

	dict_neigh_files = defaultdict(list); dict_neigh_codes_added = defaultdict(list); dict_neigh_contr_total = defaultdict(list)
	dict_neigh_files_added = defaultdict(list); dict_neigh_codes_total = defaultdict(list); dict_neigh_contr_avg = defaultdict(list)

	### neighbors of a committer
	for n in H.nodes() :
		for node in H.neighbors(n) : 
	#for n in H.nodes() :
	#    for node in nx.ego_graph(H, n) :
			if str(H.node[node]['label']) in dict_num_files :
				dict_neigh_files[str(H.node[n]['label'])].append(float(dict_num_files[str(H.node[node]['label'])]))
				dict_neigh_codes_added[str(H.node[n]['label'])].append(float(dict_code_added[str(H.node[node]['label'])]))
				dict_neigh_contr_total[str(H.node[n]['label'])].append(float(dict_net_contr_total[str(H.node[node]['label'])]))

				dict_neigh_files_added[str(H.node[n]['label'])].append(float(dict_num_files_added[str(H.node[node]['label'])]))
				dict_neigh_codes_total[str(H.node[n]['label'])].append(float(dict_code_total[str(H.node[node]['label'])]))
				dict_neigh_contr_avg[str(H.node[n]['label'])].append(float(dict_net_contr_avg[str(H.node[node]['label'])]))

	for keys, values in dict_neigh_files.items() :

		mean_files = np.mean(values); median_files = np.median(values); std_files = np.std(values)

		mean_files_added = np.mean(dict_neigh_files_added[str(keys)]); median_files_added = np.median(dict_neigh_files_added[str(keys)]); std_files_added = np.std(dict_neigh_files_added[str(keys)])

		mean_code_tot = np.mean(dict_neigh_codes_total[str(keys)]); median_code_tot = np.median(dict_neigh_codes_total[str(keys)]) ;std_code_tot = np.std(dict_neigh_codes_total[str(keys)])

		mean_code_added = np.mean(dict_neigh_codes_added[str(keys)]); median_code_added = np.median(dict_neigh_codes_added[str(keys)]) ;std_code_added = np.std(dict_neigh_codes_added[str(keys)])

		mean_net_contr_total = np.mean(dict_neigh_contr_total[str(keys)]); median_net_contr_total = np.median(dict_neigh_contr_total[str(keys)]); std_net_contr_total = np.std(dict_neigh_contr_total[str(keys)])

		mean_net_contr_avg = np.mean(dict_neigh_contr_avg[str(keys)]); median_net_contr_avg = np.median(dict_neigh_contr_avg[str(keys)]); std_net_contr_avg = np.std(dict_neigh_contr_avg[str(keys)])

#        print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( keys, np.mean(values), np.std(values), np.median(values), mean_code_tot, std_code_tot, median_code_tot, mean_net_contr, std_net_contr, median_net_contr )

		print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( keys, mean_files, std_files, median_files, mean_files_added, std_files_added, median_files_added, mean_code_tot, std_code_tot, median_code_tot, mean_code_added, std_code_added, median_code_added, mean_net_contr_total, std_net_contr_total, median_net_contr_total, mean_net_contr_avg, std_net_contr_avg, median_net_contr_avg)


#------------------------------------------------------------------------------
# Tenured time of committer. Get the overall tenure of committer and other is 
# get the active tenure of committer
#------------------------------------------------------------------------------


def tenure_committer(f1, f2) :
	datetimeFormat = '%m/%d/%Y %H:%M' 

	data1 = open(f1, 'r'); 
	outf = open(str(f2), 'w')
	print >> outf, 'committer_id|committer_tenure_active|committer_tenure_overall'


	list_time = []
	data_committer = defaultdict(list)
	for line in data1.readlines()[1:] :
		line = line.strip().split('|')
		dates = str(line[2])
		comid = str(line[0])
		list_time.append(datetime.datetime.strptime(dates, datetimeFormat))
		data_committer[comid].append(datetime.datetime.strptime(dates, datetimeFormat))
	max_overall_date_committer = max(list_time)

	for keys, values in data_committer.items() :
		min_date_committer = min(values)
		max_date_committer = max(values)

		commiter_del_time = max_date_committer - min_date_committer
		committer_del_overall_time = max_overall_date_committer - min_date_committer

		print >> outf, '%s|%s|%s' % (keys, commiter_del_time.days, committer_del_overall_time.days)



#------------------------------------------------------------------------------
# Plot the network of developers: read the gml file; color nodes as per user type
# Or as per k-shell index.
#------------------------------------------------------------------------------

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
	## Network plot
	#------------------------------------------------------------------------------
	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3];  f4 = sys.argv[4]
	#plot_network_nx(f1, f2, f3, f4)



