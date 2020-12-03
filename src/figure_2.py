#!/usr/bin/env python3
"""
Script to create subfigures for figure 2
"""

from os.path import join

import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt

import plotting, constants
from COVID19.model import TransmissionTypeEnum, AgeGroupEnum

NBINS = 30
bin_edges = np.arange(NBINS + 1) - 0.5

if __name__ == "__main__":
    
    interaction_file = sys.argv[1]
    individual_file = sys.argv[2]
    output_dir = sys.argv[3]
    file_format = sys.argv[4]
    
    plt.rcParams["savefig.format"] = file_format
    
    # Import the data output from the model
    df_interact = pd.read_csv(interaction_file)
    df_indiv = pd.read_csv(individual_file)
    
    # Find population size
    n_total = df_indiv.shape[0]
    
    # Convert network type to categorical so that zero counts are calculated
    df_interact["ID_1"] = pd.Categorical(df_interact.ID_1, categories = df_indiv.ID)
    df_interact["ID_2"] = pd.Categorical(df_interact.ID_2, categories = df_indiv.ID)
    df_interact["type"] = pd.Categorical(df_interact["type"])
    #df_interact["age_group_1"] = pd.Categorical(df_interact.age_group_1)
    #df_interact["age_group_2"] = pd.Categorical(df_interact.age_group_2)
    
    plt.rcParams['figure.figsize'] = [6, 4]
    
    #############
    # Figure 2A 
    # ---------
    # Histogram of number of daily interactions per person by network
    #################################################################
    
    # Count interactions for each individual by "type" of interaction
    df_agg = df_interact.groupby(["ID_1", "type"]).size().reset_index(name = "counts")
    
    fig, ax = plt.subplots()
    plotting.plot_hist_by_group(ax, df_agg, 
        groupvar = "type", 
        binvar = "counts", 
        groups = constants.interaction_types, 
        bins = bin_edges, 
        group_colours = plotting.network_colours, 
        group_labels = constants.interaction_labels, 
        xlimits = [-1, 30], 
        xlabel = "", 
        title = "", 
        legend_title = "Network", 
        xticklabels = [],
        normalising_constant = n_total/100)
    
    plt.savefig(join(output_dir, "fig2a_daily_interactions_by_network"))
    plt.close()
    
    
    #############
    # Figure 2B
    # ---------
    # Number of daily interactions by age
    #####################################
    
    plt.rcParams['figure.figsize'] = [6, 12]
    fig, ax = plt.subplots(nrows = constants.n_age_groups)
    
    #df_agg = df_interact.groupby(["ID_1", "age_group_1"]).size().reset_index(name = "counts")
    
    for i, age in enumerate(constants.age_group_labels):
        
        df_age = df_interact.loc[df_interact.age_group_1 == i]
        df_age["ID_1"] = pd.Categorical(df_age["ID_1"], 
             categories = df_indiv.loc[df_indiv["age_group"] == i].ID)
        
        hist = df_age.groupby(["ID_1"]).size().reset_index(name = "counts").counts
        
        # Split by age group
        #hist = df_agg.loc[df_agg["age_group_1"] == i].counts
        
        heights, bin_edges = np.histogram(hist, bin_edges)
        
        ax[i].bar(
            x = bin_edges[1:] - 0.5, 
            height = 100*heights/n_total, 
            label = constants.age_group_labels[i], 
            color = "#0072B2", 
            edgecolor = "#0072B2", 
            linewidth = 0.5, 
            zorder = 3, 
            width = 0.8)
        
        ax[i].spines["top"].set_visible(False)
        ax[i].spines["right"].set_visible(False)
        ax[i].set_ylabel("")
        ax[i].set_xlim([-1, 30])
        ax[i].set_ylim([0, 1.5])
        ax[i].set_yticks([0, 1.5])
        
        if i == (constants.n_age_groups - 1):
            ax[i].set_xlabel("", fontsize = 14)
            ax[i].set_xticks([0, 10, 20, 30])
            ax[i].set_xticklabels([0, 10, 20, 30], size = 14)
        else:
            ax[i].set_xlabel("")
            ax[i].set_xticklabels([])
    
        ax[i].text(0.75, 0.4, "{}".format(constants.age_group_labels[i]),
            ha = 'left', va = 'bottom', transform = ax[i].transAxes, fontsize = 16)
    
    plt.savefig(join(output_dir, "fig2b_daily_interactions_by_age"))
    plt.close()
    
    #####################
    # Figures 2C, 2D, 2E
    # ------------------
    # Interaction matrix by network and age
    ########################################
    
    plt.rcParams['figure.figsize'] = [14, 12]
    
    vmaxes = [1000000, 120000, 120000]
    
    # Tick labels for colourbar
    cbar_incr = [200000, 20000, 20000]
    cbar_ticks = [np.arange(incr, vmax + incr, incr) for incr, vmax in zip(cbar_incr, vmaxes)]
    cbar_ticks = [np.insert(c, 0, 1) for c in cbar_ticks]
    
    indices = ["c", "d", "e"]
    networks = ["occupation", "household", "random"]
    
    for i, (index, network) in enumerate(zip(indices, networks)):
        
        interaction_types_sub = [c.value for c in TransmissionTypeEnum \
                                                    if c.name in ["_" + network]]
        interaction_labels_sub = [c.name[1:].title() for c in TransmissionTypeEnum \
                                                    if c.name in ["_" + network]]
        
        df_interact_sub = df_interact.loc[df_interact["type"].isin(interaction_types_sub)]
        
        plotting.plot_transmission_heatmap_by_age(
            df_interact_sub, "age_group_1", "age_group_2", 
            bins = len(AgeGroupEnum), 
            xlabel = "Age of individual 1", 
            ylabel = "Age of individual 2", 
            legend_title = "Number of\ntransmission events",
            xticklabels = constants.age_group_labels, 
            yticklabels = constants.age_group_labels, 
            cbar_ticks = cbar_ticks[i], 
            vmax = vmaxes[i], vmin = 1)
        
        plt.savefig(join(output_dir, "fig2{}_transmission_matrix_{}".format(index, network)))
        plt.close()
