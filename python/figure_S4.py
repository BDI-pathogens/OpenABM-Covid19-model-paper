#!/usr/bin/env python3
"""
Script to create figure of R through time


Add smoothing ...
Add confidence interval ... sd of mean.
"""

from os.path import join

import pandas as pd, numpy as np
from matplotlib import pyplot as plt
from collections import Counter

from scipy.stats import gamma

import plotting, constants
from COVID19.model import TransmissionTypeEnum


# Import the data output from the model
df_trans = pd.read_csv(join("results", "transmission_Run1.csv"))
df_ts = pd.read_csv(join("results", "covid_timeseries_Run1.csv"))
df_params = pd.read_csv(join("OpenABM-Covid19", "tests", "data", "baseline_parameters.csv"))

# Outbreak-specific outputs
times = df_ts.time.values
end_time = df_ts.time.max()
lockdown_time = np.min(np.where(df_ts.lockdown == True))

infectiontimevar = "time_infected"
plt.rcParams["savefig.format"] = "png"

if __name__ == "__main__":
    
    plt.rcParams['figure.figsize'] = [12, 7]
    
    #############
    # Actual R
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
        label = "R (actual)", 
        lw = 3, 
        c = "#CC79A7")
    
    # This will plot a scatter plot of the offspring distribution at each point in time.  
    # for i, t in enumerate(times[1:]):
    #     ax.scatter([t]*len(actual_R[i]), actual_R[i], alpha = 0.2, c = "blue")
    
    ax.axhline(1, linestyle = "--", c = "grey", alpha = 0.8, lw = 1.5)
    ax.axvline(0, linestyle = "--", c = "grey", alpha = 0.8, lw = 1.5)
    ax.set_ylim([0, 4])
    ax.set_yticks(range(5))
    
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    
    ax.set_xlabel("Simulation time\n(day of lockdown = 0)", fontsize = 12)
    ax.set_ylabel("Reproduction number", fontsize = 12)
    
    
    plt.legend(frameon = False, fontsize = 14)
    plt.savefig(join("figures", "figS4_actual_R"), dpi = 300)
    plt.close()
