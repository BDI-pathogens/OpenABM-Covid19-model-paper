#!/usr/bin/env python3
"""
Script to create figure 4

Transmission matrix stratified by age of source and recipient and infectious status of the source
"""

from os.path import join

import pandas as pd, numpy as np
from matplotlib import pyplot as plt

import plotting
from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

age_group_labels = [enum.name[1:].replace("_","-") for enum in AgeGroupEnum]
age_group_labels[-1] = "80+"
n_age = len(age_group_labels)

infectious_compartments = ["PRESYMPTOMATIC", "PRESYMPTOMATIC_MILD", \
    "ASYMPTOMATIC", "SYMPTOMATIC", "SYMPTOMATIC_MILD"]
infectious_types = [e.value for e in EVENT_TYPES if e.name in infectious_compartments]
infectious_names = [e.name for e in EVENT_TYPES if e.name in infectious_compartments]
infectious_labels = [plotting.EVENT_TYPE_STRING[e.value] for e in EVENT_TYPES if e.name in infectious_compartments]


if __name__ == "__main__":

    plt.rcParams['figure.figsize'] = [20, 8]
    
    df_trans = pd.read_csv(join("results", "transmission_Run1.csv"))
    
    fig, ax = plotting.transmission_heatmap_by_age_by_panels(
        df_trans, "age_group_recipient", "age_group_source", bins = n_age,
        panels = infectious_types,
        panelvar = "status_source", panel_labels = infectious_labels,
        xlabel = "Age of source", ylabel = "Age of recipient",
        legend_title = "Number of\ntransmission events",
        xticklabels = age_group_labels, yticklabels = age_group_labels,
        title_fontsize = 16, spines = True)

    plt.savefig(join("figures", "fig4_transmission_matrix_by_infectiousness"))
    plt.close()
