library( data.table)
library( plotly )
file_performance = "performance.csv"
file_memory = "memory.csv"

performance = fread( file_performance )
memory = fread( file_memory )

brightRed  = "rgb(230,64,64)"
darkRed    = "rgb(150,32,32)"
brightBlue = "rgb(64,64,255)"
darkBlue   = "rgb(32,32,150)"

p1 = plot_ly(
  data = performance[ 8:17 ],
  x = ~pop_total,
  y = ~t_per_step,
  type = "scatter",
  mode = "markers+lines",
  name = "single-population/static-networks",
  line = list( color = darkRed ),
  marker = list( color = darkRed, symbol = "circle", size = 10 )
) %>%
  add_trace(
    data = performance[ 25:34 ],
    name = "single-populuation/dynamic-networks",
    line = list( color = brightRed ),
    marker = list( color = brightRed, symbol = "circle-open" )
) %>%
  add_trace(
    data = performance[ 1:7 ],
    name = "meta-population/static-networks",
    line = list( color = darkBlue ),
    marker = list( color = darkBlue, symbol = "triangle-up" )
) %>%
  add_trace(
    data = performance[ 18:24 ],
    name = "meta-population/dynamic-networks",
    line = list( color = brightBlue),
    marker = list( color = brightBlue, symbol = "triangle-up-open" )
  ) %>%
  layout(
  xaxis = list( type = "log", title = "total population", titlefont = list( size = 24), tickfont = list( size = 24)  ),
  yaxis = list( type = "log", title = "time per step (s)", titlefont = list( size = 24), tickfont = list( size = 24)  ),
  legend = list(x = 0.05, y = 0.95, font = list( size = 24))
)

p2 = plot_ly(
  data = memory[days_interactions == 1 ],
  x = ~pop_total,
  y = ~persistent_mem_mb,
  type = "scatter",
  mode = "markers+lines",
  name = "1-day of interactions stored",
  line = list( color = brightRed ),
  marker = list( color = brightRed, symbol = "circle", size = 10 )
) %>%
  add_trace(
    data =  memory[days_interactions == 7 ],
    name = "7-days of interactions stored",
    line = list( color = brightBlue),
    marker = list( color = brightBlue, symbol = "triangle-up-open" )
  ) %>%
  layout(
    xaxis = list( type = "log", title = "total population", titlefont = list( size = 24), tickfont = list( size = 24)  ),
    yaxis = list( type = "log", title = "persistent memory (Mb)", titlefont = list( size = 24 ), tickfont = list( size = 24) ),
    legend = list(x = 0.05, y = 0.95, font = list( size = 24))
  )
p2







