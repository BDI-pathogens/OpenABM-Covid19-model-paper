#!/usr/bin/env python3
"""
Script to create subfigures for figure 2
"""

from os.path import join

import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt

import plotting, constants
from COVID19.model import TransmissionTypeEnum

NBINS = 30
bin_edges = 0.5 + np.arange(NBINS + 1)

plt.rcParams["savefig.format"] = "png"

if __name__ == "__main__":
    
    interaction_file = sys.argv[1]
    individual_file = sys.argv[2]
    output_dir = sys.argv[3]
    
    # Import the data output from the model
    df_interact = pd.read_csv(interaction_file)
    df_indiv = pd.read_csv(individual_file)
    
    # Find population size
    n_total = df_indiv.shape[0]
    
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
        xlimits = [-0.5, 30], 
        xlabel = "", 
        title = "", 
        legend_title = "Network", 
        xticklabels = [],
        normalising_constant = n_total)
    
    plt.savefig(join(output_dir, "fig2a_daily_interactions_by_network.png"))
    plt.close()
    
    
    #############
    # Figure 2B
    # ---------
    # Number of daily interactions by age
    #####################################
    
    plt.rcParams['figure.figsize'] = [6, 12]
    fig, ax = plt.subplots(nrows = constants.n_age_groups)
    
    df_agg = df_interact.groupby(["ID_1", "age_group_1"]).size().reset_index(name = "counts")
    
    for i, age in enumerate(constants.age_group_labels):
        
        # Split by age group
        hist = df_agg.loc[df_agg["age_group_1"] == i].counts
        
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
        ax[i].set_xlim([-0.5, 30])
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
            ha = 'left', va = 'bottom', 
            transform = ax[i].transAxes, fontsize = 16)
    
    plt.savefig(join(output_dir, "fig2b_daily_interactions_by_age.png"))
    plt.close()
    
    #####################
    # Figures 2C, 2D, 2E
    # ------------------
    # Interaction matrix by network and age
    ########################################
    
    plt.rcParams['figure.figsize'] = [14, 12]
    
    vmaxes = [1000000, 120000, 120000]
    
    indices = ["c", "d", "e"]
    networks = ["occupation", "household", "random"]
    
    for i, (index, network) in enumerate(zip(indices, networks)):
        
        interaction_types_sub = [c.value for c in TransmissionTypeEnum if c.name in ["_" + network]]
        interaction_labels_sub = [c.name[1:].title() for c in TransmissionTypeEnum if c.name in ["_" + network]]
        
        df_interact_sub = df_interact.loc[df_interact["type"].isin(interaction_types_sub)]
        
        plotting.plot_transmission_heatmap_by_age(
            df_interact_sub, "age_group_1", "age_group_2", 
            bins = constants.n_age, 
            xlabel = "Age of individual 1", 
            ylabel = "Age of individual 2", 
            legend_title = "Number of\ntransmission events",
            xticklabels = constants.age_group_labels, 
            yticklabels = constants.age_group_labels, 
            vmax = vmaxes[i])
        
        plt.savefig(join(output_dir, "fig2{}_transmission_matrix_{}.png".format(index, network)))
        plt.close()
