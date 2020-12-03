#!/usr/bin/env Rscript
# 
# Plot of population size, smartphone usage, app uptake
# Usage: Rscript histogram_app_uptake.R app_uptake
# 
# where `app_uptake` is the proportion of the smartphone-using population that has 
# the app (uniform across age groups)

library(ggplot2)
library(RColorBrewer)
library(reshape2)

# Read input parameters
args <- commandArgs(trailingOnly = TRUE)
app_uptake <- as.numeric(args[1])
input_parameter_file <- args[2]
output_file <- args[3]
file_format <- args[4]

# Read data
df <- read.csv(file.path(input_parameter_file), stringsAsFactors = F)

# Pull out parameters of interest
params <- with(df, Name)
cols2keep <- params[grepl("population", params) | grepl("app_users_fraction", params)]

# Create new variables
df_sub <- subset(df, Name %in% cols2keep)
df_sub$age <- gsub("population_|app_users_fraction_", "", df_sub$Name)
df_sub$measure <- ifelse(grepl("population", df_sub$Name), "population", "app_users_fraction")
df_sub <- dcast(df_sub, age ~ measure, value.var = "Value")

# Find size of population of phone and app users
df_sub$smartphones <- with(df_sub, population * app_users_fraction )
df_sub$uptake <- with(df_sub, smartphones * app_uptake )

# Wide to long format
df_long <- melt(df_sub[c("age", "population", "smartphones", "uptake")], id.vars = c("age"))

# Generate and save plot
p <- ggplot(df_long, aes(x = age, y = value/1E6, fill = variable)) + 
    geom_bar(stat = "identity", position = "identity") + 
    theme_classic(base_size = 18) + 
    xlab("Ages") + 
    ylab("Number of people (millions)") + 
    scale_fill_manual(values = brewer.pal(3, "Dark2")[c(2, 1, 3)],
        name = "",
        breaks = c("population", "smartphones", "uptake"),
        labels = c("Total population", "with smartphones", 
            paste0("with app (", app_uptake*100, "% uptake)")))

ggsave(filename = file.path(paste0(output_file, ".", file_format)), plot = p, 
    width = 12, height = 6)
