use "../../Data/Stata_files/Idea02_diversity_developers_bin2months.dta"

gen balance_ratio = log10(1+num_blueprints )/log10(1+num_bugs )
gen byte touse2 = !missing(balance_ratio )

foreach var of varlist balance_ratio  {
  sum `var' if touse2 == 1
  gen double z_`var' = (`var' - r(mean))/ r(sd) 
}

mi set mlong
mi register imputed z_balance_ratio 

encode indiv_comitter_firm_type , gen(indiv_comitter_firm_type_id)

mi impute regress z_balance_ratio z_herfindahl_index z_log10_revtime2 z_max_inter_commit_days if z_herfindahl_index ~=., add(200) rseed(1234)

mi estimate : regress z_balance_ratio z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.

mi estimate : regress z_balance_ratio z_herfindahl_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.

mi estimate : regress z_balance_ratio z_herfindahl_index c.z_herfindahl_index#c.z_herfindahl_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.


clear

use "../../Data/Stata_files/Idea02_diversity_developers_bin2months.dta"

gen balance_ratio = log10(1+num_blueprints )/log10(1+num_bugs )


gen byte touse2 = !missing(balance_ratio )

foreach var of varlist balance_ratio  {
   sum `var' if touse2 == 1
   gen double z_`var' = (`var' - r(mean))/ r(sd) 
}

mi set mlong

mi register imputed z_balance_ratio 

encode indiv_comitter_firm_type , gen(indiv_comitter_firm_type_id)

mi impute regress z_balance_ratio z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days if z_mean_insularity_index  ~=., add(200) rseed(1234)

mi estimate : regress z_balance_ratio z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_mean_insularity_index  ~=.

mi estimate : regress z_balance_ratio z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_mean_insularity_index  ~=.

mi estimate : regress z_balance_ratio z_mean_insularity_index c.z_mean_insularity_index#c.z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_mean_insularity_index  ~=.


clear

use "../../Data/Stata_files/Idea02_diversity_developers_bin2months.dta"

gen balance_ratio = log10(1+num_blueprints )/log10(1+num_bugs )


gen byte touse2 = !missing(balance_ratio )

foreach var of varlist balance_ratio  {
   sum `var' if touse2 == 1
   gen double z_`var' = (`var' - r(mean))/ r(sd) 
}

mi set mlong

mi register imputed z_balance_ratio 

encode indiv_comitter_firm_type , gen(indiv_comitter_firm_type_id)

mi impute regress z_balance_ratio z_herfindahl_index z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days if z_mean_insularity_index  ~=., add(200) rseed(1234)

mi estimate : regress z_balance_ratio z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_mean_insularity_index  ~=.

mi estimate : regress z_balance_ratio z_herfindahl_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.

mi estimate : regress z_balance_ratio z_herfindahl_index c.z_herfindahl_index#c.z_herfindahl_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.

mi estimate : regress z_balance_ratio z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_mean_insularity_index  ~=.

mi estimate : regress z_balance_ratio z_mean_insularity_index c.z_mean_insularity_index#c.z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_mean_insularity_index  ~=.

mi estimate : regress z_balance_ratio z_herfindahl_index c.z_herfindahl_index#c.z_herfindahl_index z_mean_insularity_index c.z_mean_insularity_index#c.z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.

mi estimate : regress z_balance_ratio z_herfindahl_index z_mean_insularity_index c.z_herfindahl_index#c.z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.

mi estimate : regress z_balance_ratio z_herfindahl_index z_mean_insularity_index z_log10_revtime2 z_max_inter_commit_days i.indiv_comitter_firm_type_id  i.binnumber_2months if z_herfindahl_index ~=.


