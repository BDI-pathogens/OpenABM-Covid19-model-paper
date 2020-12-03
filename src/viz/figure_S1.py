#!/usr/bin/env python3
"""
Age-stratified figures of different states
"""

from os.path import join

import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt

import plotting
from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

age_group_labels = [enum.name[1:].replace("_","-") for enum in AgeGroupEnum]
age_group_labels[-1] = "80+"

if __name__ == "__main__":
    
    transmission_file = sys.argv[1]
    individual_file = sys.argv[2]
    output_dir = sys.argv[3]
    file_format = sys.argv[4]
    
    plt.rcParams["savefig.format"] = file_format
    
    df_trans = pd.read_csv(transmission_file)
    df_indiv = pd.read_csv(individual_file)
    
    ################################################################
    # Proportion of infected/recovered/death within each age group #
    ################################################################
    
    plt.rcParams['figure.figsize'] = [12, 12]
    
    groupvars = ["time_infected", "time_hospitalised", "time_death"]
    labels = ["Infected", "Hospitalisations", "Deaths"]
    n_groups = len(groupvars)
    
    df_indiv_sub = df_indiv.groupby("age_group").size().reset_index(name = "total_popn")
    
    df_trans_sub_infected = df_trans[df_trans["time_infected"] > 0].groupby("age_group_recipient").size().reset_index(name = "total_infected")
    df_trans_sub_hospitalised = df_trans[df_trans["time_hospitalised"] > 0].groupby("age_group_recipient").size().reset_index(name = "total_hospitalised")
    df_trans_sub_death = df_trans[df_trans["time_death"] > 0].groupby("age_group_recipient").size().reset_index(name = "total_death")
    
    df = pd.merge(df_indiv_sub, df_trans_sub_infected, 
        left_on = "age_group", right_on = "age_group_recipient", how = "left")
    df = pd.merge(df, df_trans_sub_hospitalised, 
        left_on = "age_group", right_on = "age_group_recipient", how = "left")
    df = pd.merge(df, df_trans_sub_death, 
        left_on = "age_group", right_on = "age_group_recipient", how = "left")
    
    df = df[["age_group", "total_popn", "total_infected", "total_hospitalised", "total_death"]]
    df = df.replace(np.nan, 0)
    
    df["prop_infected"] = df.total_infected / df.total_popn
    df["prop_hospitalised"] = df.total_hospitalised / df.total_popn
    df["prop_death"] = df.total_death / df.total_popn
    
    bins = np.arange(0, len(AgeGroupEnum) + 1) - 0.1
    plotvars = ["prop_infected", "prop_hospitalised", "prop_death"]
    xticklabels = age_group_labels
    xlabel = "Age group"
    ylims = [0.2, 0.015, 0.008]
    
    fig, ax = plt.subplots(nrows = n_groups)
    for axi, var in enumerate(plotvars):
        
        height = df[var].values
        
        ax[axi].bar(df["age_group"] + 0.4, height = height, width = 0.8,
            alpha = 1.0, color = "#0072B2", edgecolor = "#0d1a26", 
            linewidth = 0.5, zorder = 3)

        # for bi in range(len(bins) - 1):
        #     ax[axi].text(bins[bi] + 0.4, height[bi], str(np.round(height[bi], 3)),
        #         ha = "center", va = "bottom", color = "grey", size = 12)
    
        ax[axi].set_xlim([0, np.max(bins)])
        ax[axi].spines["top"].set_visible(False)
        ax[axi].spines["right"].set_visible(False)
        ax[axi].set_ylim([0, ylims[axi]])
        ax[axi].text(0.02, 0.8, labels[axi], size = 18, 
            ha = 'left', va = 'center', transform = ax[axi].transAxes, color = "black")
        
        if axi == (n_groups - 1):
            if xticklabels is not None:
                ax[axi].set_xticks(bins + 0.425)
                ax[axi].set_xticklabels(xticklabels, size = 12)
            else:
                ax[axi].set_xticks(bins + 0.425)
                ax[axi].set_xticklabels(bins, size = 12)
        else:
            ax[axi].set_xticks(bins + 0.425)
            ax[axi].set_xticks([])
    
    ax[n_groups-1].set_xlabel(xlabel, size = 18)
    
    plt.subplots_adjust(hspace = 0.5)
    
    plt.savefig(join(output_dir, "figS1_I_H_D"))
    plt.close()


    ####################################################################
    # Age distribution of hospitalisations, ICU admissions, and deaths #
    ####################################################################
    
    plt.rcParams['figure.figsize'] = [12, 12]
    groupvars = ["time_hospitalised", "time_critical", "time_death"]
    labels = ["Hospitalisations", "ICU", "Deaths"]

    fig, ax = plotting.plot_hist_by_age(df_trans, groupvars = groupvars, group_labels = labels,
        NBINS = len(AgeGroupEnum), density = True, xticklabels = age_group_labels, 
        xlabel = "Age group", ylim = 0.5, age_group_var = "age_group_recipient")
    
    plt.savefig(join(output_dir, "figS1_H_ICU_D"))
    plt.close()