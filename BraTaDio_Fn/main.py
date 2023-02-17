"""
Author: Brandon Pardi
Created: 9/7/2022, 1:53 pm
Last Modified: 2/16/2022, 10:54 pm
"""

from tkinter import *
import sys
import os
from datetime import time

from analyze import analyze_data, clear_figures
from classes import Input
from lin_reg import *

input = Input()


'''Function Defintions for UI events'''
def col_names_submit():
    global input
    input.file_name = file_name_entry.get()
    input.file_path = file_path_entry.get()
    if file_overwrite_var.get() == 1:
        input.will_overwrite_file = True
    else:
        input.will_overwrite_file = False

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
        input.abs_base_t0 = time(int(h0),int(m0),int(s0))
        input.abs_base_tf = time(int(hf),int(mf),int(sf))
    except ValueError as exc:
        err_label.grid(row=20, column=0)
        print(f"Please enter integer values for time: {exc}")
    submitted_label.grid(row=13, column=0)

def clear_file_data():
    global input
    input.abs_base_t0 = time(0, 0, 0)
    input.abs_base_tf = time(0, 0, 0)
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
    submitted_label.grid_forget()

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
    global input
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
    for channel in input.which_plot['raw']:
        input.which_plot['raw'][channel] = False
        
def select_all_raw_checks():
    global input
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
    for channel in input.which_plot['raw']:
        input.which_plot['raw'][channel] = True

def clear_clean_checks():
    global input
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
    for channel in input.which_plot['clean']:
        input.which_plot['clean'][channel] = False

def select_all_clean_checks():
    global input
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
    for channel in input.which_plot['clean']:
        input.which_plot['clean'][channel] = True

def receive_raw_checkboxes():
    global input

    if plot_raw_data_var.get() == 1:
        input.will_plot_raw_data = True
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
            input.which_plot['raw']['fundamental_freq'] = True
        else:
            input.which_plot['raw']['fundamental_freq'] = False

        if raw_ch1_dis_var.get() == 1:
            input.which_plot['raw']['fundamental_dis'] = True
        else:
            input.which_plot['raw']['fundamental_dis'] = False

        if raw_ch2_freq_var.get() == 1:
            input.which_plot['raw']['3rd_freq'] = True
        else:
            input.which_plot['raw']['3rd_freq'] = False

        if raw_ch2_dis_var.get() == 1:
            input.which_plot['raw']['3rd_dis'] = True
        else:
            input.which_plot['raw']['3rd_dis'] = False

        if raw_ch3_freq_var.get() == 1:
            input.which_plot['raw']['5th_freq'] = True
        else:
            input.which_plot['raw']['5th_freq'] = False

        if raw_ch3_dis_var.get() == 1:
            input.which_plot['raw']['5th_dis'] = True
        else:
            input.which_plot['raw']['5th_dis'] = False

        if raw_ch4_freq_var.get() == 1:
            input.which_plot['raw']['7th_freq'] = True
        else:
            input.which_plot['raw']['7th_freq'] = False

        if raw_ch4_dis_var.get() == 1:
            input.which_plot['raw']['7th_dis'] = True
        else:
            input.which_plot['raw']['7th_dis'] = False

        if raw_ch5_freq_var.get() == 1:
            input.which_plot['raw']['9th_freq'] = True
        else:
            input.which_plot['raw']['9th_freq'] = False

        if raw_ch5_dis_var.get() == 1:
            input.which_plot['raw']['9th_dis'] = True
        else:
            input.which_plot['raw']['9th_dis'] = False

    else:
        input.will_plot_raw_data = False
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
    global input
    if plot_clean_data_var.get() == 1:
        input.will_plot_clean_data = True
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
            input.which_plot['clean']['fundamental_freq'] = True
        else:
            input.which_plot['clean']['fundamental_freq'] = False

        if clean_ch1_dis_var.get() == 1:
            input.which_plot['clean']['fundamental_dis'] = True
        else:
            input.which_plot['clean']['fundamental_dis'] = False

        if clean_ch2_freq_var.get() == 1:
            input.which_plot['clean']['3rd_freq'] = True
        else:
            input.which_plot['clean']['3rd_freq'] = False

        if clean_ch2_dis_var.get() == 1:
            input.which_plot['clean']['3rd_dis'] = True
        else:
            input.which_plot['clean']['3rd_dis'] = False

        if clean_ch3_freq_var.get() == 1:
            input.which_plot['clean']['5th_freq'] = True
        else:
            input.which_plot['clean']['5th_freq'] = False

        if clean_ch3_dis_var.get() == 1:
            input.which_plot['clean']['5th_dis'] = True
        else:
            input.which_plot['clean']['5th_dis'] = False

        if clean_ch4_freq_var.get() == 1:
            input.which_plot['clean']['7th_freq'] = True
        else:
            input.which_plot['clean']['7th_freq'] = False

        if clean_ch4_dis_var.get() == 1:
            input.which_plot['clean']['7th_dis'] = True
        else:
            input.which_plot['clean']['7th_dis'] = False

        if clean_ch5_freq_var.get() == 1:
            input.which_plot['clean']['9th_freq'] = True
        else:
            input.which_plot['clean']['9th_freq'] = False

        if clean_ch5_dis_var.get() == 1:
            input.which_plot['clean']['9th_dis'] = True
        else:
            input.which_plot['clean']['9th_dis'] = False

    else:
        input.will_plot_clean_data = False
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
    global input
    if scale_time_var.get() == 1:
        time_scale_frame.grid(row=0, column=4)
        if which_time_scale_var.get() == 1:
            input.x_timescale = 's'
        elif which_time_scale_var.get() == 2:
            input.x_timescale = 'm'
        elif which_time_scale_var.get() == 3:
            input.x_timescale = 'h'
        else:
            input.x_timescale= 'u'
    else:
        time_scale_frame.grid_forget()
        input.x_timescale = 's'

def receive_file_format_radios():
    global input
    if change_fig_format_var.get() == 1:
        file_format_frame.grid(row=0, column=4)
        if which_file_format_var.get() == 1:
            input.fig_format = 'png'
        elif which_file_format_var.get() == 2:
            input.fig_format = 'tiff'
        elif which_file_format_var.get() == 3:
            input.fig_format = 'pdf'
        else:
            input.fig_format = 'u'
    else:
        file_format_frame.grid_forget()
        input.fig_format = 'png'

def receive_optional_checkboxes():
    global input

    if plot_dF_dD_together_var.get() == 1:
        input.will_plot_dF_dD_together = True
    else:
        input.will_plot_dF_dD_together = False

    if normalize_F_var.get() == 1:
        input.will_normalize_F = True
    else:
        input.will_normalize_F = False

    if plot_dD_v_dF_var.get() == 1:
        input.will_plot_dD_v_dF = True
    else:
        input.will_plot_dD_v_dF = False

    if interactive_plot_var.get() == 1:
        input.will_interactive_plot = True
        interactive_plot_opts.grid(row=6, column=4)
    else:
        input.will_interactive_plot = False
        interactive_plot_opts.grid_forget()

def err_check():
    global input
    '''Verify File Info'''
    # make sure file name was inputted
    if (input.file_name == '' or input.file_name == 'File name here (W/ EXTENSION)'):
        print("WARNING: File name not specified")
        sys.exit(1)

    if input.file_path == "Enter path to file (leave blank if in 'raw data' folder)":
        input.file_path = ""

    # verify baseline time entered, if only raw data box checked, no need to base time
    if input.will_plot_clean_data and input.abs_base_t0 == time(0,0,0) and input.abs_base_tf == time(0,0,0):
        print("WARNING: User indicated plot clean data,\ndid not enter baseline time")
        sys.exit(1)

    #verify data checks
    # find num channels tested
    clean_num_channels_tested = 0
    raw_num_channels_tested = 0

    for channel in input.which_plot['raw'].items():
        if channel[1] == True:
            raw_num_channels_tested += 1

    for channel in input.which_plot['clean'].items():
        if channel[1] == True:
            clean_num_channels_tested += 1

    total_num_channels_tested = raw_num_channels_tested + clean_num_channels_tested
    # check if any channels were selected to test
    if total_num_channels_tested == 0:
        print("WARNING: User did not select any channels to plot")
        sys.exit(1)

    # check if clean data was chosen, but no clean channels selected
    if input.will_plot_clean_data and clean_num_channels_tested == 0:
        print("WARNING: User indicated to plot clean channels,\ndid not indicate which")
        sys.exit(1)

    # check if raw data was chosen, but no raw data was selected
    if input.will_plot_raw_data and raw_num_channels_tested == 0:
        print("WARNING: User indicated to plot raw channels,\ndid not indicate which")
        sys.exit(1)

    # verify options
    if input.x_timescale == 'u':
        print("WARNING: User indicated to change timescale,\nbut did not specify what scale")
        sys.exit(1)

    if input.fig_format == 'u':
        print("WARNING: User indicated to change fig format,\nbut did not specify which")
        sys.exit(1)

    '''if interactive_plot_overtone == 0 and will_interactive_plot:
        print("WARNING: User indicated interactive plot,\nbut did not specify which overtone to analyze")
        sys.exit(1)'''



def set_window_flag():
    global input
    print("flag set")
    input.range_window_flag = True

def abort():
    sys.exit()

def submit():
    err_check()
    clear_figures()

    # only want new window to open once, not every time analysis is run
    global input

    # open secondary window with range selections for interactive plot
    if input.will_interactive_plot and not input.range_window_flag: # only open the window first time submitting
        range_select_window = Toplevel(root)
        range_select_window.bind('<Destroy>', set_window_flag)
        input.interactive_plot_overtone = int(interactive_plot_overtone_select.get())
        range_select_window.title("Select range")
        range_label = Label(range_select_window, text="Choose which section of graph\nis being selected for file saving:")
        range_label.grid(row=0, column=0, padx=10, pady=(8,16))
        
        # define and place entry for range options
        which_range_label = Label(range_select_window, text="Enter which range being selected\n(use identifier of your choosing; i.e. numbers or choice of label)" )
        which_range_label.grid(row=2, column=0, pady=(2,4), padx=4)
        which_range_entry = Entry(range_select_window, width=10, bg='white')
        which_range_entry.grid(row=3, column=0, pady=(2,4))

        # prompt to use theoretical or calibration values for peak frequency
        theoretical_or_calibration_frame = Frame(range_select_window)
        theoretical_or_calibration_frame.grid(row=5, column=0, columnspan=1)
        theoretical_or_calibration_var = IntVar()
        theoretical_or_calibration_label = Label(theoretical_or_calibration_frame, text="Use theoretical or calibration peak frequency values for calculations?\n(note: values defined in 'calibration_data' folder")
        theoretical_or_calibration_label.grid(row=5, column=0, pady=(2,4), columnspan=2, padx=6)
        theoretical_radio = Radiobutton(theoretical_or_calibration_frame, text='theoretical', variable=theoretical_or_calibration_var, value=1)
        theoretical_radio.grid(row=6, column=0, pady=(2,4))
        calibration_radio = Radiobutton(theoretical_or_calibration_frame, text='calibration', variable=theoretical_or_calibration_var, value=0)
        calibration_radio.grid(row=6, column=1, pady=(2,4))

        # run analysis button
        run_meta_analysis_button = Button(range_select_window, text="Run meta analysis\nof overtones", padx=6, pady=4, command=linear_regression)
        run_meta_analysis_button.grid(row=7, column=0, pady=4)

        # when interactive plot window opens, grabs number of range from text field
        def confirm_range():
            global input
            input.which_range_selecting = which_range_entry.get()
            input.will_use_theoretical_vals = theoretical_or_calibration_var

            print(f"Confirmed range: {input.which_range_selecting}")

        # button to submit range selected
        which_range_submit = Button(range_select_window, text='Confirm Range', padx=10, pady=4, command=confirm_range)
        which_range_submit.grid(row=4, column=0, pady=4)
        input.range_window_flag = True

    submitted_label.grid_forget()
    analyze_data(input)


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
icon = PhotoImage(file="res/m3b_comp.png")
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
file_name_entry.insert(0, "sample2.csv")
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
seconds_entry_t0.insert(0, "28")
minutes_entry_t0.insert(0, "26")
hours_entry_t0.insert(0, "16")
seconds_entry_tf.insert(0, "18")
minutes_entry_tf.insert(0, "36")
hours_entry_tf.insert(0, "16")

file_data_submit_button = Button(col0, text="Submit file information", padx=8, pady=6, width=20, command=col_names_submit)
file_data_submit_button.grid(row=10, column=0, pady=(16,4))
file_data_clear_button = Button(col0, text="Clear Entries", padx=8, pady=6, width=20, command=clear_file_data)
file_data_clear_button.grid(row=11, column=0, pady=4)


# SECOND COLUMN ENTRIES (define and place checkboxes for raw data)
plot_raw_data_var = IntVar()
plot_raw_data_check = Checkbutton(col1, text="Plot raw data", font=('TkDefaultFont', 12, 'bold'), variable=plot_raw_data_var,onvalue=1, offvalue=2, command=receive_raw_checkboxes)
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
plot_clean_data_check = Checkbutton(col2, text="Plot corrected data", font=('TkDefaultFont', 12, 'bold'), variable=plot_clean_data_var, onvalue=1, offvalue=0, command=receive_clean_checkboxes)
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

# options for the int plot
interactive_plot_opts = Frame(col3)
interactive_plot_overtone_label = Label(interactive_plot_opts, text="select overtone to analyze:")
interactive_plot_overtone_label.grid(row=0, column=0)
interactive_plot_overtone_select = Entry(interactive_plot_opts, width=10)
interactive_plot_overtone_select.grid(row=1, column=0)

# Options for changing the scale of x axis time
scale_time_var = IntVar()
which_range_var = IntVar()
scale_time_check = Checkbutton(col3, text="Change scale of time? (default (s))", variable=scale_time_var, onvalue=1, offvalue=0, command=receive_scale_radios)
scale_time_check.grid(row=7, column=4, pady=(32,0))
# default to seconds
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
#file_name = "sample2.csv"
#abs_base_t0 = time(16,26,28)
#abs_base_tf = time(16,36,18)

#file_name = "sample1.csv"
#abs_base_t0 = time(17,2,26)
#abs_base_tf = time(17,11,2)
