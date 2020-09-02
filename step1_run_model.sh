#!/usr/bin/env bash
# 
# Script to simulate an outbreak with 
# the OpenABM-Covid19 model

# Load config parameters
source config.sh

# Activate the Python virtual environment
source venv/bin/activate

# Run python script of an outbreak
python3 python/covid_outbreak.py \
    --input_parameter_file "$input_parameter_file" \
    --household_demographics_file "$household_demographics_file" \
    --output_dir "$output_dir" \
    --app_uptake_multiplier $app_uptake_multiplier \
    --lockdown_multiplier $lockdown_multiplier \
    --lockdown_duration $lockdown_duration \
    --lockdown_prevalence_trigger $lockdown_prevalence_trigger \
    --intervention_self_quarantine_fraction $intervention_self_quarantine_fraction \
    --rng_seed $rng_seed --n_total $n_total

# Deactivate the Python virtual environment
deactivate

