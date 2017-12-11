library(ergm.count)
library(latentnet)
library(ergm)
library(sna)
library(statnet)
library("igraph")
library(network)
library(latticeExtra)

rm(list=ls())

#### Next we include the node attributes in the model ####
### Node attributes could be lines of code added, revision time, tenure of a committer ###

setwd("/Users/mukher27/Dropbox (Uzzi Lab)/RH fellow project/Github_for_RH/Data/03_spatio_temporal/ERGM_cumulative_networks/")

args<-commandArgs(trailingOnly = TRUE)
my.year <- as.numeric(args[1])
my.year

i<-my.year

f<-paste('nova_spatial_temporal_network_cumulative_2012_',c(i),'.gml',sep="")
print(f)
graph_list<-read.graph(f,format=c("gml"))
summary(graph_list)

##unweighted network
el1 <-cbind(get.edgelist(graph_list))
g<-graph.data.frame(el1, directed = FALSE)
gmat<-get.adjacency(g,sparse = FALSE)
network_unw<-network(gmat,directed=FALSE, vertex.attr=vertex.attributes(graph_list), edge.attr=edge.attributes(graph_list))
class(network_unw)
network_unw

### ERGM default IV ###
#### model with edges, 2-star, 3-star, triangles

model.01 <- ergm(network_unw ~ kstar(1))
summary(model.01)
mcmc.diagnostics(model.01)
gof.1<-gof(model.01)
summary(gof.1)
plot(gof.1)


### get the node attributes ####
## network parameters 


model.02b <- ergm(network_unw ~ nodecov('s_diff_90_10_temporal'))
summary(model.02b)
tryCatch({
  mcmc.diagnostics(model.02b)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.02b<-gof(model.02b)
summary(gof.02b)
plot(gof.02b)


model.02e <- ergm(network_unw ~ nodecov('s_wt_mu_inter_commit_time'))
summary(model.02e)
tryCatch({
  mcmc.diagnostics(model.02e)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.02e<-gof(model.02e)
summary(gof.02e)
plot(gof.02e)


model.02f <- ergm(network_unw ~ nodecov('s_mean_spatial_inter'))
summary(model.02f)
tryCatch({
  mcmc.diagnostics(model.02f)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.02f<-gof(model.02f)
summary(gof.02f)
plot(gof.02f)


model.02g <- ergm(network_unw ~ nodecov('s_diff_90_10_spatial'))
summary(model.02g)
tryCatch({
  mcmc.diagnostics(model.02g)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.02g<-gof(model.02g)
summary(gof.02g)
plot(gof.02g)



model.02spt1<-ergm(network_unw ~ nodecov('s_mean_spatial_inter') + nodecov('s_wt_mu_inter_commit_time') )
summary(model.02spt1)
tryCatch({
  mcmc.diagnostics(model.02spt1)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.02spt1<-gof(model.02spt1)
summary(gof.02spt1)
plot(gof.02spt1)


model.02spt2<-ergm(network_unw ~ nodecov('s_diff_90_10_spatial') + nodecov('s_diff_90_10_temporal') )
summary(model.02spt2)
tryCatch({
  mcmc.diagnostics(model.02spt2)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.02spt2<-gof(model.02spt2)
summary(gof.02spt2)
plot(gof.02spt2)



model02d<-ergm(network_unw ~ kstar(1) + nodecov('s_diff_90_10_spatial') + nodecov('s_diff_90_10_temporal') )
summary(model02d)
tryCatch({
  mcmc.diagnostics(model02d)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof02d<-gof(model02d)
summary(gof02d)
plot(gof02d)


model02e<-ergm(network_unw ~ kstar(1) + nodecov('s_mean_spatial_inter') + nodecov('s_wt_mu_inter_commit_time') )
summary(model02e)
tryCatch({
  mcmc.diagnostics(model02e)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof02e<-gof(model02e)
summary(gof02e)
plot(gof02e)


### non network (controls)

model.03a <- ergm(network_unw ~  nodecov('tenure_committer') + nodecov('total_num_committs') + nodecov('avg_MI_committer') )
summary(model.03a)
tryCatch({
  mcmc.diagnostics(model.03a)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.03a<-gof(model.03a)
summary(gof.03a)
plot(gof.03a)


model.03e <- ergm(network_unw ~ nodecov('s_wt_mu_inter_commit_time') + nodecov('tenure_committer') + nodecov('total_num_committs') + nodecov('avg_MI_committer') )
summary(model.03e)
tryCatch({
  mcmc.diagnostics(model.03e)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.03e<-gof(model.03e)
summary(gof.03e)
plot(gof.03e)


model.03f <- ergm(network_unw ~ nodecov('s_diff_90_10_temporal') + nodecov('tenure_committer') + nodecov('total_num_committs') + nodecov('avg_MI_committer') )
summary(model.03f)
tryCatch({
  mcmc.diagnostics(model.03f)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.03f<-gof(model.03f)
summary(gof.03f)
plot(gof.03f)


model.03g <- ergm(network_unw ~ nodecov('s_diff_90_10_spatial') +  nodecov('tenure_committer') + nodecov('total_num_committs') + nodecov('avg_MI_committer') )
summary(model.03g)
tryCatch({
  mcmc.diagnostics(model.03g)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.03g<-gof(model.03g)
summary(gof.03g)
plot(gof.03g)


model.03h <- ergm(network_unw ~ nodecov('s_mean_spatial_inter') +  nodecov('tenure_committer') + nodecov('total_num_committs') + nodecov('avg_MI_committer') )
summary(model.03h)
tryCatch({
  mcmc.diagnostics(model.03h)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.03h<-gof(model.03h)
summary(gof.03h)
plot(gof.03h)

## All model
### All models together 1. spatial weight and controls 2. temporal weights and controls

model.04c <- ergm(network_unw ~  kstar(1) + nodecov('s_diff_90_10_spatial') + nodecov('s_diff_90_10_temporal') + nodecov('tenure_committer') + nodecov('total_num_committs') + nodecov('avg_MI_committer') )
summary(model.04c)
tryCatch({
  mcmc.diagnostics(model.04c)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.04c<-gof(model.04c)
summary(gof.04c)
plot(gof.04c)



model.04d <- ergm(network_unw ~  kstar(1) + nodecov('s_mean_spatial_inter') + nodecov('s_wt_mu_inter_commit_time') + nodecov('tenure_committer') + nodecov('total_num_committs') + nodecov('avg_MI_committer') )
summary(model.04d)
tryCatch({
  mcmc.diagnostics(model.04d)
}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
gof.04d<-gof(model.04d)
summary(gof.04d)
plot(gof.04d)

