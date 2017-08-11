
***** SOBEL-GOODMAN MEDIATION *****
forvalues i=2012(1)2016 {
	di `i'
	insheet using "../../Data/Idea03CSV/nova_committer_spatial_temporal_network_weights_`i'_Nodes.csv",delim(",") clear
	drop timeset 

	gen log10_code_add = log10(1+lines_of_code_added_sum)
	gen log10_code_avg = log10(1+lines_of_code_added_avg)
	gen log10_tenure = log10(1+tenure_committer)

	gen byte touse = !missing(log10_code_add, log10_code_avg,  log10_tenure, neigh_lines_of_code_added_sum , ego_lines_of_code_added_sum , neigh_lines_of_code_added_avg, ego_lines_of_code_added_avg, avg_mi_committer, s_mean_spatial_inter, s_diff_90_10_spatial, s_wt_mu_inter_commit_time, s_wt_hm_diff_first_commit_time, s_wt_hm_diff_last_commit_time )

	foreach var of varlist log10_code_add log10_code_avg  log10_tenure neigh_lines_of_code_added_sum  ego_lines_of_code_added_sum  neigh_lines_of_code_added_avg ego_lines_of_code_added_avg avg_mi_committer s_mean_spatial_inter s_diff_90_10_spatial s_wt_mu_inter_commit_time s_wt_hm_diff_first_commit_time s_wt_hm_diff_last_commit_time{
	sum `var' if touse == 1
	gen double z_`var' = (`var' - r(mean))/ r(sd) 
	
	}

** temporal is intercommit diff and spatial is inter line difference

	sgmediation z_log10_code_add, mv(z_s_mean_spatial_inter) iv(z_s_wt_mu_inter_commit_time)

	

** temporal is diff of fist commit time and spatial is difference of 90th and 10th percentile
	
	sgmediation z_log10_code_add, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_first_commit_time)

	sgmediation z_log10_code_add, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_last_commit_time)


	
********************************************************************************************************	
*********************** Get the robustness Check with DV as lines of code avg **************************
********************************************************************************************************

** temporal is intercommit diff and spatial is inter line difference

	sgmediation z_log10_code_avg, mv(z_s_mean_spatial_inter) iv(z_s_wt_mu_inter_commit_time)

	

** temporal is diff of fist commit time and spatial is difference of 90th and 10th percentile
	
	sgmediation z_log10_code_avg, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_first_commit_time)

	sgmediation z_log10_code_avg, mv(z_s_diff_90_10_spatial) iv(z_s_wt_hm_diff_last_commit_time)

}
