"""
Author: Brandon Pardi
Created: 9/7/2022, 12:40 pm
Last Modified: 11/28/2022 6:57 pm
"""

from tkinter import *
import sys
from datetime import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from scipy.optimize import curve_fit
from datetime import datetime


'''
README
- Please execute 'install_packages.py' BEFORE running this script
- when done with program, please click 'Abort' button instead of closing window
    - can cause terminal to freeze sometimes otherwise
- ensure all sheets are in the 'raw_data' folder
    - OR specify file directory in gui
- consistency in column placement and naming is required, however columns will be renamed
- if error occurs, it will be displayed in the terminal
- if uncaught error occurs, please notify me asap and describe what was done to reproduce
- specify in GUI:
    - file name (with exetension)
    - file path (if not in predefined raw_data directory)
    - indicate if new clean data file should be created
    - if plotting clean data, indicate baseline t0 and tf
    - SUBMIT FILE INFO
    - indicate which channels to plot for raw/clean data
    - indicate which special plot options
    - change scale of time if applicable
    - change file format if applicable

- For interactive plot:
    - whichever overtone is to be analyzed in the interactive plot, 
    ensure that that overtone is selected in the baseline corrected data section as well,
    as it relies on the cleaned data processing done there
    - currently only 3rd freqeuncy is available for processing with interative plot
        - option to select will come later
    - selected range is displayed in lower portion of figure, and data points written to 'selected_data.txt'
    - save multiple ranges
        - if interactive plot selected, open small new window,
        - new window will show radio buttons to indiciate which range is being selected
        - input from entry box will correlate to which file for which range is being selected
    


FUNCTIONS
- opens 'py' to define information
- opens defined file and reads it into a dataframe
- renames columns as dictated below in Variable Declarations section
- checks which_plot to determine which channels are being analyzed, and adds to lists accordingly
Clean Data:
    - find average resonant frequency of baseline, and lowers curve by that amount
    - cleans data by removing points before baseline, and lowers by aforemention average
- plots are frequencies and dissipations of each channel specified in py
- if overwrite file selected, will replace file data with the data it had just cleaned
    - Not advised if not selecting ALL plots
- plots raw data individually as specified in gui
- option to normalize data by dividing frequency by its respective overtone
- option to plot change in dissipation vs change in frequency
- option for multi axis plot with change in frequency and dissipation vs time
- option for interactive plot that opens figure of selected overtone to further analyze
    - can select a range of points of plot to zoom in and save to file for later


GUI features
- file name box (later maybe window to search for file)
- checkbox for each frequency being plotted
    - checkbox for raw and clean data
        - raw data plots are individual for overtone of each freq/dis
- abs base time t0, tf
- input for scale of time (seconds, minutes, hours)
- alternate plot options:
    - plot dF and dD together
    - normalize F
    - dD vs dF
- interactive plot selection option
- submit button runs data analysis while keeping gui window open


WIP
- for interactive plot
    - allow specification of which overtone and freq or disp
    - calculate mean, median, range of each range and put into single file
    - format int plot akin to existing saved plots
- data modeling
- small bugs
    - when submitting after first time,
    if range select window was closed, will not reopen
    - when selecting range in freq, it changes range is dis,
    but not vice versa
- ERROR CHECKING?
    - account for error if can't find valid time
    - when inputting time, check for nearest time value,
    in case time value not actually in data sheet
- refactoring (putting into frames etc)
- put columns into separate frames and refactor code to accomodate
    - i.e. remove all grid forgets and replace them with grid_forgets of that frame to simplify and scale


MEETING QUESTIONS
- interactive plot
    - do we want rf and dis in plot,
    or have 1 or the other paired with its raw data
    - do we need all the data from the span selector,
    or just have it do the calculations and put into file
'''


'''Variable Initializations'''
file_name = ''
file_path = ''
will_plot_raw_data = False
will_plot_clean_data = False
will_overwrite_file = False
abs_base_t0 = time(0, 0, 0)
abs_base_tf = time(0, 0, 0)
fig_format = 'png'
x_timescale = 's'
will_plot_dF_dD_together = False
will_normalize_F = False
will_plot_dD_v_dF = False
will_interactive_plot = False
submit_pressed = False
which_range_selecting = 'base'
which_plot = {'raw': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                    '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                    '9th_freq': False, '9th_dis': False},

            'clean': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                    '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                    '9th_freq': False, '9th_dis': False}}


'''Function Defintions for UI events'''
def col_names_submit():
    global file_name
    global file_path
    file_name = file_name_entry.get()
    file_path = file_path_entry.get()
    global will_overwrite_file
    if file_overwrite_var.get() == 1:
        will_overwrite_file = True
    else:
        will_overwrite_file = False

    global abs_base_t0
    global abs_base_tf
    h0 = hours_entry_t0.get()
    m0 = minutes_entry_t0.get()
    s0 = seconds_entry_t0.get()
    hf = hours_entry_tf.get()
    mf = minutes_entry_tf.get()
    sf = seconds_entry_tf.get()
    if(h0 == '' and m0 == '' and s0 == ''):
        h0 = 0
        m0 = 0
        s0 = 0
    if(hf == '' and mf == '' and sf == ''):
        hf = 0
        mf = 0
        sf = 0
    try:
        abs_base_t0 = time(int(h0),int(m0),int(s0))
        abs_base_tf = time(int(hf),int(mf),int(sf))
    except ValueError as exc:
        err_label.grid(row=20, column=0)
        print(f"Please enter integer values for time: {exc}")
    submitted_label.grid(row=13, column=0)

def clear_file_data():
    global file_name
    global file_path
    global abs_base_t0
    global abs_base_tf
    abs_base_t0 = time(0, 0, 0)
    abs_base_tf = time(0, 0, 0)
    cleared_label.grid(row=12, column=0)
    file_name_entry.delete(0, END)
    file_path_entry.delete(0, END)
    hours_entry_t0.delete(0, END)
    minutes_entry_t0.delete(0, END)
    seconds_entry_t0.delete(0, END)
    hours_entry_tf.delete(0, END)
    minutes_entry_tf.delete(0, END)
    seconds_entry_tf.delete(0, END)
    file_overwrite_var.set(0)

def handle_fn_focus_in(_):
    if file_name_entry.get() == "File name here (W/ EXTENSION)":
        file_name_entry.delete(0, END)
        file_name_entry.config(fg='black')

def handle_fn_focus_out(_):
    if file_name_entry.get() == "":
        file_name_entry.delete(0, END)
        file_name_entry.config(fg='gray')
        file_name_entry.insert(0, "File name here (W/ EXTENSION)")

def handle_fp_focus_in(_):
    if file_path_entry.get() == "Enter path to file (leave blank if in 'raw data' folder)":
        file_path_entry.delete(0, END)
        file_path_entry.config(fg='black')

def handle_fp_focus_out(_):
    if file_path_entry.get() == "":
        file_path_entry.delete(0, END)
        file_path_entry.config(fg='gray')
        file_path_entry.insert(0, "Enter path to file (leave blank if in 'raw data' folder)")    

def clear_raw_checks():
    raw_ch1_freq_var.set(0)
    raw_ch1_dis_var.set(0)
    raw_ch2_freq_var.set(0)
    raw_ch2_dis_var.set(0)
    raw_ch3_freq_var.set(0)
    raw_ch3_dis_var.set(0)
    raw_ch4_freq_var.set(0)
    raw_ch4_dis_var.set(0)
    raw_ch5_freq_var.set(0)
    raw_ch5_dis_var.set(0)
    for channel in which_plot['raw']:
        which_plot['raw'][channel] = False
        
def select_all_raw_checks():
    raw_ch1_freq_var.set(1)
    raw_ch1_dis_var.set(1)
    raw_ch2_freq_var.set(1)
    raw_ch2_dis_var.set(1)
    raw_ch3_freq_var.set(1)
    raw_ch3_dis_var.set(1)
    raw_ch4_freq_var.set(1)
    raw_ch4_dis_var.set(1)
    raw_ch5_freq_var.set(1)
    raw_ch5_dis_var.set(1)
    for channel in which_plot['raw']:
        which_plot['raw'][channel] = True

def clear_clean_checks():
    clean_ch1_freq_var.set(0)
    clean_ch1_dis_var.set(0)
    clean_ch2_freq_var.set(0)
    clean_ch2_dis_var.set(0)
    clean_ch3_freq_var.set(0)
    clean_ch3_dis_var.set(0)
    clean_ch4_freq_var.set(0)
    clean_ch4_dis_var.set(0)
    clean_ch5_freq_var.set(0)
    clean_ch5_dis_var.set(0)
    for channel in which_plot['clean']:
        which_plot['clean'][channel] = False

def select_all_clean_checks():
    clean_ch1_freq_var.set(1)
    clean_ch1_dis_var.set(1)
    clean_ch2_freq_var.set(1)
    clean_ch2_dis_var.set(1)
    clean_ch3_freq_var.set(1)
    clean_ch3_dis_var.set(1)
    clean_ch4_freq_var.set(1)
    clean_ch4_dis_var.set(1)
    clean_ch5_freq_var.set(1)
    clean_ch5_dis_var.set(1)
    for channel in which_plot['clean']:
        which_plot['clean'][channel] = True

def receive_raw_checkboxes():
    global will_plot_raw_data
    global which_plot

    if plot_raw_data_var.get() == 1:
        will_plot_raw_data = True
        which_raw_channels_label.grid(row=1, column=2, pady=(0,26))
        select_all_raw_checks_button.grid(row=19, column=2, padx=(0,0), pady=(12,4))
        clear_raw_checks_button.grid(row=20, column=2, padx=(0,0), pady=(4,4))
        raw_ch1_freq_check.grid(row=2, column=2)
        raw_ch1_dis_check.grid(row=3, column=2)
        raw_ch2_freq_check.grid(row=4, column=2)
        raw_ch2_dis_check.grid(row=5, column=2)
        raw_ch3_freq_check.grid(row=6, column=2)
        raw_ch3_dis_check.grid(row=7, column=2)
        raw_ch4_freq_check.grid(row=8, column=2)
        raw_ch4_dis_check.grid(row=9, column=2)
        raw_ch5_freq_check.grid(row=10, column=2)
        raw_ch5_dis_check.grid(row=11, column=2)

        if raw_ch1_freq_var.get() == 1:
            which_plot['raw']['fundamental_freq'] = True
        else:
            which_plot['raw']['fundamental_freq'] = False

        if raw_ch1_dis_var.get() == 1:
            which_plot['raw']['fundamental_dis'] = True
        else:
            which_plot['raw']['fundamental_dis'] = False

        if raw_ch2_freq_var.get() == 1:
            which_plot['raw']['3rd_freq'] = True
        else:
            which_plot['raw']['3rd_freq'] = False

        if raw_ch2_dis_var.get() == 1:
            which_plot['raw']['3rd_dis'] = True
        else:
            which_plot['raw']['3rd_dis'] = False

        if raw_ch3_freq_var.get() == 1:
            which_plot['raw']['5th_freq'] = True
        else:
            which_plot['raw']['5th_freq'] = False

        if raw_ch3_dis_var.get() == 1:
            which_plot['raw']['5th_dis'] = True
        else:
            which_plot['raw']['5th_dis'] = False

        if raw_ch4_freq_var.get() == 1:
            which_plot['raw']['7th_freq'] = True
        else:
            which_plot['raw']['7th_freq'] = False

        if raw_ch4_dis_var.get() == 1:
            which_plot['raw']['7th_dis'] = True
        else:
            which_plot['raw']['7th_dis'] = False

        if raw_ch5_freq_var.get() == 1:
            which_plot['raw']['9th_freq'] = True
        else:
            which_plot['raw']['9th_freq'] = False

        if raw_ch5_dis_var.get() == 1:
            which_plot['raw']['9th_dis'] = True
        else:
            which_plot['raw']['9th_dis'] = False

    else:
        will_plot_raw_data = False
        which_raw_channels_label.grid_forget()
        raw_ch1_freq_check.grid_forget()
        raw_ch1_dis_check.grid_forget()
        raw_ch2_freq_check.grid_forget()
        raw_ch2_dis_check.grid_forget()
        raw_ch3_freq_check.grid_forget()
        raw_ch3_dis_check.grid_forget()
        raw_ch4_freq_check.grid_forget()
        raw_ch4_dis_check.grid_forget()
        raw_ch5_freq_check.grid_forget()
        raw_ch5_dis_check.grid_forget()
        select_all_raw_checks_button.grid_forget()
        clear_raw_checks_button.grid_forget()

def receive_clean_checkboxes():
    global will_plot_clean_data
    global which_plot
    if plot_clean_data_var.get() == 1:
        will_plot_clean_data = True
        which_clean_channels_label.grid(row=1, column=3, pady=(0,12))
        select_all_clean_checks_button.grid(row=19, column=3, padx=(0,0), pady=(12,4))
        clear_clean_checks_button.grid(row=20, column=3, padx=(0,0), pady=(4,4))
        clean_ch1_freq_check.grid(row=2, column=3)
        clean_ch1_dis_check.grid(row=3, column=3)
        clean_ch2_freq_check.grid(row=4, column=3)
        clean_ch2_dis_check.grid(row=5, column=3)
        clean_ch3_freq_check.grid(row=6, column=3)
        clean_ch3_dis_check.grid(row=7, column=3)
        clean_ch4_freq_check.grid(row=8, column=3)
        clean_ch4_dis_check.grid(row=9, column=3)
        clean_ch5_freq_check.grid(row=10, column=3)
        clean_ch5_dis_check.grid(row=11, column=3)

        if clean_ch1_freq_var.get() == 1:
            which_plot['clean']['fundamental_freq'] = True
        else:
            which_plot['clean']['fundamental_freq'] = False

        if clean_ch1_dis_var.get() == 1:
            which_plot['clean']['fundamental_dis'] = True
        else:
            which_plot['clean']['fundamental_dis'] = False

        if clean_ch2_freq_var.get() == 1:
            which_plot['clean']['3rd_freq'] = True
        else:
            which_plot['clean']['3rd_freq'] = False

        if clean_ch2_dis_var.get() == 1:
            which_plot['clean']['3rd_dis'] = True
        else:
            which_plot['clean']['3rd_dis'] = False

        if clean_ch3_freq_var.get() == 1:
            which_plot['clean']['5th_freq'] = True
        else:
            which_plot['clean']['5th_freq'] = False

        if clean_ch3_dis_var.get() == 1:
            which_plot['clean']['5th_dis'] = True
        else:
            which_plot['clean']['5th_dis'] = False

        if clean_ch4_freq_var.get() == 1:
            which_plot['clean']['7th_freq'] = True
        else:
            which_plot['clean']['7th_freq'] = False

        if clean_ch4_dis_var.get() == 1:
            which_plot['clean']['7th_dis'] = True
        else:
            which_plot['clean']['7th_dis'] = False

        if clean_ch5_freq_var.get() == 1:
            which_plot['clean']['9th_freq'] = True
        else:
            which_plot['clean']['9th_freq'] = False

        if clean_ch5_dis_var.get() == 1:
            which_plot['clean']['9th_dis'] = True
        else:
            which_plot['clean']['9th_dis'] = False

    else:
        will_plot_clean_data = False
        which_clean_channels_label.grid_forget()
        clean_ch1_freq_check.grid_forget()
        clean_ch1_dis_check.grid_forget()
        clean_ch2_freq_check.grid_forget()
        clean_ch2_dis_check.grid_forget()
        clean_ch3_freq_check.grid_forget()
        clean_ch3_dis_check.grid_forget()
        clean_ch4_freq_check.grid_forget()
        clean_ch4_dis_check.grid_forget()
        clean_ch5_freq_check.grid_forget()
        clean_ch5_dis_check.grid_forget()
        select_all_clean_checks_button.grid_forget()
        clear_clean_checks_button.grid_forget()

def receive_scale_radios():
    global x_timescale
    if scale_time_var.get() == 1:
        time_scale_frame.grid(row=0, column=4)
        if which_time_scale_var.get() == 1:
            x_timescale = 's'
        elif which_time_scale_var.get() == 2:
            x_timescale = 'm'
        elif which_time_scale_var.get() == 3:
            x_timescale = 'h'
        else:
            x_timescale= 'u'
    else:
        time_scale_frame.grid_forget()
        x_timescale = 's'

def receive_file_format_radios():
    global fig_format
    if change_fig_format_var.get() == 1:
        file_format_frame.grid(row=0, column=4)
        if which_file_format_var.get() == 1:
            fig_format = 'png'
        elif which_file_format_var.get() == 2:
            fig_format = 'tiff'
        elif which_file_format_var.get() == 3:
            fig_format = 'pdf'
        else:
            fig_format = 'u'
    else:
        file_format_frame.grid_forget()
        fig_format = 'png'

def receive_optional_checkboxes():
    global will_plot_dF_dD_together
    global will_normalize_F
    global will_plot_dD_v_dF
    global will_interactive_plot

    if plot_dF_dD_together_var.get() == 1:
        will_plot_dF_dD_together = True
    else:
        will_plot_dF_dD_together = False

    if normalize_F_var.get() == 1:
        will_normalize_F = True
    else:
        will_normalize_F = False

    if plot_dD_v_dF_var.get() == 1:
        will_plot_dD_v_dF = True
    else:
        will_plot_dD_v_dF = False

    if interactive_plot_var.get() == 1:
        will_interactive_plot = True
    else:
        will_interactive_plot = False

def err_check():
    global file_name
    global file_path

    '''Verify File Info'''
    # make sure file name was inputted
    if (file_name == '' or file_name == 'File name here (W/ EXTENSION)'):
        print("File name not specified")
        sys.exit(1)

    if file_path == "Enter path to file (leave blank if in 'raw data' folder)":
        file_path = ""

    # verify baseline time entered, if only raw data box checked, no need to base time
    if will_plot_clean_data and abs_base_t0 == time(0,0,0) and abs_base_tf == time(0,0,0):
        print("User indicated plot clean data,\ndid not enter baseline time")
        sys.exit(1)

    #verify data checks
    # find num channels tested
    clean_num_channels_tested = 0
    raw_num_channels_tested = 0

    for channel in which_plot['raw'].items():
        if channel[1] == True:
            raw_num_channels_tested += 1

    for channel in which_plot['clean'].items():
        if channel[1] == True:
            clean_num_channels_tested += 1

    total_num_channels_tested = raw_num_channels_tested + clean_num_channels_tested
    # check if any channels were selected to test
    if total_num_channels_tested == 0:
        print("User did not select any channels to plot")
        sys.exit(1)

    # check if clean data was chosen, but no clean channels selected
    if will_plot_clean_data and clean_num_channels_tested == 0:
        print("User indicated to plot clean channels,\ndid not indicate which")
        sys.exit(1)

    # check if raw data was chosen, but no raw data was selected
    if will_plot_raw_data and raw_num_channels_tested == 0:
        print("User indicated to plot raw channels,\ndid not indicate which")
        sys.exit(1)

    # verify options
    if x_timescale == 'u':
        print("User indicated to change timescale,\nbut did not specify what scale")
        sys.exit(1)

    if fig_format == 'u':
        print("User indicated to change fig format,\nbut did not specify which")
        sys.exit(1)

def analyze_data():
    '''Variable Declarations'''
    abs_time_col = 'Time'
    rel_time_col = 'Relative_time'
    freqs = ['fundamental_freq', '3rd_freq', '5th_freq', '7th_freq', '9th_freq']
    disps = ['fundamental_dis', '3rd_dis', '5th_dis', '7th_dis', '9th_dis']
    t0_str = str(abs_base_t0).lstrip('0')
    tf_str = str(abs_base_tf).lstrip('0')

    # Some plot labels
    dis_fig_y = "Change in dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")"
    rf_fig_y = "Change in frequency, " + '$\it{Δf}$' + " (Hz)"


    # grab singular file and create dataframe from it
    if file_path == "":
        df = pd.read_csv(f"raw_data/{file_name}")
    else:
        df = pd.read_csv(f"{file_path}/{file_name}")

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

    # assign colors to overtones
    color_map_freq = {'fundamental_freq':'blue', '3rd_freq':'orange', '5th_freq':'green', '7th_freq':'red', '9th_freq':'purple'}
    color_map_dis = {'fundamental_dis':'blue', '3rd_dis':'orange', '5th_dis':'green', '7th_dis':'red', '9th_dis':'purple'}

    # function fills list of channels selected to be clean plot from gui
    def get_channels(scrub_level):
        freq_list = []
        disp_list = []
            
        for channel in which_plot[scrub_level].items():
            # dict entry for that channel is true then append to list
            if channel[1] == True:
                # check if channel looking at is a frequency or dissipation and append approppriately
                if channel[0].__contains__('freq'):
                    freq_list.append(channel[0])
                elif channel[0].__contains__('dis'):
                    disp_list.append(channel[0])

        return (freq_list, disp_list)

    def determine_xlabel():
        if x_timescale == 's':
            return "Time, " + '$\it{Δt}$' + " (s)"
        elif x_timescale == 'm':
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
            plt.figure(fig_num).savefig(fn + '.' + fig_format, format=fig_format, bbox_inches='tight', transparent=True, dpi=400)

    '''Cleaning Data and plotting clean data'''
    if will_plot_clean_data:
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
            baseline_dur = datetime.combine(datetime.min, abs_base_tf) - datetime.combine(datetime.min, abs_base_t0)
            # locate where baseline starts/ends
            base_t0_ind = data_df[data_df[abs_time_col].str.contains(t0_str)].index[0]
            # remove everything before baseline
            data_df = data_df[base_t0_ind:]
            data_df = data_df.reset_index(drop=True)

            # normalize by overtone
            if will_normalize_F:
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
            # shift x to left to start at 0
            data_df[rel_time_col] -= data_df[rel_time_col].iloc[0]

            # choose appropriate divisor for x scale of time
            if x_timescale == 'm':
                divisor = 60
            elif x_timescale == 'h':
                divisor = 3600
            else:
                divisor = 1
            #x_time = [num / divisor for num in x_time]
            data_df[rel_time_col] /= divisor
            x_time = data_df[rel_time_col]
            y_rf = data_df[clean_freqs[i]]
            # scale disipation by 10^6
            data_df[clean_disps[i]] *= 1000000
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
            if will_plot_dD_v_dF:
                plt.figure(5, clear=False)
                plt.plot(y_rf, y_dis, '.', markersize=1, label=f"{clean_disps[i]} vs {clean_freqs[i]}")
            
            # multi axis plot for change in freq and change in dis vs time
            if will_plot_dF_dD_together:
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

            # # put cleaned data back into original df for interactive plot
            if will_overwrite_file or will_interactive_plot:
                if i == 0:
                    cleaned_df = data_df[[abs_time_col,rel_time_col]]
                cleaned_df = pd.concat([cleaned_df,data_df[clean_freqs[i]]], axis=1)
                cleaned_df = pd.concat([cleaned_df,data_df[clean_disps[i]]], axis=1)


        if will_overwrite_file:
            print(df.head())
            df.to_csv(f"raw_data/CLEANED-{file_name}", index=False)

        # Titles, lables, etc. for plots
        if will_normalize_F:
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
        if will_plot_dD_v_dF:
            dVf_fn = f"qcmd-plots/disp_V_freq-plot"
            dVf_title = "Dissipiation against Frequency"
            setup_plot(5, rf_fig_y, dis_fig_y, dis_fig_title, dVf_fn, True)


    # Gathering raw data for individual plots
    if will_plot_raw_data:
        # plot definitions
        rf_fig_title = "RAW QCM-D Resonant Frequency"
        rf_fig_y = "Change in frequency, " + '$\it{Δf}$' + " (Hz)"
        rf_fig_x = determine_xlabel()

        dis_fig_title = "RAW QCM-D Dissipation"
        dis_fig_y = "Change in dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")"
        dis_fig_x = rf_fig_x


        raw_freqs, raw_disps = get_channels('raw')
        # gather and plot raw frequency data
        for i in range(len(raw_freqs)):
            rf_data_df = df[[abs_time_col,rel_time_col,raw_freqs[i]]]
            rf_data_df = rf_data_df.dropna(axis=0, how='any', inplace=False)
            x_time = rf_data_df[rel_time_col]
            y_rf = rf_data_df[raw_freqs[i]]
            plt.figure(3, clear=True)
            plt.plot(x_time, y_rf, '.', markersize=1, label=f"raw resonant freq - {i}", color=color_map_freq[clean_freqs[i]])
            rf_fn = f"qcmd-plots/RAW-resonant-freq-plot-{raw_freqs[i]}"
            setup_plot(3, rf_fig_x, rf_fig_y, rf_fig_title, rf_fn)
            plt.figure(3).savefig(rf_fn + '.' + fig_format, format=fig_format, bbox_inches='tight', transparent=True, dpi=400)

        # gather and plot raw dissipation data
        for i in range(len(raw_disps)):
            dis_data_df = df[[abs_time_col,rel_time_col,raw_disps[i]]]
            dis_data_df = dis_data_df.dropna(axis=0, how='any', inplace=False)
            x_time = dis_data_df[rel_time_col]
            y_dis = dis_data_df[raw_disps[i]]
            plt.figure(4, clear=True)
            plt.plot(x_time, y_dis, '.', markersize=1, label=f"raw dissipation - {i}", color=color_map_dis[clean_disps[i]])
            dis_fn = f"qcmd-plots/RAW-dissipation-plot-{raw_freqs[i]}"
            setup_plot(4, dis_fig_x, dis_fig_y, dis_fig_title, dis_fn)
            plt.figure(4).savefig(dis_fn + '.' + fig_format, format=fig_format, bbox_inches='tight', transparent=True, dpi=400)

    # interactive plot
    if will_interactive_plot:
        # clear all previous plots
        plt.close("all")
        # setup plot objects
        int_plot = plt.figure()
        int_plot.set_figwidth(10)
        int_plot.set_figheight(5)
        # nrows, ncols, position (like quadrants from l -> r)
        int_ax1 = int_plot.add_subplot(2,2,1)
        int_ax2 = int_plot.add_subplot(2,2,2)
        
        # grab data
        x_time = cleaned_df[rel_time_col]
        y_rf = cleaned_df['3rd_freq']
        y_dis = cleaned_df['3rd_dis']
        
        int_ax1.plot(x_time, y_rf, '.', color='green', markersize=1)
        int_ax2.plot(x_time, y_dis, '.', color='blue', markersize=1)
        int_ax1.set_title("Click and drag to select range")

        int_ax1_zoom = int_plot.add_subplot(2,2,3)
        int_ax2_zoom = int_plot.add_subplot(2,2,4)
        zoom_plot1, = int_ax1_zoom.plot(x_time, y_rf, '.', color='green', markersize=1)
        zoom_plot2, = int_ax2_zoom.plot(x_time, y_dis, '.', color='blue', markersize=1)


        def onselect1(xmin, xmax):
            # min and max indices are where elements should be inserted to maintain order
            imin, imax = np.searchsorted(x_time, (xmin, xmax))
            # range will be at most all elems in x, or imax
            imax = min(len(x_time)-1, imax)

            # cursor x and y for zoomed plot and data range
            zoomx = x_time[imin:imax]
            zoomy1 = y_rf[imin:imax]
            zoomy2 = y_dis[imin:imax]

            # update data to newly spec'd range
            zoom_plot1.set_data(zoomx, zoomy1)
            zoom_plot2.set_data(zoomx, zoomy2)
            print(zoomx)
            
            # set limits of tick marks
            int_ax1_zoom.set_xlim(zoomx.min(), zoomx.max())
            int_ax1_zoom.set_ylim(zoomy1.min(), zoomy1.max())
            int_ax2_zoom.set_xlim(zoomx.min(), zoomx.max())
            int_ax2_zoom.set_ylim(zoomy2.min(), zoomy2.max())
            int_plot.canvas.draw_idle()

            # statistical analysis
            mean_freq_x = np.average(zoomx)
            std_dev_freq_x = np.std(zoomx)
            median_freq_x = np.median(zoomx)
            mean_freq_y = np.average(zoomy1)
            std_dev_freq_y = np.std(zoomy1)
            median_freq_y = np.median(zoomy1)

            # save data range to file
            np.savetxt(f"selected_ranges/range_{which_range_selecting}_rf.txt", np.c_[zoomx, zoomy1])

            # save statistical data to file
            with open(f"selected_ranges/stats_{which_range_selecting}_rf.txt", 'w') as stat_file:
                stat_file.write(f"Time:\nmean: {mean_freq_x}\nstd dev: {std_dev_freq_x}\n\
median: {median_freq_x}\n\nDissipation:\nmean: {mean_freq_y}\n\
std dev: {std_dev_freq_y}\nmedian: {median_freq_y}")

        def onselect2(xmin, xmax):
            # min and max indices are where elements should be inserted to maintain order
            imin, imax = np.searchsorted(x_time, (xmin, xmax))
            # range will be at most all elems in x, or imax
            imax = min(len(x_time)-1, imax)

            # cursor x and y for zoomed plot and data range
            zoomx = x_time[imin:imax]
            zoomy2 = y_dis[imin:imax]

            # update data to newly spec'd range
            zoom_plot2.set_data(zoomx, zoomy2)
            print(zoomx)
            
            # set limits of tick marks
            int_ax2_zoom.set_xlim(zoomx.min(), zoomx.max())
            int_ax2_zoom.set_ylim(zoomy2.min(), zoomy2.max())
            int_plot.canvas.draw_idle()

            # statistical analysis
            mean_dis_x = np.average(zoomx)
            std_dev_dis_x = np.std(zoomx)
            median_dis_x = np.median(zoomx)
            mean_dis_y = np.average(zoomy2)
            std_dev_dis_y = np.std(zoomy2)
            median_dis_y = np.median(zoomy2)

            # save data range to file
            np.savetxt(f"selected_ranges/range_{which_range_selecting}_dis.txt", np.c_[zoomx, zoomy2])

            # save statistical data to file
            with open(f"selected_ranges/stats_{which_range_selecting}_dis.txt", 'w') as stat_file:
                stat_file.write(f"Time:\nmean: {mean_dis_x}\nstd dev: {std_dev_dis_x}\n\
median: {median_dis_x}\n\nDissipation:\nmean: {mean_dis_y}\n\
std dev: {std_dev_dis_y}\nmedian: {median_dis_y}")

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


def abort():
    sys.exit()

def submit():
    err_check()

    # only want new window to open once, not every time analysis is run
    global submit_pressed
    # open secondary window with range selections for interactive plot
    if interactive_plot_var.get() == 1 and submit_pressed == False:
        submit_pressed = True
        range_select_window = Toplevel(root)
        range_select_window.title("Select range")
        range_label = Label(range_select_window, text="Choose which section of graph\nis being selected for file saving:")
        range_label.grid(row=0, column=0, padx=10, pady=(8,16))
        
        # define and place radio buttons for range options
        range_num_label = Label(range_select_window, text="Enter which range being selected\n(in order from left to right starting with 1)" )
        range_num_label.grid(row=2, column=0, pady=(2,4), padx=4)
        range_num_entry = Entry(range_select_window, width=10, bg='white')
        range_num_entry.grid(row=3, column=0, pady=(2,4))

        # when interactive plot window opens, grabs number of range from text field
        def confirm_range():
            global which_range_selecting
            which_range_selecting = int(range_num_entry.get())
                

        # button to submit range selected
        range_num_submit = Button(range_select_window, text='Confirm Range', padx=4, pady=2, command=confirm_range)
        range_num_submit.grid(row=4, column=0)

    analyze_data()



'''Enter event loop for UI'''
root = Tk()
col0 = Frame(root)
col1 = Frame(root)
col2 = Frame(root)
col3 = Frame(root)
fr = Frame(col0)
fr2 = Frame(col3)
fr3 = Frame(col3)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

col0.grid(row=0, column=0, sticky='nsew', padx=(10,4), pady=(4,20))
col1.grid(row=0, column=1, sticky='nsew', padx=(4,4), pady=(4,10))
col2.grid(row=0, column=2, sticky='nsew', padx=(4,4), pady=(4,10))
col3.grid(row=0, column=3, sticky='nsew', padx=(4,10), pady=(4,10))
fr.grid(row=7, column=0, rowspan=2)
fr2.grid(row=8, column=4)
fr3.grid(row=15, column=4)

# change program icon
icon = PhotoImage(file="m3b_comp.png")
root.iconphoto(False, icon)
root.title('Quartz Mech Processing')

# define and place file info labels and buttons
# FIRST COLUMN ELEMENTS (file data)
file_name_label = Label(col0, text="Enter data file information", font=('TkDefaultFont', 12, 'bold'))
file_name_label.grid(row=0, column=0, pady=(14,16), padx=(6,0))
cleared_label = Label(col0, text="Cleared!")
submitted_label = Label(col0, text="Submitted!")
err_label = Label(col0, text="Error occured,\nplease see terminal for details", font=("Arial",14))

file_name_entry = Entry(col0, width=40, bg='white', fg='gray')
file_name_entry.grid(row=2, column=0, columnspan=1, padx=8, pady=4)
#file_name_entry.insert(0, "File name here (W/ EXTENSION)")
file_name_entry.insert(0, "10102022_Collagen 2 at 25ug per ml and SF at 37C_n=1 DD.csv")
file_name_entry.bind("<FocusIn>", handle_fn_focus_in)
file_name_entry.bind("<FocusOut>", handle_fn_focus_out)

file_path_entry = Entry(col0, width=40, bg='white', fg='gray')
file_path_entry.grid(row=3, column=0, columnspan=1, padx=8, pady=4)
file_path_entry.insert(0, "Enter path to file (leave blank if in 'raw data' folder)")
file_path_entry.bind("<FocusIn>", handle_fp_focus_in)
file_path_entry.bind("<FocusOut>", handle_fp_focus_out)

file_overwrite_var = IntVar()
file_overwrite_check = Checkbutton(col0, text='New file with processed data?', variable=file_overwrite_var, onvalue=1, offvalue=0, pady=10)
file_overwrite_check.grid(row=5, column=0)

baseline_frame = Frame(fr)
baseline_time_label = Label(col0, text="Enter absolute baseline time")
baseline_time_label.grid(row=6, column=0)

baseline_frame.grid(row=7, column=0, columnspan=1)
hours_label_t0 = Label(baseline_frame, text="H0: ")
hours_label_t0.grid(row=0, column=0)
hours_entry_t0 = Entry(baseline_frame, width=5, bg='white', fg='gray')
hours_entry_t0.grid(row=0, column=1)
minutes_label_t0 = Label(baseline_frame, text="M0: ")
minutes_label_t0.grid(row=0, column=2)
minutes_entry_t0 = Entry(baseline_frame, width=5, bg='white', fg='gray')
minutes_entry_t0.grid(row=0, column=3)
seconds_label_t0 = Label(baseline_frame, text="S0: ")
seconds_label_t0.grid(row=0, column=4)
seconds_entry_t0 = Entry(baseline_frame, width=5, bg='white', fg='gray')
seconds_entry_t0.grid(row=0, column=5)

hours_label_tf = Label(baseline_frame, text="Hf: ")
hours_label_tf.grid(row=1, column=0)
hours_entry_tf = Entry(baseline_frame, width=5, bg='white', fg='gray')
hours_entry_tf.grid(row=1, column=1)
minutes_label_tf = Label(baseline_frame, text="Mf: ")
minutes_label_tf.grid(row=1, column=2)
minutes_entry_tf = Entry(baseline_frame, width=5, bg='white', fg='gray')
minutes_entry_tf.grid(row=1, column=3)
seconds_label_tf = Label(baseline_frame, text="Sf: ")
seconds_label_tf.grid(row=1, column=4)
seconds_entry_tf = Entry(baseline_frame, width=5, bg='white', fg='gray')
seconds_entry_tf.grid(row=1, column=5)

#temp inserts to not have to reenter data every test
seconds_entry_t0.insert(0, "26")
minutes_entry_t0.insert(0, "2")
hours_entry_t0.insert(0, "17")
seconds_entry_tf.insert(0, "2")
minutes_entry_tf.insert(0, "11")
hours_entry_tf.insert(0, "17")

file_data_submit_button = Button(col0, text="Submit file information", padx=8, pady=6, width=20, command=col_names_submit)
file_data_submit_button.grid(row=10, column=0, pady=(16,4))
file_data_clear_button = Button(col0, text="Clear Entries", padx=8, pady=6, width=20, command=clear_file_data)
file_data_clear_button.grid(row=11, column=0, pady=4)


# SECOND COLUMN ENTRIES (define and place checkboxes for raw data)
plot_raw_data_var = IntVar()
plot_raw_data_check = Checkbutton(col1, text="Plot raw data?", font=('TkDefaultFont', 12, 'bold'), variable=plot_raw_data_var,onvalue=1, offvalue=2, command=receive_raw_checkboxes)
plot_raw_data_check.grid(row=0, column=2, pady=(12,8), padx=(16,32))
which_raw_channels_label = Label(col1, text="Select overtones for full data")

# a lot of checkboxes for selecting which channels to plot for clean and raw data
raw_ch1_freq_var = IntVar()
raw_ch1_freq_check = Checkbutton(col1, text="Fundamental frequency", variable=raw_ch1_freq_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch1_dis_var = IntVar()
raw_ch1_dis_check = Checkbutton(col1, text="Fundamental dissipation", variable=raw_ch1_dis_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch2_freq_var = IntVar()
raw_ch2_freq_check = Checkbutton(col1, text="3rd frequency", variable=raw_ch2_freq_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch2_dis_var = IntVar()
raw_ch2_dis_check = Checkbutton(col1, text="3rd dissipation", variable=raw_ch2_dis_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch3_freq_var = IntVar()
raw_ch3_freq_check = Checkbutton(col1, text="5th frequency", variable=raw_ch3_freq_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch3_dis_var = IntVar()
raw_ch3_dis_check = Checkbutton(col1, text="5th dissipation", variable=raw_ch3_dis_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch4_freq_var = IntVar()
raw_ch4_freq_check = Checkbutton(col1, text="7th frequency", variable=raw_ch4_freq_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch4_dis_var = IntVar()
raw_ch4_dis_check = Checkbutton(col1, text="7th dissipation", variable=raw_ch4_dis_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch5_freq_var = IntVar()
raw_ch5_freq_check = Checkbutton(col1, text="9th frequency", variable=raw_ch5_freq_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)
raw_ch5_dis_var = IntVar()
raw_ch5_dis_check = Checkbutton(col1, text="9th dissipation", variable=raw_ch5_dis_var, onvalue=1, offvalue=0, command=receive_raw_checkboxes)

clear_raw_checks_button = Button(col1, text='clear all', width=8, command=clear_raw_checks)
select_all_raw_checks_button = Button(col1, text='select all', width=8, command=select_all_raw_checks)


# THIRD COLUMN ENTRIES (define and place checkboxes for clean data)
plot_clean_data_var = IntVar()
plot_clean_data_check = Checkbutton(col2, text="Plot corrected data?", font=('TkDefaultFont', 12, 'bold'), variable=plot_clean_data_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
plot_clean_data_check.grid(row=0, column=3, pady=(12,8), padx=(32,16))
which_clean_channels_label = Label(col2, text="Select overtones for\nbaseline corrected data")

clean_ch1_freq_var = IntVar()
clean_ch1_freq_check = Checkbutton(col2, text="Fundamental frequency", variable=clean_ch1_freq_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch1_dis_var = IntVar()
clean_ch1_dis_check = Checkbutton(col2, text="Fundamental dissipation", variable=clean_ch1_dis_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch2_freq_var = IntVar()
clean_ch2_freq_check = Checkbutton(col2, text="3rd frequency", variable=clean_ch2_freq_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch2_dis_var = IntVar()
clean_ch2_dis_check = Checkbutton(col2, text="3rd dissipation", variable=clean_ch2_dis_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch3_freq_var = IntVar()
clean_ch3_freq_check = Checkbutton(col2, text="5th frequency", variable=clean_ch3_freq_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch3_dis_var = IntVar()
clean_ch3_dis_check = Checkbutton(col2, text="5th dissipation", variable=clean_ch3_dis_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch4_freq_var = IntVar()
clean_ch4_freq_check = Checkbutton(col2, text="7th frequency", variable=clean_ch4_freq_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch4_dis_var = IntVar()
clean_ch4_dis_check = Checkbutton(col2, text="7th dissipation", variable=clean_ch4_dis_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch5_freq_var = IntVar()
clean_ch5_freq_check = Checkbutton(col2, text="9th frequency", variable=clean_ch5_freq_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
clean_ch5_dis_var = IntVar()
clean_ch5_dis_check = Checkbutton(col2, text="9th dissipation", variable=clean_ch5_dis_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)

clear_clean_checks_button = Button(col2, text='clear all', width=8, command=clear_clean_checks)
select_all_clean_checks_button = Button(col2, text='select all', width=8, command=select_all_clean_checks)


# FOURTH COLUMN ENTRIES - options for graph
# scale time, df and dD together, normalize f
plot_options_label = Label(col3, text="Options for plots", font=('TkDefaultFont', 12, 'bold'))
plot_options_label.grid(row=0, column=4, pady=(14,16), padx=(0,6))

plot_dF_dD_together_var = IntVar()
plot_dF_dD_together_check = Checkbutton(col3, text="Plot Δf and Δd together", variable=plot_dF_dD_together_var, onvalue=1, offvalue=0, command=receive_optional_checkboxes)
plot_dF_dD_together_check.grid(row=2, column=4)
normalize_F_var = IntVar()
normalize_F_check = Checkbutton(col3, text="Normalize Δf with its\nrespective overtone", variable=normalize_F_var, onvalue=1, offvalue=0, command=receive_optional_checkboxes)
normalize_F_check.grid(row=3, column=4)
plot_dD_v_dF_var = IntVar()
plot_dD_v_dF_check = Checkbutton(col3, text="Plot Δd vs Δf", variable=plot_dD_v_dF_var, onvalue=1, offvalue=0, command=receive_optional_checkboxes)
plot_dD_v_dF_check.grid(row=4, column=4)
interactive_plot_var = IntVar()
interactive_plot_check = Checkbutton(col3, text="Interactive plot", variable=interactive_plot_var, onvalue=1, offvalue=0, command=receive_optional_checkboxes)
interactive_plot_check.grid(row=5, column=4)

# Options for changing the scale of x axis time
scale_time_var = IntVar()
which_range_var = IntVar()
scale_time_check = Checkbutton(col3, text="Change scale of time? (default (s))", variable=scale_time_var, onvalue=1, offvalue=0, command=receive_scale_radios)
scale_time_check.grid(row=7, column=4, pady=(32,0))
# default to seconds
# PUT INTO SUBFRAME
time_scale_frame = Frame(fr2)
which_time_scale_var = IntVar()
seconds_scale_check = Radiobutton(time_scale_frame, text="Seconds", variable=which_time_scale_var, value=1, command=receive_scale_radios)
seconds_scale_check.grid(row=0, column=0)
minutes_scale_check = Radiobutton(time_scale_frame, text="Minutes", variable=which_time_scale_var, value=2, command=receive_scale_radios)
minutes_scale_check.grid(row=0, column=1)
hours_scale_check = Radiobutton(time_scale_frame, text="Hours", variable=which_time_scale_var, value=3, command=receive_scale_radios)
hours_scale_check.grid(row=0, column=2)

# Options for changing file format of saved scatter plot figures
change_fig_format_var = IntVar()
change_fig_format_check = Checkbutton(col3, text="Change figure file format? (default .png)", variable=change_fig_format_var, onvalue=1, offvalue=0, command=receive_file_format_radios)
change_fig_format_check.grid(row=14, column=4, pady=(8,0))
# default png
# PUT INTO SUBFRAME
file_format_frame = Frame(fr3)
which_file_format_var = IntVar()
png_check = Radiobutton(file_format_frame, text=".png", variable=which_file_format_var, value=1, command=receive_file_format_radios)
png_check.grid(row=0, column=0)
tiff_check = Radiobutton(file_format_frame, text=".tiff", variable=which_file_format_var, value=2, command=receive_file_format_radios)
tiff_check.grid(row=0, column=1)
pdf_check = Radiobutton(file_format_frame, text=".pdf", variable=which_file_format_var, value=3, command=receive_file_format_radios)
pdf_check.grid(row=0, column=2)

submit_button = Button(col3, text="Submit", padx=8, pady=6, width=20, command=submit)
submit_button.grid(row=20, column=4, pady=4)

abort_button = Button(col3, text="Abort", padx=8, pady=6, width=20, command=abort)
abort_button.grid(row=19, column=4, pady=4)

# conclude UI event loop
root.mainloop()

'''TEMP ASSIGNMENTS to not have to enter into gui every time while debugging'''
#file_name = "10102022_Collagen 2 at 25ug per ml and SF at 37C_n=1 DD.csv"

#file_path = ""
#clean_num_channels_tested = 10
#abs_base_t0 = time(8,29,48)
#abs_base_t0 = time(17,2,26)
#abs_base_tf = time(9,5,55)
#abs_base_tf = time(17,11,2)
