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
rf_col = 'Frequency_1'
dis_col = 'Dissipation_0'


# grab singular file and create dataframe from it
df = pd.read_csv(f"raw_data/{file_name}{file_ext}")
data_df = df[[abs_time_col,rel_time_col, rf_col, dis_col]]
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
rf_base_avg = baseline_df[rf_col].mean()
dis_base_avg = baseline_df[dis_col].mean()

# lower rf curve s.t. baseline is approx at y=0
data_df[rf_col] -= rf_base_avg


# PLOTTING
x_time = data_df[rel_time_col]
y_rf = data_df[rf_col]
y_dis = data_df[dis_col]
plt.figure(1, clear=True)
plt.plot(x_time, y_rf, label="resonant freq")
plt.figure(1).savefig(f"qcmb-plots/{file_name}-plot.png")
plt.figure(2, clear=True)
plt.plot(x_time, y_dis, label="dissipation")




print(f"{data_df.head()}\n{data_df.tail()}")
print(f"{baseline_df.head()}\n{baseline_df.tail()}")
print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}")
