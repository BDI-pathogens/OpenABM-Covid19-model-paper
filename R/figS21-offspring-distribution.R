library( data.table)
library( VGAM)
library( plotly)
library( OpenABMCovid19 )

# calculated the offspring and sibling distributions and plots at the start of
# start of an exponential growth stage

total_cases = 0.01
t_infect = 30

# build the model
m = Model.new()

# run until the relevant number of parents have been infected
while( TRUE )
{
  Model.one_time_step(m)
  inf = Model.one_time_step_results(m)[["total_infected"]]
  if( inf > n_total * total_cases )
    break
}
t_first = Model.one_time_step_results(m)[["time"]]

# continue calculation to get all the forward transmissions
for( t in 1:t_infect )
  Model.one_time_step(m)
trans = as.data.table( Model.get_transmissions( m ) )

# get the IDs of the parent (i.e. in first period)
id_inf = trans[ time_infected <= t_first & time_infected , .( ID_source = ID_recipient ) ]
count_inf  = id_inf[,.N]

# get the number infected by each infected (put back those who infected zero)
t_trans = trans[ id_inf, on = "ID_source", nomatch = 0][ ,.(N = .N), by = "ID_source"]
t_trans = t_trans[ id_inf, on = "ID_source"][ , .(ID_source, N = ifelse( is.na(N), 0 , N))]
t = t_trans[ , .(count = .N), by = "N"]

# fit a negative-binomial distribution
coef = coef( vglm(t_trans[,N] ~ 1, negbinomial ))
mu_mle = exp( coef[[1]])
k_mle = exp( coef[[2]])

# rank by number of offspring infections and add total transmissions for siblings
t = t[order(N)]
t[, tot_trans := N * count]

# add the sample offspring/sibling distribution
t[ , prob_offspring := count / t[,sum(count)]]
t[ , prob_sibling := tot_trans / t[,sum(tot_trans)]]

# add the fitted NB offspring/sibling distributions
t[ ,prob_offspring_fit_nb := dnbinom( N, size = k_mle, mu = mu_mle) ]
t[, prob_sibling_fit_nb := prob_offspring_fit_nb * N ]
t[, prob_sibling_fit_nb := prob_sibling_fit_nb / t[ ,sum(prob_sibling_fit_nb)] ]

# add the cumulative distributions
t[ , cs_count := cumsum(count)]
t[ , cs_tot_trans := cumsum(tot_trans)]
t[, frac_count := cs_count / max(cs_count)]
t[, frac_tot_trans := cs_tot_trans / max(cs_tot_trans)]

colorOffspring  = "rgb(32,32,150)"
colorSibling   = "rgb(204,204,204)"
colorBlack     = "rgb(0,0,0)"

p = plot_ly(
  data = t,
  x = ~N,
  y = ~prob_offspring,
  type = "bar",
  name = paste( sprintf( "offspring (k=%.2f,", k_mle), "\u00B5", sprintf("=%.1f)",mu_mle ) ),
  marker = list( color = colorOffspring )
) %>%
add_bars(
  y = ~prob_sibling,
  name = "sibling" ,
  marker = list( color = colorSibling)
) %>%
add_lines(
  y = ~prob_offspring_fit_nb,
  showlegend = FALSE,
  marker = list( color = colorOffspring),
  line = list( color = colorOffspring)
) %>%
add_lines(
  y = ~prob_sibling_fit_nb,
  showlegend = FALSE,
  marker = list( color = colorSibling ),
  line = list( color = colorSibling )
) %>%
add_lines(
  x = ~frac_count,
  y = ~frac_tot_trans,
  xaxis = "x2",
  yaxis = "y2",
  showlegend = FALSE,
  marker = list( color = colorBlack),
  line = list( color = colorBlack)
) %>%
layout(
  xaxis  = list(
    range = c(-1,25),
    title = "number of offsprings/siblings"
  ),
  yaxis = list( title = "probability density"),
  xaxis2 = list(
    range  = c(0,1),
    domain = c(0.5, 0.97),
    anchor ='y2',
    title  = "cumalative offspring",
    dtick = 0.2
  ),
  yaxis2 = list(
    range = c( 0,1),
    domain = c(0.5, 0.97),
    anchor='x2',
    title  = "cumalative sibling"
  ),
  legend = list(x = 0.5, y = 0.15)
)
p


