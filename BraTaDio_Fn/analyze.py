from tkinter import *
import os
from datetime import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from scipy.optimize import curve_fit
import shutil

from lin_reg import *

def clear_figures():
    for i in range(6):
        plt.figure(i)
        plt.clf()

def analyze_data(input):
    '''Variable Declarations'''
    abs_time_col = 'Time'
    rel_time_col = 'Relative_time'
    freqs = ['fundamental_freq', '3rd_freq', '5th_freq', '7th_freq', '9th_freq']
    disps = ['fundamental_dis', '3rd_dis', '5th_dis', '7th_dis', '9th_dis']
    t0_str = str(input.abs_base_t0).lstrip('0')
    tf_str = str(input.abs_base_tf).lstrip('0')

    # Some plot labels
    dis_fig_y = "Change in dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")"
    rf_fig_y = "Change in frequency, " + '$\it{Δf}$' + " (Hz)"


    # grab singular file and create dataframe from it
    if input.file_path == "":
        df = pd.read_csv(f"raw_data/{input.file_name}")
    else:
        df = pd.read_csv(f"{input.file_path}/{input.file_name}")
    df = df.dropna()

    '''Rename Columns'''
    # check if an original column name is in df
    # if it is, all columns must be renamed
    if 'Frequency_0' in df.columns:
        df.rename(columns={'Frequency_0':freqs[0],'Dissipation_0':disps[0],
        'Frequency_1':freqs[1], 'Dissipation_1':disps[1],
        'Frequency_2':freqs[2], 'Dissipation_2':disps[2],
        'Frequency_3':freqs[3], 'Dissipation_3':disps[3],
        'Frequency_4':freqs[4], 'Dissipation_4':disps[4]}, inplace=True)
        df.to_csv(f"raw_data/{input.file_name}", index=False)

    # assign colors to overtones
    color_map_freq = {'fundamental_freq':'blue', '3rd_freq':'orange', '5th_freq':'green', '7th_freq':'red', '9th_freq':'purple'}
    color_map_dis = {'fundamental_dis':'blue', '3rd_dis':'orange', '5th_dis':'green', '7th_dis':'red', '9th_dis':'purple'}

    # function fills list of channels selected to be clean plot from gui
    def get_channels(scrub_level):
        freq_list = []
        disp_list = []
            
        for channel in input.which_plot[scrub_level].items():
            # dict entry for that channel is true then append to list
            if channel[1] == True:
                # check if channel looking at is a frequency or dissipation and append approppriately
                if channel[0].__contains__('freq'):
                    freq_list.append(channel[0])
                elif channel[0].__contains__('dis'):
                    disp_list.append(channel[0])

        return (freq_list, disp_list)

    def determine_xlabel():
        if input.x_timescale == 's':
            return "Time, " + '$\it{Δt}$' + " (s)"
        elif input.x_timescale == 'm':
            return "Time, " + '$\it{Δt}$' + " (min)"
        else:
            return "Time, " + '$\it{Δt}$' + " (hr)"


    def setup_plot(fig_num, fig_x, fig_y, fig_title, fn, will_save=False):
        plt.figure(fig_num, clear=False)
        plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.1)
        plt.xticks(fontsize=14, fontfamily='Arial')
        plt.yticks(fontsize=14, fontfamily='Arial')
        plt.xlabel(fig_x, fontsize=16, fontfamily='Arial')
        plt.ylabel(fig_y, fontsize=16, fontfamily='Arial')
        plt.title(fig_title, fontsize=16, fontfamily='Arial')
        if will_save:
            plt.figure(fig_num).savefig(fn + '.' + input.fig_format, format=input.fig_format, bbox_inches='tight', transparent=True, dpi=400)

    def find_nearest_time(time, my_df, time_col_name):
        # locate where baseline starts/ends
        print(time, my_df, time_col_name)
        time_df = my_df[my_df[time_col_name].str.contains(time)]

        # if exact time not in dataframe, find nearest one
        # convert the last 2 digits (the seconds) into integers and increment by 1, mod by 10
        # this method will find nearest time since time stamps are never more than 2 seconds apart
        while(time_df.shape[0] == 0): # iterate until string found in time dataframe
            ta = time[:7]
            print(int(time[7:]))
            tb = (int(time[7:]) + 1) % 10
            print(ta, tb)
            time = ta + str(tb)
            time_df = my_df[my_df[time_col_name].str.contains(time)]
        base_t0_ind = time_df.index[0]

        return base_t0_ind

    '''Cleaning Data and plotting clean data'''
    if input.will_plot_clean_data:
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
            
        # remove everything before baseline
        base_t0_ind = find_nearest_time(t0_str, df, abs_time_col) # baseline correction
        df = df[base_t0_ind:] # baseline correction
        print(df)
        df = df.reset_index(drop=True)
        # find baseline and grab values from baseline for avg
        base_tf_ind = find_nearest_time(tf_str, df, abs_time_col) # baseline correction
        baseline_df = df[:base_tf_ind]
        
        for i in range(clean_iters):
            # grab data from df and grab only columns we need, then drop nan values
            data_df = df[[abs_time_col,rel_time_col,clean_freqs[i],clean_disps[i]]]
            print(f"clean freq ch: {clean_freqs[i]}; clean disp ch: {clean_disps[i]}")
            data_df = data_df.dropna(axis=0, how='any', inplace=False)

            # normalize by overtone
            if input.will_normalize_F:
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

            # compute average of rf and dis
            rf_base_avg = baseline_df[clean_freqs[i]].mean() # baseline correction
            dis_base_avg = baseline_df[clean_disps[i]].mean() # baseline correction

            # lower rf curve s.t. baseline is approx at y=0
            data_df[clean_freqs[i]] -= rf_base_avg # baseline correction
            data_df[clean_disps[i]] -= dis_base_avg # baseline correction
            # shift x to left to start at 0
            data_df[rel_time_col] -= data_df[rel_time_col].iloc[0] # baseline correction

            # choose appropriate divisor for x scale of time
            if input.x_timescale == 'm':
                divisor = 60
            elif input.x_timescale == 'h':
                divisor = 3600
            else:
                divisor = 1
            data_df[rel_time_col] /= divisor # baseline correction
            x_time = data_df[rel_time_col]
            y_rf = data_df[clean_freqs[i]]
            # scale disipation by 10^6
            data_df[clean_disps[i]] *= 1000000 # baseline correction
            y_dis = data_df[clean_disps[i]]
            
            # PLOTTING
            plt.figure(1, clear=False)
            # don't plot data for channels not selected
            if i < freq_plot_cap:
                plt.plot(x_time, y_rf, '.', markersize=1, label=f"resonant freq - {clean_freqs[i]}", color=color_map_freq[clean_freqs[i]])
            plt.figure(2, clear=False)
            if i < disp_plot_cap:
                plt.plot(x_time, y_dis, '.', markersize=1, label=f"dissipation - {clean_disps[i]}", color=color_map_dis[clean_disps[i]])

            # plotting change in disp vs change in freq
            if input.will_plot_dD_v_dF:
                plt.figure(5, clear=False)
                plt.plot(y_rf, y_dis, '.', markersize=1, label=f"{clean_disps[i]} vs {clean_freqs[i]}")
            
            # multi axis plot for change in freq and change in dis vs time
            if input.will_plot_dF_dD_together:
                fig, ax1 = plt.subplots()
                ax1.set_xlabel(determine_xlabel(), fontsize=16, fontfamily='Arial')
                ax1.set_ylabel(rf_fig_y, fontsize=16, fontfamily='Arial')
                ax2 = ax1.twinx()
                ax2.set_ylabel(dis_fig_y,fontsize=16, fontfamily='Arial')
                ax1.plot(x_time, y_rf, '.', markersize=1, label=f"resonant freq - {clean_freqs[i]}", color='green')
                ax2.plot(x_time, y_dis, '.', markersize=1, label=f"dissipation - {clean_disps[i]}", color='blue')
                fig.legend(loc='upper center', fontsize=14, prop={'family': 'Arial'}, framealpha=0.1)
                plt.xticks(fontsize=14, fontfamily='Arial')
                plt.yticks(fontsize=14, fontfamily='Arial')
                plt.title("", fontsize=16, fontfamily='Arial')
                plt.savefig(f"qcmd-plots/freq_dis_V_time_{freqs[i][:3]}", bbox_inches='tight', transparent=True, dpi=400)
            
            print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}\n")

            # put cleaned data back into original df for interactive plot
            if input.will_overwrite_file or input.will_interactive_plot:
                if i == 0:
                    cleaned_df = data_df[[abs_time_col,rel_time_col]]
                cleaned_df = pd.concat([cleaned_df,data_df[clean_freqs[i]]], axis=1)
                cleaned_df = pd.concat([cleaned_df,data_df[clean_disps[i]]], axis=1)


        if input.will_overwrite_file:
            print(df.head())
            df.to_csv(f"raw_data/CLEANED-{input.file_name}", index=False)

        # Titles, lables, etc. for plots
        if input.will_normalize_F:
            rf_fig_title = "QCM-D Resonant Frequency - NORMALIZED"
            rf_fn = f"qcmd-plots/NORM-resonant-freq-plot"
        else:
            rf_fig_title = "QCM-D Resonant Frequency"
            rf_fn = f"qcmd-plots/resonant-freq-plot"
        rf_fig_x = determine_xlabel()

        dis_fig_title = "QCM-D Dissipation"
        dis_fig_x = rf_fig_x
        dis_fn = f"qcmd-plots/dissipation-plot"

        # fig 1: clean freq plot
        # fig 2: clean disp plot
        # fig 5: dD v dF
        setup_plot(1, rf_fig_x, rf_fig_y, rf_fig_title, rf_fn, True)
        setup_plot(2, dis_fig_x, dis_fig_y, dis_fig_title, dis_fn, True)
        if input.will_plot_dD_v_dF:
            dVf_fn = f"qcmd-plots/disp_V_freq-plot"
            dVf_title = "Dissipiation against Frequency"
            setup_plot(5, rf_fig_y, dis_fig_y, dis_fig_title, dVf_fn, True)


    # Gathering raw data for individual plots
    if input.will_plot_raw_data:
        # plot definitions
        rf_fig_title = "RAW QCM-D Resonant Frequency"
        rf_fig_y = "Change in frequency, " + '$\it{Δf}$' + " (Hz)"
        rf_fig_x = determine_xlabel()

        dis_fig_title = "RAW QCM-D Dissipation"
        dis_fig_y = "Change in dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")"
        dis_fig_x = rf_fig_x

        # choose appropriate divisor for x scale of time
        time_scale_divisor = 1
        if input.x_timescale == 'm':
            time_scale_divisor = 60
        elif input.x_timescale == 'h':
            time_scale_divisor = 3600

        raw_freqs, raw_disps = get_channels('raw')
        # gather and plot raw frequency data
        for i in range(len(raw_freqs)):
            rf_data_df = df[[abs_time_col,rel_time_col,raw_freqs[i]]]
            rf_data_df = rf_data_df.dropna(axis=0, how='any', inplace=False)
            x_time = rf_data_df[rel_time_col] / time_scale_divisor
            y_rf = rf_data_df[raw_freqs[i]]
            plt.figure(3, clear=True)
            plt.plot(x_time, y_rf, '.', markersize=1, label=f"raw resonant freq - {i}", color=color_map_freq[clean_freqs[i]])
            rf_fn = f"qcmd-plots/RAW-resonant-freq-plot-{raw_freqs[i]}"
            setup_plot(3, rf_fig_x, rf_fig_y, rf_fig_title, rf_fn)
            plt.figure(3).savefig(rf_fn + '.' + input.fig_format, format=input.fig_format, bbox_inches='tight', transparent=True, dpi=400)

        # gather and plot raw dissipation data
        for i in range(len(raw_disps)):
            dis_data_df = df[[abs_time_col,rel_time_col,raw_disps[i]]]
            dis_data_df = dis_data_df.dropna(axis=0, how='any', inplace=False)
            x_time = dis_data_df[rel_time_col] / time_scale_divisor
            y_dis = dis_data_df[raw_disps[i]]
            plt.figure(4, clear=True)
            plt.plot(x_time, y_dis, '.', markersize=1, label=f"raw dissipation - {i}", color=color_map_dis[clean_disps[i]])
            dis_fn = f"qcmd-plots/RAW-dissipation-plot-{raw_freqs[i]}"
            setup_plot(4, dis_fig_x, dis_fig_y, dis_fig_title, dis_fn)
            plt.figure(4).savefig(dis_fn + '.' + input.fig_format, format=input.fig_format, bbox_inches='tight', transparent=True, dpi=400)

    # removing axis lines for plots
    def remove_axis_lines(ax):
        ax.spines['top'].set_color('none')
        ax.spines['bottom'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)
        
    # interactive plot
    if input.will_interactive_plot:
        # clear all previous plots
        plt.close("all")

        # setup plot objects
        int_plot = plt.figure()
        plt.clf()
        int_plot.set_figwidth(14)
        int_plot.set_figheight(8)
        plt.subplots_adjust(hspace=0.4,wspace=0.1)
        # nrows, ncols, position (like quadrants from l -> r)
        ax = int_plot.add_subplot(1,1,1) # the 'big' subplot for shared axis
        y_ax1 = int_plot.add_subplot(2,1,1) # shared axis for easy to read titles
        y_ax2 = int_plot.add_subplot(2,1,2) 
        int_ax1 = int_plot.add_subplot(2,2,1) # individual subplots actually containing data
        plt.cla()
        int_ax2 = int_plot.add_subplot(2,2,3)
        plt.cla()
        int_ax1_zoom = int_plot.add_subplot(2,2,2)
        plt.cla()
        int_ax2_zoom = int_plot.add_subplot(2,2,4)
        plt.cla()

        # formatting and labels
        int_ax1.set_title(f"QCM-D Resonant Frequency - overtone {input.interactive_plot_overtone}", fontsize=14, fontfamily='Arial')
        int_ax2.set_title(f"QCM-D Dissipation - overtone {input.interactive_plot_overtone}", fontsize=16, fontfamily='Arial')
        int_ax1_zoom.set_title("\nFrequency Selection Data", fontsize=16, fontfamily='Arial')
        int_ax2_zoom.set_title("\nDissipation Selection Data", fontsize=16, fontfamily='Arial')
        ax.set_title("Click and drag to select range", fontsize=20, fontfamily='Arial', weight='bold', pad=40)
        y_ax1.set_ylabel("change in frequency, " + '$\it{Δf}$' + " (Hz)", fontsize=14, fontfamily='Arial', labelpad=15) # label the shared axes
        y_ax2.set_ylabel("Change in dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")", fontsize=14, fontfamily='Arial', labelpad=5)
        ax.set_xlabel (determine_xlabel(), fontsize=16, fontfamily='Arial')
        plt.sca(int_ax1)
        plt.xticks(fontsize=12, fontfamily='Arial')
        plt.yticks(fontsize=12, fontfamily='Arial')
        plt.sca(int_ax2)
        plt.xticks(fontsize=12, fontfamily='Arial')
        plt.yticks(fontsize=12, fontfamily='Arial')
        plt.sca(int_ax1_zoom)
        plt.xticks(fontsize=12, fontfamily='Arial')
        plt.yticks(fontsize=12, fontfamily='Arial')
        plt.sca(int_ax2_zoom)
        plt.xticks(fontsize=12, fontfamily='Arial')
        plt.yticks(fontsize=12, fontfamily='Arial')

        # Turn off axis lines and ticks of the big subplots
        remove_axis_lines(ax)
        remove_axis_lines(y_ax1)
        remove_axis_lines(y_ax2)

        # grab data
        x_time = cleaned_df[rel_time_col]
        # choose correct user spec'd overtone
        if input.interactive_plot_overtone == 1:
            which_int_plot_overtone = 'fundamental'
        elif input.interactive_plot_overtone == 3:
            which_int_plot_overtone = '3rd'
        else:
            which_int_plot_overtone = str(input.interactive_plot_overtone) + 'th'

        try:
            y_rf = cleaned_df[f'{which_int_plot_overtone}_freq']
            y_dis = cleaned_df[f'{which_int_plot_overtone}_dis']
        except KeyError:
            print("frequency inputted to analyze in interactive plot, was not checked for processing in 'baseline corrected data'")
        
        # write peak frequencies depending on user indication of using theoretical or calibration vals to file for linear regression calculations
        if input.will_use_theoretical_vals: # if not using calibration data, copy theoreticals to txt file
            shutil.copy("calibration_data/theoretical_vals.txt", "calibration_data/peak_frequencies.txt")
        else:
            shutil.copy("calibration_data/calibration_peak_frequencies.txt", "calibration_data/peak_frequencies.txt")

        int_ax1.plot(x_time, y_rf, '.', color='green', markersize=1)
        int_ax2.plot(x_time, y_dis, '.', color='blue', markersize=1)
        zoom_plot1, = int_ax1_zoom.plot(x_time, y_rf, '.', color='green', markersize=1)
        zoom_plot2, = int_ax2_zoom.plot(x_time, y_dis, '.', color='blue', markersize=1)

        def onselect1(xmin, xmax):
            if input.which_range_selecting == '':
                print("** WARNING: NO RANGE SELECTED VALUES WILL NOT BE ACCOUNTED FOR")

            # min and max indices are where elements should be inserted to maintain order
            imin, imax = np.searchsorted(x_time, (xmin, xmax))
            # range will be at most all elems in x, or imax
            imax = min(len(x_time)-1, imax)

            # cursor x and y for zoomed plot and data range
            zoomx = x_time[imin:imax]
            zoomy1 = y_rf[imin:imax]

            # update data to newly spec'd range
            zoom_plot1.set_data(zoomx, zoomy1)
            
            # set limits of tick marks
            int_ax1_zoom.set_xlim(zoomx.min(), zoomx.max())
            int_ax1_zoom.set_ylim(zoomy1.min(), zoomy1.max())
            int_plot.canvas.draw_idle()

            # check if label and file already exists and remove if it does before writing new data for that range
            # this allows for overwriting of only the currently selected file and frequency,
            # without having to append all data, or overwrite all data each time
            save_flag = False
            try: # try to open df from stats csv
                temp_df = pd.read_csv("selected_ranges/all_stats_rf.csv")
                if '' in temp_df['range_used'].unique(): # remove potentially erroneous range inputs
                    temp_df = temp_df.loc[temp_df['range_used'] != '']
                    save_flag = True
                if input.which_range_selecting in temp_df['range_used'].unique()\
                and input.file_name in temp_df['data_source'].unique():
                    to_drop = temp_df.loc[((temp_df['range_used'] == input.which_range_selecting)\
                                        & (temp_df['data_source'] == input.file_name))].index.values
                    temp_df = temp_df.drop(index=to_drop)
                    save_flag = True
                if save_flag:
                    temp_df.to_csv("selected_ranges/all_stats_rf.csv", float_format="%.16E", index=False)
            except pd.errors.EmptyDataError: # if first time running, dataframe will be empty
                print("rf stats file empty")
                with open(f"selected_ranges/all_stats_rf.csv", 'a') as stat_file:
                    header = f"overtone,Dfreq_mean,Dfreq_std_dev,Dfreq_median,range_used,data_source\n"
                    stat_file.write(header)

            # save statistical data to file
            with open(f"selected_ranges/all_stats_rf.csv", 'a') as stat_file:
                # statistical analysis for all desired overtones using range of selection
                for overtone, val in input.which_plot['clean'].items():
                    # if value is true it was selected in gui, and we only want to analyze freqs here
                    if val and overtone.__contains__('freq'):
                        y_data = cleaned_df[overtone]
                        y_sel = y_data[imin:imax]
                        mean_y = np.average(y_sel)
                        std_dev_y = np.std(y_sel)
                        median_y = np.median(y_sel)
                        stat_file.write(f"{overtone},{mean_y:.16E},{std_dev_y:.16E},{median_y:.16E},{input.which_range_selecting},{input.file_name}\n")
            

        def onselect2(xmin, xmax):
            if input.which_range_selecting == '':
                print("** WARNING: NO RANGE SELECTED VALUES WILL NOT BE ACCOUNTED FOR")

            # min and max indices are where elements should be inserted to maintain order
            imin, imax = np.searchsorted(x_time, (xmin, xmax))
            # range will be at most all elems in x, or imax
            imax = min(len(x_time)-1, imax)

            # cursor x and y for zoomed plot and data range
            zoomx = x_time[imin:imax]
            zoomy2 = y_dis[imin:imax]

            # update data to newly spec'd range
            zoom_plot2.set_data(zoomx, zoomy2)
            
            # set limits of tick marks
            int_ax2_zoom.set_xlim(zoomx.min(), zoomx.max())
            int_ax2_zoom.set_ylim(zoomy2.min(), zoomy2.max())
            int_plot.canvas.draw_idle()

            # check if label and file already exists and remove if it does before writing new data for that range
            # this allows for overwriting of only the currently selected file and frequency,
            # without having to append all data, or overwrite all data each time
            save_flag = False
            try: # try to open df from stats csv
                temp_df = pd.read_csv("selected_ranges/all_stats_dis.csv")
                if '' in temp_df['range_used'].unique(): # remove potentially erroneous range inputs
                    temp_df = temp_df.loc[temp_df['range_used'] != '']
                    save_flag = True
                if input.which_range_selecting in temp_df['range_used'].unique()\
                and input.file_name in temp_df['data_source'].unique():
                    to_drop = temp_df.loc[((temp_df['range_used'] == input.which_range_selecting)\
                                        & (temp_df['data_source'] == input.file_name))].index.values
                    temp_df = temp_df.drop(index=to_drop)
                    save_flag = True
                if save_flag:
                    temp_df.to_csv("selected_ranges/all_stats_dis.csv", float_format="%.16E", index=False)
            except pd.errors.EmptyDataError: # if first time running, dataframe will be empty
                print("dis stats file empty")
                with open(f"selected_ranges/all_stats_dis.csv", 'a') as stat_file:
                    header = f"overtone,Ddis_mean,Ddis_std_dev,Ddis_median,range_used,data_source\n"
                    stat_file.write(header)


            # save statistical data to file
            with open(f"selected_ranges/all_stats_dis.csv", 'a') as stat_file:
                # statistical analysis for all desired overtones using range of selection
                for overtone, val in input.which_plot['clean'].items():
                    # if value is true it was selected in gui, and we only want to analyze freqs here
                    if val and overtone.__contains__('dis'):
                        y_data = cleaned_df[overtone]
                        y_sel = y_data[imin:imax]
                        y_temp_sel = y_sel / 1000000 # unit conversion since multiplied up by 10^6 earlier in code
                        mean_y = np.average(y_temp_sel)
                        std_dev_y = np.std(y_temp_sel)
                        median_y = np.median(y_temp_sel)
                        stat_file.write(f"{overtone},{mean_y:.16E},{std_dev_y:.16E},{median_y:.16E},{input.which_range_selecting},{input.file_name}\n")

        # using plt's span selector to select area of top plot
        span1 = SpanSelector(int_ax1, onselect1, 'horizontal', useblit=True,
                    props=dict(alpha=0.5, facecolor='blue'),
                    interactive=True, drag_from_anywhere=True)

        span2 = SpanSelector(int_ax2, onselect2, 'horizontal', useblit=True,
                    props=dict(alpha=0.5, facecolor='blue'),
                    interactive=True, drag_from_anywhere=True)

        plt.show()


    # clear plots and lists for next iteration
    clean_freqs.clear()
    clean_disps.clear()
    print("*** Plots Generated ***")


if __name__ == '__main__':
    analyze_data(input)