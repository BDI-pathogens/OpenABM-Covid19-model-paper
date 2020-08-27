#!/usr/bin/env python3
"""
Script to create figure S2

Waiting-time distributions
"""

from os.path import join

import pandas as pd, numpy as np
from matplotlib import pyplot as plt

import plotting
from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

if __name__ == "__main__":

    plt.rcParams['figure.figsize'] = [14, 12]
    
    df_parameters_used = pd.read_csv(join("OpenABM-Covid19", "tests", 
        "data", "baseline_parameters.csv"))
    
    fig, ax = plotting.plot_parameter_assumptions(df_parameters_used)

    plt.savefig(join("figures", "figS2_waiting_time_distributions"))
    plt.close()
