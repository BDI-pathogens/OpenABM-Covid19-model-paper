#!/usr/bin/env python3
"""
Figure of waiting-time distributions
"""

import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt

import plotting

if __name__ == "__main__":
    
    input_parameter_file = sys.argv[1]
    output_file = sys.argv[2]
    file_format = sys.argv[3]
    
    plt.rcParams["savefig.format"] = file_format
    plt.rcParams['figure.figsize'] = [14, 12]
    
    df_parameters_used = pd.read_csv(input_parameter_file)
    
    fig, ax = plotting.plot_parameter_assumptions(df_parameters_used)

    plt.savefig(output_file)
    plt.close()
