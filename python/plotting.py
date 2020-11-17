#!/usr/bin/env python3
"""
Helper functions for plotting
"""

import numpy as np, pandas as pd
from scipy.stats import gamma

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

network_colours = ["#D55E00", "#56B4E9", "#009E73"]

# Nicely printed labels of event types from the EVENT_TYPES enum 
# as defined in OpenABM-Covid19/src/constant.h
EVENT_TYPE_STRING = {
    0: "Susceptible",
    1: "Presymptomatic (severe)",
    2: "Presymptomatic (mild)",
    3: "Asymptomatic",
    4: "Symptomatic (severe)",
    5: "Symptomatic (mild)",
    6: "Hospitalised",
    7: "ICU", 
    8: "Recovering in hospital",
    9: "Recovered",
    10: "Dead",
    11: "Quarantined", 
    12: "Quarantined release",
    13: "Test taken", 
    14: "Test result",
    15: "Case", 
    16: "Trace token release",
    17: "Transition to hospital",
    18: "Transition to critical",
    19: "N event types"
}


def gamma_params(mn, sd):
    """
    Return scale and shape parameters from a Gamma distribution from input mean and sd
    
    Arguments
    ---------
    mn : float
        Mean of the gamma distribution
    sd : float
        Standard deviation of the gamma distribution
    """
    scale = (sd**2)/mn
    shape = mn/scale
    
    return(shape, scale)


def overlapping_bins(start, stop, window, by):
    """Generate overlapping bins"""
    
    bins = []
    for i in np.arange(start, stop - window + 1, step = by):
        bins.append((i, i + window))
    return(bins)


def get_discrete_viridis_colours(n):
    """
    Generate n colours from the viridis colour map
    
    Arguments
    ---------
    n : int
        Number of colours to generate on the viridis colour map
    
    Returns
    -------
    List of length n where each elements is an RGBA list defining a colour
    """
    colourmap = cm.get_cmap('viridis', n)
    colours = [colourmap.colors[n - i - 1] for i in range(n)]
    return(colours)


def plot_hist_by_group(ax, df, groupvar, binvar, bins = None, groups = None, 
    group_labels = None, group_colours = None, xlimits = None, density = False, 
    title = "", xlabel = "", ylabel = "", legend_title = "", xticklabels = None, 
    normalising_constant = None):
    """
    Histogram with multiple groups, with histogram bars plotted side-by-side for each group
    
    Arguments
    ---------
    ax : 
        axis handle to the axis to have the plot added
    df : pandas.DataFrame
        DataFrame of model output
    groupvar : str
        Column name of `df` which stores the grouping variable
    binvar : str
        Column name of `df` over which values will be binned 
    bin : int or list
        Either a number of bins or list of bins to use
    groups : list
        Subset of categories in `group` column to plot (defaults to unique values in `groupvar` col)
    group_labels : list
        Labels to use for `groups` categories (defaults to `groups` list)
    group_colours : list
        Colours to use for the different `groups` categories (defaults to using the viridis 
        colour map with n_groups)
    xlimits : float
        Limit of the x-axis
    density : boolean
        Should histogram be normalised (passed to density arg in np.histogram)
    title, xlabel, ylabel, legend_title : str
        Title, X-axis label, Y-axis label, and legend title respectively
     xticklabels : list of str
        Labels to use for x-ticks
    normalising_constant: float
        Normalising constant (in case plotting by fraction of population is required)
    
    Returns
    -------
    ax : axis handles to the modified ax
    """
    
    if not groups:
        groups = df[groupvar].unique()
    
    if not group_labels:
        group_labels = groups
    
    n_groups = len(groups)
    
    width = np.diff(bins)[0]/(n_groups + 1)
    
    for i, g in enumerate(groups):
        heights, b = np.histogram(df.loc[df[groupvar] == g][binvar], bins, density = density)
        
        if normalising_constant:
            heights = heights/float(normalising_constant)
        
        ax.bar(bins[:-1] + width*i, heights, width = width, facecolor = group_colours[i],
            label = group_labels[i], edgecolor = group_colours[i], linewidth = 0.5, zorder = 3)
    
    ax.set_xlim(xlimits)
    
    legend = ax.legend(loc = 'best', borderaxespad = 0, frameon = False, 
        prop = {'size': 12}, fontsize = "large")
    legend.set_title(legend_title, prop = {'size':14})
    
    remove_spines(ax, ["top", "right"])
    
    ax.set_xlabel(xlabel, size = 18)
    ax.set_ylabel(ylabel, size = 18)
    ax.set_title(title, size = 20)
    
    #ax.set_yticks([0, 150000, 300000])
    
    if xlimits is not None:
        ax.set_xlim(xlimits)
    
    if xticklabels is not None:
        ax.set_xticks([0, 10, 20, 30])
    
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(10)
    
    return(ax)



def transmission_heatmap_by_age_by_panels(df, 
        group1var, group2var, panelvar, bins = None, 
        groups = None, group_labels = None,
        panels = None, panel_labels = None,
        xlabel = "", ylabel = "",
        legend_title = "", legend_loc = "right",
        xticklabels = None, yticklabels = None,
        normalise = False, title_fontsize = 20,
        spines = False, ncols = None, nrows = None, 
        vmin_panels = None, vmax_panels = None
    ):
    """
    Plot subplots of heatmaps of transmissions from one age group to another across another 
    categorical variable (panelvar)
    
    Arguments
    ---------
    group1var : str
        Column name of first grouping variable (x-axis in heatmap)
    group2var : str
        Column name of second grouping variable (x-axis in heatmap)
    panelvar
        Column name of variable for making panels
    NBINS
        Number of bins
    group_labels
    normalise
    
    """
    
    if not isinstance(bins, list):
        bin_list = np.arange(bins)
    
    if not panels: 
        panels = np.unique(df[panelvar])
    
    n_panels = len(panels)
    
    if not panel_labels:
        panel_labels = panels
    
    if not ncols:
        ncols = n_panels
        nrows = 1
    
    fig, ax = plt.subplots(ncols = ncols, nrows = nrows)
    
    ax[0][0].set_ylabel(ylabel, size = 16)
    ax[1][0].set_ylabel(ylabel, size = 16)
    
    transmission_arrays = []
    for i, panel in enumerate(panels):
        
        df_sub = df.loc[df[panelvar] == panel]
        
        array, xbins, ybins = np.histogram2d(
            x = df_sub[group1var].values, 
            y = df_sub[group2var].values, 
            bins = bin_list)
        transmission_arrays.append(array)
    
    if not vmin_panels:
        vmin_panels = 1
    if not vmax_panels:
        vmax_panels = np.max(np.array(transmission_arrays))
    
    ims = []
    
    for i, (panel, axi) in enumerate(zip(panels, ax.reshape(-1))):
        im = axi.imshow(np.ma.masked_where(transmission_arrays[i] == 0, transmission_arrays[i]), 
            origin = "lower", aspect = "equal", 
            vmin = vmin_panels, vmax = vmax_panels)
        
        ims.append(im)
        axi = adjust_ticks(axi, xtick_fontsize = 14, ytick_fontsize = 14, 
            xticklabels = xticklabels, yticklabels = yticklabels)
        
        if i > 0:
            axi.set_yticks([])
        
        axi.set_xlabel(xlabel, size = 16)
        axi.set_title(panel_labels[i], size = title_fontsize)
        
        if not spines:
            remove_spines(axi)
    
    # Start ticks from 1 (0 is shown in white)
    cbar_ticks = np.arange(200, 1600, 200)
    cbar_ticks = np.insert(cbar_ticks, 0, 1)
    
    remove_spines(ax[1,2])
    ax[1,2].set_xticks([]); ax[1,2].set_yticks([])
    
    cbaxes = inset_axes(ax[1, 2], width = "10%", height = "75%", loc = "lower left", 
        bbox_to_anchor = (0.35, 0.1, 1, 1), bbox_transform = ax[1, 2].transAxes)
    
    cbar = fig.colorbar(ims[n_panels - 1], ticks = cbar_ticks, cax = cbaxes, shrink = 0.6)
    cbar.set_label(legend_title, size = 18)
    
    return(fig, ax)


def plot_transmission_heatmap_by_age(df, group1var, group2var, bins = None, 
    group_labels = None, xlabel = "", ylabel = "", title = "", legend_title = "", 
    legend_loc = "right", xticklabels = None, yticklabels = None, normalise = False, 
    vmin = 0, vmax = None):
    """
    Plot 2D histogram (as a heatmap) of transmission events by two grouping variables
    (for instance, age group)
    
    
    Returns
    -------
    fig, ax : figure and axis handles to the generated figure using matplotlib.pyplot
    
    """
    if not isinstance(bins, list):
        bin_list = np.arange(bins)
    
    fig, ax = plt.subplots()
    
    ax, im = add_heatmap_to_axes(ax, df[group1var].values, df[group2var].values, bin_list, 
        vmin = vmin, vmax = vmax)
    
    ax = adjust_ticks(ax, xtick_fontsize = 16, ytick_fontsize = 16, 
        xticklabels = xticklabels, yticklabels = yticklabels)
    
    ax.set_xlabel(xlabel, size = 20)
    ax.set_ylabel(ylabel, size = 20)
    ax.set_title(title)
    
    cbar = fig.colorbar(im, fraction = 0.046, pad = 0.04)
    cbar.set_label(legend_title, size = 18)
    cbar.ax.tick_params(labelsize = 14)
    
    return(fig, ax)



def ifr_hist_by_age(df, 
        numerator_var, denominator_var,
        age_group_var = "age_group",
        NBINS = None,
        group_labels = None,
        xlabel = "",
        ylabel = "Infection fatality ratio (IFR)",
        xticklabels = None,
        density = False,
    ):
    """
    Plot IFR by age
    """
    
    bins = np.arange(0, NBINS + 1) - 0.5
    
    fig, ax = plt.subplots()
    
    height_n, bins_n = np.histogram(df[df[numerator_var] > 0][age_group_var], 
        bins, density = False)
    height_d, bins_d = np.histogram(df[df[denominator_var] > 0][age_group_var], 
        bins, density = False)
    
    heights = np.divide(height_n, height_d)
    
    bar_width = 0.8
    ax.bar(bins[:-1], heights, align = "center", color = "#0072B2", 
        edgecolor = "#0d1a26", linewidth = 0.5, zorder = 3, width = bar_width)
    
    remove_spines(ax, ["top", "right"])
    
    if xticklabels is not None:
        ax.set_xticks(bins[:-1])
        ax.set_xticklabels(xticklabels, size = 16)
    
    ax.set_yticks([0.0, 0.02, 0.04, 0.06, 0.08, 0.1])
    ax.set_yticklabels([0.0, 0.02, 0.04, 0.06, 0.08, 0.1], size = 16)
    
    ax.set_xlim([-1, np.max(bins)])
    ax.set_ylim([0, np.max(heights)*1.1])
    
    ax.set_xlabel(xlabel, size = 18)
    ax.set_ylabel(ylabel, size = 18)
    
    return(fig, ax)


def plot_parameter_assumptions(df_parameters, xlimits = [0, 30], lw = 3):
    """
    Plot distributions of mean transition times between compartments in the parameters of the 
    OpenABM-Covid19 model
    
    Arguments
    ---------
    df_parameters : pandas.DataFrame
        DataFrame of parameter values as input first input argument to the OpenABM-Covid19 model
        This plotting scripts expects the following columns within this dataframe: 
            mean_time_to_hospital
            mean_time_to_critical, sd_time_to_critical
            mean_time_to_symptoms, sd_time_to_symptoms
            mean_infectious_period, sd_infectious_period
            mean_time_to_recover, sd_time_to_recover
            mean_asymptomatic_to_recovery, sd_asymptomatic_to_recovery
            mean_time_hospitalised_recovery, sd_time_hospitalised_recovery
            mean_time_to_death, sd_time_to_death
            mean_time_critical_survive, sd_time_critical_survive
    
    xlimits : list of ints
        Limits of x axis of gamma distributions showing mean transition times
    lw : float
        Line width used in plotting lines of the PDFs
    
    Returns
    -------
    fig, ax : figure and axis handles to the generated figure using matplotlib.pyplot
    """
    df = df_parameters # for brevity
    x = np.linspace(xlimits[0], xlimits[1], num = 50)
    
    fig, ax = plt.subplots(nrows = 3, ncols = 3)
    
    ####################################
    # Bernoulli of mean time to hospital
    ####################################
    
    height1 = np.ceil(df.mean_time_to_hospital.values[0]) - df.mean_time_to_hospital.values[0]
    height2 = df.mean_time_to_hospital.values[0] - np.floor(df.mean_time_to_hospital.values[0])
    
    x1 = np.floor(df.mean_time_to_hospital.values[0])
    x2 = np.ceil(df.mean_time_to_hospital.values[0])
    ax[0,0].bar([x1, x2], [height1, height2], color = "#0072B2")
    
    ax[0,0].set_ylim([0, 1.0])
    ax[0,0].set_xticks([x1, x2])
    ax[0,0].set_xlabel("Time to hospital\n(from symptoms; days)")
    ax[0,0].set_ylabel("Density")
    ax[0,0].set_title("")
    remove_spines(ax[0,0], ["top", "right"])
    
    ####################################
    # Gamma of mean time to critical
    ####################################
    
    a, b = gamma_params(df.mean_time_to_critical.values, df.sd_time_to_critical.values)
    ax[1,0].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, color = "#0072B2")
    ax[1,0].axvline(df.mean_time_to_critical.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[1,0].set_xlabel("Time to critical\n(from hospitalised; days)")
    ax[1,0].set_title("")
    remove_spines(ax[1,0], ["top", "right"])
    ax[1,0].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_time_to_critical.values[0],
        df.sd_time_to_critical.values[0]), 
        ha = 'right', va = 'center', transform = ax[1,0].transAxes)
    
    
    ################################
    # Gamma of mean time to symptoms
    ################################
    
    a, b = gamma_params(df.mean_time_to_symptoms.values, df.sd_time_to_symptoms.values)
    ax[0,1].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, color = "#0072B2")
    ax[0,1].axvline(df.mean_time_to_symptoms.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[0,1].set_xlabel("Time to symptoms\n(from presymptomatic; days)")
    ax[0,1].set_title("")
    remove_spines(ax[0, 1], ["top", "right"])
    ax[0,1].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_time_to_symptoms.values[0],
        df.sd_time_to_symptoms.values[0]), 
        ha = 'right', va = 'center', transform = ax[0,1].transAxes)
    
    ################################
    # Gamma of mean infectious period
    ################################
    
    a, b = gamma_params(df.mean_infectious_period, df.sd_infectious_period)
    ax[0,2].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, color = "#0072B2")
    ax[0,2].axvline(df.mean_infectious_period.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[0,2].set_xlabel("Infectious period (days)")
    ax[0,2].set_title("")
    remove_spines(ax[0, 2], ["top", "right"])
    ax[0,2].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_infectious_period.values[0],
        df.sd_infectious_period.values[0]), 
        ha = 'right', va = 'center', transform = ax[0,2].transAxes)
    
    ################################
    # Gamma of mean time to recover
    ################################
    
    a, b = gamma_params(df.mean_time_to_recover, df.sd_time_to_recover)
    ax[1,1].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, color = "#0072B2")
    ax[1,1].axvline(df.mean_time_to_recover.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[1,1].set_xlabel("Time to recover\n(from hospitalised or critical; days)")
    ax[1,1].set_title("")
    remove_spines(ax[1, 1], ["top", "right"])
    ax[1,1].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_time_to_recover.values[0],
        df.sd_time_to_recover.values[0]), 
        ha = 'right', va = 'center', transform = ax[1,1].transAxes)
    
    ########################################
    # Gamma of mean asymptomatic to recovery
    ########################################
    
    a, b = gamma_params(df.mean_asymptomatic_to_recovery, df.sd_asymptomatic_to_recovery)
    ax[2,0].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, color = "#0072B2")
    ax[2,0].axvline(df.mean_asymptomatic_to_recovery.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[2,0].set_xlabel("Time to recover\n(from asymptomatic; days)")
    ax[2,0].set_title("")
    remove_spines(ax[2, 0], ["top", "right"])
    ax[2,0].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_asymptomatic_to_recovery.values[0],
        df.sd_asymptomatic_to_recovery.values[0]), 
        ha = 'right', va = 'center', transform = ax[2,0].transAxes)
    
    ########################################
    # Gamma of mean hospitalised to recovery
    ########################################
    
    a, b = gamma_params(df.mean_time_hospitalised_recovery, df.sd_time_hospitalised_recovery)
    ax[2,1].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, color = "#0072B2")
    ax[2,1].axvline(df.mean_time_hospitalised_recovery.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[2,1].set_xlabel("Time to recover\n(from hospitalisation to hospital discharge if not ICU\nor from ICU discharge to hospital discharge if ICU; days)")
    ax[2,1].set_title("")
    remove_spines(ax[2, 1], ["top", "right"])
    ax[2,1].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_time_hospitalised_recovery.values[0],
        df.sd_time_hospitalised_recovery.values[0]), 
        ha = 'right', va = 'center', transform = ax[2,1].transAxes)
    
    #############################
    # Gamma of mean time to death
    #############################
    
    a, b = gamma_params(df.mean_time_to_death.values, df.sd_time_to_death.values)
    ax[1,2].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, c = "#0072B2")
    ax[1,2].axvline(df.mean_time_to_death.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[1,2].set_xlabel("Time to death\n(from critical; days)")
    ax[1,2].set_title("")
    remove_spines(ax[1, 2], ["top", "right"])
    ax[1,2].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_time_to_death.values[0],
        df.sd_time_to_death.values[0]), 
        ha = 'right', va = 'center', transform = ax[1,2].transAxes)
    
    ########################################
    # Gamma of mean time to survive if critical: FIXME - definitions
    ########################################
    
    a, b = gamma_params(df.mean_time_critical_survive, df.sd_time_critical_survive)
    ax[2,2].plot(x, gamma.pdf(x, a = a, loc = 0, scale = b), linewidth= lw, color = "#0072B2")
    ax[2,2].axvline(df.mean_time_critical_survive.values, color = "#D55E00", 
        linestyle = "dashed", alpha = 0.7)
    ax[2,2].set_xlabel("Time to survive\n(if ICU; days)")
    ax[2,2].set_title("")
    remove_spines(ax[2, 2], ["top", "right"])
    ax[2,2].text(0.9, 0.7, 'mean: {}\nsd: {}'.format(df.mean_time_critical_survive.values[0],
        df.sd_time_critical_survive.values[0]), 
        ha = 'right', va = 'center', transform = ax[2,2].transAxes)
    
    plt.subplots_adjust(hspace = 0.5)
    
    return(fig, ax)


def PlotHistByAge(df, 
        groupvars, 
        age_group_var = "age_group",
        NBINS = None,
        group_labels = None,
        xlabel = "",
        xticklabels = None,
        density = False,
        ylim = 0.5
    ):
    """
    
    """
    
    a = 1.0
    bins = np.arange(0, NBINS + 1) - 0.1
    
    # Define number of groups
    n_groups = len(groupvars)
    
    if group_labels is None:
        group_labels = groupvars
    
    fig, ax = plt.subplots(nrows = n_groups)
    
    for axi, var in enumerate(groupvars):
        height, bins, objs = ax[axi].hist(df[df[var] > 0][age_group_var], bins, width = 0.8, 
            alpha = a, color = "#0072B2", edgecolor = "#0d1a26", linewidth = 0.5, 
            zorder = 3, density = density)
        
        for bi in range(len(bins) - 1):
            ax[axi].text(bins[bi] + 0.425, height[bi], str(np.round(height[bi], 2)), 
                ha = "center", va = "bottom", color = "grey", size = 12)
        
        ax[axi].set_xlim([0, np.max(bins)])
        remove_spines(ax[axi], ["top", "right"])
        
        ax[axi].set_ylim([0, ylim])
        ax[axi].text(0.02, 0.8, group_labels[axi], size = 18, 
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
    
    return(fig, ax)


######################
# Plotting utilities
# -------------------


def remove_spines(ax, locations = ["top", "right", "bottom", "left"]):
    for loc in locations:
        ax.spines[loc].set_visible(False)



def add_heatmap_to_axes(ax, x, y, bin_list, vmin, vmax):
    """
    Plot heatmap of 2D histogram.
    
    Used for 2D histograms of transmission events across two grouping variables (e.g. age)
    
    Arguments
    ---------
    ax : object of matplotlib class `Axes`
        Axis object of where to add a heatmap
    x : np.array
        Array of the x values with which to create a histogram
    y : np.array
        Array of the y values with which to create a histogram
    bin_list : list
        List of bins to use in the histogram
    
    Returns
    -------
    (ax, im)
    ax : object of matplotlib class `Axes`
        updated Axes object
    im : matplotlib.image.AxesImage
        AxesImage object returned from matplotlib.pyplot.imshow
    """
    
    array, xbins, ybins = np.histogram2d(x, y, bin_list)
    
    im = ax.imshow(np.ma.masked_where(array == 0, array), 
        origin = "lower", aspect = "equal", vmin = vmin, vmax = vmax)
    
    return(ax, im)


def adjust_ticks(ax, xtick_fontsize = 12, ytick_fontsize = 12, 
    xticklabels = None, yticklabels = None):
    """
    Adjust tick font size and ticklabels in a matplotlib.Axes object
    
    Arguments
    ---------
    ax : object of matplotlib class `Axes`
        Axis object of where to adjust tick fonts/labels
    xtick_fontsize, ytick_fontsize : int
        Font size of x-ticks and y-ticks
    xticklabels, yticklabels : list of str
        List of x and y axis tick labels to change
    
    Returns
    -------
    ax : object of matplotlib class `Axes`
        Returns the modified axis object
    """
    
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(xtick_fontsize)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(ytick_fontsize)
    
    if xticklabels is not None:
        ax.set_xticks(np.arange(len(xticklabels)))
        ax.set_xticklabels(xticklabels, rotation = 60)
    
    if yticklabels is not None:
        ax.set_yticks(np.arange(len(yticklabels)))
        ax.set_yticklabels(yticklabels)
    
    return(ax)
