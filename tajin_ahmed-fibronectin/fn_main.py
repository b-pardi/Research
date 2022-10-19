"""
Author: Brandon Pardi
Created: 8/31/2022, 1:20 pm
Last Modified: 10/19/2022 12:51 pm
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime

import gui

"""
README
- Please execute 'install_packages.py' BEFORE running this script
- ensure all sheets are in the 'raw_data' folder
    - OR specify file directory in gui
- consistency in column placement and naming is required, however columns will be renamed
- if error occurs, it will be displayed in the terminal
- if uncaught error occurs, please notify me asap and describe what was done to reproduce
- specify GUI
    - file name (with exetension)
    - file path (if not in predefined data directory)
    - indicate if new clean data file should be created
    - if plotting clean data, indicate baseline t0 and tf
    - SUBMIT FILE INFO
    - indicate which channels to plot for raw/clean data
    - indicate which special plot options
    - change scale of time if applicable

FUNCTIONS
- opens 'gui.py' to define information
- opens defined file and reads it into a dataframe
- renames columns as dictated below in Variable Declarations section
- checks which_plot to determine which channels are being analyzed, and adds to lists accordingly
Clean Data:
    - find average resonant frequency of baseline, and lowers curve by that amount
    - cleans data by removing points before baseline, and lowers by aforemention average
- plots are frequencies and dissipations of each channel specified in gui.py
- if overwrite file selected, will replace file data with the data it had just cleaned
    - Not advised if not selecting ALL plots
- plots raw data individually as specified in gui
- option to normalize data by dividing frequency by its respective overtone
- option to plot change in dissipation vs change in frequency
- option for multi axis plot with change in frequency and dissipation vs time


WIP
- ERROR CHECKING?
    - if options are selected, make sure clean plot channels are selected
    - account for error if can't find valid time
    - when inputting time, check for nearest time value,
    in case time value not actually in data sheet

"""


'''Variable Declarations'''
abs_time_col = 'Time'
rel_time_col = 'Relative_time'
freqs = ['fundamental_freq', '3rd_freq', '5th_freq', '7th_freq', '9th_freq']
disps = ['fundamental_dis', '3rd_dis', '5th_dis', '7th_dis', '9th_dis']
t0_str = str(gui.abs_base_t0).lstrip('0')
tf_str = str(gui.abs_base_tf).lstrip('0')

# Some plot labels
dis_fig_y = "Change in Dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")"
rf_fig_y = "Change in frequency, " + '$\it{Δf}$' + " (Hz)"


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

def determine_xlabel():
    if gui.x_timescale == 's':
        return "Time (s)"
    elif gui.x_timescale == 'm':
        return "Time (min)"
    else:
        return "Time (hr)"


def setup_plot(fig_num, fig_x, fig_y, fig_title, fn, will_save=False):
    plt.figure(fig_num, clear=False)
    plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.1)
    plt.xticks(fontsize=14, fontfamily='Arial')
    plt.yticks(fontsize=14, fontfamily='Arial')
    plt.xlabel(fig_x, fontsize=16, fontfamily='Arial')
    plt.ylabel(fig_y, fontsize=16, fontfamily='Arial')
    plt.title(fig_title, fontsize=16, fontfamily='Arial')
    if will_save:
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
        data_df = df[[abs_time_col,rel_time_col,clean_freqs[i],clean_disps[i]]]
        print(f"clean freq ch: {clean_freqs[i]}; clean disp ch: {clean_disps[i]}")
        data_df = data_df.dropna(axis=0, how='any', inplace=False)

        # find baseline time range
        baseline_dur = datetime.combine(datetime.min, gui.abs_base_tf) - datetime.combine(datetime.min, gui.abs_base_t0)
        # locate where baseline starts/ends
        base_t0_ind = data_df[data_df[abs_time_col].str.contains(t0_str)].index[0]
        # remove everything before baseline
        data_df = data_df[base_t0_ind:]
        data_df = data_df.reset_index(drop=True)

        # normalize by overtone
        if gui.will_normalize_F:
            overtone = 1
            if clean_freqs[i].__contains__("3"):
                overtone = 3
            if clean_freqs[i].__contains__("5"):
                overtone = 5
            if clean_freqs[i].__contains__("7"):
                overtone = 7
            if clean_freqs[i].__contains__("9"):
                overtone = 9
            data_df[clean_freqs[i]] /= overtone

        # find baseline and grab values from baseline for avg
        base_tf_ind = data_df[data_df[abs_time_col].str.contains(tf_str)].index[0]
        baseline_df = data_df[:base_tf_ind]
        # compute average of rf and dis
        rf_base_avg = baseline_df[clean_freqs[i]].mean()
        dis_base_avg = baseline_df[clean_disps[i]].mean()

        # lower rf curve s.t. baseline is approx at y=0
        data_df[clean_freqs[i]] -= rf_base_avg
        data_df[clean_disps[i]] -= dis_base_avg

        # PLOTTING
        x_time = data_df[rel_time_col]
        y_rf = data_df[clean_freqs[i]]
        # scale disipation by 10^6
        data_df[clean_disps[i]] *= 1000000
        y_dis = data_df[clean_disps[i]]
        if gui.x_timescale == 'm':
            divisor = 60
        elif gui.x_timescale == 'h':
            divisor = 3600
        else:
            divisor = 1
        x_time = [num / divisor for num in x_time]

        # PLOTTING
        plt.figure(1, clear=False)
        # don't plot data for channels not selected
        if i < freq_plot_cap:
            plt.plot(x_time, y_rf, label=f"resonant freq - {clean_freqs[i]}")
        plt.figure(2, clear=False)
        if i < disp_plot_cap:
            plt.plot(x_time, y_dis, label=f"dissipation - {clean_disps[i]}")

        # plotting change in disp vs change in freq
        if gui.will_plot_dD_v_dF:
            plt.figure(5, clear=False)
            plt.plot(y_rf, y_dis, 'o', label=f"{clean_disps[i]} vs {clean_freqs[i]}")
        
        # multi axis plot for change in freq and change in dis vs time
        if gui.will_plot_dF_dD_together:
            fig, ax1 = plt.subplots()
            ax1.set_xlabel(determine_xlabel(), fontsize=16, fontfamily='Arial')
            ax1.set_ylabel(rf_fig_y, fontsize=16, fontfamily='Arial')
            ax2 = ax1.twinx()
            ax2.set_ylabel(dis_fig_y,fontsize=16, fontfamily='Arial')
            ax1.plot(x_time, y_rf, label=f"resonant freq - {clean_freqs[i]}", color='green')
            ax2.plot(x_time, y_dis, label=f"dissipation - {clean_disps[i]}", color='blue')
            fig.legend(loc='upper center', fontsize=14, prop={'family': 'Arial'}, framealpha=0.1)
            plt.xticks(fontsize=14, fontfamily='Arial')
            plt.yticks(fontsize=14, fontfamily='Arial')
            plt.title("", fontsize=16, fontfamily='Arial')
            plt.savefig(f"qcmb-plots/freq_dis_V_time_{freqs[i][:3]}", bbox_inches='tight', transparent=True)
        
        print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}\n")

        # cleaned df to overwrite old data
        if gui.will_overwrite_file:
            if i == 0:
                cleaned_df = data_df[[abs_time_col,rel_time_col]]
            cleaned_df = pd.concat([cleaned_df,data_df[clean_freqs[i]]], axis=1)
            cleaned_df = pd.concat([cleaned_df,data_df[clean_disps[i]]], axis=1)


    if gui.will_overwrite_file:
        print(cleaned_df.head())
        cleaned_df.to_csv(f"raw_data/CLEANED-{gui.file_name}", index=False)

    # Titles, lables, etc. for plots
    if gui.will_normalize_F:
        rf_fig_title = "QCM-D Resonant Frequency - NORMALIZED"
        rf_fn = f"qcmb-plots/NORM-resonant-freq-plot.png"
    else:
        rf_fig_title = "QCM-D Resonant Frequency"
        rf_fn = f"qcmb-plots/resonant-freq-plot.png"
    rf_fig_x = determine_xlabel()

    dis_fig_title = "QCM-D Dissipation"
    dis_fig_x = rf_fig_x
    dis_fn = f"qcmb-plots/dissipation-plot.png"

    # fig 1: clean freq plot
    # fig 2: clean disp plot
    # fig 5: dD v dF
    setup_plot(1, rf_fig_x, rf_fig_y, rf_fig_title, rf_fn, True)
    setup_plot(2, dis_fig_x, dis_fig_y, dis_fig_title, dis_fn, True)
    if gui.will_plot_dD_v_dF:
        dVf_fn = f"qcmb-plots/disp_V_freq-plot.png"
        dVf_title = "Dissipiation against Frequency"
        setup_plot(5, rf_fig_y, dis_fig_y, dis_fig_title, dVf_fn, True)


# Gathering raw data for individual plots
if gui.will_plot_raw_data:
    # plot definitions
    rf_fig_title = "RAW QCM-D Resonant Frequency"
    rf_fig_y = "Change in frequency, " + '$\it{Δf}$' + " (Hz)"
    rf_fig_x = determine_xlabel()

    dis_fig_title = "RAW QCM-D Dissipation"
    dis_fig_y = "Change in Dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")"
    dis_fig_x = rf_fig_x


    raw_freqs, raw_disps = get_channels('raw')
    # gather and plot raw frequency data
    for i in range(len(raw_freqs)):
        rf_data_df = df[[abs_time_col,rel_time_col,raw_freqs[i]]]
        rf_data_df = rf_data_df.dropna(axis=0, how='any', inplace=False)
        x_time = rf_data_df[rel_time_col]
        y_rf = rf_data_df[raw_freqs[i]]
        plt.figure(3, clear=True)
        plt.plot(x_time, y_rf, label=f"raw resonant freq - {i}")
        rf_fn = f"qcmb-plots/RAW-resonant-freq-plot-{raw_freqs[i]}.png"
        setup_plot(3, rf_fig_x, rf_fig_y, rf_fig_title, rf_fn)
        plt.figure(3).savefig(rf_fn, bbox_inches='tight', transparent=True)

    # gather and plot raw dissipation data
    for i in range(len(raw_disps)):
        dis_data_df = df[[abs_time_col,rel_time_col,raw_disps[i]]]
        dis_data_df = dis_data_df.dropna(axis=0, how='any', inplace=False)
        x_time = dis_data_df[rel_time_col]
        y_dis = dis_data_df[raw_disps[i]]
        plt.figure(4, clear=True)
        plt.plot(x_time, y_dis, label=f"raw dissipation - {i}")
        dis_fn = f"qcmb-plots/RAW-dissipation-plot-{raw_freqs[i]}.png"
        setup_plot(4, dis_fig_x, dis_fig_y, dis_fig_title, dis_fn)
        plt.figure(4).savefig(dis_fn, bbox_inches='tight', transparent=True)

