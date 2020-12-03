#!/usr/bin/env python3
"""
Script to create figure 3

Histogram of generation time of transmission events stratified by infectious state of the source
"""

from os.path import join

import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt

import plotting
from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

infectious_compartments = ["PRESYMPTOMATIC", "PRESYMPTOMATIC_MILD", \
    "ASYMPTOMATIC", "SYMPTOMATIC", "SYMPTOMATIC_MILD"]
infectious_types = [e.value for e in EVENT_TYPES if e.name in infectious_compartments]
infectious_names = [e.name for e in EVENT_TYPES if e.name in infectious_compartments]
infectious_labels = [plotting.EVENT_TYPE_STRING[e.value] for e in EVENT_TYPES if e.name in infectious_compartments]


if __name__ == "__main__":
    
    transmission_file = sys.argv[1]
    timeseries_file = sys.argv[2]
    output_file = sys.argv[3]
    
    df_trans = pd.read_csv(transmission_file)
    df_ts = pd.read_csv(timeseries_file)
    
    plt.rcParams['figure.figsize'] = [10, 10]
    
    # # Find lockdown time (in simulation time)
    # lockdown_start = np.min(df_ts.loc[df_ts.lockdown == 1]["time"])
    #
    # # Window length (days)
    # window_length = 14
    #
    # # First panel will show 14 days preceding lockdown, second panel 14 days succeeding lockdown
    # window1_start = lockdown_start - window_length - 7
    # window2_start = lockdown_start + 7
    # window_start_times = [window1_start, window2_start]
    
    n_groups = len(infectious_types)
    NBINS = 18
    
    fig, ax = plt.subplots(nrows = n_groups)
    for i, state in enumerate(infectious_types):
        hist = df_trans.loc[df_trans["status_source"] == state]["generation_time"]
        bins = np.arange(NBINS)
        ax[i].hist(hist, bins, color = "#0072B2",
                   width = 0.8, edgecolor = "#0072B2",
                   linewidth = 0.5, zorder = 3,
                   label = infectious_labels[i])
        ax[i].spines["top"].set_visible(False)
        ax[i].spines["right"].set_visible(False)
        ax[i].set_xlabel("")
        ax[i].set_ylabel("")
        ax[i].set_ylim([0, 11000])
        ax[i].set_xlim([0, 15])
        
        ax[i].set_yticks([0, 10000])
        ax[i].set_yticklabels([0, 10000], size = 16)
        
        if i == (n_groups - 1):
            ax[i].set_xticks([0, 5, 10, 15])
            ax[i].set_xticklabels([0, 5, 10, 15], size = 16)
        else: 
            ax[i].set_xticks([])
        
        ax[i].text(0.75, 0.4, "{}".format(infectious_labels[i]),
            ha = 'left', va = 'bottom', transform = ax[i].transAxes, fontsize = 14)

        if i == (n_groups - 1):
            ax[i].set_xlabel("Generation time", fontsize = 20)
        if i ==0:
            ax[i].set_title("", size = 20)

    plt.savefig(output_file)
    plt.close()
