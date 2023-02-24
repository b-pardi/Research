"""
Author: Brandon Pardi
Created: 9/7/2022, 1:53 pm
Last Modified: 2/23/2022, 9:21 pm
"""

import tkinter as tk
import sys
import os
from datetime import time
import inspect

from analyze import analyze_data, clear_figures
from lin_reg import *

'''
WIP
func/class for range select window (maybe just in col 4)
remove as many selfs as possible from classes (specifically col 1 and 4)
'''

'''Variable Initializations'''
class Input:
    def __init__(self): 
        self.file_name = ''
        self.file_path = ''
        self.will_plot_raw_data = False
        self.will_plot_clean_data = False
        self.will_overwrite_file = False # if user wants copy of data data saved after processing
        self.abs_base_t0 = time(0, 0, 0) # beginning of baseline time
        self.abs_base_tf = time(0, 0, 0) # end of baseline time
        self.fig_format = 'png' # format to save figures that can be changed in the gui to tiff or pdf
        self.x_timescale = 's' # change scale of time of x axis of plots from seconds to either minutes or hours
        self.will_plot_dF_dD_together = False # indicates if user selected multi axis plot of dis and freq
        self.will_normalize_F = False # indicates if user selected to normalize frequency data
        self.will_plot_dD_v_dF = False # indicates if user selected to plot change in dis vs change in freq
        self.will_interactive_plot = False # indicates if user selected interactive plot option
        self.submit_pressed = False # submitting gui data the first time has different implications than if resubmitting
        self.which_range_selecting = '' # which range of the interactive plot is about to be selected
        self.interactive_plot_overtone = 0 # which overtone will be analyzed in the interactive plot
        self.will_use_theoretical_vals = False # indicates if using calibration data or theoretical values for peak frequencies
        self.range_frame_flag = False
        self.which_plot = {'raw': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': False, '11th_freq': False, '11th_dis': False,
                            '13th_freq': False, '13th_dis': False},

                    'clean': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': False, '11th_freq': False, '11th_dis': False,
                            '13th_freq': False, '13th_dis': False}}

input = Input()

# returns the ordinal suffix of number (i.e. the rd in 3rd)
# instead of 'st' for 1st, will return 'fundamental'
def ordinal(n):
    overtone_ordinal = ("th" if 4<=n%100<=20 else {1:"Fundamental",2:"nd",3:"rd"}.get(n%10, "th"))
    if n != 1:
        overtone_ordinal = str(n) + overtone_ordinal
    return overtone_ordinal
    
def create_checkboxes(frame, cleanliness):
    keys = list(input.which_plot[cleanliness].keys())
    checks = []
    for i in range(14):
        # assign correct overtone and determine if frequency or dissipation
        overtone = (i+1) % 2
        f_or_d = ''
        key = (cleanliness, keys[i])
        if overtone == 1:
            overtone = i+1
            f_or_d = 'frequency'
        else: 
            overtone = i
            f_or_d = 'dissipation'

        text = ordinal(overtone) + ' ' + f_or_d
        intvar = tk.IntVar()
        if cleanliness == 'raw':
            cb = tk.Checkbutton(frame, text=text, variable=intvar, onvalue=1, offvalue=0, command=frame.receive_raw_checkboxes)
        else:
            cb = tk.Checkbutton(frame, text=text, variable=intvar, onvalue=1, offvalue=0, command=frame.receive_clean_checkboxes)

        check = CheckBox(intvar, cb, key)
        checks.append(check)

    return checks

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

    # verify data checks
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


def set_frame_flag():
    global input
    print("flag set")
    input.range_frame_flag = True

def abort():
    sys.exit()


# menu class inherits Tk class 
class App(tk.Tk):
    def __init__(self):
        super().__init__() # initialize parent class for the child

        self.title = 'BraTaDio QCMd Expert'
        self.iconphoto(False, tk.PhotoImage(file="res/m3b_comp.png"))
        
        # defining containers
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # initializing frames
        self.frames = {}
        self.col1 = Col1 # file input information
        self.col2 = Col2 # indicate overtones to plot raw data
        self.col3 = Col3 # indicate overtones to plot baseline corrected data
        self.col4 = Col4 # special plot options
        self.col5 = Col5 # interactive plot options

        # define and pack frames
        for f in [Col1, Col2, Col3, Col4, Col5]:
            frame = f(self, container)
            self.frames[f] = frame
            print(f)
            if frame.is_visible:
                frame.grid(row=0, column=frame.col_position, sticky = 'nsew')

    def repack_frames(self):
        for frame in self.frames:
            frame = self.frames[frame]
            if frame.is_visible:
                print(frame)
                frame.grid(row=0, column=frame.col_position, sticky = 'nsew')
            else:
                frame.grid_forget()

class Col1(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.col_position = 0
        self.is_visible = True
        file_name_label = tk.Label(self, text="Enter data file information", font=('TkDefaultFont', 12, 'bold'))
        file_name_label.grid(row=0, column=0, pady=(14,16), padx=(6,0))
        
        self.file_name_entry = tk.Entry(self, width=40, bg='white', fg='gray')
        self.file_name_entry.grid(row=2, column=0, columnspan=1, padx=8, pady=4)
        #self.file_name_entry.insert(0, "File name here (W/ EXTENSION)")
        self.file_name_entry.insert(0, "sample2.csv")
        self.file_name_entry.bind("<FocusIn>", self.handle_fn_focus_in)
        self.file_name_entry.bind("<FocusOut>", self.handle_fn_focus_out)

        self.file_path_entry = tk.Entry(self, width=40, bg='white', fg='gray')
        self.file_path_entry.grid(row=3, column=0, columnspan=1, padx=8, pady=4)
        self.file_path_entry.insert(0, "Enter path to file (leave blank if in 'raw data' folder)")
        self.file_path_entry.bind("<FocusIn>", self.handle_fp_focus_in)
        self.file_path_entry.bind("<FocusOut>", self.handle_fp_focus_out)

        self.file_overwrite_var = tk.IntVar()
        self.file_overwrite_check = tk.Checkbutton(self, text='New file with processed data?', variable=self.file_overwrite_var, onvalue=1, offvalue=0, pady=10)
        self.file_overwrite_check.grid(row=5, column=0)

        self.baseline_frame = tk.Frame(self)
        self.baseline_time_label = tk.Label(self, text="Enter absolute baseline time")
        self.baseline_time_label.grid(row=6, column=0)

        self.baseline_frame.grid(row=7, column=0, columnspan=1)
        self.hours_label_t0 = tk.Label(self.baseline_frame, text="H0: ")
        self.hours_label_t0.grid(row=0, column=0)
        self.hours_entry_t0 = tk.Entry(self.baseline_frame, width=5, bg='white', fg='gray')
        self.hours_entry_t0.grid(row=0, column=1)
        self.minutes_label_t0 = tk.Label(self.baseline_frame, text="M0: ")
        self.minutes_label_t0.grid(row=0, column=2)
        self.minutes_entry_t0 = tk.Entry(self.baseline_frame, width=5, bg='white', fg='gray')
        self.minutes_entry_t0.grid(row=0, column=3)
        self.seconds_label_t0 = tk.Label(self.baseline_frame, text="S0: ")
        self.seconds_label_t0.grid(row=0, column=4)
        self.seconds_entry_t0 = tk.Entry(self.baseline_frame, width=5, bg='white', fg='gray')
        self.seconds_entry_t0.grid(row=0, column=5)

        self.hours_label_tf = tk.Label(self.baseline_frame, text="Hf: ")
        self.hours_label_tf.grid(row=1, column=0)
        self.hours_entry_tf = tk.Entry(self.baseline_frame, width=5, bg='white', fg='gray')
        self.hours_entry_tf.grid(row=1, column=1)
        self.minutes_label_tf = tk.Label(self.baseline_frame, text="Mf: ")
        self.minutes_label_tf.grid(row=1, column=2)
        self.minutes_entry_tf = tk.Entry(self.baseline_frame, width=5, bg='white', fg='gray')
        self.minutes_entry_tf.grid(row=1, column=3)
        self.seconds_label_tf = tk.Label(self.baseline_frame, text="Sf: ")
        self.seconds_label_tf.grid(row=1, column=4)
        self.seconds_entry_tf = tk.Entry(self.baseline_frame, width=5, bg='white', fg='gray')
        self.seconds_entry_tf.grid(row=1, column=5)

        #temp inserts to not have to reenter data every test
        self.seconds_entry_t0.insert(0, "28")
        self.minutes_entry_t0.insert(0, "26")
        self.hours_entry_t0.insert(0, "16")
        self.seconds_entry_tf.insert(0, "18")
        self.minutes_entry_tf.insert(0, "36")
        self.hours_entry_tf.insert(0, "16")

        self.cleared_label = tk.Label(self, text="Cleared!")
        self.submitted_label = tk.Label(self, text="Submitted!")
        self.err_label = tk.Label(self, text="Error occured,\nplease see terminal for details", font=("Arial",14))

        self.file_data_submit_button = tk.Button(self, text="Submit file information", padx=8, pady=6, width=20, command=self.col_names_submit)
        self.file_data_submit_button.grid(row=10, column=0, pady=(16,4))
        self.file_data_clear_button = tk.Button(self, text="Clear Entries", padx=8, pady=6, width=20, command=self.clear_file_data)
        self.file_data_clear_button.grid(row=11, column=0, pady=4)
        
    def handle_fn_focus_in(self, _):
        if self.file_name_entry.get() == "File name here (W/ EXTENSION)":
            self.file_name_entry.delete(0, tk.END)
            self.file_name_entry.config(fg='black')

    def handle_fn_focus_out(self, _):
        if self.file_name_entry.get() == "":
            self.file_name_entry.delete(0, tk.END)
            self.file_name_entry.config(fg='gray')
            self.file_name_entry.insert(0, "File name here (W/ EXTENSION)")

    def handle_fp_focus_in(self, _):
        if self.file_path_entry.get() == "Enter path to file (leave blank if in 'raw data' folder)":
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.config(fg='black')

    def handle_fp_focus_out(self, _):
        if self.file_path_entry.get() == "":
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.config(fg='gray')
            self.file_path_entry.insert(0, "Enter path to file (leave blank if in 'raw data' folder)")    

    def col_names_submit(self):
        global input
        input.file_name = self.file_name_entry.get()
        input.file_path = self.file_path_entry.get()
        if self.file_overwrite_var.get() == 1:
            input.will_overwrite_file = True
        else:
            input.will_overwrite_file = False

        h0 = self.hours_entry_t0.get()
        m0 = self.minutes_entry_t0.get()
        s0 = self.seconds_entry_t0.get()
        hf = self.hours_entry_tf.get()
        mf = self.minutes_entry_tf.get()
        sf = self.seconds_entry_tf.get()
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
            self.err_label.grid(row=20, column=0)
            print(f"Please enter integer values for time: {exc}")
        self.submitted_label.grid(row=13, column=0)
        self.submitted_label.after(5000, lambda: self.submitted_label.grid_forget())


    def clear_file_data(self):
        global input
        input.abs_base_t0 = time(0, 0, 0)
        input.abs_base_tf = time(0, 0, 0)
        self.cleared_label.grid(row=12, column=0)
        self.file_name_entry.delete(0, tk.END)
        self.file_path_entry.delete(0, tk.END)
        self.hours_entry_t0.delete(0, tk.END)
        self.minutes_entry_t0.delete(0, tk.END)
        self.seconds_entry_t0.delete(0, tk.END)
        self.hours_entry_tf.delete(0, tk.END)
        self.minutes_entry_tf.delete(0, tk.END)
        self.seconds_entry_tf.delete(0, tk.END)
        self.file_overwrite_var.set(0)
        self.submitted_label.grid_forget()

class Time_Input(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)

class CheckBox:
    def __init__(self, intvar, checkbutton, key):
        self.intvar = intvar
        self.checkbutton = checkbutton
        self.key = key 
    

class Col2(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.col_position = 1
        self.is_visible = True
        self.plot_raw_data_var = tk.IntVar()
        self.plot_raw_data_check = tk.Checkbutton(self, text="Plot raw data", font=('TkDefaultFont', 12, 'bold'), variable=self.plot_raw_data_var, onvalue=1, offvalue=2, command=self.receive_raw_checkboxes)
        self.plot_raw_data_check.grid(row=0, column=0, pady=(12,8), padx=(16,32))
        self.which_raw_channels_label = tk.Label(self, text="Select overtones for full data")

        # checkboxes for selecting which channels to plot for raw data
        self.raw_checks = create_checkboxes(self, 'raw')

        self.clear_raw_checks_button = tk.Button(self, text='clear all', width=8, command=self.clear_raw_checks)
        self.select_all_raw_checks_button = tk.Button(self, text='select all', width=8, command=self.select_all_raw_checks)

    def receive_raw_checkboxes(self):
        global input

        if self.plot_raw_data_var.get() == 1:
            input.will_plot_raw_data = True
            self.which_raw_channels_label.grid(row=1, column=0, pady=(0,26))
            self.select_all_raw_checks_button.grid(row=19, column=0, padx=(0,0), pady=(12,4))
            self.clear_raw_checks_button.grid(row=20, column=0, padx=(0,0), pady=(4,4))
            
            for i, cb in enumerate(self.raw_checks):
                cb.checkbutton.grid(row=i+2, column=0)

                if cb.intvar.get() == 1:
                    input.which_plot[cb.key[0]][cb.key[1]] = True
                else:
                    input.which_plot[cb.key[0]][cb.key[1]] = False

        else:
            input.will_plot_raw_data = False
            self.which_raw_channels_label.grid_forget()

            for cb in self.raw_checks:
                cb.checkbutton.grid_forget()

            self.select_all_raw_checks_button.grid_forget()
            self.clear_raw_checks_button.grid_forget()
        
    def clear_raw_checks(self):
        global input
        for cb in self.raw_checks:
            cb.intvar.set(0)

        for channel in input.which_plot['raw']:
            input.which_plot['raw'][channel] = False
            
    def select_all_raw_checks(self):
        global input
        for cb in self.raw_checks:
            cb.intvar.set(1)

        for channel in input.which_plot['raw']:
            input.which_plot['raw'][channel] = True

        print(input.which_plot)


class Col3(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.col_position = 2
        self.is_visible = True
        self.plot_clean_data_var = tk.IntVar()
        self.plot_clean_data_check = tk.Checkbutton(self, text="Plot corrected data", font=('TkDefaultFont', 12, 'bold'), variable=self.plot_clean_data_var, onvalue=1, offvalue=0, command=self.receive_clean_checkboxes)
        self.plot_clean_data_check.grid(row=0, column=0, pady=(12,8), padx=(32,16))
        self.which_clean_channels_label = tk.Label(self, text="Select overtones for\nbaseline corrected data")

        # checkboxes for selecting which channels to plot for clean data
        self.clean_checks = create_checkboxes(self, 'clean')

        self.clear_clean_checks_button = tk.Button(self, text='clear all', width=8, command=self.clear_clean_checks)
        self.select_all_clean_checks_button = tk.Button(self, text='select all', width=8, command=self.select_all_clean_checks)


    def receive_clean_checkboxes(self):
        global input
        if self.plot_clean_data_var.get() == 1:
            input.will_plot_clean_data = True
            self.which_clean_channels_label.grid(row=1, column=0, pady=(0,12))
            self.select_all_clean_checks_button.grid(row=19, column=0, padx=(0,0), pady=(12,4))
            self.clear_clean_checks_button.grid(row=20, column=0, padx=(0,0), pady=(4,4))
            
            for i, cb in enumerate(self.clean_checks):
                cb.checkbutton.grid(row=i+2, column=0)

                if cb.intvar.get() == 1:
                    input.which_plot[cb.key[0]][cb.key[1]] = True
                else:
                    input.which_plot[cb.key[0]][cb.key[1]] = False

        else:
            input.will_plot_clean_data = False
            self.which_clean_channels_label.grid_forget()
            
            for cb in self.clean_checks:
                cb.checkbutton.grid_forget()

            self.select_all_clean_checks_button.grid_forget()
            self.clear_clean_checks_button.grid_forget()

    def clear_clean_checks(self):
        global input
        for cb in self.clean_checks:
            cb.intvar.set(0)

        for channel in input.which_plot['clean']:
            input.which_plot['clean'][channel] = False

    def select_all_clean_checks(self):
        global input

        for cb in self.clean_checks:
            cb.intvar.set(1)

        for channel in input.which_plot['clean']:
            input.which_plot['clean'][channel] = True


class Col4(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        #tk.Frame.__init__(self)
        #App.__init__(self)
        self.col_position = 3
        self.is_visible = True
        self.parent = parent
        self.container = container
        self.plot_options_label = tk.Label(self, text="Options for plots", font=('TkDefaultFont', 12, 'bold'))
        self.plot_options_label.grid(row=0, column=4, pady=(14,16), padx=(0,6))

        self.plot_dF_dD_together_var = tk.IntVar()
        self.plot_dF_dD_together_check = tk.Checkbutton(self, text="Plot Δf and Δd together", variable=self.plot_dF_dD_together_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.plot_dF_dD_together_check.grid(row=2, column=4)
        self.normalize_F_var = tk.IntVar()
        self.normalize_F_check = tk.Checkbutton(self, text="Normalize Δf with its\nrespective overtone", variable=self.normalize_F_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.normalize_F_check.grid(row=3, column=4)
        self.plot_dD_v_dF_var = tk.IntVar()
        self.plot_dD_v_dF_check = tk.Checkbutton(self, text="Plot Δd vs Δf", variable=self.plot_dD_v_dF_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.plot_dD_v_dF_check.grid(row=4, column=4)
        self.interactive_plot_var = tk.IntVar()
        self.interactive_plot_check = tk.Checkbutton(self, text="Interactive plot", variable=self.interactive_plot_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.interactive_plot_check.grid(row=5, column=4)

        # options for the int plot
        self.interactive_plot_opts = tk.Frame(self)
        self.interactive_plot_overtone_label = tk.Label(self.interactive_plot_opts, text="select overtone to analyze:")
        self.interactive_plot_overtone_label.grid(row=0, column=0)
        self.interactive_plot_overtone_select = tk.Entry(self.interactive_plot_opts, width=10)
        self.interactive_plot_overtone_select.grid(row=1, column=0)

        # Options for changing the scale of x axis time
        self.scale_time_var = tk.IntVar()
        self.which_range_var = tk.IntVar()
        self.scale_time_check = tk.Checkbutton(self, text="Change scale of time? (default (s))", variable=self.scale_time_var, onvalue=1, offvalue=0, command=self.receive_scale_radios)
        self.scale_time_check.grid(row=7, column=4, pady=(32,0))
        # default to seconds
        self.time_scale_frame = tk.Frame(self)
        self.which_time_scale_var = tk.IntVar()
        self.seconds_scale_check = tk.Radiobutton(self.time_scale_frame, text="Seconds", variable=self.which_time_scale_var, value=1, command=self.receive_scale_radios)
        self.seconds_scale_check.grid(row=0, column=0)
        self.minutes_scale_check = tk.Radiobutton(self.time_scale_frame, text="Minutes", variable=self.which_time_scale_var, value=2, command=self.receive_scale_radios)
        self.minutes_scale_check.grid(row=0, column=1)
        self.hours_scale_check = tk.Radiobutton(self.time_scale_frame, text="Hours", variable=self.which_time_scale_var, value=3, command=self.receive_scale_radios)
        self.hours_scale_check.grid(row=0, column=2)

        # Options for changing file format of saved scatter plot figures
        self.change_fig_format_var = tk.IntVar()
        self.change_fig_format_check = tk.Checkbutton(self, text="Change figure file format? (default .png)", variable=self.change_fig_format_var, onvalue=1, offvalue=0, command=self.receive_file_format_radios)
        self.change_fig_format_check.grid(row=14, column=4, pady=(8,0))
        # default png
        self.file_format_frame = tk.Frame(self)
        self.which_file_format_var = tk.IntVar()
        self.png_check = tk.Radiobutton(self.file_format_frame, text=".png", variable=self.which_file_format_var, value=1, command=self.receive_file_format_radios)
        self.png_check.grid(row=0, column=0)
        self.tiff_check = tk.Radiobutton(self.file_format_frame, text=".tiff", variable=self.which_file_format_var, value=2, command=self.receive_file_format_radios)
        self.tiff_check.grid(row=0, column=1)
        self.pdf_check = tk.Radiobutton(self.file_format_frame, text=".pdf", variable=self.which_file_format_var, value=3, command=self.receive_file_format_radios)
        self.pdf_check.grid(row=0, column=2)

        self.submit_button = tk.Button(self, text="Submit", padx=8, pady=6, width=20, command=self.submit)
        self.submit_button.grid(row=20, column=4, pady=4)

        self.abort_button = tk.Button(self, text="Abort", padx=8, pady=6, width=20, command=abort)
        self.abort_button.grid(row=19, column=4, pady=4)

    def receive_scale_radios(self):
        global input
        if self.scale_time_var.get() == 1:
            self.time_scale_frame.grid(row=8, column=4)
            if self.which_time_scale_var.get() == 1:
                input.x_timescale = 's'
            elif self.which_time_scale_var.get() == 2:
                input.x_timescale = 'm'
            elif self.which_time_scale_var.get() == 3:
                input.x_timescale = 'h'
            else:
                input.x_timescale= 'u'
        else:
            self.time_scale_frame.grid_forget()
            input.x_timescale = 's'

    def receive_file_format_radios(self):
        global input
        if self.change_fig_format_var.get() == 1:
            self.file_format_frame.grid(row=15, column=4)
            if self.which_file_format_var.get() == 1:
                input.fig_format = 'png'
            elif self.which_file_format_var.get() == 2:
                input.fig_format = 'tiff'
            elif self.which_file_format_var.get() == 3:
                input.fig_format = 'pdf'
            else:
                input.fig_format = 'u'
        else:
            self.file_format_frame.grid_forget()
            input.fig_format = 'png'

    def receive_optional_checkboxes(self):
        global input

        if self.plot_dF_dD_together_var.get() == 1:
            input.will_plot_dF_dD_together = True
        else:
            input.will_plot_dF_dD_together = False

        if self.normalize_F_var.get() == 1:
            input.will_normalize_F = True
        else:
            input.will_normalize_F = False

        if self.plot_dD_v_dF_var.get() == 1:
            input.will_plot_dD_v_dF = True
        else:
            input.will_plot_dD_v_dF = False

        if self.interactive_plot_var.get() == 1:
            input.will_interactive_plot = True
            input.range_frame_flag = True
            self.parent.frames[Col5].is_visible = True
            self.parent.repack_frames()
            self.interactive_plot_opts.grid(row=6, column=4)
        else:
            print("ELSE")
            input.will_interactive_plot = False
            input.range_frame_flag = False
            self.parent.frames[Col5].is_visible = False
            self.parent.repack_frames()
            self.interactive_plot_opts.grid_forget()

    def submit(self):
        err_check()
        clear_figures()
        global input
        col5 = self.parent.frames[Col5]
        input.interactive_plot_overtone = int(self.interactive_plot_overtone_select.get())

        analyze_data(input)



class Col5(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.col_position = 4
        self.is_visible = input.range_frame_flag
        self.parent = parent
        col4 = self.parent.frames[Col4]
        header_label = tk.Label(self, text="Interactive Plot Details", font=('TkDefaultFont', 12, 'bold'))
        header_label.grid(row=0, column=0, pady=(14,16), padx=(0,6))
        range_label = tk.Label(self, text="Choose which section of graph\nis being selected for file saving:")
        range_label.grid(row=1, column=0, padx=10, pady=(8,16))
        # open secondary window with range selections for interactive plot
        
        # define and place entry for range options
        which_range_label = tk.Label(self, text="Enter which range being selected\n(use identifier of your choosing\ni.e. numbers or choice of label)" )
        which_range_label.grid(row=2, column=0, pady=(2,4), padx=4)
        which_range_entry = tk.Entry(self, width=10, bg='white')
        which_range_entry.grid(row=3, column=0, pady=(2,4))

        # prompt to use theoretical or calibration values for peak frequency
        theoretical_or_calibration_frame = tk.Frame(self)
        theoretical_or_calibration_frame.grid(row=5, column=0, columnspan=1)
        theoretical_or_calibration_var = tk.IntVar()
        theoretical_or_calibration_label = tk.Label(theoretical_or_calibration_frame, text="Use theoretical or calibration\npeak frequency values for calculations?\n(note: values defined in 'calibration_data' folder")
        theoretical_or_calibration_label.grid(row=5, column=0, pady=(2,4), columnspan=2, padx=6)
        theoretical_radio = tk.Radiobutton(theoretical_or_calibration_frame, text='theoretical', variable=theoretical_or_calibration_var, value=1)
        theoretical_radio.grid(row=6, column=0, pady=(2,4))
        calibration_radio = tk.Radiobutton(theoretical_or_calibration_frame, text='calibration', variable=theoretical_or_calibration_var, value=0)
        calibration_radio.grid(row=6, column=1, pady=(2,4))

        # run analysis button
        run_meta_analysis_button = tk.Button(self, text="Run meta analysis\nof overtones", padx=6, pady=4, command=linear_regression)
        run_meta_analysis_button.grid(row=7, column=0, pady=4)

        # when interactive plot window opens, grabs number of range from text field
        def confirm_range():
            global input
            input.which_range_selecting = which_range_entry.get()
            input.will_use_theoretical_vals = theoretical_or_calibration_var

            print(f"Confirmed range: {input.which_range_selecting}")

        # button to submit range selected
        which_range_submit = tk.Button(self, text='Confirm Range', padx=10, pady=4, command=confirm_range)
        which_range_submit.grid(row=4, column=0, pady=4)
        input.range_frame_flag = True


menu = App()
menu.mainloop()



'''TEMP ASSIGNMENTS to not have to enter into gui every time while debugging'''
#file_name = "sample2.csv"
#abs_base_t0 = time(16,26,28)
#abs_base_tf = time(16,36,18)

#file_name = "sample1.csv"
#abs_base_t0 = time(17,2,26)
#abs_base_tf = time(17,11,2)
