# Configuration file for running scripts for generating 
# figures from the OpenABM-Covid19 model
# 

# Name of the directory into which to clone the model
# name of the release to be cloned
model_dir="OpenABM-Covid19"
release="0.3"

output_dir="results"
input_parameter_file="$model_dir/tests/data/baseline_parameters.csv"
household_demographics_file="$model_dir/tests/data/baseline_household_demographics.csv"
hospital_file="$model_dir/tests/data/hospital_baseline_parameters.csv"

# Model parameters

lockdown_multiplier=0.29
app_uptake_multiplier=0.6
rng_seed=2020
lockdown_duration=70
lockdown_prevalence_trigger=2
intervention_self_quarantine_fraction=0.65

