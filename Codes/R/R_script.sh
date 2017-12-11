#! /bin/bash

i=2012

while [ $i -le 2016 ]
do
	echo $i

###	Rscript  03_ERGM_cumulative_spatio-temporal_networks.R.R $i

###	Rscript  03_spatio-temporal_networks_descriptives.R $i

###	Rscript  03_mediation_monte_carlo_method.R $i

	i=`expr $i + 1`
done

