#!/usr/bin/env python3
"""
Script to create figure 6

Overall IFR, stratified by age

"""

from os.path import join

import pandas as pd, numpy as np
from matplotlib import pyplot as plt

import plotting
from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

n_age = len(AgeGroupEnum) + 1
age_group_labels = [enum.name[1:].replace("_","-") for enum in AgeGroupEnum]
age_group_labels[-1] = "80+"

if __name__ == "__main__":

    plt.rcParams['figure.figsize'] = [12, 8]
    
    df_trans = pd.read_csv(join("results", "transmission_Run1.csv"))
    
    fig, ax = plotting.PlotHistIFRByAge(df_trans, "time_death", "time_infected", NBINS = n_age - 1, 
        xticklabels = age_group_labels, xlabel = "Age group", age_group_var = "age_group_recipient")
    
    plt.savefig(join("figures", "fig6_ifr"))
    plt.close()

