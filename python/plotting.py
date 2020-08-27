
import numpy as np, pandas as pd

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import cm


# network_colours = ["#bdbdbd", "#f0f0f0", "#636363"]
network_colours = ["#ffffbf", "#fc8d59", "#91bfdb"]

age_colors_greys = ["#ffffff", "#f0f0f0", "#d9d9d9", "#bdbdbd", 
    "#969696", "#737373", "#525252", "#252525", "#000000"]

#f7fbff
#deebf7
#c6dbef
#9ecae1
#6baed6
#4292c6
#2171b5
#08519c
#08306b

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
    title = "", xlabel = "", ylabel = "", legend_title = "", xticklabels = None):
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
    
    Returns
    -------
    ax : axis handles to the modified ax
    """
    
    if not groups:
        groups = df[groupvar].unique()
    
    if not group_labels:
        group_labels = groups
    
    n_groups = len(groups)
    
    if not isinstance(bins, list):
        if binvar == "age_group":
            bin_list = np.arange(0, bins + 1) - 0.1
        else:
            bin_list = np.arange(bins)
    else:
        bin_list = bins
    
    if group_colours is None:
        group_colours = get_discrete_viridis_colours(n_groups)
    
    width = np.diff(bin_list)[0]/(n_groups + 1)
    
    for i, g in enumerate(groups):
        heights, b = np.histogram(df.loc[df[groupvar] == g][binvar], bin_list, density = density)
        
        ax.bar(bin_list[:-1] + width*i, heights, width = width, facecolor = group_colours[i],
            label = group_labels[i], edgecolor = "#0d1a26", linewidth = 0.5, zorder = 3)
    
    ax.set_xlim(xlimits)
    
    legend = ax.legend(loc = 'best', borderaxespad = 0, frameon = False, 
        prop = {'size': 16}, fontsize = "x-large")
    legend.set_title(legend_title, prop = {'size':18})
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_xlabel(xlabel, size = 18)
    ax.set_ylabel(ylabel, size = 18)
    ax.set_title(title, size = 20)
    
    if xlimits is not None:
        ax.set_xlim(xlimits)
    
    if xticklabels is not None:
        ax.set_xticks(bin_list + n_groups/2*width - width/2.)
        ax.set_xticklabels(xticklabels, size = 14)
    
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    
    return(ax)



def transmission_heatmap_by_age_by_panels(df, 
        group1var, group2var, panelvar, bins = None, 
        groups = None, group_labels = None,
        panels = None, panel_labels = None,
        xlabel = "", ylabel = "",
        legend_title = "", legend_loc = "right",
        xticklabels = None, yticklabels = None,
        normalise = False, title_fontsize = 20,
        spines = False, ncols = None, nrows = None
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
    
    ax[0].set_ylabel(ylabel, size = 16)
    
    transmission_arrays = []
    for i, panel in enumerate(panels):
        
        df_sub = df.loc[df[panelvar] == panel]
        
        array, xbins, ybins = np.histogram2d(
            x = df_sub[group1var].values, 
            y = df_sub[group2var].values, 
            bins = bin_list)
        transmission_arrays.append(array)
    
    vmin_panels = 0
    vmax_panels = np.max(np.array(transmission_arrays))
    
    ims = []

    for i, panel in enumerate(panels):
        im = ax[i].imshow(np.ma.masked_where(transmission_arrays[i] == 0, transmission_arrays[i]), 
            origin = "lower", aspect = "equal", 
            vmin = vmin_panels, vmax = vmax_panels)
        
        ims.append(im)
        ax[i] = adjust_ticks(ax[i], xtick_fontsize = 14, ytick_fontsize = 14, 
            xticklabels = xticklabels, yticklabels = yticklabels)
        
        if i > 0:
            ax[i].set_yticks([])
        
        ax[i].set_xlabel(xlabel, size = 16)
        ax[i].set_title(panel_labels[i], size = title_fontsize)
        
        if not spines:
            ax[i].spines["top"].set_visible(False)
            ax[i].spines["right"].set_visible(False)
            ax[i].spines["bottom"].set_visible(False)
            ax[i].spines["left"].set_visible(False)
    
    fig.subplots_adjust(right = 0.85)
    axes_cbar = fig.add_axes([0.9, 0.3, 0.02, 0.4])
    cbar = fig.colorbar(ims[n_panels - 1], cax = axes_cbar)
    
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
    
    ax, im = add_heatmap_to_axes(ax, df[group1var].values, df[group2var].values, bin_list)
    
    ax = adjust_ticks(ax, xtick_fontsize = 16, ytick_fontsize = 16, 
        xticklabels = xticklabels, yticklabels = yticklabels)
    
    ax.set_xlabel(xlabel, size = 20)
    ax.set_ylabel(ylabel, size = 20)
    ax.set_title(title)
    
    cbar = fig.colorbar(im, fraction = 0.046, pad = 0.04)
    cbar.set_label(legend_title, size = 18)
    cbar.ax.tick_params(labelsize = 14)
    
    return(fig, ax)


def add_heatmap_to_axes(ax, x, y, bin_list):
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
        origin = "lower", aspect = "equal", vmin = 0)
    
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




