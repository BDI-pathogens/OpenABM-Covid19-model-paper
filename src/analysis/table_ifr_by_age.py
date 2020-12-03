#!/usr/bin/env python3
"""
Table of infection fatality ratio (IFR) stratified by age
"""

from os.path import join

import pandas as pd, numpy as np, sys
from matplotlib import pyplot as plt

from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

n_age = len(AgeGroupEnum)
age_group_labels = [enum.name[1:].replace("_","-") for enum in AgeGroupEnum]
age_group_labels[-1] = "80+"

if __name__ == "__main__":
    numerator_var = "time_death"
    denominator_var = "time_infected"
    age_group_var = "age_group_recipient"
    
    transmission_file = sys.argv[1]
    output_table = sys.argv[2]
    
    df_trans = pd.read_csv(transmission_file)
    
    bins = np.arange(0, n_age + 1) - 0.5
    
    height_n, bins_n = np.histogram(df_trans[df_trans[numerator_var] > 0][age_group_var], 
        bins, density = False)
    height_d, bins_d = np.histogram(df_trans[df_trans[denominator_var] > 0][age_group_var], 
        bins, density = False)
    
    heights = np.divide(height_n, height_d)
    overall_ifr = height_n.sum()/height_d.sum()
    
    col_titles = ["Age group", "Infection fatality ratio (IFR; %)"]
    col_age = age_group_labels + [ "Whole population" ]
    col_ifr = np.insert(heights, len(heights), overall_ifr)
    
    df_ifr = pd.DataFrame({"age_group": col_age, "ifr": col_ifr*100})
    df_ifr.ifr = df_ifr.ifr.map("{:,.4f}".format)
    df_ifr.columns = col_titles
    df_ifr.to_csv(output_table, index = False)

