.PHONY: all data figure2 figure3 figure4 table1 figureS1_S2 \
	figureS3 figureS4 figureS13 figure_generation_time

figure_format="png"

####################
# Complete analysis
# ------------------

all: data
	make figure2
	make figure3
	make figure4
	make table1
	make figureS1_S2
	make figureS3
	make figureS4
	make figureS13
	make figure_generation_time

# Without data-generation prerequisite
all_output: 
	make figure2
	make figure3
	make figure4
	make table1
	make figureS1_S2
	make figureS3
	make figureS4
	make figureS13
	make figure_generation_time

####################
# Generate the data
# simulate an outbreak
# ------------------

# Output files/directories
model_dir=OpenABM-Covid19
output_dir=data
input_parameter_file="$(model_dir)/tests/data/baseline_parameters.csv"
household_demographics_file="$(model_dir)/tests/data/baseline_household_demographics.csv"
hospital_file="$(model_dir)/tests/data/hospital_baseline_parameters.csv"
	
# Simulation parameters
n_total=1000000                              # Population size to simulate
rng_seed=2020                                # Random seed to use in the simulation
lockdown_duration=77                         # Lockdown duration
lockdown_prevalence_trigger=1.55                # Prevalence (%) at which point lockdown is triggered
intervention_prevalence_trigger=0.3875          # Prevalence (%) at which point self-isolation on symptoms and positive test is triggered
intervention_self_quarantine_fraction=0.65   # Proportion of symptomatics that self-isolate on symptoms

data:
	python src/covid_outbreak.py \
		--input_parameter_file $(input_parameter_file) \
		--household_demographics_file $(household_demographics_file) \
		--output_dir $(output_dir) \
		--lockdown_duration $(lockdown_duration) \
		--lockdown_prevalence_trigger $(lockdown_prevalence_trigger) \
		--intervention_prevalence_trigger $(intervention_prevalence_trigger) \
		--intervention_self_quarantine_fraction $(intervention_self_quarantine_fraction) \
		--rng_seed $(rng_seed) \
		--n_total $(n_total)

#######################
# Main figures
# ---------------------

# figure 1 is a schematic of the networks

figure2:
	python src/viz/figure_2.py \
		"data/interactions_Run1.csv" \
		"data/individual_file_Run1.csv" \
		"output/figures" \
		$(figure_format)

figure3:
	python src/viz/transmission_heatmap_by_age_by_infectiousness.py \
		"data/transmission_Run1.csv" \
		"output/figures/fig3_transmission_matrix_by_age_by_infectiousness" \
		$(figure_format)


figure4:
	python src/viz/ifr_hist_by_age.py \
		"data/transmission_Run1.csv" \
		"output/figures/fig4_ifr_by_age" \
		$(figure_format)


# figure 5 is a fit of the baseline parameters to observed data (using another repo)
# figure 6 is a schematic of the model

#######################
# Main tables
# ---------------------

table1:
	python src/analysis/table_ifr_by_age.py \
		"data/transmission_Run1.csv" \
		"output/tables/tab1_ifr_by_age.csv"

#######################
# Supplementary figures
# ---------------------

figureS1_S2:
	python src/viz/figure_S1.py \
		"data/transmission_Run1.csv" \
		"data/individual_file_Run1.csv" \
		"output/figures/" \
		$(figure_format)

figureS3:
	python src/viz/waiting_time_distributions.py \
		"OpenABM-Covid19/tests/data/baseline_parameters.csv" \
		"output/figures/figS3_waiting_time_distributions" \
		$(figure_format)


app_uptake=0.6
figureS4:
	Rscript src/viz/histogram_app_uptake.R \
		$(app_uptake) \
		"OpenABM-Covid19/tests/data/baseline_parameters_transpose.csv" \
		"output/figures/figS4_histogram_app_uptake" \
		$(figure_format)


figureS13:
	python src/viz/plot_R_timeseries.py \
		"data/transmission_Run1.csv" \
		"data/covid_timeseries_Run1.csv" \
		"OpenABM-Covid19/tests/data/baseline_parameters.csv" \
		"output/figures/figS13_actual_R" \
		$(figure_format)

#######################
# Miscellaneous figures
# ---------------------

figure_generation_time:
	python src/viz/generation_time_by_infectiousness.py \
		"data/transmission_Run1.csv" \
		"data/covid_timeseries_Run1.csv" \
		"output/figures/generation_time_by_infectiousness" \
		$(figure_format)
