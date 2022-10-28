"""
Author: Brandon Pardi
Created: 9/7/2022, 12:40 pm
Last Modified: 10/27/2022 8:39 pm
"""

from tkinter import *
import sys
from datetime import time

'''
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


WIP
- options for saving different file types
- error checking? (need gui testing)
- look into:
    - interactive plots (plotly)
    - open explorer to search for file
'''


'''Variable Initializations'''

file_info = ['','']
will_plot_raw_data = False
will_plot_clean_data = False
will_overwrite_file = False
abs_base_t0 = time(0, 0, 0)
abs_base_tf = time(0, 0, 0)
x_timescale = 's'
will_plot_dF_dD_together = False
will_normalize_F = False
will_plot_dD_v_dF = False
will_interactive_plot = False
which_plot = {'raw': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                    '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                    '9th_freq': False, '9th_dis': False},

            'clean': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                    '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                    '9th_freq': False, '9th_dis': False}}


'''Function Defintions for UI events'''
def col_names_submit():
    file_info[0] = file_name_entry.get()
    file_info[1] = file_path_entry.get()
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
    global file_info
    global abs_base_t0
    global abs_base_tf
    file_info = []
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
        time_scale_frame.grid(row=9, column=4)
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


'''Enter event loop for UI'''
root = Tk()
col0 = Frame(root)
col1 = Frame(root)
col2 = Frame(root)
col3 = Frame(root)
fr = Frame(col0)
fr2 = Frame(col3)
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
fr2.grid(row=10, column=4)


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
file_name_entry.insert(0, "File name here (W/ EXTENSION)")
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
interactive_plot_check = Checkbutton(col3, text="Interactive plot (not avail)", variable=interactive_plot_var, onvalue=1, offvalue=0, command=receive_optional_checkboxes)
interactive_plot_check.grid(row=5, column=4)

scale_time_var = IntVar()
scale_time_check = Checkbutton(col3, text="Change scale of time? (default (S))", variable=scale_time_var, onvalue=1, offvalue=0, command=receive_scale_radios)
scale_time_check.grid(row=8, column=4, pady=(32,0))
# default to seconds
# PUT INTO FRAME
time_scale_frame = Frame(fr2)
which_time_scale_var = IntVar()
seconds_scale_check = Radiobutton(time_scale_frame, text="Seconds", variable=which_time_scale_var, value=1, command=receive_scale_radios)
seconds_scale_check.grid(row=0, column=0)
minutes_scale_check = Radiobutton(time_scale_frame, text="Minutes", variable=which_time_scale_var, value=2, command=receive_scale_radios)
minutes_scale_check.grid(row=0, column=1)
hours_scale_check = Radiobutton(time_scale_frame, text="Hours", variable=which_time_scale_var, value=3, command=receive_scale_radios)
hours_scale_check.grid(row=0, column=2)

# conclude UI event loop
root.mainloop()

''' Grab data from UI temp into variables for data analysis'''


# assign file info data
print(which_plot)
print(f"{abs_base_t0}\n{abs_base_tf}")
raw_num_channels_tested = 0
clean_num_channels_tested = 0
for channel in which_plot['raw'].items():
    if channel[1] == True:
        raw_num_channels_tested += 1

for channel in which_plot['clean'].items():
    if channel[1] == True:
        clean_num_channels_tested += 1

total_num_channels_tested = raw_num_channels_tested + clean_num_channels_tested
print(total_num_channels_tested)

''' ERROR CHECKING '''

'''Verify File Info'''
# make sure file name was inputted
if len(file_info) == 0:
    print("please define file information!")
    sys.exit(1)
elif (file_info[0] == '' or file_info[0] == 'File name here (W/ EXTENSION)'):
    print("File name not specified")
    sys.exit(1)
else:
    file_name = file_info[0]
    if file_info[1] == "Enter path to file (leave blank if in 'raw data' folder)":
        file_path = ""
    else:
        file_path = file_info[1]

# verify baseline time entered, if only raw data box checked, no need to base time
if will_plot_clean_data and abs_base_t0 == time(0,0,0) and abs_base_tf == time(0,0,0):
    print("User indicated plot clean data,\ndid not enter baseline time")
    sys.exit(1)

#verify data checks
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

print(file_info)
print(will_plot_dF_dD_together)
print(x_timescale)

print("\n\n")

'''TEMP ASSIGNMENTS to not have to enter into gui every time while debugging'''
file_name = "10102022_Collagen 2 at 25ug per ml and SF at 37C_n=1 DD.csv"

#file_path = ""
#clean_num_channels_tested = 10
#abs_base_t0 = time(8,29,48)
abs_base_t0 = time(17,2,26)
#abs_base_tf = time(9,5,55)
abs_base_tf = time(17,11,2)
