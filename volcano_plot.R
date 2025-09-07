# Volcano Plot in R
# Load required libraries
library(ggplot2)
library(dplyr)

# Create sample differential expression data (if you don't have your own)
set.seed(123)
n_genes <- 1000
sample_data <- data.frame(
  gene_name = paste0("Gene_", 1:n_genes),
  log2FoldChange = rnorm(n_genes, 0, 2),
  pvalue = runif(n_genes, 0, 1)
)

# If you have your own data, uncomment and modify this line:
# data <- read.csv("your_data.csv")
data <- sample_data

# Create significance categories
data$significance <- "Not Significant"
data$significance[data$pvalue < 0.05 & data$log2FoldChange > 1] <- "Up-regulated"
data$significance[data$pvalue < 0.05 & data$log2FoldChange < -1] <- "Down-regulated"

# Create -log10 p-value for y-axis
data$neg_log10_pvalue <- -log10(data$pvalue)

# Create volcano plot
volcano_plot <- ggplot(data, aes(x = log2FoldChange, y = neg_log10_pvalue, color = significance)) +
  geom_point(alpha = 0.6, size = 1.5) +
  scale_color_manual(values = c("Down-regulated" = "blue", 
                               "Not Significant" = "grey", 
                               "Up-regulated" = "red")) +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed", alpha = 0.5) +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed", alpha = 0.5) +
  labs(title = "Volcano Plot", 
       x = "Log2 Fold Change", 
       y = "-Log10 P-value",
       color = "Regulation") +
  theme_minimal() +
  theme(legend.position = "bottom")

# Save the plot
ggsave("volcano_plot.png", volcano_plot, width = 10, height = 8, dpi = 300)

# Display the plot
print(volcano_plot)

# Print summary statistics
cat("Summary of differential expression:\n")
print(table(data$significance))