
***** SOBEL-GOODMAN MEDIATION *****
forvalues i=2012(1)2016 {
	di `i'
	insheet using "/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/04_Network_Ideas/Idea03_06/Data/Stata/Nodes/nova_committer_spatial_temporal_network_weights_`i'_Nodes.csv",delim(",") clear


	gen log10_code_add = log10(1+lines_of_code_added_sum)
	gen log10_code_avg = log10(1+lines_of_code_added_avg)
	gen log10_tenure = log10(1+tenure_committer)
	gen log10_num_commits = log10(1+total_num_committs)

	gen byte touse = !missing(log10_code_add, log10_code_avg,  log10_tenure, log10_num_commits, neigh_lines_of_code_added_sum , ego_lines_of_code_added_sum , neigh_lines_of_code_added_avg, ego_lines_of_code_added_avg, avg_mi_committer, s_mean_spatial_inter, s_diff_90_10_spatial, s_diff_90_10_temporal, s_wt_mu_inter_commit_time, s_wt_hm_diff_first_commit_time, s_wt_hm_diff_last_commit_time )

	foreach var of varlist log10_code_add log10_code_avg  log10_tenure log10_num_commits neigh_lines_of_code_added_sum  ego_lines_of_code_added_sum  neigh_lines_of_code_added_avg ego_lines_of_code_added_avg avg_mi_committer s_mean_spatial_inter s_diff_90_10_spatial s_diff_90_10_temporal s_wt_mu_inter_commit_time s_wt_hm_diff_first_commit_time s_wt_hm_diff_last_commit_time{
	sum `var' if touse == 1
	gen double z_`var' = (`var' - r(mean))/ r(sd) 
	
	}
	
*** pairwise correlation ****
	
	pwcorr z_log10_code_add z_log10_tenure z_log10_num_commits z_avg_mi_committer, sig
	

** temporal is intercommit diff and spatial is inter line difference

	sgmediation z_log10_code_add, mv(z_s_mean_spatial_inter) iv(z_s_wt_mu_inter_commit_time) cv(z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg)

	
** temporal and spatial are difference of 90th and 10th percentile

	sgmediation z_log10_code_add, mv(z_s_diff_90_10_spatial) iv(z_s_diff_90_10_temporal) cv(z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg)
	
	
** temporal is diff of fist commit time and spatial is difference of 90th and 10th percentile
	
	*sgmediation z_log10_code_add, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_first_commit_time)

	*sgmediation z_log10_code_add, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_last_commit_time)

	
*** regressions ***

	reg z_log10_code_add z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg , robust
	estat ic
	
	reg z_log10_code_add z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_wt_mu_inter_commit_time, robust
	estat ic	

	reg z_log10_code_add z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_wt_mu_inter_commit_time z_s_mean_spatial_inter, robust
	estat ic
	


	reg z_log10_code_add z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_diff_90_10_temporal, robust
	estat ic	

	reg z_log10_code_add z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_diff_90_10_temporal z_s_diff_90_10_spatial, robust
	estat ic
********************************************************************************************************	
*********************** Get the robustness Check with DV as lines of code avg **************************
********************************************************************************************************

	
*** pairwise correlation ****
	
	pwcorr z_log10_code_avg z_log10_tenure z_log10_num_commits z_avg_mi_committer z_neigh_lines_of_code_added_avg, sig
	

** temporal is intercommit diff and spatial is inter line difference

	sgmediation z_log10_code_avg, mv(z_s_mean_spatial_inter) iv(z_s_wt_mu_inter_commit_time) cv(z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg)

	
** temporal and spatial are difference of 90th and 10th percentile

	sgmediation z_log10_code_avg, mv(z_s_diff_90_10_spatial) iv(z_s_diff_90_10_temporal) cv(z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg)
	
	
** temporal is diff of fist commit time and spatial is difference of 90th and 10th percentile
	
	*sgmediation z_log10_code_add, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_first_commit_time)

	*sgmediation z_log10_code_add, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_last_commit_time)

	
*** regressions ***

	reg z_log10_code_avg z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg, robust
	estat ic
	
	reg z_log10_code_avg z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_wt_mu_inter_commit_time, robust
	estat ic	

	reg z_log10_code_avg z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_wt_mu_inter_commit_time z_s_mean_spatial_inter, robust
	estat ic
	


	reg z_log10_code_avg z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_diff_90_10_temporal, robust
	estat ic	

	reg z_log10_code_avg z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_diff_90_10_temporal z_s_diff_90_10_spatial, robust
	estat ic
}	





***** descriptives and pairwise correlation *****
forvalues i=2012(1)2016 {
	di `i'
	insheet using "/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/04_Network_Ideas/Idea03_06/Data/Stata/Nodes/nova_committer_spatial_temporal_network_weights_`i'_Nodes.csv",delim(",") clear


	gen log10_code_add = log10(1+lines_of_code_added_sum)
	gen log10_code_avg = log10(1+lines_of_code_added_avg)
	gen log10_tenure = log10(1+tenure_committer)
	gen log10_num_commits = log10(1+total_num_committs)

	gen byte touse = !missing(log10_code_add, log10_code_avg,  log10_tenure,  neigh_lines_of_code_added_avg, avg_mi_committer, s_mean_spatial_inter, s_diff_90_10_spatial, s_diff_90_10_temporal, s_wt_mu_inter_commit_time )

	foreach var of varlist log10_code_add log10_code_avg  log10_tenure  neigh_lines_of_code_added_avg avg_mi_committer s_mean_spatial_inter s_diff_90_10_spatial s_diff_90_10_temporal s_wt_mu_inter_commit_time {
	sum `var' if touse == 1
	gen double z_`var' = (`var' - r(mean))/ r(sd) 

	}
	
*** descriptives *****

	sum z_log10_code_add z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_wt_mu_inter_commit_time z_s_mean_spatial_inter

	
*** pairwise correlation ****

	pwcorr z_log10_code_add z_log10_tenure z_avg_mi_committer z_neigh_lines_of_code_added_avg z_s_wt_mu_inter_commit_time z_s_mean_spatial_inter, sig

}	
