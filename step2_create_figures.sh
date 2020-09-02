#!/usr/bin/env bash
# 
# Create figures for the model paper


source config.sh

# Figures in the main text
# ------------------------

# Figure 1 is the schematic of networks
python3 python/figure_2.py
python3 python/figure_3.py
python3 python/figure_4.py
# Figure 5 is the schematic of the model
python3 python/figure_6.py


# Supplementary figures
# ---------------------

python3 python/figure_S1.py
python3 python/figure_S2.py
Rscript R/histogram_app_uptake.R $app_uptake

