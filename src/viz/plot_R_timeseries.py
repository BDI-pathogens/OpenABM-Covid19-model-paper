#!/usr/bin/env python3
"""
Calculate and plot R through time
"""

from os.path import join

import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt
from collections import Counter

from scipy.stats import gamma

import plotting, constants
from COVID19.model import TransmissionTypeEnum

if __name__ == "__main__":
    
    transmission_file = sys.argv[1]
    timeseries_file = sys.argv[2]
    baseline_parameters_file = sys.argv[3]
    output_file = sys.argv[4]
    file_format = sys.argv[5]
    
    # Import the data output from the model
    df_trans = pd.read_csv(transmission_file)
    df_ts = pd.read_csv(timeseries_file)
    df_params = pd.read_csv(baseline_parameters_file)
    
    # Outbreak-specific outputs
    times = df_ts.time.values
    end_time = df_ts.time.max()
    lockdown_time = np.min(np.where(df_ts.lockdown == True))
    intervention_time = np.min(np.where(df_ts.total_infected/1E6 >= 0.005))

    infectiontimevar = "time_infected"
    
    plt.rcParams["savefig.format"] = file_format
    plt.rcParams['figure.figsize'] = [12, 8]
    
    #############
    # Actual R (R from transmission file)
    # --------
    # At each time point, calculate the number of future infections for each individual
    # that is infected at the time point in question
    
    # Change seed cases to be nan values for ID_source
    df_trans.loc[df_trans.ID_source == df_trans.ID_recipient, "ID_source"] = np.nan
    
    # Total offspring for each source
    offspring = Counter(df_trans.ID_source)
    
    actual_R = []
    for t in times:
        # Find individuals who were infected precisely at the time point in question.  
        condition = df_trans[infectiontimevar] == t
        
        # Count number of recipients in the future for each currently infected individual
        offspring_values = [offspring[i] for i in df_trans[ condition ].ID_recipient.values]
        actual_R.append(offspring_values)
    
    actual_R_means = [np.mean(np.array(R)) for R in actual_R if (len(R) > 0)]
    
    fig, ax = plt.subplots()
    
    ax.plot(times[1:] - lockdown_time, actual_R_means, 
        label = "$R_{actual}$", 
        lw = 3, alpha = 0.8,
        c = "#CC79A7")
    
    # This will plot a scatter plot of the offspring distribution at each point in time.  
    # for i, t in enumerate(times[1:]):
    #     ax.scatter([t]*len(actual_R[i]), actual_R[i], alpha = 0.2, c = "blue")
    
    ax.axhline(1, linestyle = "--", c = "grey", alpha = 0.8, lw = 1.5)
    ax.axvline(0, linestyle = "--", c = "grey", alpha = 0.8, lw = 1.5)
    ax.axvline(intervention_time - lockdown_time, 
        linestyle = "--", c = "grey", alpha = 0.8, lw = 1.5)
    
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    
    ax.set_xlabel("Simulation time\n(lockdown on day 0; self-isolation on symptoms on day " + \
        str(intervention_time - lockdown_time) + ")", fontsize = 16)
    ax.set_ylabel("Reproduction number", fontsize = 16)
    
    ax.set_ylim([0, 6])
    ax.set_yticks(range(7))
    
    #############
    # R from timeseries data
    # --------------------

    # Calculate parameters for gamma distribution of infectious period
    a, b = plotting.gamma_params(
        df_params["mean_infectious_period"],
        df_params["sd_infectious_period"])

    # Container for R
    R = []
    
    # Calculate daily incidence (seed cases as first element)
    daily_incidence = df_ts.total_infected.diff(1)
    daily_incidence[0] = df_ts.total_infected.values[0]
    
    # Loop over days of simulation
    for t in times[:-1]:
        I_t = daily_incidence[t]
        
        # Loop "back" through time
        G = 0
        for k in np.arange(1, t + 1):
            G += (gamma.cdf(k, a, loc = 0, scale = b) - \
                gamma.cdf(k - 1, a, loc = 0, scale = b)) * (daily_incidence[t - k])
        
        R.append(I_t / G)
    
    ax.plot(times[1:] - lockdown_time, R,
        label = "$R_{instantaneous}$", lw = 3, alpha = 0.8, c = "#0072B2")
    
    plt.legend(frameon = False, fontsize = 20)
    plt.savefig(output_file, dpi = 300)
    plt.close()
