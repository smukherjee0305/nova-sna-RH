#!/usr/bin/env python
# encoding: utf-8
"""
networkx version is 1.11 / 
Satyam Mukherjee
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
# Count duplicates in a list and tuple
#------------------------------------------------------------------------------

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
# Form pairs of committers 
#------------------------------------------------------------------------------

def pair_of_committers(f1, f2):

    data1 = open(f1, 'r') 

    outf = open(str(f2), 'w')
    print >> outf, 'committer_id|co_committer_id|count_pairs|feature_type|binnumber_2months'

    dict_combo = defaultdict(list); commiter_combos = defaultdict(list)

    for line in data1.readlines()[1:] :
        line = line.strip().split('|')
        dict_combo[str(line[1])+'|'+str(line[3])+'|'+str(line[4])].append(str(line[0]))

    for keys, values in dict_combo.items() :
        if len(values) > 0 :
            edges = combinations(values,2)
            G2 = nx.Graph(); G2.add_edges_from(edges) 
            for u,v in G2.edges() :
                if u != v :
                    commiter_combos[str(keys.split('|')[1])+'|'+str(keys.split('|')[2])].append(( str(u), str(v) ))


    for keys, values in commiter_combos.items() :
        count_pair_committer = countDuplicatesInList(values)

        for u, v in count_pair_committer :
            print >> outf, '%s|%s|%s|%s' %  (u[0], u[1], v, keys)


#------------------------------------------------------------------------------
# Add neighbor, Ego network's effect 
#------------------------------------------------------------------------------
def network_attribute_node_type(files_csv, gml_file, output_txt) : 

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

#### The cumulative plot of number of pairs at each bin; average number of pairs
#### pairs of committers who move among Bugs, Blueprints and both in different time stamps

def fraction_feature_move(f1, f2, f3, f4) :
    
    data1 = open(f1, 'r'); outf2 = open(str(f2), 'w'); outf3 = open(str(f3), 'w'); outf4 = open(str(f4), 'w')

    committer_bin = defaultdict(list); committer_all_bin = defaultdict(list)

    for line in data1.readlines()[1:] :
        line = line.strip().split('|')
        committer_bin[str(line[0])+'|'+str(line[2])].append(str(line[1]))
        committer_all_bin[str(line[0])].append(str(line[1]))

    for keys, values in committer_bin.items() :

        if len(values) == 2 :

            print >> outf2, keys.split('|')[0], keys.split('|')[1]

        for v in values :
            if str(v) == "bug" :
                print >> outf3, keys.split('|')[0], keys.split('|')[1]

            if str(v) == "blueprint" :
                print >> outf4, keys.split('|')[0], keys.split('|')[1]



def interevent_distribution(f1, outfile) :
    #datetimeFormat = '%m/%d/%Y %H:%M' 
    datetimeFormat = '%Y-%m-%d %H:%M:%S'
    data1 = open(f1, 'r'); 

    list_time = []; date_dict = defaultdict(list); data_committer = defaultdict(list); max_overall_date_committer = defaultdict(list)

    for line in data1.readlines()[1:] :
        line = line.strip().split('|')

        dates = str(line[2])
        comid = str(line[0])
        feature_type = str(line[15]); feature_id = str(line[1]); bin_num = str(line[16])
        
        #if feature_type == "bug" :
        date_dict[datetime.datetime.strptime(dates, datetimeFormat)] = dates

        list_time.append(datetime.datetime.strptime(dates, datetimeFormat))
        #data_committer[comid+'|'+feature_id].append(datetime.datetime.strptime(dates, datetimeFormat))
        data_committer[comid+'|'+bin_num].append(datetime.datetime.strptime(dates, datetimeFormat))

    for keys, values in data_committer.items() :
        values.sort()
        inter_event_days = [(t - s).days for s, t in zip(values, values[1:])]
        time_first_committed = min(values)
        if len(inter_event_days) > 0 :
        #    max_overall_date_committer[str(keys.split('|')[0])].append(max(inter_event_days))

            max_overall_date_committer[str(keys)] = str(max(inter_event_days))+'|'+str(time_first_committed)
        if len(inter_event_days) == 0 :
            max_overall_date_committer[str(keys)] = "0"+'|'+str(time_first_committed)

    #return clean_cdf_degree
    return max_overall_date_committer

### Exract the unique committers and committer pairs per bin ###

def new_nodes_edges(f1, outf) :
    data1 = open(f1, 'r'); list_running = []

    dataw = open(outf, 'w')

    dict_bin_commiter = defaultdict(list)

    for line in data1.readlines()[1:] :
        line = line.strip().split('|')
        #if str(line[3]) == "blueprint" :
        	#dict_bin_commiter[int(line[4])].append(int(line[0]))
        dict_bin_commiter[int(line[4])].append(str(line[0])+'|'+str(line[1]))


    for keys in sorted(dict_bin_commiter.iterkeys()):
    	list_running = list_running + list(set(dict_bin_commiter[int(keys)-1])) 
    	intersection =  set(list_running).intersection(set(dict_bin_commiter[int(keys)]))  #(list(set(list_running)))(list(set(dict_bin_commiter[int(keys)])))

        print >> dataw, keys, len(list(set(dict_bin_commiter[int(keys)]) - intersection))

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

### we need to get number of bluprints and bugs for every committer within a bin. 
### Get the tenure and revision time as well ??? 


#------------------------------------------------------------------------------
# Committer pairs and their evolution through time 
#------------------------------------------------------------------------------

def committer_pairs_per_bin_REM(f1, f2) :
    
    data1 = open(f1, 'r'); 
    outf = open(str(f2), 'w')
    print >> outf, 'feature_id_id|bug_or_blueprint|bin_2months|committer_id|firm_type|committer_neighbor_id|neighbor_firm_type|count'

    dict_create_whole_pairs = defaultdict(list); dict_create_bin_pairs = defaultdict(list); dict_committer_type = defaultdict(list)
    dict_feature_type = defaultdict(list)

    for line in data1.readlines()[1:] :
        line = line.strip().split('|')
        feature_id = str(line[1]) ; bin_num = str(line[16]); feature_type = str(line[15]); firm_type = str(line[14])
        committer_id = str(line[0])

        dict_create_whole_pairs[feature_id].append(committer_id)
        dict_create_bin_pairs[feature_id+'|'+bin_num].append(committer_id)

        dict_committer_type[committer_id] = firm_type
        dict_feature_type[feature_id] = feature_type

    G = nx.Graph() ; all_pairs = []; dict_pairs_committer = defaultdict(list)

    for keys, values in dict_create_bin_pairs.items() :
        
        edges = values
        committer_pairs = combinations(edges,2)

        for (u,v) in committer_pairs :
            if u != v :
                dict_pairs_committer[str(keys)].append(u+'|'+v)

    dict_pairs_committer_bin_count = defaultdict(list)
    for keys, values in dict_pairs_committer.items() :

        for k in countDuplicatesInList(values) :

            pairs = k[0]; count = k[1]; featureid = keys.split('|')[0] ; binnum = keys.split('|')[1]
            feature_type2 = dict_feature_type[str(featureid)]
            

            print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s' % (featureid, feature_type2, binnum, pairs.split('|')[0], dict_committer_type[str(pairs.split('|')[0])] ,pairs.split('|')[1], dict_committer_type[str(pairs.split('|')[1])], count )


            #print >> outf, '%s|%s|%s' % (keys, pairs, count)


#------------------------------------------------------------------------------
# Committer pairs column by column with time. Reformat from rows to columns
#------------------------------------------------------------------------------
def last_or_default(list, default):
    if len(list) > 0:
        return list[-1]
    return default

def initial_or_apply(list, f, y):
    if list == []:
        return [y]
    return list + [f(list[-1], y)]

def running_initial(f, initial):
    return (lambda x, y: x + [f(last_or_default(x,initial), y)])

def running(f):
    return (lambda x, y: initial_or_apply(x, f, y))

#totaler = lambda x, y: y
#running_totaler = running(totaler)
#running_running_totaler = running_initial(running_totaler, [])

def build_committer_pairs_through_time(f1, f2): 
    data1 = open(f1, 'r')
    
    outf = open(str(f2), 'w')
    print >> outf, 'bin|feature_id_id|feature_type|committer_id|firm_type|committer_neighbor_id|neighbor_firm_type|bin_2months|count'

    dic = defaultdict(list); dic_c = defaultdict(list); dic_new = defaultdict(list)

    for l in data1.readlines()[1:] :
        l = l.strip().split('|') 
        dic[int(l[2])].append(l[0]+'|'+l[1]+'|'+l[3]+'|'+l[4]+'|'+l[5]+'|'+l[6]) ## get the dictionary of pairs
        dic_c[l[0]+'|'+l[1]+'|'+l[3]+'|'+l[4]+'|'+l[5]+'|'+l[6]+'|'+l[2]] = l[7] ### Let's get the count of each pair for a feature within a bin

    l = []
    for keys,values in dic.iteritems() :
        data = values
        l = l + data
        dic_new[keys] = l ## This step creates the running list and a cumulative list in each bin
    
    for k, v  in dic_new.iteritems() :
        for v1 in v :
            if not v1+'|'+str(k) in dic_c :
                dic_c[v1+'|'+str(k)] = 0
            
            print >> outf, '%d|%s|%s' % ( int(k), v1+'|'+str(k), dic_c[v1+'|'+str(k)] )

def build_committer_pair_variables(f1, f2, f3) :

    data1 = open(f1, 'r'); ### Open the data containing committer information and attributes 
    data2 = open(f2, 'r') ### Open the data containing the pair wise information add the node level attributes

    outf = open(str(f3), 'w'); dic_num_code = defaultdict(list)
    print >> outf, 'bin|count|eature_id_id|feature_type|committer_id|committer_firm_type|committer_num_code_added|committer_num_code_total|committer_neighbor_id|neighbor_firm_type|neighbor_num_code_added|neighbor_num_code_total'

    for l in data1.readlines()[1:] :
        line = l.strip().split('|') 

        feature_id = str(line[1]) ; bin_num = str(line[2]); firm_type = str(line[3]); committer_id = str(line[0])

        num_code_added = str(line[7]); num_code_total = str(line[10])

        dic_num_code[bin_num+'|'+feature_id+'|'+committer_id+'|'+firm_type] = num_code_added+'|'+num_code_total

    for l in data2.readlines()[1:] :
        line = l.strip().split('|') 
        feature_id = str(line[1]) ; bin_num = str(line[0]); feature_type = str(line[2]); 
        committer_id = str(line[3]); firm_type = str(line[4])
        committer_neighbor_id = str(line[5]); neighbor_firm_type = str(line[6])
        pair_count = str(line[8])

        if not bin_num+'|'+feature_id+'|'+committer_id+'|'+firm_type in dic_num_code :
            dic_num_code[bin_num+'|'+feature_id+'|'+committer_id+'|'+firm_type] = "0"+'|'+"0"

        if not bin_num+'|'+feature_id+'|'+committer_neighbor_id+'|'+neighbor_firm_type in dic_num_code :
            dic_num_code[bin_num+'|'+feature_id+'|'+committer_neighbor_id+'|'+neighbor_firm_type] = "0"+'|'+"0"

        print >> outf,'%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( bin_num, pair_count, feature_id, feature_type, committer_id, firm_type, dic_num_code[bin_num+'|'+feature_id+'|'+committer_id+'|'+firm_type], committer_neighbor_id, neighbor_firm_type, dic_num_code[bin_num+'|'+feature_id+'|'+committer_neighbor_id+'|'+neighbor_firm_type] )



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

##############################################################################################################################
###### Get the code-hrefs links for every gitweb pages along with author name and committer name as well as code names #######
##############################################################################################################################

def extract_from_gitweb_code_links_committer_info(f2) :
    from bs4 import BeautifulSoup
    import glob

    '''
    From the gitweb pages get the code href 
    '''
    outf = open(str(f2), 'w'); 
    print >> outf, 'code_git_link|code_text|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'

    globhtmlfiles = glob.glob('../../../NewData_html/Nova/gitweb_links_html/commits/*.xhtml'); globhtmlfiles.sort()

    for htmlsource in globhtmlfiles :

        html_read = open(htmlsource,'r')
        page_source = BeautifulSoup(html_read, "html.parser")
        page_source.prettify
        try :
            list_source_codes = page_source('table',{"class":"diff_tree"}) 

            time_commit_author = page_source('table', {'class':'object_header'})[0]('span',{'class':'datetime'})[0].text
            time_commit_committer = page_source('table', {'class':'object_header'})[0]('span',{'class':'datetime'})[1].text
        
            commit_author = page_source('tr')[0]('a')[0].text.encode('ascii', 'ignore')
            commit_committer = page_source('tr')[2]('a')[0].text.encode('ascii', 'ignore')
        
            commit_author_email = page_source('tr')[0]('a')[1].text
            commit_committer_email = page_source('tr')[2]('a')[1].text


            for k in list_source_codes[0]('tr') :

                code_git_link = k('a',{'class':'list'})[0]['href']
                code_text =  k('a',{'class':'list'})[0].text

                codelink = "https://review.openstack.org/"+str(code_git_link)

                print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s' % (code_git_link, code_text, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer)

        except IndexError,e :
            continue

##############################################################################################################################
######      Get the code-hrefs links for every gitweb pages along with author name and commit lines in each code       #######
##############################################################################################################################

def extract_from_gitweb_commit_lines_code_info(f1, f2) :
    from bs4 import BeautifulSoup
    import glob

    globhtmlfiles = glob.glob('../../../NewData_html/Nova/gitweb_links_html/commits/*.xhtml'); globhtmlfiles.sort()
    
    #outf = open(str(f2), 'w'); 
    #print >> outf, 'code_init|code_line_start_range|code_final|code_line_end_range|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'
    #print >> outf, 'code_text|code_init|code_final|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'
    
    outf1 = open(str(f1), 'w'); outf2 = open(str(f2), 'w') 
    print >> outf1, 'lines_of_code_added|code_init|code_final|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'
    print >> outf2, 'lines_of_code_removed|code_init|code_final|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'

    for htmlsource in globhtmlfiles :

        html_read = open(htmlsource,'r')
        page_source = BeautifulSoup(html_read, "html.parser")
        page_source.prettify

        try :
            list_source_codes = page_source('div',{"class":"diff chunk_header"}) 
            
            time_commit_author = page_source('table', {'class':'object_header'})[0]('span',{'class':'datetime'})[0].text
            time_commit_committer = page_source('table', {'class':'object_header'})[0]('span',{'class':'datetime'})[1].text
        
            commit_author = page_source('tr')[0]('a')[0].text.encode('ascii', 'ignore')
            commit_committer = page_source('tr')[2]('a')[0].text.encode('ascii', 'ignore')
            
            commit_author_email = page_source('tr')[0]('a')[1].text
            commit_committer_email = page_source('tr')[2]('a')[1].text

            for k in page_source('div',{'class':'patch'}) :
 
                code_init = k('div',{"class":"diff chunk_header"})[0]('a')[0]['href']
                code_final = k('div',{"class":"diff chunk_header"})[0]('a')[1]['href']
                
                code_text_str = []; code_text_str_add = []; code_text_str_rem = []

                for s in k('div',{'class':'diff add'}) :
                    #if "index" not in str(s.text.encode('ascii', 'ignore')) and "diff --git" not in str(s.text.encode('ascii', 'ignore')) and "@@" not in str(s.text.encode('ascii', 'ignore')) and "---" not in str(s.text.encode('ascii', 'ignore')) and "+++" not in str(s.text.encode('ascii', 'ignore')):
                        if len(str(s.text.encode('ascii', 'ignore'))) > 0 :
                            code_text_str_add.append(str(s.text.encode('ascii', 'ignore')))

                #res_code_txt = " ".join(code_text_str)       
                print >> outf1, '%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( len(code_text_str_add), code_init, code_final, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )


                for s in k('div',{'class':'diff rem'}) :
                    #if "index" not in str(s.text.encode('ascii', 'ignore')) and "diff --git" not in str(s.text.encode('ascii', 'ignore')) and "@@" not in str(s.text.encode('ascii', 'ignore')) and "---" not in str(s.text.encode('ascii', 'ignore')) and "+++" not in str(s.text.encode('ascii', 'ignore')):
                        if len(str(s.text.encode('ascii', 'ignore'))) > 0 :
                            code_text_str_rem.append(str(s.text.encode('ascii', 'ignore')))
      
                print >> outf2, '%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( len(code_text_str_rem), code_init, code_final, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )


                #print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( res_code_txt, code_init, code_final, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )

            #for k in list_source_codes:
            #    code_init = k('a')[0]['href']
            #    code_line_start_range = k('a')[0].text
            #    code_final = k('a')[1]['href']
            #    code_line_end_range = k('a')[1].text
            #    print code_init, code_line_start_range, k, '\n'
                #print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( code_init, code_line_start_range, code_final, code_line_end_range, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )

        except IndexError,e :
            continue


def code_count(f1, yearstr, f2, f3) :
    data1 = open(f1, 'r')
    dict_committer_codes = defaultdict(list); dict_committer_codes_time_commit = defaultdict(list)
    
    for line in data1.readlines()[1:] :
        line = line.strip().split('|')

        committer_name = str(line[5].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0]); 
        committer_email = re.sub('[!#$IV()<>]', '', str(line[6])).encode('ascii', 'ignore') 
        if "Gerrit" not in committer_name and "Bot" not in committer_name:
            committer_id = committer_name #+'__'+committer_email

        codes = str(line[1])

        ## get the tag of time for creating the time-weighted network
        if " -" in str(line[7]) : 
            time_of_commit = str(line[7].split(', ')[1].split(' -')[0])
        
        if " +" in str(line[7]) : 
            time_of_commit = str(line[7].split(', ')[1].split(' +')[0])

        year = time_of_commit.split(' ')[2]

        if int(year) == int(yearstr) :
            dict_committer_codes_time_commit[codes+'|'+committer_id].append(time_of_commit)
            dict_committer_codes[codes].append(committer_id+'|'+time_of_commit)

    outf2 = open(str(f2), 'w'); outf3 = open(str(f3), 'w')

    for keys, values in dict_committer_codes_time_commit.items() :

            print >> outf2, '%s|%s' % (keys, len(values))

    for keys, values in dict_committer_codes.items() :

            print >> outf3, '%s|%s' % (keys, len(values))

def distributions_cdf(f1, f2, num) :

    '''
    mean spatial : column 31
    spatial difference of 90th and 10th : column 53
    mean temporal : column 43
    harmonic mean, first : column 51
    harmonic mean, last : column 39
    '''

    data1 = open(f1, 'r'); outf2 = open(str(f2), 'w')
    values = []
    for line in data1.readlines()[1:]:
        line = line.strip().split(',')
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


def create_release_type_date(f2) :
    from bs4 import BeautifulSoup

    globhtmlfiles = glob.glob("../../../githubnovareleasehtml/*.htm")
    outf = open(f2, 'w')

    for htmlsource in globhtmlfiles :
        
        html_read = open(htmlsource,'r')
        page_source = BeautifulSoup(html_read, "html.parser")
        page_source.prettify

        zip_page_source = zip((page_source('relative-time')), (page_source('span',{"class":"tag-name"})))
        for n in zip_page_source :
            date = n[0].text
            release = n[1].text
            print >> outf, '%s|%s' % (date, release)

def data_plot_networks_data() :

    import matplotlib.pyplot as plt

    globgmlfiles = glob.glob('../../../data_for_analysis_openstack_webscraping/Analysis_modeling/time_bins/three_months/incl_gerrit_bot/directed_network_committer_nova_bin_number_*.gml')
    scatter_n = defaultdict(list)
    scatter_e = defaultdict(list)
    dict_key1 = defaultdict(list)
    for gml_file in globgmlfiles :
        binn = gml_file.split('/')[8][:-4].split('_')[6]
        H = nx_old.read_gml(gml_file)
        num_nodes = len(H.nodes())
        num_edges = len(H.edges())
        #print int(binn), num_nodes, num_edges

        scatter_n[int(binn)] = int(num_nodes)
        scatter_e[int(binn)] = int(num_edges)
        for n in H.nodes() :
            dict_key1[int(binn)].append(H.node[n]['reciprocity'])

    #plt.plot(scatter_n.keys(), scatter_n.values(), 'blue', linewidth=3, label='Number of nodes')
    #plt.plot(scatter_e.keys(), scatter_e.values(), 'red', linewidth=3, label='Number of edges')

    means_l = []; std_l = []

    for k, v in dict_key1.items() :
        print k, "\t", np.mean(v)
    #    means_l.append(np.mean(v))
    #    std_l.append(np.std(v))

    ax = plt.gca()
    fontsize = 14
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize(fontsize)

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(fontsize)

    #plt.errorbar(np.array(dict_key1.keys()), np.array(means_l), np.array(std_l), linestyle='None', marker='^')

    #lg = pl.legend(fontsize=16,loc=(0.7, 0.82))
    #lg.draw_frame(True)
    #ymin = 0.00; ymax = 0.12; xmin = 1950; xmax = 2000
    #ymin = 0.5; ymax = 0.72; xmin = 5; xmax = 50
    #pl.axis([xmin, xmax, ymin, ymax])
    #pl.xticks(np.arange(xmin, xmax+1, 5)); pl.yticks(np.arange(ymin, ymax+0.005, 0.01))
    #pl.ylabel ('Mean dissimilarity', size=22)
    #pl.xlabel('Years', size=22)

    #plt.show()
    
    #for n in H.nodes(data=True):
        #    print n[1].keys()

def get_code_complexity_measures(n1, n2):



    globzipfiles = glob.glob('../../../NewData_html/Nova/github_archives/nova-*.zip')
    for zipfile2 in globzipfiles[int(n1):int(n2)] :
        print zipfile2
        commit_id = zipfile2.split('/')[6][:-4]
        
        outf1 = open('/media/mukherjee/OpenStack_Ext_Ha/Nova/Functionname_complexity/'+str(commit_id)+'.txt', 'w')
        outf2 = open('/media/mukherjee/OpenStack_Ext_Ha/Nova/Filename_complexity/'+str(commit_id)+'.txt', 'w')

        print >> outf1, 'filename|commit_id|function_name|function_letter|function_startline|function_endline|function_complexity'

        print >> outf2, 'filename|commit_id|MI|LOC|LLOC|SLOC|multi|blank|single_comments|halstead_volume|cyclomatic_complexity'

        with zipfile.ZipFile(zipfile2) as z:
            for filename in z.namelist():
                if filename.endswith(".py") :
                    if not os.path.isdir(filename):

# iter through filenames starting from the current directory
# you can pass ignore or exclude patterns here (as strings)
# for example: ignore='tests,docs'

                        with z.open(filename) as fobj:
                            source = fobj.read()

                            # get cc blocks
                            try :
                                blocks = cc_visit(source)
                                if len(blocks) > 0 :
                                    for k in blocks :
                                        function_startline = k.lineno
                                        function_endline = k.endline
                                        function_letter = k.letter
                                        function_classname = k.name
                                        function_complexity = k.complexity

                                        print >> outf1, '%s|%s|%s|%s|%s|%s|%s' % (filename, commit_id, function_classname, function_letter, function_startline, function_endline, function_complexity)


                                # get MI score
                                mi = mi_visit(source, True)

                                # get raw metrics
                                raw = analyze(source)
                                LOC = raw[0]
                                LLOC = raw[1]
                                SLOC = raw[2]
                                multi = raw[4]
                                blank = raw[5]
                                single_comments = raw[6]

                                # get MI parameters 
                                mi_par = mi_parameters(source)
                                halstead_volume = mi_par[0]
                                cyclomatic_complexity = mi_par[1]

                                print >> outf2, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( filename, commit_id, mi, LOC, LLOC, SLOC, multi, blank, single_comments, halstead_volume, cyclomatic_complexity )
                            except SyntaxError,e :
                                continue

def gen_committerid_semantic_measures(f1, gml_file, yearstr, f2):
    '''
    code to extract the semantic measures of code snippets by each committer
    and then utilizing it as a DV

    '''

    data1 = open(f1, 'r')
    dict_committer_codes_text = defaultdict(list); dict_committer = defaultdict(list)

    G = nx_old.read_gml(gml_file) ## read the networks files

    outfile = open(str(f2),'w')
    print >> outfile, 'label|mean_levinstein|median_levinstein|std_levinstein|ninetieth_levinstein|tenth_levinstein'

    for line in data1.readlines()[1:]:
        
        line = line.strip().split('|')
        
        author_name = str(line[3]); author_email = str(line[4]); author_commit_time = str(line[5])
        committer_name = str(line[6].replace(' ','_').replace('-','_').replace('__','_').split('_(')[0]); committer_email = str(line[7]); committer_commit_time = str(line[8])

        if "Gerrit" not in committer_name and "Bot" not in committer_name: ### We don't want any Bots ##

                #commitid = str(line[2].split(';')[4].split('#')[0].split('=')[1])
            try:
                codes = str(line[2].split(';')[2].split('=')[1])

                code_text = str(line[0])

                #print codes, code_text


                if " -" in str(line[8]) : 
                    time_of_commit = str(line[8].split(', ')[1].split(' -')[0])
                if " +" in str(line[8]) : 
                    time_of_commit = str(line[8].split(', ')[1].split(' +')[0])

                year = time_of_commit.split(' ')[2]

                if int(year) == int(yearstr) :
                    dict_committer_codes_text[committer_name+'|'+codes].append(code_text)
            except IndexError,e :
                continue

    #print dict_committer_codes_text.keys()

    for keys, values in dict_committer_codes_text.items() :
        combinations_codes = combinations(values,2)
        committer = keys.split('|')[0]

        for (p,q) in combinations_codes :
            if str(p) != str(q) :
                #product_codes = product(u, v)
                #for p, q in product_codes :
                    stringmatch_score = difflib.SequenceMatcher(None, str(p), str(q)).ratio()
                    dict_committer[str(committer)].append(float(stringmatch_score))

    #print dict_committer.keys()
    for n in G.nodes() :
        if str(G.node[n]['label']) in dict_committer :

            committer_mean_levinstein_distance = np.mean(dict_committer[str(G.node[n]['label'])])
            committer_median_levinstein_distance = np.median(dict_committer[str(G.node[n]['label'])])
            committer_std_levinstein_distance = np.std(dict_committer[str(G.node[n]['label'])])
            committer_90th_levinstein_distance = scipy.stats.scoreatpercentile(dict_committer[str(G.node[n]['label'])], 90)
            committer_10th_levinstein_distance = scipy.stats.scoreatpercentile(dict_committer[str(G.node[n]['label'])], 10)

            print >> outfile, '%s|%s|%s|%s|%s|%s' % (str(G.node[n]['label']), committer_mean_levinstein_distance, committer_median_levinstein_distance, committer_std_levinstein_distance, committer_90th_levinstein_distance, committer_10th_levinstein_distance)


            G.node[n]['mean_levinstein_distance'] = committer_mean_levinstein_distance
            G.node[n]['median_levinstein_distance'] = committer_median_levinstein_distance
            G.node[n]['std_levinstein_distance'] = committer_std_levinstein_distance
            G.node[n]['ninetieth_levinstein_distance'] = committer_90th_levinstein_distance
            G.node[n]['tenth_levinstein_distance'] = committer_10th_levinstein_distance

    gmlw = gml_file.split('/')[-1]
    fgml = '/'.join(gml_file.split('/')[:-1])

    G = nx_old.write_gml(G, str(fgml)+'/'+'levenstein_'+str(gmlw)) 


if __name__ == '__main__':


#------------------------------------------------------------------------------

#------------------------------------------------------------------------------ 
    #f1 = sys.argv[1]; f2 = sys.argv[2]
    #create_output_from_gml(f1, f2)

    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
    #create_blueprint_bug_feauture_committer(f1, f2, f3, f4)
    
    #f1 = sys.argv[1]; f2 = sys.argv[2]
    #tenure_committer(f1, f2)

    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
    #histogram_dates(f1, f2, f3)

    #f1 = sys.argv[1]; f2 = sys.argv[2]
    #pair_of_committers(f1, f2)

    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
    #fraction_feature_move(f1, f2, f3, f4)

    #f1 = sys.argv[1]; outfile = sys.argv[2]
    #list_val = interevent_distribution(f1,outfile)
    #outw = open(str(outfile), 'w')
    #for u,v in list_val :
    #    print >> outw, u, v

    #f1 = sys.argv[1]; f2 = sys.argv[2]
    #new_nodes_edges(f1, f2)

    #f1 = sys.argv[1]; f2 = sys.argv[2]
    #bin_by_bin_edges_codes_contribution(f1, f2)

    #f1 = sys.argv[1]; f2 = sys.argv[2]
    #committer_pairs_per_bin_REM(f1,f2)

    #f1 = sys.argv[1]; f2 = sys.argv[2]
    #build_committer_pairs_through_time(f1, f2)


    #f1 = sys.argv[1]; outfile = sys.argv[2]
    #list_val = interevent_distribution(f1,outfile)
    #outw = open(str(outfile), 'w')
    #print >> outw, 'committer_id|binnumber_2months|max_inter_commit_days|time_first_committed'
    #for keys, values in list_val.items():
    #    print >> outw, '%s|%s' % (keys, values)

    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
    #build_committer_pair_variables(f1, f2, f3)

    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
    #create_diversity_developers(f1, f2, f3, f4)
    
    #f1 = sys.argv[1]
    #extract_from_gitweb_code_links_committer_info()
    
    #f1 = sys.argv[1]
    #extract_from_gitweb_commit_lines_code_info(f1)

    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
    #convert_gml_to_table_for_analysis(f1, f2, f3, f4)
    
    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
    #code_count(f1, f2, f3, f4)

    f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3];
    distributions_cdf(f1, f2, f3)
    
    #f1 = sys.argv[1];
    #create_release_type_date(f1)

    #data_plot_networks_data()

    #f1 = sys.argv[1]; f2 = sys.argv[2];
    #get_code_complexity_measures(f1, f2)

    #f1 = sys.argv[1]; f2 = sys.argv[2];
    #extract_from_gitweb_commit_lines_code_info(f1, f2)


    #f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]; f4 = sys.argv[4]
    #gen_committerid_semantic_measures(f1, f2, f3, f4)
