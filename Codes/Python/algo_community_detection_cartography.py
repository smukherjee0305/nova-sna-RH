
#    Created on 2017
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI


"""Codes for community detection using Infomap algorithm, cartographic measures of nodes."""
"""

Provides:

 - rolescartography()
 - communityroledetectionInfomap()
 - findCommunitiesInfomap()

References:
 - networkx:     https://networkx.github.io/
 - Cartography algorithm: Cartography of complex networks: modules and universal roles.Guimera, R, Amaral, LAN. J. Stat. Mech.-Theory Exp.,  P02001 (2005)
 - Infomap algorithm: http://www.mapequation.org/code.html
"""

#! /usr/bin/env python
import sys
import os, re
import networkx as nx
#from matplotlib import pyplot
import old_gml as nx_old
from itertools import combinations, product, permutations
from collections import defaultdict
import copy, difflib
from datetime import datetime
import time, glob
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from sets import Set
sys.path.insert(0, '../../CommunityStructure/Infomap/examples/python/infomap/')
import infomap ### Let's get the community structure using infomap algorithm
import math


def rolescartography (H, detectionalgo):

	"""

Acknowledge the members of the Amaral lab.

Given a name.gml file of a network with community structure (atributte 'community' of each node indicates to which community it belongs),
it clasifies the nodes of the GC into different roles,
according to its connectivity inside/outside its own community.

It modifies the file name.gml with new atributtes for the nodes:
   Within-module degree zscore ('zi')
   Participation coefficient ('Pi')
   The role the node belongs to ('role')

For further detail, see: Cartography of complex networks: modules and universal roles.Guimera, R, Amaral, LAN. J. Stat. Mech.-Theory Exp.,  P02001 (2005).


	"""
				   
	G = H

	list_nodes_GC=G.nodes()

	num_nodes_GC=int(len(list_nodes_GC))

	
	label_comm=[] #list of community labels
	for i in list_nodes_GC: 
		G.node[i]['nzi'+'_'+str(detectionalgo)]=0.0  # i add a new attribute to the nodes
		G.node[i]['nPi'+'_'+str(detectionalgo)]=0.0  # i add a new attribute to the nodes


		community_index=G.node[i]['community_index_label'+'__'+str(detectionalgo)].split('__')[0]
	   # community_size=G.node[i]['community'].split('_')[1]
		
		G.node[i]['community_index'+'_'+str(detectionalgo)]=int(community_index)
	   # G.node[i]['community_size']=community_size

		#print G.node[i]['community_index_label'+'__'+str(detectionalgo)],community_index,G.node[i]['community_index'+'_'+str(detectionalgo)]#,G.node[i]['community_size']
		#raw_input()
		# the label comunity in the gml file: index_size


		if G.node[i]['community_index'+'_'+str(detectionalgo)] not in label_comm:
			label_comm.append(G.node[i]['community_index'+'_'+str(detectionalgo)])
	num_com=int(len(label_comm))
	#print label_comm,len(label_comm)
	



# calculate the within-module degree zscore (zi):

	average_ksi=[] #list of averages of total degree, computed inside each community si
	nodes_in_comm=[] #list of number of nodes for each community si
	deviation=[]  # standard deviation of k in community si
	for i in range(num_com):  # community indexes go from 0 to num_com-1
		average_ksi.append(0.0)
		nodes_in_comm.append(0.0)
		deviation.append(0.0)
   

	for i in list_nodes_GC:  # loop over all nodes in GC         
		#print i, G.degree(i)
		average_ksi[G.node[i]['community_index'+'_'+str(detectionalgo)]]=average_ksi[G.node[i]['community_index'+'_'+str(detectionalgo)]]+G.degree(i)
		nodes_in_comm[G.node[i]['community_index'+'_'+str(detectionalgo)]]=nodes_in_comm[G.node[i]['community_index'+'_'+str(detectionalgo)]]+1
	 
		
	for i in range(num_com): 
		average_ksi[i]=average_ksi[i]/nodes_in_comm[i]   
   



	for i in list_nodes_GC:
		deviation[G.node[i]['community_index'+'_'+str(detectionalgo)]]=deviation[G.node[i]['community_index'+'_'+str(detectionalgo)]]+(G.degree(i)-average_ksi[G.node[i]['community_index'+'_'+str(detectionalgo)]])**2


	for i in range(num_com):
		deviation[i]=math.sqrt(deviation[i]/nodes_in_comm[i])



	for i in list_nodes_GC:   
		ki=0.0
		for node in G.neighbors(i):  # loop over  i's neighbors
			if G.node[i]['community_index'+'_'+str(detectionalgo)]==G.node[node]['community_index'+'_'+str(detectionalgo)]: #if both belong to the same comm
				ki=ki+1        
		#print  ki, average_ksi[G.node[i]['community_index']],deviation[G.node[i]['community_index']], G.node[i]['community_index'] 
		if  deviation[G.node[i]['community_index'+'_'+str(detectionalgo)]] >0.0:    
			G.node[i]['nzi'+'_'+str(detectionalgo)]=(ki-average_ksi[G.node[i]['community_index'+'_'+str(detectionalgo)]])/deviation[G.node[i]['community_index'+'_'+str(detectionalgo)]]


	


# calculate participation coefficient:
	for i in list_nodes_GC:    
		add=0.0
		for c in range(num_com):  # loop over all communities
			kis=0.0 # number of neighbors of i belonging to comm c
			fraction=0.0     
			for node in G.neighbors(i):   #loop over i's neighbors
				if G.node[node]['community_index'+'_'+str(detectionalgo)]==c:
					kis=kis+1.0  
			fraction=(kis/float(G.degree(i)))**2
			add=add+fraction
		G.node[i]['nPi'+'_'+str(detectionalgo)]=1.0-add


	num_R1=num_R2=num_R3=num_R4=num_R5=num_R6=num_R7=0

# asign a role to each node:

	for i in list_nodes_GC:
	  if G.node[i]['nzi'+'_'+str(detectionalgo)] > 2.0 :
		if G.node[i]['nPi'+'_'+str(detectionalgo)] > 1.0/(1.5*G.node[i]['nzi'+'_'+str(detectionalgo)]) :
				G.node[i]['nrole'+'_'+str(detectionalgo)]='R6'
				H.node[i]['nrole'+'_'+str(detectionalgo)]='R6'

				num_R6+=1


	for i in list_nodes_GC:
		if G.node[i]['nzi'+'_'+str(detectionalgo)]>= 2.0: #it is a hub
			if G.node[i]['nPi'+'_'+str(detectionalgo)]< 0.3:
				G.node[i]['nrole'+'_'+str(detectionalgo)]='R5'
				H.node[i]['nrole'+'_'+str(detectionalgo)]='R5'

				num_R5+=1
			#elif( (G.node[i]['Pi']>= 0.3) and (G.node[i]['Pi']< 0.75)):
			#    G.node[i]['role']='R6'
			#    H.node[i]['role']='R6'
			#    num_R6+=1
			  #  print H.node[i]['role'],H.node[i]['label'],"activity",H.node[i]['activity'],"degree",H.node[i]['degree'],"time",H.node[i]['time_in_system']

			elif  G.node[i]['nPi'+'_'+str(detectionalgo)]>= 0.75:
				G.node[i]['nrole'+'_'+str(detectionalgo)]='R7'
				num_R7+=1
		else: # it is not a hub
			if G.node[i]['nPi'+'_'+str(detectionalgo)]< 0.05:
				G.node[i]['nrole'+'_'+str(detectionalgo)]='R1'
				H.node[i]['nrole'+'_'+str(detectionalgo)]='R1'
				num_R1+=1

			elif ((G.node[i]['nPi'+'_'+str(detectionalgo)]>= 0.05) and (G.node[i]['nPi'+'_'+str(detectionalgo)]< 0.65)):
				G.node[i]['nrole'+'_'+str(detectionalgo)]='R2'
				H.node[i]['nrole'+'_'+str(detectionalgo)]='R2'
				num_R2+=1

			elif ((G.node[i]['nPi'+'_'+str(detectionalgo)]>= 0.65) and (G.node[i]['nPi'+'_'+str(detectionalgo)]< 0.8)):
				G.node[i]['nrole'+'_'+str(detectionalgo)]='R3'
				H.node[i]['nrole'+'_'+str(detectionalgo)]='R3'
				num_R3+=1

				#print G.node[i]['Pi'],G.node[i]['role']

			elif round(G.node[i]['nPi'+'_'+str(detectionalgo)]) >= 0.80:
			   
				G.node[i]['nrole'+'_'+str(detectionalgo)]='R4'
				H.node[i]['nrole'+'_'+str(detectionalgo)]='R4'
				#print G.node[i]['Pi'],G.node[i]['role']
				num_R4+=1

	  

	#print H,"GC:",len(G.nodes()), "R1s:",num_R1, "R2s:",num_R2, "R3s:", num_R3,"R4s:", num_R4,"R5s:", num_R5,"R6s:", num_R6,"R7s:", num_R7


	return G

	#H = nx.write_gml(G,str(name))

#------------------------------------------------------------------------------
# Commuity Structure for reading graph
#------------------------------------------------------------------------------

def communityroledetectionInfomap(H, detectionalgo):
	"""
	Partition network with the Infomap algorithm.
	Annotates nodes with 'community' id and return number of communities found.
	"""

	G = H
	infomapWrapper = infomap.Infomap("-d -N10 --silent")

	#print("Building Infomap network from a NetworkX graph...")
	for e in G.edges_iter():
		infomapWrapper.addLink(*e)

	#print("Find communities with Infomap...")
	infomapWrapper.run();

	tree = infomapWrapper.tree
	#print tree

	#print("Found %d top modules with codelength: %f" % (tree.numTopModules(), tree.codelength()))

	communities = {}
	for node in tree.leafIter(1):
			communities[node.originalLeafIndex] = node.moduleIndex()
	
	lv = communities.values()
	
	nx.set_node_attributes(G, 'community'+'__'+str(detectionalgo), communities)
	
	#print tree.numTopModules()

	for n in G.nodes() :
			if n in communities:
				G.node[n]['community_index_label'+'__'+str(detectionalgo)] = str(communities[n])+'__'+str(n)
	#print G.nodes(data=True)
	#return communities #tree.numTopModules()

	#print list(set(communities.values()))

	G = rolescartography(G, str(detectionalgo))

	return G


#------------------------------------------------------------------------------
# Commuity Structure for reading gml files
#------------------------------------------------------------------------------

def findCommunitiesInfomap(n1, n2, detectionalgo):
	"""
	Partition network with the Infomap algorithm.
	Annotates nodes with 'community' id and return number of communities found.
	"""

	globgml = glob.glob('/media/mukherjee/My Book/OpenStack/WeightedDSM/Idea5_weighted_dsm/nova-*.gml')
	for gml_file in globgml[int(n1):int(n2)] :
		print gml_file

		G = nx_old.read_gml(gml_file)
		infomapWrapper = infomap.Infomap("-d -N10 --silent")

	#print("Building Infomap network from a NetworkX graph...")
		for e in G.edges_iter():
			infomapWrapper.addLink(*e)

	#print("Find communities with Infomap...")
		infomapWrapper.run();

		tree = infomapWrapper.tree
	#print tree

	#print("Found %d top modules with codelength: %f" % (tree.numTopModules(), tree.codelength()))

		communities = {}
		for node in tree.leafIter(1):
			communities[node.originalLeafIndex] = node.moduleIndex()
	
		lv = communities.values()
	
		nx.set_node_attributes(G, 'community'+'__'+str(detectionalgo), communities)
	
	#print tree.numTopModules()

		for n in G.nodes() :
			if n in communities:
				G.node[n]['community_index_label'+'__'+str(detectionalgo)] = str(communities[n])+'__'+str(n)
	#print G.nodes(data=True)
	#return communities #tree.numTopModules()

	#print list(set(communities.values()))

		G = rolescartography(G, str(detectionalgo))
		G = nx_old.write_gml(G, '/media/mukherjee/My Book/OpenStack/WeightedDSM/Idea5_weighted_dsm_cartography/'+str(gml_file.split('/')[-1]))

if __name__ == '__main__':
	f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	findCommunitiesInfomap(f1, f2, f3)

