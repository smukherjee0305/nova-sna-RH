use  "../../Data/Stata_files/Idea01_Data_committer_network_variables.dta", clear

*** DV as log_10 (num files, num code added, num code total) net contribution and standardize them along with IV

gen log10_revtime2 = log10(1+time_revision)
gen log10_num_files2 = log10(1+num_files)
gen log10_num_code_added2 = log10(1+num_code_added)
gen log10_num_code_total2 = log10(1+num_code_total)

gen log10_num_blueprints2 = log10(1+num_blueprints)
gen log10_num_bugs2 = log10(1+num_bugs)

gen log10_tot_blueprint2 = log10(1+num_code_total_blueprint)
gen log10_tot_bug2 = log10(1+num_code_total_bug)

gen log10_added_blueprint2 = log10(1+num_code_added_blueprint)
gen log10_added_bug2 = log10(1+num_code_added_bug)

gen byte touse = !missing(log10_num_blueprints2, log10_num_bugs2, log10_tot_blueprint2, log10_tot_bug2, log10_added_blueprint2, log10_added_bug2, num_code_total_blueprint, num_code_total_bug, num_code_added_blueprint, num_code_added_bug, num_blueprints, num_bugs, num_files, num_code_added, num_code_total, log10_num_files2, log10_num_code_added2, log10_num_code_total2, total_net_contr, time_revision, log10_revtime2, committer_tenure_overall, neighbor_mean_files, neighbor_mean_codes_tot, neighbor_mean_codes_added, neighbor_mean_net_contr_total , degree, kshell_index  )

foreach var of varlist log10_num_blueprints2 log10_num_bugs2 log10_tot_blueprint2 log10_tot_bug2 log10_added_blueprint2 log10_added_bug2 num_code_total_blueprint num_code_total_bug num_code_added_blueprint num_code_added_bug num_blueprints num_bugs num_files num_code_added num_code_total log10_num_files2 log10_num_code_added2 log10_num_code_total2 total_net_contr time_revision log10_revtime2 committer_tenure_overall neighbor_mean_files neighbor_mean_codes_tot neighbor_mean_codes_added neighbor_mean_net_contr_total degree kshell_index {
sum `var' if touse == 1
gen double z_`var' = (`var' - r(mean))/ r(sd) 
}

gen ratio_blueprints_bugs = num_blueprints / num_bugs
gen ratio_z_blueprints_bugs = z_num_blueprints / z_num_bugs

gen ratio_log10_blueprints_bugs = log10_num_blueprints2 / log10_num_bugs2
gen ratio_z_log10_blueprints_bugs = z_log10_num_blueprints2 / z_log10_num_bugs2

gen ratio_log10_numcodetot = log10_tot_blueprint2 / log10_tot_bug2
gen ratio_z_log10_numcodetot = z_log10_tot_blueprint2 / z_log10_tot_bug2

gen ratio_log10_numcodeadd = log10_added_blueprint2 / log10_added_bug2
gen ratio_z_log10_numcodeadd = z_log10_added_blueprint2 / z_log10_added_bug2


*** First perform the regression with ratio_blueprints_bugs ****
mi set mlong
mi register imputed ratio_blueprints_bugs 
mi impute regress ratio_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_blueprints_bugs degree if category == "networked"
mi estimate : regress ratio_blueprints_bugs kshell_index if category == "networked"

*** perform the regression with standardized ratio_z_blueprints_bugs ****
mi set mlong
mi register imputed ratio_z_blueprints_bugs 
mi impute regress ratio_z_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_z_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_z_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_z_blueprints_bugs z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_z_blueprints_bugs degree if category == "networked"
mi estimate : regress ratio_z_blueprints_bugs kshell_index if category == "networked"

*** take log transformation ***
mi set mlong
mi register imputed ratio_log10_blueprints_bugs  
mi impute regress ratio_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_log10_blueprints_bugs  degree if category == "networked"
mi estimate : regress ratio_log10_blueprints_bugs  kshell_index if category == "networked"

*** take log transformation and standardized IV***
mi set mlong
mi register imputed ratio_z_log10_blueprints_bugs  
mi impute regress ratio_z_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_z_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_z_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_z_log10_blueprints_bugs  z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_z_log10_blueprints_bugs  degree if category == "networked"
mi estimate : regress ratio_z_log10_blueprints_bugs  kshell_index if category == "networked"


*********************************************************
** DV is ratio of blueprint codes to bugs codes total ***
*********************************************************


*** First perform the regression with ratio_blueprints_bugs ****
mi set mlong
mi register imputed ratio_log10_numcodetot 
mi impute regress ratio_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_log10_numcodetot degree if category == "networked"
mi estimate : regress ratio_log10_numcodetot kshell_index if category == "networked"

*** perform the regression with standardized ratio_z_blueprints_bugs ****
mi set mlong
mi register imputed ratio_z_log10_numcodetot 
mi impute regress ratio_z_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_z_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_z_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_z_log10_numcodetot z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_z_log10_numcodetot degree if category == "networked"
mi estimate : regress ratio_z_log10_numcodetot kshell_index if category == "networked"


*********************************************************
** DV is ratio of blueprint codes to bugs codes added ***
*********************************************************

mi set mlong
mi register imputed ratio_log10_numcodeadd 
mi impute regress ratio_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_log10_numcodeadd degree if category == "networked"
mi estimate : regress ratio_log10_numcodeadd kshell_index if category == "networked"

*** perform the regression with standardized ratio_z_blueprints_bugs ****
mi set mlong
mi register imputed ratio_z_log10_numcodeadd 
mi impute regress ratio_z_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress ratio_z_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress ratio_z_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress ratio_z_log10_numcodeadd z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress ratio_z_log10_numcodeadd degree if category == "networked"
mi estimate : regress ratio_z_log10_numcodeadd kshell_index if category == "networked"


*** Here I take the log10 (ratio) once and then standardize as well *****

gen log10_ratio = log10(1 + num_blueprints / num_bugs)
gen log10_ratio_tot = log10(1 + num_code_total_blueprint / num_code_total_bug)
gen log10_ratio_added = log10(1 + num_code_added_blueprint / num_code_added_bug)

gen byte touse2 = !missing(log10_ratio, log10_ratio_tot, log10_ratio_added)

foreach var of varlist log10_ratio log10_ratio_tot log10_ratio_added {
sum `var' if touse2 == 1
gen double z_`var' = (`var' - r(mean))/ r(sd) 
}

mi set mlong
mi register imputed z_log10_ratio 
mi impute regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress z_log10_ratio degree if category == "networked"
mi estimate : regress z_log10_ratio kshell_index if category == "networked"


mi set mlong
mi register imputed z_log10_ratio_tot 
mi impute regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress z_log10_ratio_tot degree if category == "networked"
mi estimate : regress z_log10_ratio_tot kshell_index if category == "networked"


mi set mlong
mi register imputed z_log10_ratio_added 
mi impute regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall kshell_index if category == "networked"
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall degree if category == "networked"
mi estimate : regress z_log10_ratio_added degree if category == "networked"
mi estimate : regress z_log10_ratio_added kshell_index if category == "networked"

*** Here I take the log10 ratios once and then standardize as well *****

gen log10_ratio = log10(1 + num_blueprints) / log10(1 + num_bugs)
gen log10_ratio_tot = log10(1 + num_code_total_blueprint) / log10(1 + num_code_total_bug)
gen log10_ratio_added = log10(1 + num_code_added_blueprint) / log10(1 + num_code_added_bug)

gen byte touse2 = !missing(log10_ratio, log10_ratio_tot, log10_ratio_added)

foreach var of varlist log10_ratio log10_ratio_tot log10_ratio_added {
sum `var' if touse2 == 1
gen double z_`var' = (`var' - r(mean))/ r(sd) 
}

mi set mlong
mi register imputed z_log10_ratio 
mi impute regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall kshell_index z_degree if category == "networked" , add(200) rseed(1234)
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall z_degree if category == "networked"
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall z_kshell_index if category == "networked"
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall z_eigenvector_centrality  if category == "networked"
mi estimate : regress z_log10_ratio z_log10_revtime2 z_committer_tenure_overall z_degree z_kshell_index z_eigenvector_centrality  if category == "networked"
mi estimate : regress z_log10_ratio z_degree if category == "networked"
mi estimate : regress z_log10_ratio z_kshell_index if category == "networked"
mi estimate : regress z_log10_ratio z_eigenvector_centrality if category == "networked"


mi set mlong
mi register imputed z_log10_ratio_tot 
mi impute regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall z_kshell_index z_degree z_eigenvector_centrality if category == "networked" , add(200) rseed(1234)
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall z_degree if category == "networked"
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall z_kshell_index if category == "networked"
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall z_eigenvector_centrality if category == "networked"
mi estimate : regress z_log10_ratio_tot z_log10_revtime2 z_committer_tenure_overall z_degree z_kshell_index z_eigenvector_centrality if category == "networked"
mi estimate : regress z_log10_ratio_tot z_degree if category == "networked"
mi estimate : regress z_log10_ratio_tot z_kshell_index if category == "networked"
mi estimate : regress z_log10_ratio_tot z_eigenvector_centrality if category == "networked"

mi set mlong
mi register imputed z_log10_ratio_added 
mi impute regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall z_kshell_index z_degree z_eigenvector_centrality if category == "networked" , add(200) rseed(1234)
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall if category == "networked"
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall z_degree if category == "networked"
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall z_kshell_index if category == "networked"
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall z_eigenvector_centrality if category == "networked"
mi estimate : regress z_log10_ratio_added z_log10_revtime2 z_committer_tenure_overall z_degree z_eigenvector_centrality z_kshell_index if category == "networked"
mi estimate : regress z_log10_ratio_added z_degree if category == "networked"
mi estimate : regress z_log10_ratio_added z_kshell_index if category == "networked"
mi estimate : regress z_log10_ratio_added z_eigenvector_centrality if category == "networked"
