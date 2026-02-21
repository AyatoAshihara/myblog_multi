if (!requireNamespace("blogdown", quietly=TRUE)) {
  install.packages("blogdown", repos="https://cran.r-project.org")
}
if (!requireNamespace("blogdown", quietly=TRUE)) stop('blogdown install failed')
if (!blogdown::hugo_available()) blogdown::install_hugo()
blogdown::hugo_build()
