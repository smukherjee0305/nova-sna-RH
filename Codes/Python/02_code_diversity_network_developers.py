
"""
networkx version is 1.11 / 
"""

#    Created on Nov 2016
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI

"""Codes for diversity measures per bins of 2months/4months."""
"""

Provides:

 - histogram_dates()
 - bin_by_bin_edges_codes_contribution()
 - create_diversity_developers()


References:
 - Herfindahl Index: https://www.investopedia.com/terms/h/hhi.asp/

Publication title:
 - The role of collaboration diversity on knowledge contribution
  Sabine Brunswicker and Satyam Mukherjee
  Under Preparation 

"""
import sys
import os
import networkx as nx
#from matplotlib import pyplot
import old_gml as nx_old
from itertools import combinations, product
from collections import defaultdict
import copy, glob, zipfile
import datetime, difflib
import numpy as np, re
from sets import Set
import scipy.stats


#------------------------------------------------------------------------------
# Form histogram of committing dates; two/four months from 2013 to 2015
#------------------------------------------------------------------------------

def histogram_dates(f1, f2, bin_size) :
	#datetimeFormat = '%m/%d/%Y %H:%M' 
	datetimeFormat = '%Y-%m-%d %H:%M:%S' 

	data1 = open(f1, 'r'); 
	outf = open(str(f2), 'w')
	#print >> outf, 'committer_id|feature_id_id|time_commit_committer|num_files|additions_code_sum|changes_code_sum|deletions_code_sum|net_contribution|bug_or_bluepint|binnumber_2months'

	print >> outf, 'committer_id|feature_id_id|time_commit_committer|num_files|num_files_added|num_files_removed|num_files_modified|num_files_comments|num_code_added|num_code_removed|num_code_modified|num_code_total|net_contribution|time_revision|indiv_comitter_firm_type|bug_or_bluepint|binnumber_2months'

	list_time = []; date_dict = defaultdict(list)

	data_committer = defaultdict(list)
	for line in data1.readlines()[1:] :
		line = line.strip().split('|')

		dates = str(line[5])
		comid = str(line[0])
		feature_type = str(line[17]); feature_id = str(line[1]) 
		time_revision = str(line[3])
		### add the part on number of codes, changes, etc and net contribution ###
		#num_files = int(line[3]); code_add = int(line[4]); code_changes = int(line[5]); code_del = int(line[6])
		#net_contribution = code_add - 0.5*code_del + code_changes
		date_dict[datetime.datetime.strptime(dates, datetimeFormat)] = dates

		list_time.append(datetime.datetime.strptime(dates, datetimeFormat))
		#data_committer[comid].append((datetime.datetime.strptime(dates, datetimeFormat), feature_id, feature_type))
		#data_committer[comid].append((datetime.datetime.strptime(dates, datetimeFormat), feature_id, num_files, code_add, code_changes, code_del, float(net_contribution), feature_type))

		### I am adding the headers and variables from Data_Commit.csv in the Processed data folder ###
		num_files = int(line[6]); num_files_added = int(line[7]); num_files_removed = int(line[8]); num_files_modified = int(line[9]); num_files_comments = int(line[10]); 
		num_code_added = float(line[11]); num_code_removed = float(line[12]); num_code_modified = float(line[13]); num_code_total = float(line[14]);
		net_contribution = num_code_added - 0.5*num_code_removed + num_code_modified
		indiv_comitter_firm_type = str(line[16])
		data_committer[comid].append((datetime.datetime.strptime(dates, datetimeFormat), feature_id, num_files, num_files_added, num_files_removed, num_files_modified, num_files_comments, num_code_added, num_code_removed, num_code_modified, num_code_total, float(net_contribution), time_revision,indiv_comitter_firm_type, feature_type))

	#list_time.sort()
	#list_time.reverse()
	max_overall_date_committer = max(list_time)
	min_overall_date_committer = min(list_time)

	#start_date = datetime.datetime.strptime( str(min_overall_date_committer), datetimeFormat)
	#end_date = datetime.datetime.strptime( str(max_overall_date_committer), datetimeFormat)
 
	start_date = min_overall_date_committer
	end_date = max_overall_date_committer

	list2 = []; bin_size = bin_size

	## create the bins ###
	if start_date <= end_date:
		for n in range( 0, ( end_date - start_date ).days + 1, int(bin_size) ):
			list2.append( start_date + datetime.timedelta( n ) )
	else:
		for n in range( 0, ( start_date - end_date ).days + 1, int(bin_size)):
			list2.append( start_date - datetime.timedelta( n ) )

	l = []
	for d in list2 :
	   l.append(datetime.datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S"))

	### where the dates fall in the bins and enumerate them 
	bin_date_dict = defaultdict(list)
	for i in list_time:
		for j in range(len(l)):
			if l[j-1] < i < l[j]:
				bin_date_dict[str(i)] = j

	for keys, values in data_committer.items() :

		for v in values :

			date_v = str(v[0])
			print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' %  (keys,  v[1], date_dict[v[0]], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12], v[13], v[14], bin_date_dict[date_v])


#------------------------------------------------------------------------------
# Within the histograms get the the code contributions
#------------------------------------------------------------------------------

def bin_by_bin_edges_codes_contribution(f1, f2) :

	### First for each feature in every bin get the committer nodes 
	data1 = open(f1, 'r');    
	outf = open(str(f2), 'w')
	#print >> outf, 'committer_id|bin_2months|num_files|total_code_added|total_code_change|total_code_del|sum_net_contr|avg_net_contr|mean_neighbr_files|mean_neighbr_code_add|mean_neighbr_code_change|mean_neighbr_code_del|mean_neighbr_avg_avg_netcontr|mean_neighbr_avg_sum_netcontr'
	print >> outf, 'committer_id|feature_id_id|bin_2months|firm_type|num_files|time_revision_sum|time_revision_mean|num_code_added|num_code_change|num_code_del|num_code_total|sum_net_contr|avg_net_contr|mean_neighbr_files|mean_neighbr_code_add|mean_neighbr_code_change|mean_neighbr_code_del|mean_neighbr_code_total|mean_neighbr_avg_avg_netcontr|mean_neighbr_avg_sum_netcontr|num_neighbors'

	dict_bin_commiter_files = defaultdict(list); dict_bin_commiter_codeaddsum = defaultdict(list)
	dict_bin_commiter_cdoechangesum = defaultdict(list); dict_bin_commiter_codedelsum = defaultdict(list)
	dict_bin_commiter_netcontr = defaultdict(list); dict_bin_commiter = defaultdict(list); dict_bin_commiter_codetotal = defaultdict(list)

	dict_bin_commiter_details = defaultdict(list); dict_bin_commiter_rev_time = defaultdict(list)
	committer_code_added  = defaultdict(list); committer_code_changes = defaultdict(list); committer_code_del = defaultdict(list); committer_code_total = defaultdict(list)
	committer_avg_netcontr = defaultdict(list); committer_sum_netcontr = defaultdict(list); committer_files = defaultdict(list)
	committer_code_time_rev_sum = defaultdict(list); committer_code_time_rev_mean = defaultdict(list)

	for line in data1.readlines()[1:] :
		line = line.strip().split('|')
		feature_id = str(line[1]) ; bin_num = str(line[16]); firm_type = str(line[14])
		committer = str(line[0])
		
		dict_bin_commiter_files[committer+'|'+feature_id+'|'+bin_num+'|'+firm_type].append(float(line[3]))
		dict_bin_commiter_codeaddsum[committer+'|'+feature_id+'|'+bin_num+'|'+firm_type].append(float(line[8]))
		dict_bin_commiter_cdoechangesum[committer+'|'+feature_id+'|'+bin_num+'|'+firm_type].append(float(line[10]))
		dict_bin_commiter_codedelsum[committer+'|'+feature_id+'|'+bin_num+'|'+firm_type].append(float(line[9]))
		dict_bin_commiter_netcontr[committer+'|'+feature_id+'|'+bin_num+'|'+firm_type].append(float(line[12]))
		dict_bin_commiter_codetotal[committer+'|'+feature_id+'|'+bin_num+'|'+firm_type].append(float(line[11]))

		dict_bin_commiter[feature_id+'|'+bin_num].append(committer+'|'+feature_id+'|'+bin_num+'|'+firm_type)

		dict_bin_commiter_rev_time[committer+'|'+feature_id+'|'+bin_num+'|'+firm_type].append(float(line[13]))


	for keys, values in dict_bin_commiter_netcontr.items() :

		total_codeadd_sum_bin = np.sum(dict_bin_commiter_codeaddsum[str(keys)])
		total_codchange_sum_bin = np.sum(dict_bin_commiter_cdoechangesum[str(keys)])
		total_coddel_sum_bin = np.sum(dict_bin_commiter_codedelsum[str(keys)])
		netcontr_sum_bin = np.sum(dict_bin_commiter_netcontr[str(keys)])
		netcontr_avg_bin = np.mean(dict_bin_commiter_netcontr[str(keys)])
		total_files_bin = np.sum(dict_bin_commiter_files[str(keys)])

		num_code_total = np.sum(dict_bin_commiter_codetotal[str(keys)])

		time_revision_sum = np.sum(dict_bin_commiter_rev_time[str(keys)])
		time_revision_mean = np.mean(dict_bin_commiter_rev_time[str(keys)])

		dict_bin_commiter_details[str(keys)] = str(total_files_bin)+'|'+str(time_revision_sum)+'|'+str(time_revision_mean)+'|'+str(total_codeadd_sum_bin)+'|'+str(total_codchange_sum_bin)+'|'+str(total_coddel_sum_bin)+'|'+str(num_code_total)+'|'+str(netcontr_sum_bin)+'|'+str(netcontr_avg_bin)

		committer_code_added[str(keys)] = float(total_codeadd_sum_bin)
		committer_code_changes[str(keys)] = float(total_codchange_sum_bin)
		committer_code_del[str(keys)] = float(total_coddel_sum_bin)
		committer_sum_netcontr[str(keys)] = float(netcontr_sum_bin)
		committer_avg_netcontr[str(keys)] = float(netcontr_avg_bin)
		committer_files[str(keys)] = float(total_files_bin)

		committer_code_total[str(keys)] = float(num_code_total)

		#committer_code_time_rev_sum[str(keys)] = float(time_revision_sum)
		#committer_code_time_rev_mean[str(keys)] = float(time_revision_mean)

	G = nx.Graph(); edgelist = []

	### Create the network edges by bin #####

	for keys in dict_bin_commiter :
		values = list(set(dict_bin_commiter[str(keys)]))

		if len(values) > 0 :
			edges = combinations(values, 2)

			for (u,v) in list(set(edges)) :

				edgelist.append((u,v))

	G.add_edges_from(edgelist)

	for n in G.nodes() :

				avg_files_neighbor = np.mean([committer_files[str(x)] for x in G.neighbors(n)])
				avg_code_added_neighbor = np.mean([committer_code_added[str(x)] for x in G.neighbors(n)])
				avg_code_changes_neighbor = np.mean([committer_code_changes[str(x)] for x in G.neighbors(n)])
				avg_code_del_neighbor = np.mean([committer_code_del[str(x)] for x in G.neighbors(n)])
				avg_mean_netcontr_neighbor = np.mean([committer_avg_netcontr[str(x)] for x in G.neighbors(n)])
				avg_sum_netcontr_neighbor = np.mean([committer_sum_netcontr[str(x)] for x in G.neighbors(n)])
				avg_mean_codetotal_neighbor = np.mean([committer_code_total[str(x)] for x in G.neighbors(n)])


				print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( n, dict_bin_commiter_details[str(n)], avg_files_neighbor, avg_code_added_neighbor, avg_code_changes_neighbor,  avg_code_del_neighbor, avg_mean_codetotal_neighbor, avg_mean_netcontr_neighbor, avg_sum_netcontr_neighbor, len(G.neighbors(n)))
				print n

#------------------------------------------------------------------------------
# Within the bins of histograms estimate the diversity indices: Herfindahl Index
# and Insularity indices, similarity index
#------------------------------------------------------------------------------

def create_diversity_developers(f1,f2, f3, f4) :


	### First for each feature in every bin get the committer nodes 

	data1 = open(f1, 'r');    
	outf = open(str(f2), 'w'); outf2 = open(str(f3), 'w'); outf3 = open(str(f4), 'w')
	print >> outf, 'committer_id|bin_2months|firm_type|herfindahl_index'
	print >> outf2, 'committer_id|bin_2months|firm_type|mean_insularity_index|std_insularity_index'
	print >> outf3, 'committer_id|bin_2months|firm_type|mean_similarity_index|std_similarity_index'



	dict_bin_commiter = defaultdict(list); dict_committer_type = defaultdict(list)

	dict_hi_items = defaultdict(list); dict_insularity = defaultdict(list); dict_similarity = defaultdict(list)

	for line in data1.readlines()[1:] :
		line = line.strip().split('|')
		feature_id = str(line[1]) ; bin_num = str(line[16]); firm_type = str(line[14])
		committer = str(line[0])
		
		dict_bin_commiter[feature_id+'|'+bin_num].append(committer+'|'+bin_num)
		dict_committer_type[committer+'|'+bin_num] = firm_type

	G = nx.Graph(); edgelist = []

	### Create the network edges by bin #####

	for keys in dict_bin_commiter :
		values = list(set(dict_bin_commiter[str(keys)]))

		if len(values) > 0 :
			edges = combinations(values, 2)

			for (u,v) in list(set(edges)) :

				edgelist.append((u,v))

	G.add_edges_from(edgelist)

	for n in G.nodes() :
		dict_hi_items[n] = [dict_committer_type[str(x)] for x in G.neighbors(n)]

	### Get Herfindahl Index ###
	for key, values in dict_hi_items.items() :
		d = {}
		try :
			for i in values:
				if len(i) >0 :
					d[i] = values.count(i) 
			print >> outf, '%s|%s|%s' %( key, dict_committer_type[str(key)], sum([(float(n1*1.0/sum(d.values())))**2 for n1 in d.values()]) )

		except ValueError,e :
			continue

	### Get Insularity Index ###
	for n in G.nodes() :
		for x in G.neighbors(n) :
			if str(dict_committer_type[str(n)]) == str(dict_committer_type[str(x)]) :
				Insularity = 1
				dict_insularity[str(n)].append(Insularity)
			if str(dict_committer_type[str(n)]) != str(dict_committer_type[str(x)]) :
				Insularity = 0
				dict_insularity[str(n)].append(Insularity)

	for key, values in dict_insularity.items() :
		print >> outf2, '%s|%s|%s|%s' %( key, dict_committer_type[str(key)], np.mean(values), np.std(values) )


	### Get pairwise similarity of neighbors #### 
	for n in G.nodes() :
		neighborlist = G.neighbors(n)
		neighborpairs = combinations(neighborlist,2)

		for u,v in neighborpairs :
			if dict_committer_type[str(u)] == dict_committer_type[str(v)] :
				similarity_index = 1
				dict_similarity[str(n)].append(similarity_index)

			if dict_committer_type[str(u)] != dict_committer_type[str(v)] :
				similarity_index = 0
				dict_similarity[str(n)].append(similarity_index)

	for key, values in dict_similarity.items() :
		print >> outf3, '%s|%s|%s|%s' %( key, dict_committer_type[str(key)], np.mean(values), np.std(values) )




if __name__ == '__main__':

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	#histogram_dates(f1, f2, f3)

	#f1 = sys.argv[1]; f2 = sys.argv[2]
	#bin_by_bin_edges_codes_contribution(f1, f2)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
	#create_diversity_developers(f1, f2, f3, f4)
	

