library( data.table)
library( plotly)
library( OpenABMCovid19 )

# calculate the secondary household attack rate
# look at all the infections from first 1% of people infected (to prevent
# multiple external infections in household members).
# only consider the first person infected in each household

total_cases = 0.01
n_total = 1e6
t_infect = 30

# build the model
m = Model.new( params = list( n_total = n_total ))

# run until the relevant number of parents have been infected
while( TRUE )
{
  Model.one_time_step(m)
  inf = Model.one_time_step_results(m)[["total_infected"]]
  if( inf > n_total * total_cases )
    break
}
t_first = Model.one_time_step_results(m)[["time"]]

# continue simulation to get all the forward transmissions from these individuals
for( t in 1:t_infect )
  Model.one_time_step(m)
trans = as.data.table( Model.get_transmissions( m ) )

# get the individual data and the hnumber of people in each household
indiv = as.data.table(m$get_individuals() )
house_members = indiv[ , .( N_in_house = .N ), by = "house_no" ]

calculate_household_sar = function( trans, indiv, house_members )
{
  # get the IDs of those first infected (i.e. in first period)
  id_infected = trans[ time_infected <= t_first & time_infected, .( ID_source = ID_recipient, time_infected ) ]

  # get the id of the first infected in each house
  id_infected_first = indiv[ ,.( ID_source = ID, house_no ) ][ id_infected, on = "ID_source" ]
  id_infected_first = id_infected_first[ order( time_infected)][ , .( ID_source = first( ID_source ) ), by = "house_no"]

  # get the number of people they infected in each house
  n_house_transmissions_by_source = trans[ house_no_recipient == house_no_source, .(N_house_trans = .N ), by= "ID_source"]

  # combine the number of transmission with the number of people in the household
  dt_household_trans = n_house_transmissions_by_source[ id_infected_first, on = "ID_source", ]
  dt_household_trans[ , N_house_trans := ifelse( is.na( N_house_trans ), 0, N_house_trans)]
  dt_household_trans = house_members[ dt_household_trans, on = "house_no" ]

  # calculate the household SAR (-1 since don't include the initial infected person)
  household_sar = dt_household_trans[ , sum( N_house_trans ) / sum( N_in_house - 1)]
  cat( sprintf( "Household SAR = %.2f", household_sar ) )
}

calculate_household_sar( trans, indiv, house_members )


