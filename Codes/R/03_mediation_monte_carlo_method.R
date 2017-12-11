library("igraph")
library(psych)
library(picante)

### This part is for the descriptives of ERGM results ###
rm(list=ls())

### Read the Cumulative networks of spatial-temporal weights
### Network in 2013 is with commits from 2012 and 2013
setwd("/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/Github_for_RH/Data/03_spatio_temporal/ERGM_cumulative_networks/")

args<-commandArgs(trailingOnly = TRUE)
my.year <- as.numeric(args[1])
my.year

i<-my.year

f<-paste('nova_spatial_temporal_network_cumulative_2012_',c(i),'.gml',sep="")
print(f)
graph_list<-read.graph(f,format=c("gml"))
summary(graph_list)

#### Descriptive statistics ##
temporal1<-V(graph_list)$s_wt_mu_inter_commit_time
describe(temporal1)[2:4]

spatial1<-V(graph_list)$s_mean_spatial_inter
describe(spatial1)[2:4]

temporal2<-V(graph_list)$s_diff_90_10_temporal
describe(temporal2)[2:4]

spatial2<-V(graph_list)$s_diff_90_10_spatial
describe(spatial2)[2:4]

LCA <- V(graph_list)$lines_of_code_added_sum
describe(LCA)[2:4]

Tenure<- V(graph_list)$tenure_committer
describe(Tenure)[2:4]

Commits <- V(graph_list)$total_num_committs
describe(Commits)[2:4]

MI <- V(graph_list)$avg_MI_committer
describe(MI)[2:4]

## pairwise correlation
el1<-cbind(temporal1, spatial1, LCA, Tenure, Commits, MI)
cor.table(el1, cor.method="pearson")

el2<-cbind(temporal2, spatial2, LCA, Tenure, Commits, MI)
cor.table(el2, cor.method="pearson")

el3<-cbind(temporal1, spatial1, temporal2, spatial2, LCA, Tenure, Commits, MI)
cor.table(el3, cor.method="pearson")

el4<-cbind(temporal1, spatial1, temporal2, spatial2, Tenure, Commits, MI)
cor.table(el4, cor.method="pearson")

el5<-cbind(temporal1, spatial1, Tenure, Commits, MI)
cor.table(el5, cor.method="pearson")

el6<-cbind(temporal2, spatial2, Tenure, Commits, MI)
cor.table(el6, cor.method="pearson")


### This part is for the descriptives of mediation results ###

f_output<-'descriptives_spatio-temporal_per_years_mediation_results.txt'

setwd("/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/Github_for_RH/Data/03_spatio_temporal/networks_per_year_mediation/")

files <- Sys.glob("nova_committer_spatial_temporal_network_weights_*.gml")

for (f in files) {
  print(f)
  
  graph_list<-read.graph(f,format=c("gml"))
  
  ### generate the IVs, DV and controls 
  
  spatial_x1 <-V(graph_list)$s_mean_spatial_inter
  temporal_x1<-V(graph_list)$s_wt_mu_inter_commit_time
  
  LCA <- V(graph_list)$lines_of_code_added_sum ## Dependent variable
  Tenure<- V(graph_list)$tenure_committer
  MI <- V(graph_list)$avg_MI_committer
  neighbors<-V(graph_list)$neigh_lines_of_code_added_avg
  
  log10_code_add <-log10(1+LCA)
  log10_tenure <- log10(1+Tenure)
  
  e_spatial_x1 <-E(graph_list)$mean_spatial_inter
  e_temporal_x1<-E(graph_list)$wt_mu_inter_commit_time
  
  
  lcadesc<-describe(log10_code_add)[2:4]
  tenuredesc<-describe(log10_tenure)[2:4]
  MIdesc<-describe(MI)[2:4]
  neighbordesc<-describe(neighbors)[2:4]
  temporaldesc<-describe(temporal_x1)[2:4]
  spatialdesc<-describe(spatial_x1)[2:4]
  etemporaldesc<-describe(e_temporal_x1)[2:4]
  espatialdesc<-describe(e_spatial_x1)[2:4]
  
  ##print the descriptives
  out<-cbind(f, lcadesc$mean, lcadesc$sd, tenuredesc$mean, tenuredesc$sd, MIdesc$mean, MIdesc$sd, neighbordesc$mean, neighbordesc$sd, temporaldesc$mean, temporaldesc$sd, spatialdesc$mean, spatialdesc$sd, etemporaldesc$mean, etemporaldesc$sd, espatialdesc$mean, espatialdesc$sd)
  write.table(out, paste("/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/04_Network_Ideas/Idea03_06/Data/", f_output, sep=""), row.names=FALSE, col.names=FALSE,append = TRUE)
  
}

