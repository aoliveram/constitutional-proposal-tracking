# =============================================================================
# 01-model-valued-ergm.R
# Model 1: Co-Sponsorship Network Formation (Valued ERGM)
#
# Runs a Valued ERGM (Poisson reference) on the POOLED cumulative co-authorship
# network across all 5 commissions (C1, C3, C5, C6, C7).
# Extracts structural metrics (degree, betweenness, eigenvector centrality).
# =============================================================================

if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite", repos = "http://cran.us.r-project.org")
if (!requireNamespace("statnet", quietly = TRUE)) install.packages("statnet", repos = "http://cran.us.r-project.org")

library(jsonlite)
library(statnet)

set.seed(42)

base_dir <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking"
data_dir <- file.path(base_dir, "playground/research-proposal-implementation/data")

# =============================================================================
# 1. Load pooled network and profiles
# =============================================================================

cat("--- Loading pooled cumulative network ---\n")
edges_df <- read.csv(file.path(data_dir, "pooled_cumulative_network.csv"),
                     stringsAsFactors = FALSE)
cat(sprintf("  Edges: %d, Total weight: %d\n", nrow(edges_df), sum(edges_df$weight)))

profiles <- fromJSON(file.path(base_dir, "conventionals-bcn-webscrapping/conventional-profiles.json"))
cat(sprintf("  Profiles loaded: %d\n", nrow(profiles)))

# =============================================================================
# 2. Build the valued network
# =============================================================================

# Get all unique nodes from the edge list
all_nodes <- sort(unique(c(edges_df$source, edges_df$target)))
n_nodes <- length(all_nodes)
cat(sprintf("  Unique nodes in network: %d\n", n_nodes))

# Helper to get profile attributes
get_attr <- function(name, attr_col, default_val) {
  idx <- match(name, profiles$nombre_armonizado)
  if (!is.na(idx) && !is.na(profiles[[attr_col]][idx])) {
    return(profiles[[attr_col]][idx])
  }
  return(default_val)
}

# Initialize undirected valued network
net <- network.initialize(n_nodes, directed = FALSE)
network.vertex.names(net) <- all_nodes

# Set vertex attributes from profiles
set.vertex.attribute(net, "afiliacion_agrupada",
                     sapply(all_nodes, function(n) get_attr(n, "afiliacion_agrupada", "Desconocida")))
set.vertex.attribute(net, "es_abogado",
                     sapply(all_nodes, function(n) get_attr(n, "es_abogado", 0)))
set.vertex.attribute(net, "es_mujer",
                     sapply(all_nodes, function(n) get_attr(n, "es_mujer", 0)))
set.vertex.attribute(net, "edad_al_asumir",
                     sapply(all_nodes, function(n) get_attr(n, "edad_al_asumir", 45)))
set.vertex.attribute(net, "experiencia_previa_institucional",
                     sapply(all_nodes, function(n) get_attr(n, "experiencia_previa_institucional", 0)))

# Add edges with weights
tail_ids <- match(edges_df$source, all_nodes)
head_ids <- match(edges_df$target, all_nodes)
add.edges(net, tail = tail_ids, head = head_ids)
set.edge.attribute(net, "weight", edges_df$weight)

cat(sprintf("  Network: %d nodes, %d edges\n", network.size(net), network.edgecount(net)))

# Check profile matching rate
n_matched <- sum(all_nodes %in% profiles$nombre_armonizado)
cat(sprintf("  Profile match: %d/%d nodes (%.1f%%)\n",
            n_matched, n_nodes, 100 * n_matched / n_nodes))

# =============================================================================
# 3. Fit Valued ERGM (Poisson reference)
# =============================================================================

cat("\n--- Fitting Valued ERGM on Pooled Network ---\n")
cat("  Terms: sum + nodematch(afiliacion_agrupada) + nodematch(experiencia_previa)\n")
cat("         + nodematch(es_abogado) + nodematch(es_mujer) + absdiff(edad)\n")
cat("         + nodecov(edad_al_asumir)\n")
cat("  Reference: Poisson\n\n")

fit_valued <- ergm(net ~ sum +
                     nodematch("afiliacion_agrupada") +
                     nodematch("experiencia_previa_institucional") +
                     nodematch("es_abogado") +
                     nodematch("es_mujer") +
                     absdiff("edad_al_asumir") +
                     nodecov("edad_al_asumir"),
                   response = "weight",
                   reference = ~Poisson,
                   control = control.ergm(seed = 42))

cat("\n--- MODEL SUMMARY ---\n")
print(summary(fit_valued))

# Save model object
saveRDS(fit_valued, file.path(data_dir, "ergm_pooled_results.rds"))
cat(sprintf("\nModel saved to: %s\n", file.path(data_dir, "ergm_pooled_results.rds")))

# =============================================================================
# 4. Extract structural metrics
# =============================================================================

cat("\n--- Extracting Structural Metrics ---\n")

# Compute centrality metrics on the weighted network
deg <- degree(net, gmode = "graph")
w_deg <- sapply(1:n_nodes, function(i) {
  eids <- get.edgeIDs(net, i)
  if (length(eids) == 0) return(0)
  sum(get.edge.attribute(net, "weight")[eids])
})
bet <- betweenness(net, gmode = "graph")

# Eigenvector centrality via sna
eig <- evcent(net, gmode = "graph")

# Build metrics data frame
metrics_df <- data.frame(
  nombre_armonizado = all_nodes,
  degree = deg,
  weighted_degree = w_deg,
  betweenness = bet,
  eigenvector = eig,
  stringsAsFactors = FALSE
)

# Add profile covariates for reference
metrics_df$afiliacion_agrupada <- sapply(all_nodes, function(n) get_attr(n, "afiliacion_agrupada", "Desconocida"))
metrics_df$es_abogado <- sapply(all_nodes, function(n) get_attr(n, "es_abogado", 0))
metrics_df$es_mujer <- sapply(all_nodes, function(n) get_attr(n, "es_mujer", 0))
metrics_df$edad_al_asumir <- sapply(all_nodes, function(n) get_attr(n, "edad_al_asumir", NA))
metrics_df$experiencia_previa_institucional <- sapply(all_nodes, function(n) get_attr(n, "experiencia_previa_institucional", 0))

# Save
metrics_path <- file.path(data_dir, "network_metrics.csv")
write.csv(metrics_df, metrics_path, row.names = FALSE)
cat(sprintf("Network metrics saved: %s (%d convencionales)\n", metrics_path, nrow(metrics_df)))

# Print top 10 by weighted degree
cat("\n--- Top 10 by Weighted Degree ---\n")
top10 <- metrics_df[order(-metrics_df$weighted_degree), ][1:10, c("nombre_armonizado", "degree", "weighted_degree", "betweenness", "eigenvector")]
print(top10, row.names = FALSE)

# Print top 10 by betweenness
cat("\n--- Top 10 by Betweenness ---\n")
top10b <- metrics_df[order(-metrics_df$betweenness), ][1:10, c("nombre_armonizado", "degree", "weighted_degree", "betweenness")]
print(top10b, row.names = FALSE)

cat("\n--- Done ---\n")
