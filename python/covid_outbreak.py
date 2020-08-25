#!/usr/bin/env python3
"""


Created: August 2020
Authors: p-robot, aneln
"""

import os, sys, argparse
import numpy as np, pandas as pd
from os.path import join

from COVID19.model import Model, Parameters, ModelParameterException
import COVID19.simulation as simulation


if __name__ == "__main__":
    
    ################################
    # Parse command-line arguments #
    ################################

    parser = argparse.ArgumentParser()

    # -------------------------
    # Default args to the model
    # -------------------------

    parser.add_argument("--input_parameter_file", type = str, 
        help = "Input parameter file (path to csv file)", required = True)

    parser.add_argument("--parameter_line_number", type = int,
        help = "Line number of the parameter file to use for input parameters", default = 1)

    parser.add_argument("--results_dir", type = str, 
        help = "Directory of results for output files", required = True)

    parser.add_argument("--household_demographics_file", type = str,
        help = "Household demographics file", required = True)

    # -------------------------
    # Project-specific parameters (these aren't default parameter inputs to the model)
    # -------------------------

    parser.add_argument("--lockdown_prevalence_trigger", type = float,
        help = "Prevalence (%) of SARS-CoV-2 in popn at which point lockdown is triggered", 
        default = 2)

    parser.add_argument("--lockdown_multiplier", type = float,
        help = "Multiplier on number of daily contacts during lockdown", required = True)

    parser.add_argument("--lockdown_duration", type = int,
        help = "Duration of lockdown (days)", default = 70)

    parser.add_argument("--intervention_self_quarantine_fraction", type = float,
        help = "Fraction of symptomatics self-quarantining when interventions start", 
        default = 0.65)

    parser.add_argument("--app_uptake_multiplier", type = float, default = 0.6, 
        help = "Proportion of phone users that use the contact tracing app")

    parser.add_argument("--file_prefix", type = str,
        help = "Prefix of timeseries files", default = "covid19_timeseries")

    #
    # app_uptake_multiplier = float(sys.argv[2])
    # lockdown_multiplier = float(sys.argv[3])
    # rng_seed = int(sys.argv[6])
    # dir_name = str(sys.argv[7])
    #
    # final_simulation_time = 300
    #
    #
    #
    # params.set_param( "app_users_fraction_0_9",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_0_9") )
    # params.set_param( "app_users_fraction_10_19",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_10_19") )
    # params.set_param( "app_users_fraction_20_29",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_20_29") )
    # params.set_param( "app_users_fraction_30_39",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_30_39") )
    # params.set_param( "app_users_fraction_40_49",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_40_49") )
    # params.set_param( "app_users_fraction_50_59",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_50_59") )
    # params.set_param( "app_users_fraction_60_69",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_60_69") )
    # params.set_param( "app_users_fraction_70_79",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_70_79") )
    # params.set_param( "app_users_fraction_80",
    #     app_uptake_multiplier * params.get_param( "app_users_fraction_80") )
    #
    # params.set_param( "self_quarantine_fraction", 0 )
    # params.set_param( "end_time", final_simulation_time )


    # ---------------------------------------------------------------------------
    # All remaining parameters are interpreted as parameters native to the model
    # ---------------------------------------------------------------------------

    args, additional_args = parser.parse_known_args()

    # Parse the additional args to create a param-name: param-value dictionary
    additional_args = [a[2:] if "--" in a else a for a in additional_args]
    param_dict = dict(zip(additional_args[::2], additional_args[1::2]))
    print(param_dict)

    params = Parameters(
        args.input_parameter_file, 
        args.parameter_line_number, 
        args.output_dir, 
        args.household_demographics_file)

    # Set any parameter values that have been passed to the model
    params.set_param_dict(param_dict)
    
    # Instantiate the model/simulation object
    model = simulation.COVID19IBM(model = Model(params))
    sim = simulation.Simulation(env = model, end_time = params.get_param( "end_time" ) )
    
    # Start the epidemic
    sim.steps(1)
    et = 1 # record elapsed time
    
    # check whether it is time for self-isolation: 0.5% of population infected
    while ( ( sim.results["total_infected"][ -1]/params.get_param("n_total") ) < 0.005 ):
        sim.steps(1)
        et += 1
    
    # during self-isolation, 65% people self-isolate with their HH on symptoms until 2% 
    # of population infected
    sim.env.model.update_running_params( "self_quarantine_fraction", 0.65 )
    sim.env.model.update_running_params( "quarantine_household_on_symptoms", 1 )
    sim.env.model.update_running_params( "quarantine_household_on_positive", 1 )
    
    # lockdown on when 2% of population infected
    while ( ( sim.results["total_infected"][ -1]/params.get_param("n_total") ) <  0.02 ):
        sim.steps(1)
        et += 1
    
    sim.env.model.update_running_params("lockdown_on", 1)
    sim.env.model.update_running_params("lockdown_house_interaction_multiplier", 1.5)
    sim.env.model.update_running_params("lockdown_random_network_multiplier", 0.29)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_primary_network", 0.29)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_secondary_network", 0.29)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_working_network", 0.29)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_retired_network", 0.29)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_elderly_network", 0.29)
    
    el = 0 # elapsed lockdown
    while el < (lockdown_duration - 7):
        sim.steps(1)
        et += 1
        el += 1
    
    # Turn on app in all scenarios one week prior to the end of lockdown
    sim.env.model.update_running_params( "app_turned_on", 1 )
    sim.env.model.update_running_params( "quarantine_on_traced", 1 )
    sim.env.model.update_running_params( "trace_on_positive", 1 )
    
    # Using parameters in line with Scenario 7.1 from app paper
    # "Trace on test fast: with trace on positive and a fast test turn around"
    sim.env.model.update_running_params( "test_on_symptoms", 1 )
    sim.env.model.update_running_params( "quarantine_household_on_positive", 1 )
    sim.env.model.update_running_params( "quarantine_household_on_traced_positive", 0 )
    sim.env.model.update_running_params( "quarantine_household_on_traced_symptoms", 0 )
    sim.env.model.update_running_params( "test_order_wait", 1 )
    sim.env.model.update_running_params( "test_result_wait", 1 )
    sim.env.model.update_running_params( "trace_on_symptoms", 0 )
    sim.env.model.update_running_params( "test_on_traced", 0 )
    
    while el < lockdown_duration:
        sim.steps(1)
        et += 1
        el += 1
    
    # lockdown off 
    last_day_of_lockdown = et
    
    # scenarios-independent parameters
    sim.env.model.update_running_params("self_quarantine_fraction", 0.8 )
    sim.env.model.update_running_params("lockdown_house_interaction_multiplier", 1)
    
    sim.env.model.update_running_params("lockdown_random_network_multiplier", lockdown_multiplier)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_primary_network",
         lockdown_multiplier)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_secondary_network",
         lockdown_multiplier)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_working_network",
         lockdown_multiplier)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_retired_network",
         lockdown_multiplier)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_elderly_network",
         lockdown_multiplier)
    
    # Turn on shielding of the elderly.  
    sim.env.model.update_running_params("lockdown_occupation_multiplier_retired_network", 0.5)
    sim.env.model.update_running_params("lockdown_occupation_multiplier_elderly_network", 0.5)
    
    # Run until end of simulation
    while et < final_simulation_time:
        sim.steps(1)
        et += 1
    
    sim.env.model.write_transmissions()
    
    timeseries = pd.DataFrame( sim.results )
    timeseries.to_csv(join(dir_name, "covid_timeseries_Run1.csv"), index = False)
