#    Created on 2017
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI

"""Codes to generate network of files.
	Two files are connected if there is a function call (directed graph)
	Two files are connected if they share a common package (Architecture reuse network)
	or they share a common function (Function reuse network) """
"""

Provides:

 - countDuplicatesInList()
 - network_measures()
 - get_code_complexity_measures()
 - get_import_dsm()
 - gen_network_function_reuse()
 - gen_network_architectural_reuse()

References:
 - radon:     https://pypi.python.org/pypi/radon/
 - networkx:     https://networkx.github.io/
 - findimports:     https://pypi.python.org/pypi/findimports/
 - Haltead Volume: https://en.wikipedia.org/wiki/Halstead_complexity_measures
 - Cyclomatic complexity : https://en.wikipedia.org/wiki/Cyclomatic_complexity
 - Maintainability Index: http://www.projectcodemeter.com/cost_estimation/help/GL_maintainability.htm

Publication:
 - Motifs and modularity in complex systems (Under Preparation)
"""

from radon.raw import analyze
from radon.metrics import *
from radon.complexity import cc_visit
from radon.cli.tools import iter_filenames
import os,sys, re
import zipfile, glob
from modulefinder import ModuleFinder
from collections import defaultdict
from itertools import combinations, product, permutations
import networkx as nx
from sets import Set
import matplotlib.pyplot as plt
import old_gml as nx_old
import numpy as np
import operator
import inspect, importlib as implib

def countDuplicatesInList(dupedList):
	"""Returns list/tuple of elements and their counts."""

   uniqueSet = Set(item for item in dupedList)
   return [(item, dupedList.count(item)) for item in uniqueSet]

def network_measures(G) :

	"""Returns graph with node attributes"""
	"""
	Using networkx module we get the degree, normalized weighted betweenness centrality,
	number of triangles of a node and local clustering coefficient. The node attributes 
	are then stored in a gml file
	"""
	H = G

	## get the strenght (or weighted degree of a node)
	for node, val in nx.degree(H, weight='weight').items() :
		H.node[node]['strength'] = float(val)

	## get the normalized betweenness centrality of nodes
	betweenness_dictionary = nx.betweenness_centrality(H,weight='weight',normalized=True)
	for u,v in betweenness_dictionary.items() :
		H.node[u]['normalized_bc'] = float(v)

	## number of triangles a node is part of
	for node, val in nx.triangles(H).items() :
		H.node[node]['triangle'] = float(val)

	### local clustering coefficient ###
	for node, val in nx.clustering(H, weight='weight').items() :
		H.node[node]['local_clustering_coefficient'] = float(val)


	return H

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



def get_import_dsm(sourcedir, destdir, n1, n2) :

	"""
	References:
 	Hidden structure: Using network methods to map system architecture
 	Research Policy
	Volume 43, Issue 8, October 2014, Pages 1381-1397
	Carliss Baldwin, Alan MacCormack, John Rusnak
	"""
	"""
	Procedure:
	1. Read the zip files for each commit in Nova (or Cinder/Neutron/any other package in OpenStack)
	2. Using the findimports module, gather the information of "import packages" in every file.
	3. From the file and corresponding imported package, form the directed graph of files: Two files are connected if 
	a file imports a function from another file. For example, if file A imports a function from file B, a directed link
	exists from B to A
	4.convert the zip files to a directed network of files and store in gml format with node attributes
	"""
	"""
	Usage:
	
	sourcedir : the directory where we stored the zip folder of Nova packages
	destdir: the directory where we save the gml files
	n1,n2 : Gives the range of the files we are reading
	"""
	import findimports
	from findimports import ImportFinder, ImportFinderAndNameTracker, Module, ModuleCycle, ModuleGraph
	import ast, sys


	globzipfiles = glob.glob(sourcedir+'*.zip')
	
	for zipfile2 in globzipfiles[int(n1):int(n2)] :
		
		print zipfile2

		dict_matrix_inbuilt = defaultdict(list)
		dict_matrix_local = defaultdict(list) 
		edgelist_file_call_import = []

		dict_file_mi = defaultdict(list)

		with zipfile.ZipFile(zipfile2) as z:

			for filename in z.namelist():
				
				if filename.endswith(".py") :
					if not os.path.isdir(filename):

						with z.open(filename) as fobj:
							source_fobj = fobj.read()
							try :
								mi_par = mi_parameters(source_fobj)
								halstead_volume = mi_par[0]
								cyclomatic_complexity = mi_par[1]
								mi = mi_visit(source_fobj, True)
							
								dict_file_mi[str(filename)] = str(halstead_volume)+'|'+str(cyclomatic_complexity)+'|'+str(mi)

							
								source = ast.parse(source_fobj, filename)
								
							except SyntaxError,e :
								continue

						visitor = ImportFinderAndNameTracker(filename)
						try :
							
								visitor.warn_about_duplicates = ImportFinderAndNameTracker.warn_about_duplicates
								visitor.verbose = ImportFinderAndNameTracker.verbose
								visitor.visit(source)

								importslist = visitor.imports

								if len(importslist) > 0 :
									for mods in importslist :
										searchname_module = mods.name.split('.')[-1]+'.'
										linenomod = mods.lineno
										filenamemod =  filename

										### The filename from which a function is being imported:
										importfilename = str(filenamemod.split('/')[0])+'/'+mods.name.replace('.','/')+".py"
										
										### Create the unweighted-directed network as per Baldwin's DSM 

										l = 1
										for lines in source_fobj.splitlines() :

												#### Now we add weights to the links as per the count of the import function used
												#### First we get the location where the import is called in filename. We mark the function/class being used
												#### Next we look for the function/class in the importfilename. 

												for m in re.finditer(r'\b'+re.escape(searchname_module)+r'\b', str(lines)) :
														if importfilename in z.namelist():
															with z.open(importfilename) as fobjimp:
																source_import = fobjimp.read()
																import_func = lines.split(str(searchname_module))[1]
																import_func = re.sub('[!@#]', '', import_func).encode('ascii', 'ignore')
																edgelist_file_call_import.append((str(importfilename), str(filenamemod)))

												l += 1



						except ValueError,e :
							continue
		outgmlname = zipfile2.split('/')[-1][:-4]
		### Start creating the networks 

		count_edges = countDuplicatesInList(edgelist_file_call_import)
		edgelist_file_call_import_weight = []; edgelist_file_call_import_lnweight = []; 

		#generate an empty directed graph with networkx
		G_wt_dsm = nx.DiGraph()
		for u,v in count_edges :
			edgelist_file_call_import_lnweight.append(( u[0], u[1], np.log10(1+int(v)) ))
			edgelist_file_call_import_weight.append((u[0], u[1], int(v)))

		## create the weighted network of directed links
		## weight is equal to the number of times a file imports from another file
		G_wt_dsm.add_weighted_edges_from(edgelist_file_call_import_weight,weight='weight')

		G_wt_dsm.add_weighted_edges_from(edgelist_file_call_import_lnweight,weight='log10weight')


		nodelist = G_wt_dsm.nodes()
		### Now include the node attributes: Halstead volume, cyclomatic complexity, maintainability index
		for n in nodelist :
			if n in dict_file_mi :
				G_wt_dsm.add_node(n, halstead_volume=dict_file_mi[n].split('|')[0])
				G_wt_dsm.add_node(n, cyclomatic_complexity=dict_file_mi[n].split('|')[1])
				G_wt_dsm.add_node(n, maintainability_index=dict_file_mi[n].split('|')[2])

		## Now save the networks in gml format
		G_wt_dsm = nx_old.write_gml(G_wt_dsm, destdir+str(outgmlname)+'.gml')


def gen_network_function_reuse(sourcedir, destdir1, destdir2, n1, n2) :

	"""
	Procedure:
	1. Read the zip files for each commit in Nova (or Cinder/Neutron/any other package in OpenStack)
	2. Using the findimports module, gather the information of "import packages" in every file.
	3. From the file and corresponding imported package, form the network of files: Two files are connected if 
	they import the same function from a module. For example two files A and B import from another file C. 
	If they import the same function we form an undirected link between A and B. No link is formed if A & B 
	import different function from C. The weight of a link (A-B) is thus the unique number of such functions.
	4. There are two kinds of packages - system inbuilt (like numpy, scipy, sys, os) and local inbuilt (Nova)
	5.convert the zip files to a directed network of files and store in gml format with node attributes once 
	for system inbuilt and again for local inbuilt

	"""
	
	"""
	Usage:
	
	sourcedir : the directory where we stored the zip folder of Nova packages
	destdir1: the directory where we save the gml files for local inbuilt networks
	destdir2: the directory where we save the gml files for system inbuilt networks
	n1,n2 : Gives the range of the files we are reading
	"""
	import findimports
	from findimports import ImportFinder, ImportFinderAndNameTracker, Module, ModuleCycle, ModuleGraph
	import ast, sys

	globzipfiles = glob.glob(sourcedir+str(start_yr)+'/'+'*.zip')
	

	for zipfile2 in globzipfiles[int(n1):int(n2)] :
		
			print zipfile2

			dict_matrix_inbuilt = defaultdict(list)
			dict_matrix_local = defaultdict(list) 
			edgelist_file_call_import = []

			dict_file_mi = defaultdict(list)

			with zipfile.ZipFile(zipfile2) as z:

				for filename in z.namelist():
				
					if filename.endswith(".py") :
						if not os.path.isdir(filename):

							with z.open(filename) as fobj:
								source_fobj = fobj.read()
								try :

									###get the complexity indices of the files
									mi_par = mi_parameters(source_fobj)
									halstead_volume = mi_par[0]
									cyclomatic_complexity = mi_par[1]
									mi = mi_visit(source_fobj, True)
							
									dict_file_mi[str(filename)] = str(halstead_volume)+'|'+str(cyclomatic_complexity)+'|'+str(mi)

							
									source = ast.parse(source_fobj, filename)
								
								except SyntaxError,e :
									continue

							visitor = ImportFinderAndNameTracker(filename)
							try :
							
								visitor.warn_about_duplicates = ImportFinderAndNameTracker.warn_about_duplicates
								visitor.verbose = ImportFinderAndNameTracker.verbose
								visitor.visit(source)

								importslist = visitor.imports

								if len(importslist) > 0 :
									for mods in importslist :
										searchname_module = mods.name.split('.')[-1]+'.'
										linenomod = mods.lineno
										filenamemod =  filename

										importfilename = str(filenamemod.split('/')[0])+'/'+mods.name.replace('.','/')+".py"
										
										l = 1
										for lines in source_fobj.splitlines() :

												#### Now we add weights to the links as per the count of the import function used
												#### First we get the location where the import is called in filename. We mark the function/class being used
												#### Next we look for the function/class in the importfilename. 

												"""
												Use regular expression (re in Python) we locate the packages and functions in the file
												Next we form a dictionary of files and corresponding functions as values
												"""
												for m in re.finditer(r'\b'+re.escape(searchname_module)+r'\b', str(lines)) :
														if importfilename in z.namelist():

															with z.open(importfilename) as fobjimp:

																source_import = fobjimp.read()
																import_func = lines.split(str(searchname_module))[1]
																import_func = re.sub('[!@#]', '', import_func).encode('ascii', 'ignore')

																import_func_call = re.split(r'[()]', import_func)[0]

																import_func_plus_call = mods.name+'.'+import_func_call

																#### Get the matrix for system inbuilt matrix and local inbuilt matrix
																#### If two codes import from the same file, the two codes are connected with a weight
																#### weight is equal to the number of imported functions in common bwteen the two codes.

																### system inbuilt
																if not "nova" in str(mods.name) and "novalib" not in str(mods.name): 
																		dict_matrix_inbuilt[filename].append(str(import_func_plus_call))

																### local
																if "nova" in str(mods.name) :
																		dict_matrix_local[filename].append(str(import_func_plus_call))



												l += 1


							except ValueError,e :
								continue


			outgmlname = zipfile2.split('/')[-1][:-4]
			
			### Start creating the networks 
			## form the combination of pairs of files
			
			combinations_local = combinations(dict_matrix_local.keys(), 2)

			combinations_inbuilt = combinations(dict_matrix_inbuilt.keys(), 2)

			G_local = nx.Graph(); G_inbuilt = nx.Graph(); edge_l = []; edge_inb = []; edge_l2 = []; edge_inb2 = []
		
			for u,v in combinations_local :
				list_int_loc = list(set(dict_matrix_local[u]).intersection(dict_matrix_local[v]))
				if len(list_int_loc) > 0 :
					num_times_common_function_call_local = len(list(set(list_int_loc)))

					edge_l.append((u, v, np.log10(1+num_times_common_function_call_local)))
					edge_l2.append((u, v, num_times_common_function_call_local))

			G_local.add_weighted_edges_from(edge_l, weight='log10weight')
			G_local.add_weighted_edges_from(edge_l2, weight='weight')

		### Now include the node attributes: Halstead volume, cyclomatic complexity, maintainability index

			for n in G_local.nodes() :
				if n in dict_file_mi :
					G_local.add_node(n, halstead_volume=dict_file_mi[n].split('|')[0])
					G_local.add_node(n, cyclomatic_complexity=dict_file_mi[n].split('|')[1])
					G_local.add_node(n, maintainability_index=dict_file_mi[n].split('|')[2])


			for u,v in combinations_inbuilt :
				list_int_inb = list(set(dict_matrix_inbuilt[u]).intersection(dict_matrix_inbuilt[v]))
				if len(list_int_inb) > 0 :
					num_times_common_function_call_inbuilt = len(list(set(list_int_inb)))		
						
					edge_inb.append((u, v, np.log10(1+num_times_common_function_call_inbuilt)))
					edge_inb2.append((u, v, num_times_common_function_call_inbuilt))

			G_inbuilt.add_weighted_edges_from(edge_inb, weight='log10weight')
			G_inbuilt.add_weighted_edges_from(edge_inb2, weight='weight')

		### Now include the node attributes: Halstead volume, cyclomatic complexity, maintainability index

			for n in G_inbuilt.nodes() :
				if n in dict_file_mi :
					G_inbuilt.add_node(n, halstead_volume=dict_file_mi[n].split('|')[0])
					G_inbuilt.add_node(n, cyclomatic_complexity=dict_file_mi[n].split('|')[1])
					G_inbuilt.add_node(n, maintainability_index=dict_file_mi[n].split('|')[2])

			### Get the network measures for the networks
			G_local_net_measures = network_measures(G_local)
			G_inbuilt_net_measures = network_measures(G_inbuilt)
		
			### Save the networks in gml format
			G_local = nx_old.write_gml(G_local, destdir1+str(start_yr)+'/'+str(outgmlname)+'-local'+'.gml')
			G_inbuilt = nx_old.write_gml(G_inbuilt, destdir2+str(start_yr)+'/'+str(outgmlname)+'-inbuilt'+'.gml')
		

def gen_network_architectural_reuse(sourcedir, destdir1, n1, n2) :

	"""
	Procedure:
	1. Read the zip files for each commit in Nova (or Cinder/Neutron/any other package in OpenStack)
	2. Using the findimports module, gather the information of "import packages" in every file.
	3. From the file and corresponding imported package, form the network of files: Two files are connected if 
	they import the same package(module). For example two files A and B import from another file C. A and B are thus linked.
	The weight of a link (A-B) is thus the unique number of such packages.
	4. Here we consider only local inbuilt network (Nova)
	5.convert the zip files to a directed network of files and store in gml format with node attributes once 
	for system inbuilt and again for local inbuilt

	"""
	
	"""
	Usage:
	
	sourcedir : the directory where we stored the zip folder of Nova packages
	destdir1: the directory where we save the gml files for local inbuilt networks
	n1,n2 : Gives the range of the files we are reading

	"""
	import findimports
	from findimports import ImportFinder, ImportFinderAndNameTracker, Module, ModuleCycle, ModuleGraph
	import ast, sys

	globzipfiles = glob.glob(sourcedir+'*.zip')
	
	for zipfile2 in globzipfiles[int(n1):int(n2)] :
		
		print zipfile2

		dict_matrix_inbuilt = defaultdict(list)
		dict_matrix_local = defaultdict(list) 
		edgelist_file_call_import = []

		dict_file_mi = defaultdict(list)

		with zipfile.ZipFile(zipfile2) as z:

			for filename in z.namelist():
				
				if filename.endswith(".py") :
					if not os.path.isdir(filename):

						with z.open(filename) as fobj:
							source_fobj = fobj.read()
							try :
								mi_par = mi_parameters(source_fobj)
								halstead_volume = mi_par[0]
								cyclomatic_complexity = mi_par[1]
								mi = mi_visit(source_fobj, True)
							
								dict_file_mi[str(filename)] = str(halstead_volume)+'|'+str(cyclomatic_complexity)+'|'+str(mi)

							
								source = ast.parse(source_fobj, filename)
								
							except SyntaxError,e :
								continue

						## start finding the modules that are imported in the file
						visitor = ImportFinderAndNameTracker(filename)
						try :

								visitor.warn_about_duplicates = ImportFinderAndNameTracker.warn_about_duplicates
								visitor.verbose = ImportFinderAndNameTracker.verbose
								visitor.visit(source)
								#visitor.generic_visit(source)

								importslist = visitor.imports

								if len(importslist) > 0 :
									for mods in importslist :
										searchname_module = mods.name.split('.')[-1]+'.'
										linenomod = mods.lineno
										filenamemod =  filename

										importfilename = str(filenamemod.split('/')[0])+'/'+mods.name.replace('.','/')+".py"
										#create dictionary of files as keys and imported modules (packages) as values
										if "nova" in str(mods.name) :
											dict_matrix_local[filename].append(str(mods.name))


						except ValueError,e :
							continue


		outgmlname = zipfile2.split('/')[-1][:-4]
		### Start creating the networks 
		## form the combination of pairs of files
		combinations_local = combinations(dict_matrix_local.keys(), 2)

		G_local = nx.Graph();  edge_l = []; edge_inb = []; edge_l2 = []; edge_inb2 = []
		##using the file pairs, check if there are common packages in their values
		for u,v in combinations_local :
			list_int_loc = list(set(dict_matrix_local[u]).intersection(dict_matrix_local[v]))
			if len(list_int_loc) > 0 :
				#get the unique number of modules that are common to a pair of file
				num_times_common_package_call_local = len(list(set(list_int_loc)))

				edge_l.append((u, v, np.log10(1+num_times_common_package_call_local)))
				edge_l2.append((u, v, num_times_common_package_call_local))

		G_local.add_weighted_edges_from(edge_l, weight='log10weight')
		G_local.add_weighted_edges_from(edge_l2, weight='weight')

		### Now include the node attributes: Halstead volume, cyclomatic complexity, maintainability index

		for n in G_local.nodes() :
			if n in dict_file_mi :
				G_local.add_node(n, halstead_volume=dict_file_mi[n].split('|')[0])
				G_local.add_node(n, cyclomatic_complexity=dict_file_mi[n].split('|')[1])
				G_local.add_node(n, maintainability_index=dict_file_mi[n].split('|')[2])

		### Get the network measures for the networks
		G_local_net_measures = network_measures(G_local)

		### Save the networks in gml format
		G_local = nx_old.write_gml(G_local, destdir1+str(outgmlname)+'-local'+'.gml')




if __name__ == '__main__':

	f1 = sys.argv[1];f2 = sys.argv[2]; f3 = sys.argv[3];f4 = sys.argv[4]; #f5 = sys.argv[5]

	#gen_network_attr_reuse(f1, f2, f3, f4)
	#gen_network_function_reuse(f1, f2, f3, f4, f5)
	gen_network_architectural_reuse(f1, f2, f3, f4)