library(mediation)
library(latentnet)
library(sna)
library(statnet)
library("igraph")
library(network)
library(latticeExtra)
require(broom)
library(spdep)
library("robustbase")

f_output<-'p-values_controls_IVs_networks_from_raw_data_shuffle2_robustSE__2016.txt'

### RUN linear models on the null networks ###
setwd("/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/Github_for_RH/Data/03_spatio_temporal/Null_model_monte_carlo_example/")

files <- Sys.glob("sim__*.gml")

for (f in files) {
  print(f)
  graph_list<-read.graph(f,format=c("gml"))

###create the network
  el1 <-cbind(get.edgelist(graph_list))
  g<-graph.data.frame(el1, directed = FALSE)
  gmat<-get.adjacency(g,sparse = FALSE)
  network_unw<-network(gmat,directed=FALSE, vertex.attr=vertex.attributes(graph_list), edge.attr=edge.attributes(graph_list))
  class(network_unw)
### generate the IVs, DV and controls 
  spatial_x1 <-V(graph_list)$s_mean_spatial_inter
  temporal_x1<-V(graph_list)$s_wt_mu_inter_commit_time
  
  LCA <- V(graph_list)$lines_of_code_added_sum ## Dependent variable
  Tenure<- V(graph_list)$tenure_committer
  MI <- V(graph_list)$avg_MI_committer
  neighbors_lca <- V(graph_list)$neigh_lines_of_code_added_sum
  
  log10_code_add <-log10(1+LCA)
  log10_tenure <- log10(1+Tenure)
  
## Standardize the varibales 

  z_MI <-(MI - mean(MI)) / sd(MI)
  z_spatial_x1 <-(spatial_x1 - mean(spatial_x1)) / sd(spatial_x1)
  z_temporal_x1 <-(temporal_x1 - mean(temporal_x1)) / sd(temporal_x1)
  z_log10_code_add <-(log10_code_add - mean(log10_code_add)) / sd(log10_code_add)
  z_log10_tenure <-(log10_tenure - mean(log10_tenure)) / sd(log10_tenure)
  z_neighbors_lca <-(neighbors_lca - mean(neighbors_lca)) / sd(neighbors_lca)
  
## controls models
  model.0 <- lmrob(z_log10_code_add ~ z_log10_tenure + z_MI + z_neighbors_lca)
##controls + temporal
  model.T <- lmrob(z_log10_code_add ~ z_log10_tenure + z_MI + z_neighbors_lca + z_temporal_x1)
### controls + temporal + spatial
  model.S <- lmrob(z_log10_code_add ~ z_log10_tenure + z_MI + z_neighbors_lca + z_temporal_x1 + z_spatial_x1)  

## get the p-values of the coefficients
  coeff_pval.0 <-summary(model.0)$coefficients[,4]
  coeff_pval.T <-summary(model.T)$coefficients[,4]  
  coeff_pval.S <-summary(model.S)$coefficients[,4]
## nullify the variable names
  names(coeff_pval.0)<-NULL
  names(coeff_pval.T)<-NULL
  names(coeff_pval.S)<-NULL
### Float the numbers
  options(scipen = 999)

##print the coefficients
  #out<-cbind(f, coeff_pval.T[5], coeff_pval.S[5], coeff_pval.S[6], glance(model.T)$BIC, glance(model.S)$BIC)
  out<-cbind(f, coeff_pval.T[5], coeff_pval.S[5], coeff_pval.S[6]) ## For Robust SE
  #write.csv(out, f_output)
  write.table(out, paste("/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/Github_for_RH/Data/03_spatio_temporal/Null_model_monte_carlo_example/", f_output, sep=""), row.names=FALSE, col.names=FALSE,append = TRUE)
}
