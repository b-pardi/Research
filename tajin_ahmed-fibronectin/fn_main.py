"""
Author: Brandon Pardi
Created: 8/31/2022, 1:20 pm
Last Modified: 9/6/2022 2:16 pm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path
from datetime import datetime, time

import tempgui

"""
README
- Please execute 'install_packages.py' BEFORE running this script
- ensure all sheets are in the 'raw_data' folder
- ensure all user defined variables are established under 'INPUT DEFINITIONS'
    - these include: data file extension, data column names, and baseline time stamps
- consistency in column placement AND naming is required

FUNCTIONS
- opens defined file and reads it into a dataframe
- find average resonant frequency of baseline, and lowers curve by that amount
- cleans data by removing points before baseline, and lowers by aforemention average
WIP

- account for multiple tonal resonant frequencies (fund, 3rd, 5th, 7th)
- plot rf and dissipation as func of time (indv and comb)
- gui
    - tempgui will hold input variables until gui is working
    - when entering col names, autopopulate based on first entry
Q's
- what are the baseline times of the sample data sent?
- do we need this script to process multiple sheets at once?
    if so, how do we establish a baseline time for each sheet?
- scrub data towards end like how it is before baseline?
- what is expected of me from the research update presentation?
"""


# grab singular file and create dataframe from it
df = pd.read_csv(f"raw_data/{tempgui.file_name}{tempgui.file_ext}")

for i in range(tempgui.num_freqs_tested):
    data_df = df[[tempgui.abs_time_col,tempgui.rel_time_col, tempgui.rf_cols[i], tempgui.dis_cols[i]]]
    data_df = data_df.dropna(axis=0, how='any', inplace=False)

    # find baseline time range
    baseline_dur = datetime.combine(datetime.min, tempgui.abs_base_tf) - datetime.combine(datetime.min, tempgui.abs_base_t0)
    # locate where baseline starts/ends
    base_t0_ind = data_df[data_df[tempgui.abs_time_col].str.contains(str(tempgui.abs_base_t0))].index[0]
    # remove everything before baseline
    data_df = data_df[base_t0_ind:]
    data_df = data_df.reset_index(drop=True)

    # grab values from baseline for avg
    base_tf_ind = data_df[data_df[tempgui.abs_time_col].str.contains(str(tempgui.abs_base_tf))].index[0]
    baseline_df = data_df[:base_tf_ind]
    rf_base_avg = baseline_df[tempgui.rf_cols[i]].mean()
    dis_base_avg = baseline_df[tempgui.dis_cols[i]].mean()

    # lower rf curve s.t. baseline is approx at y=0
    data_df[tempgui.rf_cols[i]] -= rf_base_avg

    # PLOTTING
    x_time = data_df[tempgui.rel_time_col]
    y_rf = data_df[tempgui.rf_cols[i]]
    y_dis = data_df[tempgui.dis_cols[i]]
    plt.figure(1, clear=True)
    plt.axhline(0, color='gray')
    plt.plot(x_time, y_rf, label=f"resonant freq - {i}")
    plt.legend(loc='best')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency')
    plt.title(f"QCMB Resonant Frequency {i}")
    plt.figure(1).savefig(f"qcmb-plots/{tempgui.file_name}-rf{i}-plot.png")
    plt.figure(2, clear=True)
    plt.plot(x_time, y_dis, label=f"dissipation - {i}")
    plt.legend(loc='best')
    plt.xlabel('Time (s)')
    plt.ylabel('Dissipation')
    plt.title(f"QCMB Dissipation {i}")
    plt.grid(True, which='major', axis='y', color='gray', linewidth='1')
    plt.figure(2).savefig(f"qcmb-plots/{tempgui.file_name}-dis{i}-plot.png")


    print(f"{data_df.head()}\n{data_df.tail()}")
    print(f"{baseline_df.head()}\n{baseline_df.tail()}")
    print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}")
