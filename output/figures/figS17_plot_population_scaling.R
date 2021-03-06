library( data.table )
library( plotly )

file = "population_scaling.csv"
dt = fread( file )
dt[ , n_pops_str := as.character( n_pops )]
dt[ , n_total_str := format( n_total, big.mark = "," )]
dt$n_total_str = factor( dt$n_total_str, dt[order( n_total)][ , unique(n_total_str)] )
dt$n_pops_str = factor( dt$n_pops_str, dt[order( n_pops)][ , unique(n_pops_str)] )


p1 = plot_ly(
  data = dt[  s_total >= 20000 & n_pops == 1],
  x = ~n_total_str,
  y = ~doubling_time,
  color = ~n_pops_str,
  type = "box",
  offsetgroup = "1"
) %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 2],offsetgroup = "2") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 3],offsetgroup = "3") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 5],offsetgroup = "5") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 10],offsetgroup = "10") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 20],offsetgroup = "20") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 50],offsetgroup = "50") %>%
  layout(
  yaxis = list( title = "doubling time", range = c(2.75,4.25)),
  boxmode = "group",
  legend = list( title = list( text = "N sub-populations") )
)

p2 = plot_ly(
  dt[  s_total >= 20000 & n_pops == 1 ],
  x = ~n_total_str,
  y = ~herd,
  color = ~n_pops_str,
  type = "box",
  showlegend = FALSE,
  offsetgroup = "1"
) %>%
add_trace(data = dt[  s_total >= 20000 & n_pops == 2],offsetgroup = "2") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 3],offsetgroup = "3") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 5],offsetgroup = "5") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 10],offsetgroup = "10") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 20],offsetgroup = "20") %>%
add_trace( data = dt[  s_total >= 20000 & n_pops == 50],offsetgroup = "50") %>%
  layout(
  xaxis = list( title = "total population"),
  yaxis = list( title = "fraction infected", range = c(0.835,0.87)),
  boxmode = "group"
)

subplot( list( p1, p2), nrows = 2, shareX = TRUE, titleY = TRUE)

