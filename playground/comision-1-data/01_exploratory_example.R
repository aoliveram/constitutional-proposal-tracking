# --- PROJECT: CONSTITUTIONAL PROPOSAL TRACKING ---
# Exploratory Analysis and Case Study for Commission 1 (Political System)

rm(list=ls())

# 1. Setup Data Path
aqui <- "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking/playground/comision-1-data"
data_path <- file.path(aqui, "data", "C1_texto-sistematizado_enriched_manual.json")

library(jsonlite)
library(dplyr)
library(ggplot2)
library(purrr)

print(paste("Loading data from:", data_path))

# 2. Read and Transform JSON Data
raw_data <- fromJSON(data_path)
df_final <- as_tibble(raw_data)

# Extract only valid articles (ignoring structural titles)
articles_df <- df_final %>% filter(!is.na(article_uid))

# ==========================================
# PART A: GENERAL EXPLORATORY ANALYSIS
# ==========================================
print("==== OVERALL STATISTICS ====")
total_articles <- nrow(articles_df)
print(paste("Total valid articles in final draft:", total_articles))

# Count the number of modifications per article
# In the nested JSON structure, the 'history' column contains a dataframe of indications
articles_df <- articles_df %>%
  mutate(mod_count = map_int(history, ~if (is.null(.x) || length(.x) == 0) 0 else nrow(as.data.frame(.x))))

total_mods <- sum(articles_df$mod_count)
print(paste("Total number of modifications (indications) tracked:", total_mods))

# Plot: Histogram of modifications per article
# To view this plot in RStudio, simply run this block or the full script
histogram_plot <- ggplot(articles_df, aes(x = mod_count)) +
  geom_histogram(binwidth = 1, fill = "steelblue", color = "white") +
  theme_minimal() +
  labs(title = "Distribution of Modifications per Article (Commission 1)",
       x = "Number of Modifications (Indications)",
       y = "Frequency of Articles")

print(histogram_plot)

# ==========================================
# PART B: SINGLE ARTICLE CASE STUDY
# ==========================================
# Let's track the evolution of "Artículo 1" (UID: C1-GEN-CH01-ART01)
target_uid <- "C1-GEN-CH01-ART01"
case_study_data <- articles_df %>% filter(article_uid == target_uid)

if (nrow(case_study_data) == 0) {
  stop("Article not found!")
}

print("\n==== CASE STUDY: ARTICLE EVOLUTION ====")
print(paste("Article ID:", case_study_data$article))
print(paste("Genesis Text:", substr(case_study_data$text, 1, 150), "..."))
print(paste("Original Authors Count:", length(case_study_data$authors[[1]])))
print(paste("Final Status in the Draft:", case_study_data$final_status))

print("\n-- Legislative History (Indications) --")
history_df <- case_study_data$history[[1]]

if (!is.null(history_df) && nrow(as.data.frame(history_df)) > 0) {
  history_df <- as.data.frame(history_df)
  print(paste("Total Modification Events for this article:", nrow(history_df)))
  
  # Summary of what actions were taken (e.g., ADD, DELETE, SUBSTITUTE, WORDING)
  action_summary <- history_df %>% 
    group_by(action) %>% 
    summarise(count = n(), .groups = "drop")
  
  print("Actions Summary:")
  print(action_summary)
  
  # Deep dive into the very first modification
  cat("\n-> Snapshot: The very first applied modification\n")
  first_mod <- history_df[1, ]
  cat("Timestamp:", first_mod$timestamp, "\n")
  cat("Action Type:", first_mod$action, "\n")
  if (!is.na(first_mod$content) && nchar(first_mod$content) > 0) {
    cat("Content added/modified:", first_mod$content, "\n")
  }
  if (!is.na(first_mod$content_to_remove) && nchar(first_mod$content_to_remove) > 0) {
    cat("Content removed:", first_mod$content_to_remove, "\n")
  }
  
  # Authors of the indication
  authors_list <- first_mod$authors[[1]]
  if(is.list(authors_list) || is.vector(authors_list)) {
    cat("Number of co-authors pushing this indication:", length(authors_list), "\n")
  }

}
