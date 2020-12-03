#!/usr/bin/env python3
"""
Python script to run OpenABM-Covid19 with a basic intervention scenario of self-isolation on 
symptoms or positive test, and lockdown.  Triggers for self-isolation on symptoms and lockdown
are based upon prevalence.  

Created: August 2020
Authors: p-robot, aneln
"""

import argparse, numpy as np, pandas as pd
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

    parser.add_argument("--output_dir", type = str, 
        help = "Directory of results for output files", required = True)

    parser.add_argument("--household_demographics_file", type = str,
        help = "Household demographics file", required = True)

    # -------------------------
    # Project-specific parameters (these aren't default parameter inputs to the model)
    # -------------------------

    parser.add_argument("--lockdown_prevalence_trigger", type = float,
        help = "Prevalence (%) of SARS-CoV-2 in popn at which point lockdown is triggered", 
        default = 2)

    parser.add_argument("--lockdown_duration", type = int,
        help = "Duration of lockdown (days)", default = 70)

    parser.add_argument("--intervention_prevalence_trigger", type = float,
        help = "Prevalence (%) of SARS-CoV-2 in popn at which point self-isolation on symptoms is triggered", 
        default = 0.5)

    parser.add_argument("--intervention_self_quarantine_fraction", type = float,
        help = "Fraction of symptomatics self-quarantining when interventions start", 
        default = 0.65)

    parser.add_argument("--file_prefix", type = str,
        help = "Prefix of timeseries files", default = "covid19_timeseries")

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
    
    end_time = params.get_param( "end_time" )

    # Instantiate the model/simulation object
    model = simulation.COVID19IBM(model = Model(params))
    sim = simulation.Simulation(env = model, end_time = end_time )
    
    # Start the epidemic
    sim.steps(1)
    et = 1 # record elapsed time
    
    # Write the interactions file on the first day of the simulation
    sim.env.model.write_interactions_file()
    
    # Turn on self-isolation on symptoms when a specific prevalence is met
    while ( ( sim.results["total_infected"][ -1]/params.get_param("n_total") ) < args.intervention_prevalence_trigger/100. ):
        sim.steps(1)
        et += 1
    
    # During self-isolation, assume a specific proportion of population self-isolate 
    # (with their HH) on symptoms, and also do so on return of a positive test
    sim.env.model.update_running_params( "self_quarantine_fraction", args.intervention_self_quarantine_fraction )
    sim.env.model.update_running_params( "quarantine_household_on_symptoms", 1 )
    sim.env.model.update_running_params( "quarantine_household_on_positive", 1 )
    
    # Turn lockdown on when a specific prevalence of population infected
    while ( ( sim.results["total_infected"][ -1]/params.get_param("n_total") ) < args.lockdown_prevalence_trigger/100. ):
        sim.steps(1)
        et += 1
    
    sim.env.model.update_running_params("lockdown_on", 1)
    
    el = 0 # elapsed lockdown
    while el < (args.lockdown_duration - 7):
        sim.steps(1)
        et += 1
        el += 1
    
    while el < args.lockdown_duration:
        sim.steps(1)
        et += 1
        el += 1
    
    print("Elapsed time:", el)
    
    # Write output files
    sim.env.model.write_transmissions()
    sim.env.model.write_individual_file()
    
    # Write timeseries file
    timeseries = pd.DataFrame( sim.results )
    timeseries.to_csv(join(args.output_dir, "covid_timeseries_Run1.csv"), index = False)

