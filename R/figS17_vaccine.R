#
# Fig S18 Vaccination R plot
#
# This script calculates the plots of the comparison of the vaccine programmes
#
#
# The population is populated at the rate of 2% of adults the population a day
##
# Created: 8 April 2021
# Author: roberthinch
#

library( OpenABMCovid19)

run_model = function( n_total, vaccinate, vaccine_type )
{
  # get the model overiding a couple of params
  model  = Model.new( params = list( n_total = n_total ) )

  # Run the model until there are 2% infections
  model$one_time_step()
  while( model$one_time_step_results()[["total_infected"]] < n_total * 0.02 )
    model$one_time_step()

  # Turn on lockdown and run the model for another 30 days and vaccinated
  Model.update_running_params( model, "self_quarantine_fraction", 0.75 )
  model$update_running_params( "lockdown_on", 1 )

  # define the vaccination programme
  vaccine = VaccineSchedule$new(
    frac_0_9 = 0,
    frac_10_19 = 0,
    frac_20_29 = 0.02,
    frac_30_39 = 0.02,
    frac_40_49 = 0.02,
    frac_50_59 = 0.02,
    frac_60_69 = 0.02,
    frac_70_79 = 0.02,
    frac_80 = 0.02,
    efficacy = 0.9,
    time_to_protect = 15,
    vaccine_type = vaccine_type
  )

  for( t in 1:30 )
  {
    model$one_time_step( )
    if( vaccinate )
      model$vaccinate_schedule( vaccine )
  }

  # Turn off lockdown and run the model for another 50 days and vaccinated
  model$update_running_params( "lockdown_on", 0 )
  for( t in 1:50 )
  {
    model$one_time_step( )
    if( vaccinate )
      model$vaccinate_schedule( vaccine )
  }

  results = model$results()
  rm( model )
  return( results )
}

n_total = 100000;
res_vac_full = as.data.table( run_model( n_total, TRUE, VACCINE_TYPES[["FULL"]] ) )
res_vac_symp = as.data.table( run_model( n_total, TRUE, VACCINE_TYPES[["SYMPTOM"]]  ) )
res_base     = as.data.table( run_model( n_total, FALSE, VACCINE_TYPES[["FULL"]]  ) )

lockdown_start = res_base[ lockdown == 1, min( time )]
lockdown_end   = res_base[ lockdown == 1, max( time )]
lockdown_shade = list(
  type = "rect",
  fillcolor = "blue",
  line = list( color = "blue" ),
  opacity = 0.3,
  x0 = lockdown_start,
  x1 = lockdown_end,
  xref = "x",
  y0 = 0.05,
  y1 = 1.13,
  yref = "paper"
)
lockdown_title = list(
  showarrow = F,
  x = lockdown_start + 6,
  y = 1,
  text = "<b>lockdown</b>",
  xanchor = "left",
  xref = "x",
  yref = "paper",
  font = list( size = 18, color = "white")
)

p1 = plot_ly(
  res_base,
  x = ~time,
  y = ~total_death,
  name = "no vaccine",
  type = "scatter",
  mode = "lines",
  color = "no"
) %>%
add_trace(
  data = res_vac_full,
  name = "vaccine (full-protection)",
  color = "vaccine_full"
) %>%
add_trace(
    data = res_vac_symp,
    name = "vaccine (symptoms-only)",
    color = "vaccine"
) %>%
layout(
  xaxis = list( title = "time" ),
  yaxis = list( title = "total deaths"),
  shapes = list( lockdown_shade ),
  legend = list( x = 0.05, y = 0.95)
)

p2 = plot_ly(
  res_base,
  x = ~time,
  y = ~total_infected,
  name = "no vaccine",
  type = "scatter",
  mode = "lines",
  color = "no",
  showlegend = FALSE
) %>%
add_trace(
  data = res_vac_full,
  name = "vaccine (full-protection)",
  color = "vaccine_full"
) %>%
add_trace(
  data = res_vac_symp,
  name = "vaccine (symptoms-only)",
  color = "vaccine"
) %>%
  layout(
    xaxis = list( title = "time" ),
    yaxis = list( title = "total infections"),
    shapes = list( lockdown_shade ),
    annotations = list( lockdown_title )
  )
subplot( list( p1, p2), nrows = 2, shareX = TRUE, titleY = TRUE)




