# Runs the cases of cases.json with rallicagram and stores what happens.
# Usage: Rscript run_r.R <path to rallicagram> <cases.json> <output.json>
args <- commandArgs(trailingOnly = TRUE)
pkgload::load_all(args[1], quiet = TRUE)
cases <- jsonlite::fromJSON(args[2], simplifyVector = TRUE, simplifyDataFrame = FALSE)

urls <- character()
ns <- asNamespace("rallicagram")
original_read <- get("read_data_gallicagram", ns)
wrapped <- function(url) {
  urls <<- c(urls, url)
  original_read(url)
}
unlockBinding("read_data_gallicagram", ns)
assign("read_data_gallicagram", wrapped, ns)

run <- function(case) {
  urls <<- character()
  warns <- character()
  error <- NULL
  value <- withCallingHandlers(
    tryCatch(
      do.call(case$fn, case$args, envir = ns),
      error = function(e) {
        error <<- conditionMessage(e)
        NULL
      }
    ),
    warning = function(w) {
      warns <<- c(warns, conditionMessage(w))
      invokeRestart("muffleWarning")
    }
  )
  columns <- NULL
  if (is.data.frame(value)) {
    value <- as.data.frame(value)
    columns <- names(value)
    value[] <- lapply(value, function(x) if (inherits(x, "Date")) as.character(x) else x)
  }
  list(urls = urls, warnings = unique(warns), error = error,
       columns = columns, value = value)
}

results <- lapply(cases, run)
writeLines(
  jsonlite::toJSON(results, dataframe = "columns", digits = NA, na = "null",
                   null = "null", auto_unbox = FALSE),
  args[3], useBytes = TRUE
)
