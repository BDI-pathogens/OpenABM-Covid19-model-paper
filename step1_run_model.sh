# Script to run the OpenABM-Covid19 model

source config.sh


source venv/bin/activate

python3 python/covid_outbreak.py \
    --input_parameter_file "$input_parameter_file" \
    --household_demographics_file "$household_demographics_file" \
    --output_dir "$output_dir" \
    --app_uptake_multiplier $app_uptake_multiplier \
    --lockdown_multiplier $lockdown_multiplier \
    --lockdown_duration $lockdown_duration \
    --lockdown_prevalence_trigger $lockdown_prevalence_trigger \
    --intervention_self_quarantine_fraction $intervention_self_quarantine_fraction \
    --rng_seed $rng_seed --n_total 1000000

deactivate
