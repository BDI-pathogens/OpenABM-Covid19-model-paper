#!/usr/bin/env python3
"""
Script to create figure 4

Transmission matrix stratified by age of source and recipient and infectious status of the source
"""

from os.path import join
import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt

import plotting
from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

age_group_labels = [enum.name[1:].replace("_","-") for enum in AgeGroupEnum]
age_group_labels[-1] = "80+"
n_age = len(age_group_labels)

# Ordering of panels
infectious_names = [ \
    "ASYMPTOMATIC", \
    "PRESYMPTOMATIC_MILD", \
    "PRESYMPTOMATIC", \
    "SYMPTOMATIC_MILD", \
    "SYMPTOMATIC"]

# Pull the names and values of the above infectious types
infectious_types = []; infectious_labels = []
for i in infectious_names:
    for e in EVENT_TYPES:
        if i == e.name:
            infectious_types.append(e.value)
            infectious_labels.append(plotting.EVENT_TYPE_STRING[e.value])

if __name__ == "__main__":
    
    transmission_file = sys.argv[1]
    output_figure = sys.argv[2]
    file_format = sys.argv[3]
    
    plt.rcParams["savefig.format"] = file_format
    plt.rcParams['figure.figsize'] = [12, 10]
    
    df_trans = pd.read_csv(transmission_file)
    
    fig, ax = plotting.transmission_heatmap_by_age_by_panels(
        df_trans, "age_group_recipient", "age_group_source", bins = n_age,
        panels = infectious_types,
        panelvar = "status_source", panel_labels = infectious_labels,
        xlabel = "Age of source", ylabel = "Age of recipient",
        legend_title = "Number of\ntransmission events",
        xticklabels = age_group_labels, yticklabels = age_group_labels,
        title_fontsize = 16, spines = True, vmin_panels = 1, 
        ncols = 3, nrows = 2)

    plt.savefig(output_figure)
    plt.close()
