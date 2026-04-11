# setup environment
if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "http://cran.us.r-project.org")
if (!requireNamespace("statnet", quietly = TRUE)) install.packages("statnet", repos = "http://cran.us.r-project.org")

library(jsonlite)
library(statnet)

set.seed(42)

base_dir <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"

# 1. Load Data
profiles <- fromJSON(file.path(base_dir, "conventionals-bcn-webscrapping/conventional-profiles.json"))
waves_data <- fromJSON(file.path(base_dir, "playground/research-proposal-implementation/network-visualization/C1_dynamic_networks.json"))

all_nodes <- unique(unlist(lapply(waves_data, function(w) c(w$source, w$target))))
node_names <- sort(all_nodes)
n_nodes <- length(node_names)

get_attr <- function(name, attr_col, default_val) {
  idx <- match(name, profiles$nombre_armonizado)
  if(!is.na(idx) && !is.na(profiles[[attr_col]][idx])) return(profiles[[attr_col]][idx])
  return(default_val)
}

wave <- waves_data[[1]] # Genesis

# 2. Build Valued Network (Statnet format)
net <- network.initialize(n_nodes, directed = FALSE)
network.vertex.names(net) <- node_names

set.vertex.attribute(net, "afiliacion_agrupada", sapply(node_names, function(n) get_attr(n, "afiliacion_agrupada", "Desconocida")))
set.vertex.attribute(net, "es_abogado", sapply(node_names, function(n) get_attr(n, "es_abogado", 0)))
set.vertex.attribute(net, "edad_al_asumir", sapply(node_names, function(n) get_attr(n, "edad_al_asumir", 45)))
set.vertex.attribute(net, "experiencia_previa_institucional", sapply(node_names, function(n) get_attr(n, "experiencia_previa_institucional", 0)))

if (nrow(wave) > 0) {
  # Add edges
  add.edges(net, tail=match(wave$source, node_names), head=match(wave$target, node_names))
  # Set edge weights
  set.edge.attribute(net, "weight", wave$weight)
}

cat("--- Fitting Valued ERGM for Comisión 1 (GENESIS) ---\n")

# Model specification (No structural terms like gwesp to prevent explosion, just exogenous covariates for the count baseline)
# Poisson reference distribution. 'sum' acts as the baseline intercept (log expected count).
fit_valued <- ergm(net ~ sum + 
                     nodematch("afiliacion_agrupada") + 
                     nodematch("experiencia_previa_institucional") +
                     nodematch("es_abogado") +
                     absdiff("edad_al_asumir"),
                   response = "weight",
                   reference = ~Poisson,
                   control = control.ergm(seed = 42))

summary(fit_valued)
