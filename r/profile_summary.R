# Day 1: Basic data profiling in R.
# Run from the repository root:
# Rscript r/profile_summary.R data/sample_customers.csv

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("Usage: Rscript r/profile_summary.R <csv-path>")
}

input_path <- args[[1]]

if (!file.exists(input_path)) {
  stop(paste("Input file not found:", input_path))
}

data <- read.csv(
  input_path,
  stringsAsFactors = FALSE,
  na.strings = c("", "NA")
)

cat("DATASET SUMMARY\n")
cat("Rows:", nrow(data), "\n")
cat("Columns:", ncol(data), "\n\n")

cat("COLUMN TYPES\n")
print(sapply(data, function(column) class(column)[1]))

cat("\nMISSING VALUES BY COLUMN\n")
print(colSums(is.na(data)))

cat("\nDUPLICATE ROWS\n")
cat(sum(duplicated(data)), "\n")

numeric_columns <- vapply(data, is.numeric, logical(1))

if (any(numeric_columns)) {
  cat("\nNUMERIC SUMMARY\n")
  print(summary(data[, numeric_columns, drop = FALSE]))
}
