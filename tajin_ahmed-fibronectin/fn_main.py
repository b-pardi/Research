"""
Author: Brandon Pardi
Created: 8/31/2022, 1:20 pm
Last Modified: 9/27/2022 3:56 pm
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime, time

import gui

"""
README
- Please execute 'install_packages.py' BEFORE running this script
- ensure all sheets are in the 'raw_data' folder
    - OR specify file directory in gui
- consistency in column placement and naming is required, however columns will be renamed
- if error occurs, it will be displayed in the terminal

FUNCTIONS
- opens defined file and reads it into a dataframe
- find average resonant frequency of baseline, and lowers curve by that amount
- cleans data by removing points before baseline, and lowers by aforemention average
- plots are frequencies and dissipations of each channel specified in gui.py

WIP
- gui
- plot data for each channel based on 'gui.whichplot' dict
    - currently only works when selecting all for plot clean data
- plotting raw data
- write to csv new column names
- write csv with cleaned data (dependent on checkbox in gui)
"""

'''Variable Declarations'''
abs_time_col = 'Time'
rel_time_col = 'Relative_time'
freqs = ['fundamental_freq', '3rd_freq', '5th_freq', '7th_freq', '9th_freq']
disps = ['fundamental_dis', '3rd_dis', '5th_dis', '7th_dis', '9th_dis']
t0_str = str(gui.abs_base_t0).lstrip('0')
tf_str = str(gui.abs_base_tf).lstrip('0')

# grab singular file and create dataframe from it
if gui.file_path == "":
    df = pd.read_csv(f"raw_data/{gui.file_name}")
else:
    df = pd.read_csv(f"{gui.file_path}/{gui.file_name}")

'''Rename Columns'''
# check if an original column name is in df
# if it is, all columns must be renamed
if 'Frequency_0' in df.columns:
    df.rename(columns={'Frequency_0':freqs[0],'Dissipation_0':disps[0],
    'Frequency_1':freqs[1], 'Dissipation_1':disps[1],
    'Frequency_2':freqs[2], 'Dissipation_2':disps[2],
    'Frequency_3':freqs[3], 'Dissipation_3':disps[3],
    'Frequency_4':freqs[4], 'Dissipation_4':disps[4]}, inplace=True)


for i in range(int(gui.clean_num_channels_tested/2)+1):
    # grab data from df and grab only columns we need, then drop nan values
    data_df = df[[abs_time_col,rel_time_col,freqs[i] ,disps[i]]]
    data_df = data_df.dropna(axis=0, how='any', inplace=False)

    # find baseline time range
    baseline_dur = datetime.combine(datetime.min, gui.abs_base_tf) - datetime.combine(datetime.min, gui.abs_base_t0)
    # locate where baseline starts/ends
    base_t0_ind = data_df[data_df[abs_time_col].str.contains(t0_str)].index[0]
    # remove everything before baseline
    data_df = data_df[base_t0_ind:]
    data_df = data_df.reset_index(drop=True)

    # find baseline and grab values from baseline for avg
    base_tf_ind = data_df[data_df[abs_time_col].str.contains(tf_str)].index[0]
    baseline_df = data_df[:base_tf_ind]
    # compute average of rf and dis
    rf_base_avg = baseline_df[freqs[i]].mean()
    dis_base_avg = baseline_df[disps[i]].mean()

    # lower rf curve s.t. baseline is approx at y=0
    data_df[freqs[i]] -= rf_base_avg
    data_df[disps[i]] -= dis_base_avg

    # PLOTTING
    x_time = data_df[rel_time_col]
    y_rf = data_df[freqs[i]]
    y_dis = data_df[disps[i]]
    plt.figure(1, clear=False)
    plt.plot(x_time, y_rf, label=f"resonant freq - {i}")
    plt.figure(2, clear=False)
    plt.plot(x_time, y_dis, label=f"dissipation - {i}")

    plt.figure(3, clear=True)
    plt.plot(x_time, y_rf, label=f"indv resonant freq - {i}")
    plt.figure(3).savefig(f"qcmb-plots/resonant-freq-plot-indv{i}.png")

    '''print(f"{data_df.head()}\n{data_df.tail()}")
    print(f"{baseline_df.head()}\n{baseline_df.tail()}")
    print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}\n")'''

# Titles, lables, etc. for plots
plt.figure(1, clear=False)
plt.axhline(0, color='gray')
plt.legend(loc='best')
plt.xlabel('Time (s)')
plt.ylabel('Frequency')
plt.title(f"QCMB Resonant Frequency")
plt.figure(1).savefig(f"qcmb-plots/resonant-freq-plot.png")
plt.figure(2, clear=False)
plt.legend(loc='best')
plt.xlabel('Time (s)')
plt.ylabel('Dissipation')
plt.title(f"QCMB Dissipation")
plt.grid(True, which='major', axis='y', color='gray', linewidth='1')
plt.figure(2).savefig(f"qcmb-plots/dissipation-plot.png")