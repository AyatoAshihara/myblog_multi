## Ensure a writable user library is first in .libPaths()
user_lib <- Sys.getenv("R_LIBS_USER")
if (user_lib == "" || is.na(user_lib)) {
  user_lib <- file.path(Sys.getenv("USERPROFILE"), "R", paste0("win-library/", paste(R.version$major, R.version$minor, sep=".")))
}
if (!dir.exists(user_lib)) dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(user_lib, .libPaths()))

if (!requireNamespace("blogdown", quietly = TRUE)) {
  install.packages("blogdown", repos = "https://cran.r-project.org")
}
if (!requireNamespace("blogdown")) stop("blogdown install failed")
if (!blogdown::hugo_available()) {
  blogdown::install_hugo()
}
blogdown::serve_site(dir = '.')
