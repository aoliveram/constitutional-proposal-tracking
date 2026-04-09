# setup environment
if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "http://cran.us.r-project.org")
if (!requireNamespace("statnet", quietly = TRUE)) install.packages("statnet", repos = "http://cran.us.r-project.org")
if (!requireNamespace("btergm", quietly = TRUE)) install.packages("btergm", repos = "http://cran.us.r-project.org")

library(jsonlite)
library(statnet)
library(btergm)

base_dir <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"

# 1. Load Nodes data
profiles <- fromJSON(file.path(base_dir, "conventionals-bcn-webscrapping/conventional-profiles.json"))

# 2. Load C1 Networks data
waves_data <- fromJSON(file.path(base_dir, "playground/research-proposal-implementation/C1_dynamic_networks.json"))

# Create base node set based on the network authors.
all_nodes <- unique(unlist(lapply(waves_data, function(w) c(w$source, w$target))))
node_names <- sort(all_nodes)
n_nodes <- length(node_names)

# Function to safely extract node attributes
get_attr <- function(name, attr_col, default_val) {
  # Match name to conventional-profiles using some fuzzy or exact match.
  # First try exact match
  idx <- match(name, profiles$nombre_armonizado)
  if(!is.na(idx) && !is.na(profiles[[attr_col]][idx])) {
    return(profiles[[attr_col]][idx])
  }
  return(default_val)
}

# 3. Create a list of network objects for each wave
net_list <- list()

for (wf_name in names(waves_data)) {
  wave <- waves_data[[wf_name]]
  
  # Initialize empty network
  net <- network.initialize(n_nodes, directed = FALSE)
  network.vertex.names(net) <- node_names
  
  # Set node attributes
  # 1. afiliacion_agrupada
  afiliaciones <- sapply(node_names, function(n) get_attr(n, "afiliacion_agrupada", "Desconocida"))
  set.vertex.attribute(net, "afiliacion_agrupada", afiliaciones)
  
  # 2. es_abogado
  es_abogado <- sapply(node_names, function(n) get_attr(n, "es_abogado", 0))
  set.vertex.attribute(net, "es_abogado", es_abogado)
  
  # 3. edad_al_asumir
  edades <- sapply(node_names, function(n) get_attr(n, "edad_al_asumir", 45)) # default to mean roughly if missing
  set.vertex.attribute(net, "edad_al_asumir", edades)
  
  # 4. experiencia_previa_institucional
  exp_previa <- sapply(node_names, function(n) get_attr(n, "experiencia_previa_institucional", 0))
  set.vertex.attribute(net, "experiencia_previa_institucional", exp_previa)
  
  # 5. es_mujer
  es_mujer <- sapply(node_names, function(n) get_attr(n, "es_mujer", 0))
  set.vertex.attribute(net, "es_mujer", es_mujer)
  
  # Add edges
  if (nrow(wave) > 0) {
    # statnet wants edge list as vertex indices or names. 
    # With network, we can add edges using vertex names.
    edges_df <- data.frame(
      tail = wave$source,
      head = wave$target
    )
    add.edges(net, tail=match(edges_df$tail, node_names), head=match(edges_df$head, node_names))
    # Note: edges only added if weight > 0, we assume all listed edges in JSON exist.
    # Currently weights are not used in binary ERGM but can be tracked
  }
  
  net_list[[wf_name]] <- net
}

cat("Networks created:", length(net_list), "\n")
cat("Nodes in network:", n_nodes, "\n")

# 4. TERGM Estimation
# We use btergm (Bootstrapped TERGM) which is great for multiple network panels
cat("Fitting Initial TERGM Model...\n")

model_formula <- net_list ~ edges + 
  gwesp(0.5, fixed=TRUE) + 
  nodematch("afiliacion_agrupada") + 
  nodematch("experiencia_previa_institucional") + 
  nodematch("es_abogado") + 
  absdiff("edad_al_asumir")

# We will fit a simple cross-sectional ERGM on the final wave first to check for degeneracy
cat("Checking single wave ERGM (T-final) to test specification...\n")
fit_ergm <- ergm(net_list[[length(net_list)]] ~ edges + gwesp(0.5, fixed=TRUE) + nodematch("afiliacion_agrupada") + nodematch("es_abogado"),
                 control = control.ergm(MCMC.samplesize = 500, MCMC.interval = 100))

summary(fit_ergm)

# Since btergm takes time, we save the workspace objects so user can run it interactively
save(net_list, waves_data, profiles, file=file.path(base_dir, "playground/research-proposal-implementation/tergm_environment.RData"))
cat("Networks and environment saved to tergm_environment.RData.\n")
cat("You can load this RData and run the full btergm(model_formula) at your convenience.\n")
