


#######################
# Main figures
# ---------------------

# figure 1 is a schematic of networks

figure2:
	python python/figure_2.py \
		"results/interactions_Run1.csv" \
		"results/individual_file_Run1.csv" \
		"figures" \
		"pdf"

figure3:
	python python/transmission_heatmap_by_age_by_infectiousness.py \
		"results/transmission_Run1.csv" \
		"figures/fig3_transmission_matrix_by_age_by_infectiousness" \
		"pdf"

# figure 4 is a schematic of the model

figure5:
	python python/ifr_hist_by_age.py \
		"results/transmission_Run1.csv" \
		"figures/fig5_ifr_by_age.png"


#######################
# Main tables
# ---------------------

table1:
	python python/table_ifr_by_age.py \
		"results/transmission_Run1.csv" \
		"tables/tab1_ifr_by_age.csv"

#######################
# Supplementary figures
# ---------------------

figureS2:
	python python/waiting_time_distributions.py \
		"OpenABM-Covid19/tests/data/baseline_parameters.csv" \
		"figures/figS2_waiting_time_distributions.png"


app_uptake=0.6
figureS3:
	Rscript R/histogram_app_uptake.R \
	$(app_uptake) \
	"OpenABM-Covid19/tests/data/baseline_parameters_transpose.csv" \
	"figures/figS3_histogram_app_uptake.png"


figureS4:
	python python/plot_R_timeseries.py \
		"results/transmission_Run1.csv" \
		"results/covid_timeseries_Run1.csv" \
		"OpenABM-Covid19/tests/data/baseline_parameters.csv" \
		"figures/figS4_actual_R.png"


#######################
# Miscellaneous figures
# ---------------------

figure_generation_time:
	python python/generation_time_by_infectiousness.py \
		"results/transmission_Run1.csv" \
		"results/covid_timeseries_Run1.csv" \
		"figures/generation_time_by_infectiousness.png"