
Content of the Repo

Files All codes are commented with descriptions, reference and Usage. 

Python
1.	00_download_scrape_openstack_git.py
2.	01_code_embeddedness_developers.py
3.	02_code_diversity_network_developers.py
4.	03_spatio_temporal_developer_network.py
5.	03_create_monte_carlo_spatio_temporal_network.py
6.	04_code_complexity_motifs.py
7.	05_create_DSM_motif_counts_propagation_cost.py
8.	algo_community_detection_cartography.py

R
1.	03_ERGM_cumulative_spatio-temporal_networks.R
2.	03_mediation_monte_carlo_method.R
3.	03_spatio-temporal_networks_descriptives.R
4.	R_script.sh

Stata 
1.	imputation_code_DV_ratio.do
2.	code_diversity_interactions.do
3.	Idea03_code_mediation.do


Data 
(Due to excessive file size of some of the data, we have included only a part of the full sample. 
You may run the codes to generate the full data in your local drive)

1.	00_data_from_git/status_q_merged_pages_html/status_q_merged_800.html
2.	00_data_from_git/subject_pages_html/subject_page_nova_4743.html
3.	00_data_from_git/gitweb_links_html_commits/commits_2766__01e6f7575a3c75bd73e297f3d9d003292e0a0e1e.xhtml
4.	00_data_from_git/github_archives/nova-eab5851b0b55c4230cc11460f9efc6b617ae2e68.zip
5.	00_data_from_git/data_commits_developers_from_html_text/openstack_NOVA_codes_lines_added_comitter_author_code_details.txt
6.	00_data_from_git/data_commits_developers_from_html_text/openstack_NOVA_codes_lines_removed_comitter_author_code_details.txt
7.	01_network_developers/02_processd_all_firms_data__committer_network_from_common_feature_modified.gml
8.	03_spatio_temporal/ERGM_cumulative_networks/nova_spatial_temporal_network_cumulative_2012_2013.gml
9.	03_spatio_temporal/networks_per_year_mediation/nova_committer_spatial_temporal_network_weights_2012.gml
10.	03_spatio_temporal/Null_model_monte_carlo_example/sim__100.gml
11.	04_network_of_files/network_of_files_example/nova-eab5851b0b55c4230cc11460f9efc6b617ae2e68.gml
12.	04_network_of_files/dsm_examples__2012.gephi




Analyses completed

1.	Download html/xhtml and Nova repositories
	File: 00_download_scrape_openstack_git.py
	i.	download_status_q_merged_pages_html 
		Downloads the pages from “https://review.openstack.org/#/q/status:merged,”

	ii.	download_subject_pages_html
		Read the html pages and save in a text formatted table

	iii.	download_status_pages
		Download the status pages from the data of merged pages

	iv.	download_gitweb_pages
		From the subject pages, get the commit ID and save the commit pages. We get the committer ID from these commit pages.

	v.	extract_from_gitweb_commit_lines_code_info
		From the commit pages get the information of commiter, lines of code added/removed and codenames and commit ID

	vi.	download_codes_github
		Download the zip folders of each commit in Nova 
		Same code could be used for other OpenStack packages

——————————————————————————————————————————————————————————————————————————-

2.	Manuscript: Central or in a Nucleus? Joint Problem Solving Relationships and Individual Knowledge Creation in Open Collaboration (Under Review 2017)
	File: 01_code_embeddedness_developers.py
	i.	create_edge_list 
		Creates an edgelist from the input file containing Developer data and feature ID (obtained from Albert Armisen’s dataset)

	ii.	network_create_gml
		Generate network in gml format and add attributes

	iii.	network_measures
		Algorithms for degree, betweenness centrality and k-shell index

	iv.	network_attribute_node_type
		Add node attributes – types of developers

	v.	create_blueprint_bug_feauture_committer
		Create dataset for exploration-exploitation analysis

	vi.	neighbor_attribute_node_type
		Add neighbor’s contribution in terms of lines of code added into the gml file and save in table format as well

	vii.	tenure_committer
		Get the tenure of a developer

	viii.	create_output_from_gml
		Convert gml data to table data for regression analysis

	ix.	plot_network_nx
		Plot developers’ network in networkx module


——————————————————————————————————————————————————————————————————————————-


3.	Manuscript: Temporal and Spatial Distance and Knowledge Contribution (Under Preparation)
	File: 03_spatio_temporal_developer_network.py
	i.	countDuplicatesInList 
		Counts the number of times a tuple appears in a list. This function is used to count the weight of an edge during formation of network links.

	ii.	network_measures
		Network parameters – degree, betweenness centrality, k-shell

	iii.	create_spatial_temporal_network_of_developers
		Create the spatio-temporal network of developers separated in time and space. We generate the network from the commit time data of developers.

	iv.	measure_developer_attributes
		Get the node attributes – lines of code added/removed by a developer
		Average code complexity of files on which developers work on

	v.	spatio_temporal_network_neighbor_ego_effect
		Get the neighbor and Ego effect on the developers

	File: 03_create_monte_carlo_spatio_temporal_network.py
	i.	null_model_shuffle_edge_weights 
		Here we randomly shuffle the edge weights of the network, keeping the structure of the network fixed. So, the neighbors of a developer are the same, but the weights are randomly shuffled. Repeat 100 times. 

	ii.	gen_null_network_from_raw_data
		Create random samples of the commit data using Monte Carlo sampling. Here we randomly shuffle from the original commit data – A developer commits at time t1 and t2 on file f1 at lines L1-15, would commit randomly at times t10, t25 on file f4 at lines L18-45. Repeat these 100 times.

	iii.	spatio_temporal_network_neighbor_ego_effects
		Get the neighbor and Ego effect on the developers using the networks obtained from Monte Carlo sampling

	File: 03_mediation_monte_carlo.R 
		(R script to run mediation model on networks obtained from Monte Carlo sampling and check how many times mediating role of spatial distance exist)
						
	File: 03_spatio-temporal_networks_descriptives.R 
		(R script to run descriptives of the spatio-temporal network of developers)


——————————————————————————————————————————————————————————————————————————-


4.	Manuscript: Exponential Random Graph Model (ERGM) in explaining the emergence of problem-centric knowledge collaboration (Under Preparation)
	File: 03_ERGM_cumulative_spatio-temporal_networks.R 
	(R script to run ERGM on the spatio-temporal networks of developers )




——————————————————————————————————————————————————————————————————————————-




5.	Manuscript: Motifs and modularity in complex systems (Under Preparation)
	File: 04_code_complexity_motifs.py
	i.	countDuplicatesInList 
		Counts the number of times a tuple appears in a list. This function is used to count the weight of an edge during formation of network links

	ii.	network_measures
		Algorithms for degree, betweenness centrality and k-shell index

	iii.	get_code_complexity_measures
		From the zip folder of nova get the code complexity measures – CC, HV, MI

	iv.	get_import_dsm
		Algorithm to generate Design Structure Matrix from the folders of each commit

	v.	gen_network_function_reuse
		Algorithm to create the network of files from functional reuse. Two files are connected if the use the same function. For example, two files using mean function of numpy gets connected by a link.

	vi.	gen_network_architectural_reuse
		Two files are connected if they import the same package. Two files importing numpy module in Python gets connected.


——————————————————————————————————————————————————————————————————————————-


6.	Manuscript: Motifs and modularity in complex systems (Under Preparation)
	File: 05_create_DSM_motif_counts_propagation_cost.py
	i.	subgraph_pattern 
		Motif detection algorithm. Count all k-subgraphs in the network. Which of those subgraphs are isomorphic (i.e. topologically equivalent) and count only once every such isomorphic groups.

	ii.	check_cycles
		Count all cyclical subgraphs in the network

	iii.	check_Motifs
		Count all k-subgraphs in the network.
		
	iv.	write_network_attr_gml
		Node and edge attributes of each file-file dependency network (DSM)

	v.	gen_visibility_matrix_dsm_adjacency
		Generate the visibility matrix of DSM and evaluate the propagation cost as defined by Baldwin


——————————————————————————————————————————————————————————————————————————-




7.	Algorithm: Community detection and Cartographic measures
	File: algo_commuity_detection_cartography.py
	i.	rolescartography 
		Given a community structure, this function classifies the node into various roles

	ii.	communityroledetectionInfomap
		Infomap algorithm to detect communities

	iii.	findCommunitiesInfomap
		Annotates nodes with 'community' id and return number of communities found.


——————————————————————————————————————————————————————————————————————————-



8.	Manuscript: The role of collaboration diversity on knowledge contribution (Under Preparation)
	File: 02_code_diversity_network_developers.py
	i.	histogram_dates 
		Create the bin of 2months/4months 

	ii.	bin_by_bin_edges_codes_contribution
		Code contribution of developers in each bin

	iii.	create_diversity_developers
		Herfindahl index, Insularity index and similarity index of developers: diversity measure












