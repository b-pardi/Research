"""
Author: Brandon Pardi
Created: 8/31/2022, 1:20 pm
Last Modified: 9/27/2022 4:35 pm
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
- opens 'gui.py' to define information
- opens defined file and reads it into a dataframe
- renames columns as dictated below in Variable Declarations section
- checks which_plot to determine which channels are being analyzed, and adds to lists accordingly
- find average resonant frequency of baseline, and lowers curve by that amount
- cleans data by removing points before baseline, and lowers by aforemention average
- plots are frequencies and dissipations of each channel specified in gui.py
- if overwrite file selected, will replace file data with the data it had just cleaned
    - Not advised if not selecting ALL plots

WIP
- ERROR CHECKING?
- plotting raw data
- alternate plot options:
    - plot dF and dD together
    - normalize F
    - dD vs dF

- scale to minutes for x axis (gui input to determine)
- y axis for dissipation scale * 10^(-6)

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
    df.to_csv("raw_data/08102022_n=2_Fn at 500 ug per ml and full SF on func gold at 37C.csv", index=False)

# function fills list of channels selected to be clean plot from gui
def get_channels(scrub_level):
    freq_list = []
    disp_list = []
        
    for channel in gui.which_plot[scrub_level].items():
        # dict entry for that channel is true then append to list
        if channel[1] == True:
            # check if channel looking at is a frequency or dissipation and append approppriately
            if channel[0].__contains__('freq'):
                freq_list.append(channel[0])
            elif channel[0].__contains__('dis'):
                disp_list.append(channel[0])

    return (freq_list, disp_list)
    
def set_plot(fig_num, fig_x, fig_y, fig_title, fn):
    plt.figure(fig_num, clear=False)
    plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.1)
    plt.xticks(fontsize=14, fontfamily='Arial')
    plt.yticks(fontsize=14, fontfamily='Arial')
    plt.xlabel(fig_x, fontsize=16, fontfamily='Arial')
    plt.ylabel(fig_y, fontsize=16, fontfamily='Arial')
    plt.title(fig_title, fontsize=16, fontfamily='Arial')
    plt.figure(fig_num).savefig(fn, bbox_inches='tight', transparent=True)

'''Cleaning Data and plotting clean data'''
if gui.will_plot_clean_data:
    clean_freqs, clean_disps = get_channels('clean')
    clean_iters = 0
    freq_plot_cap = len(clean_freqs)
    disp_plot_cap = len(clean_disps)
    diff = len(clean_freqs) - len(clean_disps)
    # if different num of freq and raw channels, must do equal amount for plotting,
    # but can just not plot the results later; set plot cap for the lesser
    # diff pos -> more freq channels than disp
    if diff > 0:
        clean_iters = len(clean_freqs)
        disp_plot_cap = len(clean_disps)
        for i in range(diff, clean_iters):
            clean_disps.append(disps[i])
    # diff neg -> more disp channels than freq
    elif diff < 0:
        clean_iters = len(clean_disps)
        freq_plot_cap = len(clean_freqs)
        for i in range(abs(diff), clean_iters):
            clean_freqs.append(freqs[i])
    # if length same, then iterations is length of either
    else:
        clean_iters = len(clean_freqs)
        
    for i in range(clean_iters):
        # grab data from df and grab only columns we need, then drop nan values
        data_df = df[[abs_time_col,rel_time_col,freqs[i],disps[i]]]
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
        # don't plot data for channels not selected
        if i < freq_plot_cap:
            plt.plot(x_time, y_rf, label=f"resonant freq - {i}")
        plt.figure(2, clear=False)
        if i < disp_plot_cap:
            plt.plot(x_time, y_dis, label=f"dissipation - {i}")

        '''plt.figure(3, clear=True)
        plt.plot(x_time, y_rf, label=f"indv resonant freq - {i}")
        plt.figure(3).savefig(f"qcmb-plots/resonant-freq-plot-indv{i}.png")
        '''
        
        print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}\n")

        # cleaned df to overwrite old data
        if gui.will_overwrite_file:
            if i == 0:
                cleaned_df = data_df[[abs_time_col,rel_time_col]]
            cleaned_df = pd.concat([cleaned_df,data_df[freqs[i]]], axis=1)
            cleaned_df = pd.concat([cleaned_df,data_df[disps[i]]], axis=1)

    if gui.will_overwrite_file:
        print(cleaned_df.head())
        cleaned_df.to_csv(f"raw_data/CLEANED-{gui.file_name}", index=False)



# Titles, lables, etc. for plots
rf_fig_title = "QCM-D Resonant Frequency"
rf_fig_y = "Change in frequency " + '$\it{Δf}$' + " (" + '$\it{Hz}$' + ")"
if gui.x_timescale == 's':
    rf_fig_x = "Time (" + '$\it{s}$' + ")"
elif gui.x_timescale == 'm':
    rf_fig_x = "Time (" + '$\it{m}$' + ")"
else:
    rf_fig_x = "Time (" + '$\it{h}$' + ")"

rf_fn = f"qcmb-plots/resonant-freq-plot.png"

dis_fig_title = "QCM-D Dissipation"
dis_fig_y = "Change in Dissipation " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")"
dis_fig_x = rf_fig_x
dis_fn = f"qcmb-plots/dissipation-plot.png"

set_plot(1, rf_fig_x, rf_fig_y, rf_fig_title, rf_fn)
set_plot(2, dis_fig_x, dis_fig_y, dis_fig_title, dis_fn)
