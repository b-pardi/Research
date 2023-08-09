"""
Author: Brandon Pardi
Created: 2/19/2022, 10:46 am (result of refactor)
Last Modified: 3/11/2022, 9:21 pm
"""

from tkinter import *
import os
from datetime import time
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib
try:
    matplotlib.use('TkAgg')  # Set the backend to TkAgg
except:
    matplotlib.use('Agg')  # Set the backend to default
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from scipy.optimize import curve_fit
import sys
import json

import Exceptions

''' ANALYSIS VARIABLES '''
class Analysis:
    def __init__(self, fn):
        file_name, _ = os.path.splitext(fn)
        file_name = os.path.basename(file_name)
        if fn.__contains__("Formatted"):
            self.formatted_fn = f"raw_data/{file_name}.csv"
        else:
            self.formatted_fn = f"raw_data/Formatted-{file_name}.csv"
        
        print(f"Using formatted file: {self.formatted_fn}")

        self.time_col = 'Time' # relative time
        self.abs_time_col = 'abs_time' # for qcmd with abs and rel time
        self.temp_col = 'Temp'
        self.temp_time_col = 'Temp_Time'

        self.freqs = ['fundamental_freq', '3rd_freq', '5th_freq', '7th_freq', '9th_freq', '11th_freq', '13th_freq']
        self.disps = ['fundamental_dis', '3rd_dis', '5th_dis', '7th_dis', '9th_dis', '11th_dis', '13th_dis']

''' UTILITY FUNCTIONS '''
def get_plot_preferences():
    with open ("plot_opts/plot_customizations.json", 'r') as fp:
        plot_customs = json.load(fp)  
    return plot_customs  

# function fills list of channels selected to be clean plot from gui
def get_channels(channels):
    freq_list = []
    disp_list = []
        
    for channel in channels:
        # dict entry for that channel is true then append to list
        if channel[1] == True:
            # check if channel looking at is a frequency or dissipation and append approppriately
            if channel[0].__contains__('freq'):
                freq_list.append(channel[0])
            elif channel[0].__contains__('dis'):
                disp_list.append(channel[0])

    return (freq_list, disp_list)

def get_num_from_string(string):
    if string.__contains__("fundamental"):
        return 1
    nums = []
    for char in string:
        if char.isdigit():
            nums.append(char)
    num = 0
    for i, digit in enumerate(reversed(list(nums))):
        num += int(digit) * 10**i
    return int(num)

# returns the ordinal suffix of number (i.e. the rd in 3rd)
# instead of 'st' for 1st, will return 'fundamental'
def ordinal(n):
    overtone_ordinal = ("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
    overtone_ordinal = str(n) + overtone_ordinal
    return overtone_ordinal

def rotate_point(x, y, theta):
    x_rot = x * np.cos(theta) - y * np.sin(theta)
    y_rot = x * np.sin(theta) + y * np.cos(theta)
    return x_rot, y_rot

def shift_by_slope(x_time, y_data, baseline_df, time_col, freq):
    from modeling import linear # import in function to avoid circular import

    # slope accounted baseline correction
    params, _ = curve_fit(linear, baseline_df[time_col], baseline_df[freq])
    m, b = params
    theta = -np.arctan(m) # negate the angle s.t. the baseline will have a slope of 0

    x_time_adjsuted, y_data_adjusted = rotate_point(x_time, y_data, theta)
    x_time_adjsuted = np.asarray(x_time_adjsuted)
    y_data_adjusted = np.asarray(y_data_adjusted)

    print(f"*****SLOPE: {m}; y-intercept: {b}")

    return x_time_adjsuted, y_data_adjusted

def determine_xlabel(x_timescale):
    if x_timescale == 's':
        return "Time, " + '$\it{t}$' + " (s)"
    elif x_timescale == 'min':
        return "Time, " + '$\it{t}$' + " (min)"
    elif x_timescale == 'hr':
        return "Time, " + '$\it{t}$' + " (hr)"
    else:
        return "placeholder"
    
def determine_ylabel(ydata_type, is_normalized, is_raw_data=False):
    if ydata_type == 'dis':
        if is_raw_data:
            return r"Dissipation, $\mathit{d_{n}}$"
        else:
            return r"Change in dissipation, $\mathit{Δd_{n}}$ ($10^{-6}$)"
    if ydata_type == 'freq':
        if is_raw_data:
            return r"Frequency, $\mathit{f_{n}}$ (Hz)"
        if is_normalized:
            return r"Change in frequency, $\frac{\mathit{Δf_{n}}}{\mathit{n}}$ (Hz)"
        else:
            return r"Change in frequency, $\mathit{Δf_{n}}$ (Hz)"

def setup_plot(fig, ax, fig_x, fig_y, fig_title, fn, will_save=False, legend=True):
    plot_customs = get_plot_preferences()
    fig_format = plot_customs['fig_format']
    plt.figure(fig.number)

    if legend:
        ax.legend(loc='best', fontsize=plot_customs['legend_text_size'], prop={'family': plot_customs['font']}, framealpha=0.1)
    
    # set the bounds of data plotted, based on user input, looking at axis label to determine with bound inputted to use
    if fig_y.__contains__('frequency'):
        y_bound = (plot_customs['frequency_lower_bound'], plot_customs['frequency_upper_bound'])
    elif fig_y.__contains__('dissipation'):
        y_bound = (plot_customs['dissipation_lower_bound'], plot_customs['dissipation_upper_bound'])
    else:
        y_bound = ('auto','auto')
    
    if fig_x.__contains__('Time'):
        x_bound = (plot_customs['time_lower_bound'], plot_customs['time_upper_bound'])
    elif fig_x.__contains__('dissipation'):
        x_bound = (plot_customs['dissipation_lower_bound'], plot_customs['dissipation_upper_bound'])
    else:
        x_bound = ('auto','auto')

    if x_bound[0] != x_bound[1]:
        plt.xlim(int(x_bound[0]), int(x_bound[1]))
    if y_bound[0] != y_bound[1]:
        plt.ylim(float(y_bound[0]), float(y_bound[1]))

    plt.xticks(fontsize=plot_customs['value_text_size'], fontfamily=plot_customs['font'])
    plt.yticks(fontsize=plot_customs['value_text_size'], fontfamily=plot_customs['font'])
    plt.xlabel(fig_x, fontsize=plot_customs['label_text_size'], fontfamily=plot_customs['font'])
    plt.ylabel(fig_y, fontsize=plot_customs['label_text_size'], fontfamily=plot_customs['font'])
    plt.tick_params(axis='both', direction=plot_customs['tick_dir'])
    plt.title(fig_title, fontsize=plot_customs['title_text_size'], fontfamily=plot_customs['font'])
    if will_save:
        fig.savefig(fn + '.' + fig_format, format=fig_format, bbox_inches='tight', transparent=True, dpi=400)

def find_nearest_time(time, my_df, time_col_name, is_relative_time):
    # locate where baseline starts/ends
    if is_relative_time:
        time_df = my_df.iloc[(my_df[time_col_name] - int(time)).abs().argsort()[:1]]
        base_t0_ind = time_df.index[0]
    else:
        time_df = my_df[my_df[time_col_name].str.contains(time)]

        # if exact time not in dataframe, find nearest one
        # convert the last 2 digits (the seconds) into integers and increment by 1, mod by 10
        # this method will find nearest time since time stamps are never more than 2 seconds apart
        while(time_df.shape[0] == 0): # iterate until string found in time dataframe
            ta = time[:7]
            tb = (int(time[7:]) + 1) % 10
            time = ta + str(tb)
            time_df = my_df[my_df[time_col_name].str.contains(time)]
        base_t0_ind = time_df.index[0]

    return base_t0_ind

def plot_multiaxis(input, x_time, y_rf, y_dis, freq_label, dis_label, fig, ax1, ax2, color):
    plt.figure(fig.number)
    plot_customs = get_plot_preferences()
    points_idx = plot_customs['points_plotted_index']
    x_time_freq, x_time_dis = x_time

    x_bound = (plot_customs['time_lower_bound'], plot_customs['time_upper_bound'])
    y1_bound = (plot_customs['frequency_lower_bound'], plot_customs['frequency_upper_bound'])
    y2_bound = (plot_customs['dissipation_lower_bound'], plot_customs['dissipation_upper_bound'])

    if x_bound[0] != x_bound[1]:
        plt.xlim(int(x_bound[0]), int(x_bound[1]))
    if y1_bound[0] != y1_bound[1]:
        plt.ylim(int(y1_bound[0]), int(y1_bound[1]))
    if y2_bound[0] != y2_bound[1]:
        plt.ylim(int(y2_bound[0]), int(y2_bound[1]))

    ax1.set_xlabel(determine_xlabel(plot_customs['time_scale']), fontsize=plot_customs['label_text_size'], fontfamily=plot_customs['font'])
    ax1.set_ylabel(determine_ylabel('freq', input.will_normalize_F), fontsize=plot_customs['label_text_size'], fontfamily=plot_customs['font'])
    ax2.set_ylabel(determine_ylabel('dis', input.will_normalize_F), fontsize=plot_customs['label_text_size'], fontfamily=plot_customs['font'])
    ax1.plot(x_time_freq[::points_idx], y_rf[::points_idx], 'o', markersize=1, label=freq_label, color=color)
    ax2.plot(x_time_dis[::points_idx], y_dis[::points_idx], 'o', markersize=2, label=dis_label, markerfacecolor='none', markeredgecolor=color, markeredgewidth=0.32)
    ax1.tick_params(axis='both', direction=plot_customs['tick_dir'])
    ax2.tick_params(axis='both', direction=plot_customs['tick_dir'])
    plt.xticks(fontsize=plot_customs['value_text_size'], fontfamily=plot_customs['font'])
    plt.yticks(fontsize=plot_customs['value_text_size'], fontfamily=plot_customs['font'])
    plt.title("Change in Frequency vs Change in Dissipation", fontsize=plot_customs['title_text_size'], fontfamily=plot_customs['font'])

def plot_temp_v_time(fig, ax, time, temp, x_scale, fig_format):
    plot_prefs = get_plot_preferences()
    points_idx = plot_prefs['points_plotted_index']
    ax.plot(time[::points_idx], temp[::points_idx], '.', markersize=1)
    setup_plot(fig, ax, determine_xlabel(x_scale), r"Temperature, $\it{t}$ °C", "QCM-D Temperature vs Time", "qcmd-plots/temp_vs_time_plot", True, False)

# check if label and file already exists and remove if it does before writing new data for that range
# this allows for overwriting of only the currently selected file and frequency,
# without having to append all data, or overwrite all data each time
def prepare_stats_file(header, which_range, src_fn, stats_fn):
    save_flag = False # flag determines if file will need to be saved or not after opening df
    try: # try to open df from stats csv
        try:
            temp_df = pd.read_csv(stats_fn)
        except Exception as e:
            print(f"err 1: {e}")
            print("Creating modeling file...")
            with open(stats_fn) as creating_new_modeling_file: 
                creating_new_modeling_file.write('')
            temp_df = pd.read_csv(stats_fn)
        if '' in temp_df['range_name'].unique(): # remove potentially erroneous range inputs
            temp_df = temp_df.loc[temp_df['range_name'] != '']
            save_flag = True
        if which_range in temp_df['range_name'].unique()\
        and src_fn in temp_df['data_source'].unique():
            to_drop = temp_df.loc[((temp_df['range_name'] == which_range)\
                                & (temp_df['data_source'] == src_fn))].index.values
            temp_df = temp_df.drop(index=to_drop)
            save_flag = True
        if save_flag:
            temp_df.to_csv(stats_fn, float_format="%.16E", index=False)
    except (FileNotFoundError, pd.errors.EmptyDataError, KeyError) as e:
        print(f"err 2: {e}")
        print("making new stats file...")
        with open(stats_fn, 'w') as new_file:
            new_file.write(header)

def range_statistics(df, imin, imax, overtone_sel, which_range, which_fmt, fn):
    which_overtones = []
    for ov in overtone_sel:
        if ov[1]:
            which_overtones.append(ov[0])
        
    dis_stat_file = open(f"selected_ranges/{which_fmt.upper()}_all_stats_dis.csv", 'a')
    rf_stat_file = open(f"selected_ranges/{which_fmt.upper()}_all_stats_rf.csv", 'a')

    # statistical analysis for all desired overtones using range of selection
    range_df = pd.DataFrame()
    x_data = df["Time"]
    x_sel = x_data[imin:imax]
    for overtone in overtone_sel:
        ov = overtone[0] # label of current overtone
        if overtone[1]: # if current overtone selected for plotting
            y_data = df[ov]
            y_sel = y_data[imin:imax]
            if ov.__contains__('dis'):
                y_sel = y_sel / 1000000 # unit conversion since multiplied up by 10^6 earlier in code
            mean_y = np.average(y_sel)
            std_dev_y = np.std(y_sel)
            median_y = np.median(y_sel)
        
            if ov.__contains__('freq'):
                rf_stat_file.write(f"{ov},{mean_y:.16E},{std_dev_y:.16E},{median_y:.16E},{which_range},{np.min(x_sel)},{np.max(x_sel)},{fn}\n")
            elif ov.__contains__('dis'):
                dis_stat_file.write(f"{ov},{mean_y:.16E},{std_dev_y:.16E},{median_y:.16E},{which_range},{np.min(x_sel)},{np.max(x_sel)},{fn}\n")
        
        else:
            print(f"\n{ov} not selected\n")
            if ov.__contains__('freq'):
                rf_stat_file.write(f"{ov},{0:.16E},{0:.16E},{0:.16E},{which_range},{0:.16E},{0:.16E},{fn}\n")

            elif ov.__contains__('dis'):
                dis_stat_file.write(f"{ov},{0:.16E},{0:.16E},{0:.16E},{which_range},{0:.16E},{0:.16E},{fn}\n")
    
    
    dis_stat_file.close()
    rf_stat_file.close()

def save_calibration_data(df, imin, imax, which_plots, range, fn):
    calibration_file = open(f"calibration_data/calibration_data.csv", 'a')
    for overtone in which_plots:
        ov = overtone[0]
        if overtone[1] and ov.__contains__('freq'):
            y_data=df[ov]
            y_sel = y_data[imin:imax]
            mean_y = np.average(y_sel)
            std_dev_y = np.std(y_sel)
            n = get_num_from_string(ov)
            calibration_file.write(f"{n},{mean_y:.16E},{std_dev_y:.16E},{range},{fn}\n")


# removing axis lines for plots
def remove_axis_lines(ax):
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)

def map_colors():
    plot_customs = get_plot_preferences()
    colors = plot_customs['colors'].values()
    freq_colors = {'fundamental_freq':'', '3rd_freq':'', '5th_freq':'',
                    '7th_freq':'', '9th_freq':'', '11th_freq':'', '13th_freq':''}
    freq_colors_keys = list(freq_colors.keys())
    dis_colors = {'fundamental_dis':'', '3rd_dis':'', '5th_dis':'',
                    '7th_dis':'', '9th_dis':'', '11th_dis':'', '13th_dis':''}
    dis_colors_keys = list(dis_colors.keys())

    for i, color in enumerate(colors):
        freq_key = freq_colors_keys[i]
        dis_key = dis_colors_keys[i]
        freq_colors[freq_key] = color
        dis_colors[dis_key] = color

    return freq_colors, dis_colors

def set_x_entry():
    def handle_focus_in(entry):
        x_entry.delete(0,"end")
        x_entry.config(foreground='black')

    def handle_focus_out(entry):
        if x_entry.get() == "":
            x_entry.delete(0, tk.END)
            x_entry.config(foreground='gray')
            x_entry.insert(0, "xmin,xmax")

    plot_win = tk.Tk() # init tk backend for having entry field
    x_entry_label = ttk.Label(plot_win, text="Enter time range selection here or make selection below", font=('TkDefaultFont', 16, 'bold'))
    x_entry_label.pack(pady=4)
    x_entry = ttk.Entry(plot_win, width=20, font=('TkDefaultFont', 16)) # Create the text entry widget
    x_entry.config(foreground='gray')
    x_entry.insert(0, "xmin,xmax")
    x_entry.bind('<FocusIn>', handle_focus_in)
    x_entry.bind('<FocusOut>', handle_focus_out)
    x_entry.pack()

    return plot_win, x_entry

def generate_interactive_plot(int_plot_overtone, time_scale, df, time_col):
    plt.close("all") # clear all previous plots

    # setup plot objects
    int_plot = plt.figure()
    plt.clf()
    int_plot.set_figwidth(14)
    int_plot.set_figheight(8)
    plt.subplots_adjust(hspace=0.4,wspace=0.2)
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
    int_ax1.set_title(f"QCM-D Resonant Frequency - overtone {int_plot_overtone}", fontsize=14, fontfamily='Arial')
    int_ax2.set_title(f"QCM-D Dissipation - overtone {int_plot_overtone}", fontsize=16, fontfamily='Arial')
    int_ax1_zoom.set_title("\nFrequency Selection Data", fontsize=16, fontfamily='Arial')
    int_ax2_zoom.set_title("\nDissipation Selection Data", fontsize=16, fontfamily='Arial')
    ax.set_title("Click and drag to select range", fontsize=20, fontfamily='Arial', weight='bold', pad=40)
    y_ax1.set_ylabel(determine_ylabel('freq', False), fontsize=14, fontfamily='Arial', labelpad=20) # label the shared axes
    y_ax2.set_ylabel(determine_ylabel('dis', False), fontsize=14, fontfamily='Arial', labelpad=5)
    ax.set_xlabel(determine_xlabel(time_scale), fontsize=16, fontfamily='Arial')
    plt.sca(int_ax1)
    plt.xticks(fontsize=12, fontfamily='Arial')
    plt.yticks(fontsize=12, fontfamily='Arial')
    plt.sca(int_ax2)
    plt.xticks(fontsize=12, fontfamily='Arial')
    plt.yticks(fontsize=12, fontfamily='Arial')
    int_ax2.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
    plt.sca(int_ax1_zoom)
    plt.xticks(fontsize=12, fontfamily='Arial')
    plt.yticks(fontsize=12, fontfamily='Arial')
    plt.sca(int_ax2_zoom)
    plt.xticks(fontsize=12, fontfamily='Arial')
    plt.yticks(fontsize=12, fontfamily='Arial')
    int_ax2_zoom.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))

    # Turn off axis lines and ticks of the big subplots
    remove_axis_lines(ax)
    remove_axis_lines(y_ax1)
    remove_axis_lines(y_ax2)

    # grab data
    x_time = df[time_col]
    # choose correct user spec'd overtone
    int_plot_overtone = ordinal(get_num_from_string(str(int_plot_overtone))).lower()
    if f'{int_plot_overtone}_freq' not in df.columns:
        raise Exceptions.InputtedIntPlotOvertoneNotSelectedException('',int_plot_overtone)

    y_rf = df[f'{int_plot_overtone}_freq']
    y_dis = df[f'{int_plot_overtone}_dis']

    int_ax1.plot(x_time, y_rf, '.', color='green', markersize=1)
    int_ax2.plot(x_time, y_dis, '.', color='blue', markersize=1)
    zoom_plot1, = int_ax1_zoom.plot(x_time, y_rf, '.', color='green', markersize=1)
    zoom_plot2, = int_ax2_zoom.plot(x_time, y_dis, '.', color='blue', markersize=1)

    return int_plot, int_ax1, int_ax2, int_ax1_zoom, int_ax2_zoom, y_rf, y_dis

def update_interactive_plot(spans, int_plot, int_ax1_zoom, int_ax2_zoom, plot_customs,
                              xmin, xmax, x_time, y_rf, y_dis, x_scale):
    
    from modeling import linearly_analyze # import in function to avoid circular import
    
    for span in spans:
        if span.active:
            span.extents = (xmin, xmax)

    # clear previous linear fit
    int_ax1_zoom.cla()
    int_ax2_zoom.cla()

    # min and max indices are where elements should be inserted to maintain order
    imin, imax = np.searchsorted(x_time[0], (xmin, xmax))
    # range will be at most all elems in x, or imax
    imax = min(len(x_time[0])-1, imax)

    # cursor x and y for zoomed plot and data range
    zoomx = x_time[0][imin:imax]
    zoomy1 = y_rf[imin:imax]
    zoomy2 = y_dis[imin:imax]

    # update data to newly spec'd range
    int_ax1_zoom.plot(zoomx, zoomy1, '.', color='green', markersize=1)
    int_ax2_zoom.plot(zoomx, zoomy2, '.', color='blue', markersize=1)
    
    # linear regression on zoomed data
    freq_units = f"Hz/{x_scale}"
    dis_units = f"1/{x_scale}"
    linearly_analyze(zoomx, zoomy1, int_ax1_zoom, "frequency drift: ", freq_units)
    linearly_analyze(zoomx, zoomy2, int_ax2_zoom, "dissipation drift: ", dis_units)
    int_ax1_zoom.legend(loc='best', fontsize=plot_customs['legend_text_size'], prop={'family': plot_customs['font']}, framealpha=0.3)
    int_ax2_zoom.legend(loc='best', fontsize=plot_customs['legend_text_size'], prop={'family': plot_customs['font']}, framealpha=0.3)

    # set limits of tick marks
    int_ax1_zoom.set_xlim(zoomx.min(), zoomx.max())
    int_ax1_zoom.set_ylim(zoomy1.min(), zoomy1.max())
    int_ax2_zoom.set_xlim(zoomx.min(), zoomx.max())
    int_ax2_zoom.set_ylim(zoomy2.min(), zoomy2.max())

    int_plot.canvas.draw_idle()

    return imin, imax

def interactive_plot_analysis(fn, df, range, imin, imax, which_plot, which_fmt):
    # prep and save data to file
    # frequency stats for bandwidth shift
    stats_out_fn = f'selected_ranges/{which_fmt}_all_stats_rf.csv'
    header = f"overtone,Dfreq_mean,Dfreq_std_dev,Dfreq_median,range_name,x_lower,x_upper,data_source\n"
    prepare_stats_file(header, range[which_fmt], fn, stats_out_fn)
    
    # dissipation stats for bandwidth shift
    stats_out_fn = f'selected_ranges/{which_fmt}_all_stats_dis.csv'
    header = f"overtone,Ddis_mean,Ddis_std_dev,Ddis_median,range_name,x_lower,x_upper,data_source\n"
    prepare_stats_file(header, range[which_fmt], fn, stats_out_fn)

    range_statistics(df, imin, imax, which_plot, range[which_fmt], which_fmt, fn)

def cleaned_interactive_plot(input, cleaned_df, x_time, time_col):
    plot_customs = get_plot_preferences()

    int_plot_analysis = Analysis(input.file)
    spans = []        
    int_plot, int_ax1, int_ax2, int_ax1_zoom, int_ax2_zoom, y_rf, y_dis = generate_interactive_plot(input.interactive_plot_overtone['clean'], plot_customs['time_scale'], cleaned_df, time_col)

    which_fmt = [fmt[0] for fmt in input.interactive_plot_data_fmt.items() if fmt[1] == True][0]


    def update_text(event):
        if input.which_range_selecting == '':
            print("** WARNING: NO RANGE SELECTED VALUES WILL NOT BE ACCOUNTED FOR")
            return
        text = x_entry.get()
        try:
            xmin, xmax = map(float, text.split(','))
            int_ax1_zoom.set_xlim(xmin, xmax)
            int_plot.canvas.draw()
        except ValueError:
            print("Invalid input format. Please enter a valid range.")

        imin, imax = update_interactive_plot(spans, int_plot, int_ax1_zoom, int_ax2_zoom, plot_customs,
                                  xmin, xmax, x_time, y_rf, y_dis, plot_customs['time_scale'])
        interactive_plot_analysis(int_plot_analysis.formatted_fn, cleaned_df, input.which_range_selecting,
                                  imin, imax, input.which_plot['clean'].items(), which_fmt)
    
    plot_win, x_entry = set_x_entry()
    x_entry.bind('<Return>', update_text)

    # draw initial figure
    canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(int_plot, master=plot_win)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def on_clean_select(xmin, xmax):
        if input.which_range_selecting == '':
            print("** WARNING: NO RANGE SELECTED VALUES WILL NOT BE ACCOUNTED FOR")
            return
        
        imin, imax = update_interactive_plot(spans, int_plot, int_ax1_zoom, int_ax2_zoom, plot_customs,
                                  xmin, xmax, x_time, y_rf, y_dis, plot_customs['time_scale'])
        interactive_plot_analysis(int_plot_analysis.formatted_fn, cleaned_df, input.which_range_selecting,
                                  imin, imax, input.which_plot['clean'].items(), which_fmt)

            
        x_entry.delete(0,"end") # update text field to match
        x_entry.insert(0,f"{xmin:.2f},{xmax:.2f}") 
        canvas.draw()
        canvas.get_tk_widget().pack()

    # using plt's span selector to select area of top plot
    span1 = SpanSelector(int_ax1, on_clean_select, 'horizontal', useblit=True,
                props=dict(alpha=0.5, facecolor='blue'),
                interactive=True, drag_from_anywhere=True)
    
    span2 = SpanSelector(int_ax2, on_clean_select, 'horizontal', useblit=True,
                props=dict(alpha=0.5, facecolor='blue'),
                interactive=True, drag_from_anywhere=True)
    
    
    spans = [span1, span2]
    plot_win.mainloop()

    plt.show()

def raw_interactive_plot(input, raw_df, overtone_select, which_range, x_time, time_col):
    plot_customs = get_plot_preferences()
    int_plot, int_ax1, int_ax2, int_ax1_zoom, int_ax2_zoom, y_rf, y_dis = generate_interactive_plot(overtone_select, plot_customs['time_scale'], raw_df, time_col)
    int_plot_analysis = Analysis(input.file)
    def on_raw_select(xmin, xmax):
        if which_range == '':
            print("** WARNING: NO RANGE SELECTED VALUES WILL NOT BE ACCOUNTED FOR")
        else:
            # adjust other span to match the moved span
            for span in spans:
                if span.active:
                    span.extents = (xmin, xmax)

            # min and max indices are where elements should be inserted to maintain order
            imin, imax = np.searchsorted(x_time, (xmin, xmax))
            # range will be at most all elems in x, or imax
            imax = min(len(x_time)-1, imax)

            # cursor x and y for zoomed plot and data range
            zoomx = x_time[imin:imax]
            zoomy1 = y_rf[imin:imax]
            zoomy2 = y_dis[imin:imax]

            # update data to newly spec'd range
            int_ax1_zoom.plot(zoomx, zoomy1, '.', color='green', markersize=1)
            int_ax2_zoom.plot(zoomx, zoomy2, '.', color='blue', markersize=1)
            
            # set limits of tick marks
            int_ax1_zoom.set_xlim(zoomx.min(), zoomx.max())
            int_ax1_zoom.set_ylim(zoomy1.min(), zoomy1.max())
            int_ax2_zoom.set_xlim(zoomx.min(), zoomx.max())
            int_ax2_zoom.set_ylim(zoomy2.min(), zoomy2.max())
            int_plot.canvas.draw_idle()

            # prep and save data to file
            stats_out_fn = 'calibration_data/calibration_data.csv'
            header = f"overtone,calibration_freq,std_dev,range_used,data_source\n"
            prepare_stats_file(header, which_range, int_plot_analysis.formatted_fn, stats_out_fn)
            save_calibration_data(raw_df, imin, imax, input.which_plot['raw'].items(), which_range, int_plot_analysis.formatted_fn)
        
    # using plt's span selector to select area of top plot
    span1 = SpanSelector(int_ax1, on_raw_select, 'horizontal', useblit=True,
                props=dict(alpha=0.5, facecolor='blue'),
                interactive=True, drag_from_anywhere=True)
    
    span2 = SpanSelector(int_ax2, on_raw_select, 'horizontal', useblit=True,
                props=dict(alpha=0.5, facecolor='blue'),
                interactive=True, drag_from_anywhere=True)
    
    spans = [span1, span2]
    plt.show()

def select_calibration_data(input, overtone_select, which_range):
    # prepare raw data
    raw_analysis = Analysis(input.file)
    raw_df = pd.read_csv(raw_analysis.formatted_fn)
    drop_cols = [key for key, val in input.which_plot['raw'].items() if val == False]
    raw_df.drop(drop_cols, axis=1, inplace=True)
    x_time = raw_df[raw_analysis.time_col]
    print(raw_df.head())

    raw_interactive_plot(input, raw_df, overtone_select, which_range, x_time, raw_analysis.time_col)

def analyze_data(input):

    analysis = Analysis(input.file)
    t0_str = str(input.abs_base_t0).lstrip('0')
    tf_str = str(input.abs_base_tf).lstrip('0')

    # grab singular file and create dataframe from it
    df = pd.read_csv(analysis.formatted_fn)
    freq_color_map, dis_color_map = map_colors()

    plot_customs = get_plot_preferences()
    points_idx = plot_customs['points_plotted_index']

    '''Cleaning Data and plotting clean data'''
    if input.will_plot_clean_data:
        clean_freqs, clean_disps = get_channels(input.which_plot['clean'].items())
        freq_plot_cap = len(clean_freqs)
        disp_plot_cap = len(clean_disps)
        diff = len(clean_freqs) - len(clean_disps)

        # plotting objects
        freq_fig = plt.figure()
        freq_ax = freq_fig.add_subplot(111)
        dis_fig = plt.figure()
        dis_ax = dis_fig.add_subplot(111)

        if input.will_plot_dD_v_dF:
            disVfreq_fig = plt.figure()
            disVfreq_ax = disVfreq_fig.add_subplot(111)

        # prepare multiaxis if desired by user
        if input.will_plot_dF_dD_together:
            mult_fig, mult_ax1 = plt.subplots()
            mult_ax2 = mult_ax1.twinx()

        # if different num of freq and raw channels, must do equal amount for plotting,
        # but can just not plot the results later; set plot cap for the lesser
        # diff pos -> more freq channels than disp
        if diff > 0:
            clean_iters = len(clean_freqs)

            for i, ov in enumerate(clean_freqs):
                if ov not in clean_disps:
                    corr_dis = 'fundamental_dis' if ov.__contains__('fundamental') else ov[:4] + 'dis'
                    clean_disps.insert(i, corr_dis)

        # diff neg -> more disp channels than freq
        elif diff < 0:
            clean_iters = len(clean_disps)
            for i in range(abs(diff)):
                clean_freqs.append(analysis.freqs[i])
        # if length same, then iterations is length of either
        else:
            clean_iters = len(clean_freqs)
            
        # remove everything before baseline
        if input.is_relative_time: 
            base_t0_ind = find_nearest_time(input.rel_t0, df, analysis.time_col, input.is_relative_time) # baseline correction
        else:
            base_t0_ind = find_nearest_time(t0_str, df, analysis.abs_time_col, input.is_relative_time) # baseline correction
        df = df[base_t0_ind:] # baseline correction
        df = df.reset_index(drop=True)
        # find baseline and grab values from baseline for avg
        if input.is_relative_time: 
            base_tf_ind = find_nearest_time(input.rel_tf, df, analysis.time_col, input.is_relative_time) # baseline correction
        else:
            base_tf_ind = find_nearest_time(tf_str, df, analysis.abs_time_col, input.is_relative_time) # baseline correction
        baseline_df = df[:base_tf_ind].copy()
        
        if input.will_plot_temp_v_time:
            try:
                if input.file_src_type == 'Qsense':
                    analysis.time_col = analysis.temp_time_col
                temperature_df = df[[analysis.time_col, analysis.temp_col]].copy()
                temperature_df = temperature_df.dropna(axis=0, how='any', inplace=False)
            except Exception as e:
                print(f"Experiment file does not have temperature data\nerr: {e}")
                temperature_df = df[[analysis.time_col]]
                temperature_df[analysis.temp_col] = 0

        # choose appropriate divisor for x scale of time
        if plot_customs['time_scale'] == 'min':
            divisor = 60
        elif plot_customs['time_scale'] == 'hr':
            divisor = 3600
        else:
            divisor = 1
        
        for i in range(clean_iters):
            # grab data from df and grab only columns we need, then drop nan values
            data_df = df[[analysis.time_col,clean_freqs[i],clean_disps[i]]]
            print(f"clean freq ch: {clean_freqs[i]}; clean disp ch: {clean_disps[i]}")
            data_df = data_df.dropna(axis=0, how='any', inplace=False)
            if data_df.empty:
                print(f"ERROR: there is no data for either {clean_freqs[i]} or {clean_disps[i]}",
                      "\nPlease either uncheck these overtones, or check file for missing data and try again")
                sys.exit(1)

            # normalize by overtone
            if input.will_normalize_F:
                overtone = get_num_from_string(clean_freqs[i])
                data_df[clean_freqs[i]] /= overtone
                baseline_df[clean_freqs[i]] /= overtone

            # compute average of rf and dis
            rf_base_avg = baseline_df[clean_freqs[i]].mean() # baseline correction
            dis_base_avg = baseline_df[clean_disps[i]].mean() # baseline correction

            # lower rf curve s.t. baseline is approx at y=0
            data_df[clean_freqs[i]] -= rf_base_avg # baseline correction
            data_df[clean_disps[i]] -= dis_base_avg # baseline correction
            # shift x to left to start at 0
            baseline_start = data_df[analysis.time_col].iloc[0]
            data_df[analysis.time_col] -= baseline_start # baseline correction
            data_df[analysis.time_col] /= divisor
            
            x_time = data_df[analysis.time_col]
            y_freq = data_df[clean_freqs[i]]
            data_df[clean_disps[i]] *= 1000000 # unit conversion
            y_dis = data_df[clean_disps[i]]

            if input.will_correct_slope:
                slope_corrected_df = data_df.copy()
                x_time_freq, y_freq = shift_by_slope(x_time, y_freq ,baseline_df, analysis.time_col, clean_freqs[i])
                x_time_dis, y_dis = shift_by_slope(x_time, y_dis, baseline_df, analysis.time_col, clean_disps[i])
                slope_corrected_df[clean_freqs[i]] = y_freq
                slope_corrected_df[clean_disps[i]] = y_dis
            else:
                x_time_freq = x_time
                x_time_dis = x_time

            if input.will_normalize_F: # need freqs NOT normalized for int plot and modeling purposes
                if input.will_correct_slope:
                    unnormalized_df = slope_corrected_df.copy()
                else:
                    unnormalized_df = data_df.copy()
                unnormalized_df[clean_freqs[i]] *= overtone

            # PLOTTING
            if i < freq_plot_cap:
                freq_ax.plot(x_time_freq[::points_idx], y_freq[::points_idx], '.', markersize=1, label=ordinal(get_num_from_string(clean_freqs[i])), color=freq_color_map[clean_freqs[i]])
        
            if i < disp_plot_cap:
                dis_ax.plot(x_time_dis[::points_idx], y_dis[::points_idx], '.', markersize=1, label=ordinal(get_num_from_string(clean_disps[i])), color=dis_color_map[clean_disps[i]])

            # plotting change in disp vs change in freq
            if input.will_plot_dD_v_dF:
                disVfreq_ax.plot(y_freq[::points_idx], y_dis[::points_idx], '.', markersize=1, label=ordinal(get_num_from_string(clean_freqs[i])))
            
            # multi axis plot for change in freq and change in dis vs time
            if input.will_plot_dF_dD_together:
                plot_multiaxis(input, (x_time_freq, x_time_dis), y_freq, y_dis,
                               ordinal(get_num_from_string(clean_freqs[i])),
                               ordinal(get_num_from_string(clean_disps[i])),
                               mult_fig, mult_ax1, mult_ax2,freq_color_map[clean_freqs[i]])

            print(f"rf mean: {rf_base_avg}; dis mean: {dis_base_avg}\n")

            # put cleaned data back into original df for interactive plot
            if input.will_overwrite_file or input.enable_interactive_plot:
                if i == 0:
                    cleaned_df = data_df[[analysis.time_col]]
                    if input.will_normalize_F:
                        unnormalized_cleaned_df = data_df[[analysis.time_col]]
                    if input.will_correct_slope:
                        slope_corrected_cleaned_df = data_df[[analysis.time_col]]
                cleaned_df = pd.concat([cleaned_df,data_df[clean_freqs[i]]], axis=1)
                cleaned_df = pd.concat([cleaned_df,data_df[clean_disps[i]]], axis=1)
                if input.will_normalize_F:
                    unnormalized_cleaned_df = pd.concat([unnormalized_cleaned_df,unnormalized_df[clean_freqs[i]]], axis=1)
                    unnormalized_cleaned_df = pd.concat([unnormalized_cleaned_df,unnormalized_df[clean_disps[i]]], axis=1)
                if input.will_correct_slope:
                    slope_corrected_cleaned_df = pd.concat([slope_corrected_cleaned_df,slope_corrected_df[clean_freqs[i]]], axis=1)
                    slope_corrected_cleaned_df = pd.concat([slope_corrected_cleaned_df,slope_corrected_df[clean_disps[i]]], axis=1)
                
        if input.will_plot_temp_v_time:
            temperature_df[analysis.time_col] -= baseline_start
            temperature_df[analysis.time_col] /= divisor
            tempVtime_fig = plt.figure()
            tempVtime_ax = tempVtime_fig.add_subplot(111)
            plot_temp_v_time(tempVtime_fig, tempVtime_ax, temperature_df[analysis.time_col].values, temperature_df[analysis.temp_col].values, plot_customs['time_scale'], plot_customs['fig_format'])    

        if input.will_overwrite_file:
            df.to_csv(f"raw_data/CLEANED-{analysis.formatted_fn}", index=False)

        # Titles, lables, etc. for plots
        rf_fig_title = "QCM-D Resonant Frequency"
        rf_fn = "qcmd-plots/resonant-freq-plot"
        fig_x = determine_xlabel(plot_customs['time_scale'])

        dis_fig_title = "QCM-D Dissipation"
        dis_fn = f"qcmd-plots/dissipation-plot"

        # format and save figures
        setup_plot(freq_fig, freq_ax, fig_x, determine_ylabel('freq', input.will_normalize_F),
                   rf_fig_title, rf_fn)
        setup_plot(dis_fig, dis_ax, fig_x, determine_ylabel('dis', input.will_normalize_F),
                   dis_fig_title, dis_fn)
        
        freq_fig.savefig(f"qcmd-plots/frequency_plot.{plot_customs['fig_format']}", format=plot_customs['fig_format'], bbox_inches='tight', transparent=True, dpi=400)
        dis_fig.savefig(f"qcmd-plots/dissipation_plot.{plot_customs['fig_format']}", format=plot_customs['fig_format'], bbox_inches='tight', transparent=True, dpi=400)
        
        if input.will_plot_dD_v_dF:
            dVf_fn = f"qcmd-plots/disp_V_freq-plot"
            setup_plot(disVfreq_fig, disVfreq_ax, determine_ylabel('freq', input.will_normalize_F), determine_ylabel('dis', input.will_normalize_F),
                       dis_fig_title, dVf_fn)
            disVfreq_fig.savefig(f"qcmd-plots/disp_V_freq_plot.{plot_customs['fig_format']}", format=plot_customs['fig_format'], bbox_inches='tight', transparent=True, dpi=400)
            

        # saving multiaxis plot.
        if input.will_plot_dF_dD_together:
            box = mult_ax1.get_position()
            mult_ax1.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
            mult_fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.1), ncol=2, fancybox=True, shadow=True, fontsize=plot_customs['legend_text_size'], prop={'family': 'Arial'}, framealpha=0.1)
            mult_fig.savefig(f"qcmd-plots/freq_dis_V_time.{plot_customs['fig_format']}", format=plot_customs['fig_format'], bbox_inches='tight', transparent=True, dpi=800)

    # Gathering raw data for individual plots
    if input.will_plot_raw_data:
        # plot definitions
        rf_fig_title = "RAW QCM-D Resonant Frequency"
        fig_x = determine_xlabel(plot_customs['time_scale'])
        dis_fig_title = "RAW QCM-D Dissipation"

        # choose appropriate divisor for x scale of time
        time_scale_divisor = 1
        if plot_customs['time_scale'] == 'min':
            time_scale_divisor = 60
        elif plot_customs['time_scale'] == 'hr':
            time_scale_divisor = 3600

        raw_freqs, raw_disps = get_channels(input.which_plot['raw'].items())
        raw_freq_fig = plt.figure()
        raw_freq_ax = raw_freq_fig.add_subplot(111)
        # gather and plot raw frequency data
        for i in range(len(raw_freqs)):
            rf_data_df = df[[analysis.time_col,raw_freqs[i]]]
            rf_data_df = rf_data_df.dropna(axis=0, how='any', inplace=False)
            x_time = rf_data_df[analysis.time_col] / time_scale_divisor
            y_freq = rf_data_df[raw_freqs[i]]
        
            raw_freq_ax.plot(x_time[::points_idx], y_freq[::points_idx], '.', markersize=1, label=ordinal(get_num_from_string(raw_freqs[i])), color=freq_color_map[raw_freqs[i]])
            
        # gather and plot raw dissipation data
        raw_dis_fig = plt.figure()
        raw_dis_ax = raw_dis_fig.add_subplot(111)
        for i in range(len(raw_disps)):
            dis_data_df = df[[analysis.time_col,raw_disps[i]]]
            dis_data_df = dis_data_df.dropna(axis=0, how='any', inplace=False)
            x_time = dis_data_df[analysis.time_col] / time_scale_divisor
            y_dis = dis_data_df[raw_disps[i]]
            raw_dis_ax.plot(x_time[::points_idx], y_dis[::points_idx], '.', markersize=1, label=ordinal(get_num_from_string(raw_disps[i])), color=dis_color_map[raw_disps[i]])
            
        # save raw frequency plots
        rf_fn = f"qcmd-plots/RAW-resonant-freq-plot"
        setup_plot(raw_freq_fig, raw_freq_ax, fig_x, determine_ylabel('freq', False, True), rf_fig_title, rf_fn, plot_customs['fig_format'])
        raw_freq_fig.savefig(rf_fn + '.' + plot_customs['fig_format'], format=plot_customs['fig_format'], bbox_inches='tight', transparent=True, dpi=400)

        # save raw dissipation plots
        dis_fn = f"qcmd-plots/RAW-dissipation-plot"
        setup_plot(raw_dis_fig, raw_dis_ax, fig_x, determine_ylabel('dis', False, True), dis_fig_title, dis_fn,  plot_customs['fig_format'])
        raw_dis_fig.savefig(dis_fn + '.' + plot_customs['fig_format'], format=plot_customs['fig_format'], bbox_inches='tight', transparent=True, dpi=400)

    print(input.interactive_plot_overtone, ';', input.enable_interactive_plot)
    # interactive plot
    print(input.enable_interactive_plot)
    if input.enable_interactive_plot:
        print("clean int plot")
        if input.interactive_plot_data_fmt['clean']:
            if input.will_normalize_F:
                cleaned_interactive_plot(input, unnormalized_cleaned_df, (x_time_freq, x_time_dis), analysis.time_col)
            elif input.will_correct_slope:
                cleaned_interactive_plot(input, slope_corrected_cleaned_df, (x_time_freq, x_time_dis), analysis.time_col)
            else:
                cleaned_interactive_plot(input, cleaned_df, (x_time_freq, x_time_dis), analysis.time_col)

        if input.interactive_plot_data_fmt['raw']:
            print("raw int plot")
            cleaned_interactive_plot(input, df, (x_time, x_time), analysis.time_col)

    # clear plots and lists for next iteration
    if input.will_plot_clean_data:
        clean_freqs.clear()
        clean_disps.clear()
    print("*** Plots Generated ***")


if __name__ == '__main__':
    analyze_data()