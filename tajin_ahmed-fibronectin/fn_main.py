"""
Author: Brandon Pardi
Created: 8/31/2022, 1:20 pm
Last Modified: 6/27/2022 10:31 am
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.optimize import curve_fit
from pathlib import Path
from datetime import datetime, time
import sys
import os


"""
README
- Please execute 'install_packages.py' BEFORE running this script
- ensure all sheets are in the 'raw_data' folder
- ensure all user defined variables are established under 'INPUT DEFINITIONS'
    - these include: data file extension, data column names, and baseline time stamps
FUNCTIONS
- opens defined file and reads it into a dataframe
- find average resonant frequency of baseline, and lowers curve by that amount
- cleans data by removing points before baseline, and lowers by aforemention average
WIP
- account for multiple tonal resonant frequencies (fund, 3rd, 5th, 7th)
- plot rf and dissipation as func of time (indv and comb)
- gui
    - when entering col names, autopopulate based on first entry
Q's
- what are the baseline times of the sample data sent?
- do we need this script to process multiple sheets at once?
    if so, how do we establish a baseline time for each sheet?
- scrub data towards end like how it is before baseline?
- what is expected of me from the research update presentation?
"""

### INPUT DEFINITIONS ###
file_name = "08102022_n=2_Fn at 500 ug per ml and full SF on func gold at 37C"
file_ext = '.csv'
abs_base_t0 = time(8, 35, 52)
abs_base_tf = time(9, 9, 19)
# column names
abs_time_col = 'Time'
rel_time_col = 'Relative_time'
num_freqs_tested = 5
# number after indicates which resonant frequency testing on (fundamental, 1st, 3rd, etc)
rf_col_fund = 'Frequency_0'
dis_col_fund = 'Dissipation_0'
rf_col_3 = 'Frequency_1'
dis_col_3 = 'Dissipation_1'
rf_col_5 = 'Frequency_2'
dis_col_5 = 'Dissipation_2'
rf_col_7 = 'Frequency_3'
dis_col_7 = 'Dissipation_3'
rf_col_9 = 'Frequency_4'
dis_col_9 = 'Dissipation_4' 


# grab singular file and create dataframe from it
df = pd.read_csv(f"raw_data/{file_name}{file_ext}")
data_df = df[[abs_time_col,rel_time_col, rf_col_fund, dis_col_fund]]
data_df = data_df.dropna(axis=0, how='any', inplace=False)

# find baseline time range
baseline_dur = datetime.combine(datetime.min, abs_base_tf) - datetime.combine(datetime.min, abs_base_t0)
# locate where baseline starts/ends
base_t0_ind = data_df[data_df[abs_time_col].str.contains(str(abs_base_t0))].index[0]
# remove everything before baseline
data_df = data_df[base_t0_ind:]
data_df = data_df.reset_index(drop=True)

# grab values from baseline for avg
base_tf_ind = data_df[data_df[abs_time_col].str.contains(str(abs_base_tf))].index[0]
baseline_df = data_df[:base_tf_ind]
rf_base_avg = baseline_df[rf_col_fund].mean()
dis_base_avg = baseline_df[dis_col_fund].mean()

# lower rf curve s.t. baseline is approx at y=0
data_df[rf_col_fund] -= rf_base_avg

# PLOTTING
x_time = data_df[rel_time_col]
y_rf = data_df[rf_col_fund]
y_dis = data_df[dis_col_fund]
plt.figure(1, clear=True)
plt.axhline(0, color='gray')
plt.plot(x_time, y_rf, label="resonant freq")
plt.figure(1).savefig(f"qcmb-plots/{file_name}-rf-plot.png")
plt.figure(2, clear=True)
plt.plot(x_time, y_dis, label="dissipation")
plt.grid(True, which='major', axis='y', color='gray', linewidth='1')
plt.figure(2).savefig(f"qcmb-plots/{file_name}-dis-plot.png")


print(f"{data_df.head()}\n{data_df.tail()}")
print(f"{baseline_df.head()}\n{baseline_df.tail()}")
print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}")
