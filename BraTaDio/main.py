"""
Author: Brandon Pardi
Created: 9/7/2022, 1:53 pm
Last Modified: 3/8/2022, 9:16 pm
"""

import tkinter as tk
from tkinter import filedialog
import sys
import os
from datetime import time
from tkinter import colorchooser
import json
import pandas as pd

import Exceptions
from analyze import analyze_data, ordinal, select_calibration_data
from format_file import format_raw_data
from modeling import thin_film_liquid_analysis, thin_film_air_analysis, sauerbrey, avgs_analysis, gordon_kanazawa

'''Variable Initializations'''
class Input:
    def __init__(self): 
        self.file = ''
        self.calibration_file = ''
        self.will_plot_raw_data = False
        self.will_plot_clean_data = False
        self.will_overwrite_file = False # if user wants copy of data data saved after processing
        self.abs_base_t0 = time(0, 0, 0) # beginning of baseline time
        self.abs_base_tf = time(0, 0, 0) # end of baseline time
        self.rel_t0 = 0
        self.rel_tf = 0
        self.fig_format = 'png' # format to save figures that can be changed in the gui to tiff or pdf
        self.x_timescale = 's' # change scale of time of x axis of plots from seconds to either minutes or hours
        self.will_plot_dF_dD_together = False # indicates if user selected multi axis plot of dis and freq
        self.will_normalize_F = False # indicates if user selected to normalize frequency data
        self.will_plot_dD_v_dF = False # indicates if user selected to plot change in dis vs change in freq
        self.will_interactive_plot = False # indicates if user selected interactive plot option
        self.submit_pressed = False # submitting gui data the first time has different implications than if resubmitting
        self.which_range_selecting = '' # which range of the interactive plot is about to be selected
        self.interactive_plot_overtones = {'raw': 0, 'clean': 0} # which overtones for clean and raw
        self.range_frame_flag = False
        self.first_run = True
        self.latex_installed = False
        self.will_use_theoretical_vals = True
        self.calibration_data_from_file = False
        self.will_plot_temp_v_time = False
        self.will_correct_slope = False
        self.is_relative_time = False # depending on file src input, some machines record time relatively (start at 0) or absolutely (start at current time of day)
        self.file_src_type = '' # different machines output data differently
        self.which_plot = {'raw': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': False, '11th_freq': False, '11th_dis': False,
                            '13th_freq': False, '13th_dis': False},

                    'clean': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': False, '11th_freq': False, '11th_dis': False,
                            '13th_freq': False, '13th_dis': False}}

input = Input()

INPUT_ALTERED_FLAG = False

def set_input_altered_flag(flag, notif=True):
    global input
    global INPUT_ALTERED_FLAG
    if not INPUT_ALTERED_FLAG and notif:
        print("Input altered, will run calculations")
    INPUT_ALTERED_FLAG = flag
    
def check_entries(frame, data):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Entry):
            entry_text = widget.get()
            if not entry_text.strip():  # Check if the entry is empty or contains only whitespace
                key = widget.cget("text")  # Assuming the Entry's text corresponds to a key in the dictionary
                if key in data:
                    widget.delete(0, tk.END)
                    widget.insert(tk.END, data[key])

def browse_files(file_dir, btn_title):
    fp = filedialog.askopenfilename(initialdir=os.path.join(os.getcwd(), file_dir),
                                          title=btn_title,
                                          filetypes=(("Comma Separated Value files", "*.csv"),
                                                    ("Excel file 2007 and later", "*.xlsx"),
                                                    ("Excel file 1997-2003", "*.xls"),
                                                    ("Text file", "*.txt")))
    
    return fp

def select_data_file(label):
    global input
    fp = browse_files('raw_data', 'Select Data File')
    input.file = fp
    label.configure(text=f"File Selected: {os.path.basename(fp)}")
    print(input.file)

def select_calibration_file(label):
    global input
    fp = browse_files('offset_data', 'Select Calibration File')
    input.calibration_file = fp
    label.configure(text=f"File Selected: {os.path.basename(fp)}")
    print(input.calibration_file)

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

def generate_labelled_entries(frame):
    keys = list(input.which_plot['clean'].keys())
    labelled_entries = []
    for i in range(14): # 7 different overtones each with freq and dis
        overtone = (i+1) % 2
        key = keys[i]
        overtone = i+1 if overtone == 1 else i
        f_or_d = 'frequency' if overtone == i+1 else 'dissipation'
        text = ordinal(overtone) + ' ' + f_or_d
        label = tk.Label(frame, text=text)
        entry = tk.Entry(frame)
        labelled_entries.append(LabelledEntry(label, entry))

    return labelled_entries

def err_check():
    global input
    '''Verify File Info'''
    # make sure file name was inputted
    if (input.file == ''):
        print("WARNING: File name not specified")
        sys.exit(1)

    # verify baseline time entered, if only raw data box checked, no need to base time
    if (not input.is_relative_time and input.will_plot_clean_data) and input.abs_base_t0 == time(0,0,0) and input.abs_base_tf == time(0,0,0):
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

def exit():
    sys.exit()

# menu class inherits Tk class 
class App(tk.Tk):
    def __init__(self):
        super().__init__() # initialize parent class for the child

        self.title('BraTaDio - Quartz Crystal Microbalance Analysis Tool')
        self.iconphoto(False, tk.PhotoImage(file="res/m3b_comp.png"))
        #self.configure(bg=DARKEST)
        #self.tk_setPalette(background=DARKEST, foreground=WHITE)

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

        # define and pack frames
        for f in [Col1, Col2, Col3, Col4]:
            frame = f(self, container)
            self.frames[f] = frame
            print(f)
            if frame.is_visible:
                frame.grid(row=0, column=frame.col_position, sticky = 'nsew')

        # intialize calibration window to be opened later
        self.calibration_window = CalibrationWindow

        # intialize modeling window to be opened later
        self.modeling_window = ModelingWindow

        # initialize plot customizations with previously saved values
        self.plot_opts_window = PlotOptsWindow
        with open('plot_opts/plot_customizations.json', 'r') as fp:
            self.options = json.load(fp)
        self.prev_opts = self.options

    def repack_frames(self):
        for frame in self.frames:
            frame = self.frames[frame]
            if frame.is_visible:
                print(frame)
                frame.grid(row=0, column=frame.col_position, sticky = 'nsew')
            else:
                frame.grid_forget()

    def open_plot_opts_window(self):
        self.plot_opts_window.open_opts_window(self)
        self.plot_opts_window.fill_opts_window(self)

    def open_calibration_window(self):
        self.calibration_window.open_calibration_window(self)
        self.calibration_window.fill_calibration_window(self)

    def clear_selections(self):
        self.calibration_window.clear_selections(self)

    def confirm_values(self):
        self.calibration_window.confirm_values(self)

    def open_model_window(self):
        self.modeling_window.open_modeling_window(self)
        self.modeling_window.fill_modeling_window(self)

    def test_model_window(self):
        self.modeling_window.test_modeling_window(self)

    def choose_color(self, ov_num):
        self.plot_opts_window.choose_color(self, ov_num)

    def receive_scale_radios(self):
        self.plot_opts_window.receive_scale_radios(self)

    def receive_file_format_radios(self):
        self.plot_opts_window.receive_file_format_radios(self)

    def set_default_values(self):
        self.plot_opts_window.set_default_values(self)

    def confirm_opts(self):
        self.plot_opts_window.confirm_opts(self)

    def set_text(self, entry, text):
        self.plot_opts_window.set_text(self, entry, text)

    def confirm_range(self):
        self.modeling_window.confirm_range(self)

class srcFileFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        self.file_src_types = ['QCM-d', 'QCM-i', 'Qsense']
        self.file_src_type = ''
        file_src_label = tk.Label(self, text="What is the source of the data file?")
        file_src_label.grid(row=0, column=0, columnspan=3, pady=(0,4), padx=6)
        self.file_src_var = tk.IntVar(value=5) # set value to one not in radios, so none selected by default
        self.opt1_radio = tk.Radiobutton(self, text="Open QCM Next", variable=self.file_src_var, value=0, command=self.handle_radios)
        self.opt1_radio.grid(row=1, column=0)
        self.opt2_radio = tk.Radiobutton(self, text="QCM-I ", variable=self.file_src_var, value=1, command=self.handle_radios)
        self.opt2_radio.grid(row=1, column=1)
        self.opt3_radio = tk.Radiobutton(self, text="QSense ", variable=self.file_src_var, value=2, command=self.handle_radios)
        self.opt3_radio.grid(row=1, column=2)

        self.calibration_warning_label = tk.Label(self, text="WARNING: When using Qsense,\nif not calibration data entered,\nuser is limited to only basic visualizations")

    def handle_radios(self):
        self.file_src_type = self.file_src_types[self.file_src_var.get()]
        if self.file_src_type == 'QCM-d':
            input.is_relative_time = False
        elif self.file_src_type == 'QCM-i':
            input.is_relative_time = True
        elif self.file_src_type == 'Qsense':
            input.is_relative_time = True
            self.calibration_warning_label.grid(row=2, column=0, columnspan=3)
        self.container.blit_time_input_frame(input.is_relative_time)

class calibrationValsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # prompt to use theoretical or calibration values for peak frequency
        self.theoretical_or_calibration_peak_freq_frame = tk.Frame(self)
        self.theoretical_or_calibration_peak_freq_frame.grid(row=7, column=0, columnspan=1, pady=(16,0))
        self.theoretical_or_calibration_peak_freq_var = tk.IntVar()
        self.theoretical_or_calibration_peak_freq_var.set(-1)
        theoretical_or_calibration_peak_freq_label = tk.Label(self.theoretical_or_calibration_peak_freq_frame,
                                                text="Use theoretical or offset\npeak frequency values for calculations")
        theoretical_or_calibration_peak_freq_label.grid(row=0, column=0, pady=(2,4), columnspan=2, padx=6)
        
        self.theoretical_peak_freq_radio = tk.Radiobutton(self.theoretical_or_calibration_peak_freq_frame, text='theoretical', variable=self.theoretical_or_calibration_peak_freq_var, value=1, command=self.handle_radios)
        self.theoretical_peak_freq_radio.grid(row=1, column=0, pady=(2,4))
        self.calibration_peak_freq_radio = tk.Radiobutton(self.theoretical_or_calibration_peak_freq_frame, text='offset', variable=self.theoretical_or_calibration_peak_freq_var, value=0, command=self.handle_radios)
        self.calibration_peak_freq_radio.grid(row=1, column=1, pady=(2,4))

        #self.filename_label = tk.Label(self.theoretical_or_calibration_peak_freq_frame, text="Calibration File")
        #self.browse_files_button = tk.Button(self.theoretical_or_calibration_peak_freq_frame, text="Select Calibration File", command=lambda: select_calibration_file(self.filename_label))
        
        self.calibration_file_label = tk.Label(self.theoretical_or_calibration_peak_freq_frame, text="Copy/paste values\ndirectly into file in \n'offset_data' folder\n\nOR")
        self.calibration_vals_window_button = tk.Button(self.theoretical_or_calibration_peak_freq_frame, text="Enter Values Here", command=self.open_calibration_window)

    def open_calibration_window(self):
        self.parent.parent.open_calibration_window()

    def handle_radios(self):
        global input
        set_input_altered_flag(True)
        input.will_use_theoretical_vals = self.theoretical_or_calibration_peak_freq_var.get()
        if not input.will_use_theoretical_vals:
            self.calibration_file_label.grid(row=3, column=0, columnspan=2, pady=(2,4))
            self.calibration_vals_window_button.grid(row=4, column=0, columnspan=2, pady=(8,4))
        else:
            self.calibration_file_label.grid_forget()
            self.calibration_vals_window_button.grid_forget()

class absTimeInputFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        baseline_time_label = tk.Label(self, text="Enter absolute baseline time")
        baseline_time_label.grid(row=0, column=0, columnspan=6)
        self.hours_label_t0 = tk.Label(self, text="H0: ")
        self.hours_label_t0.grid(row=1, column=0)
        self.hours_entry_t0 = tk.Entry(self, width=5)
        self.hours_entry_t0.grid(row=1, column=1)
        self.minutes_label_t0 = tk.Label(self, text="M0: ")
        self.minutes_label_t0.grid(row=1, column=2)
        self.minutes_entry_t0 = tk.Entry(self, width=5)
        self.minutes_entry_t0.grid(row=1, column=3)
        self.seconds_label_t0 = tk.Label(self, text="S0: ")
        self.seconds_label_t0.grid(row=1, column=4)
        self.seconds_entry_t0 = tk.Entry(self, width=5)
        self.seconds_entry_t0.grid(row=1, column=5)

        self.hours_label_tf = tk.Label(self, text="Hf: ")
        self.hours_label_tf.grid(row=2, column=0)
        self.hours_entry_tf = tk.Entry(self, width=5)
        self.hours_entry_tf.grid(row=2, column=1)
        self.minutes_label_tf = tk.Label(self, text="Mf: ")
        self.minutes_label_tf.grid(row=2, column=2)
        self.minutes_entry_tf = tk.Entry(self, width=5)
        self.minutes_entry_tf.grid(row=2, column=3)
        self.seconds_label_tf = tk.Label(self, text="Sf: ")
        self.seconds_label_tf.grid(row=2, column=4)
        self.seconds_entry_tf = tk.Entry(self, width=5)
        self.seconds_entry_tf.grid(row=2, column=5)

    def get_abs_time(self):
        h0 = self.hours_entry_t0.get()
        m0 = self.minutes_entry_t0.get()
        s0 = self.seconds_entry_t0.get()
        hf = self.hours_entry_tf.get()
        mf = self.minutes_entry_tf.get()
        sf = self.seconds_entry_tf.get()

        try:
            return (time(int(h0),int(m0),int(s0)), time(int(hf),int(mf),int(sf)))
        except ValueError as exc:
            print(f"Please enter integer values for time: {exc}")

    def clear(self):
        self.hours_entry_t0.delete(0, tk.END)
        self.minutes_entry_t0.delete(0, tk.END)
        self.seconds_entry_t0.delete(0, tk.END)
        self.hours_entry_tf.delete(0, tk.END)
        self.minutes_entry_tf.delete(0, tk.END)
        self.seconds_entry_tf.delete(0, tk.END)

class relTimeInputFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        baseline_time_label = tk.Label(self, text="Enter relative baseline time")
        baseline_time_label.grid(row=0, column=0, columnspan=2)
        self.t0_label = tk.Label(self, text="t0 (s): ")
        self.t0_label.grid(row=1, column=0)
        self.t0_entry = tk.Entry(self, width=5)
        self.t0_entry.grid(row=1, column=1)
        self.tf_label = tk.Label(self, text="tf (s): ")
        self.tf_label.grid(row=2, column=0)
        self.tf_entry = tk.Entry(self, width=5)
        self.tf_entry.grid(row=2, column=1)

        self.t0_entry.insert(0, '2') # REMOVE FOR RELEASE
        self.tf_entry.insert(0, '120') # REMOVE FOR RELEASE

    def get_rel_time(self):
        try:
            t0 = self.t0_entry.get()
            tf = self.tf_entry.get()
        except Exception as exc:
            print(f"ERROR: please enter valid relative time input in seconds\n{exc}")
        return t0, tf

    def clear(self):
        self.t0_entry.delete(0, tk.END)
        self.tf_entry.delete(0, tk.END)

class CheckBox:
    def __init__(self, intvar, checkbutton, key):
        self.intvar = intvar
        self.checkbutton = checkbutton
        self.key = key 
    
class LabelledEntry:
    def __init__(self, label, entry):
        self.label = label
        self.entry = entry

class CalibrationWindow():
    def __init__(self, parent, container):
        super().__init__(container) # initialize parent class for the child
        self.parent = parent

    def open_calibration_window(self):
        calibration_window = tk.Toplevel(self)
        calibration_window.title('Input/Select Offset Data')
        self.calibration_frame = tk.Frame(calibration_window)
        self.calibration_frame.pack(anchor='n')

    def fill_calibration_window(self):
        self.calibration_label = tk.Label(self.calibration_frame, text="Offset Data", font=('TkDefaultFont', 12, 'bold'))
        self.calibration_label.grid(row=1, column=0, columnspan=2, padx=16, pady=12)
        instructions = "Input offset frequency values here\nthese values will be used for modeling purposes\n" +\
                        "\nfor Qsense, these values will be added\nto all data points for full frequency values\n" +\
                        "Supports exponential format. i.e. 2.5e-6 or 1.34e7"
        self.instruction_label = tk.Label(self.calibration_frame, text=instructions)
        self.instruction_label.grid(row=2, column=0, columnspan=2, padx=16, pady=12)

        self.labelled_entries = generate_labelled_entries(self.calibration_frame)
        print(self.labelled_entries)
        for i, labelled_entry in enumerate(self.labelled_entries):
            labelled_entry.label.grid(row=i+3, column=0)
            labelled_entry.entry.grid(row=i+3, column=1)

        self.clear_selections_button = tk.Button(self.calibration_frame, text="Clear All Selections", padx=6, pady=4, width=20, command=self.clear_selections)
        self.clear_selections_button.grid(row=30, column=0, columnspan=2, pady=12)  
        self.confirm_selections_button = tk.Button(self.calibration_frame, text="Confirm Selections", padx=6, pady=4, width=20, command=self.confirm_values)
        self.confirm_selections_button.grid(row=31, column=0, columnspan=2, pady=12)  

    def clear_selections(self):
        for le in self.labelled_entries:
            le.entry.delete(0,tk.END)
        print("CLEARED")
        
    def confirm_values(self):
        calibration_vals = []
        warned_flag = False
        for le in self.labelled_entries:
            try:
                calibration_vals.append(float(le.entry.get()))
            except ValueError as ve:
                if not warned_flag:
                    print("WARNING: AT LEAST ONE ENTRY EXISTS WITH A MISSING OR INVALID INPUT\nWILL CONVERT THESE ENTRIES TO 0")
                    warned_flag = True
                calibration_vals.append(0.0)
            
        calibration_df = pd.read_csv("offset_data/COPY-PASTE_OFFSET_VALUES_HERE.csv")
        calibration_df.loc[0] = calibration_vals
        calibration_df.to_csv("offset_data/COPY-PASTE_OFFSET_VALUES_HERE.csv")
        print(f"Offset values written succesfully\n: {calibration_df.head()}")

class Col1(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.col_position = 0
        self.is_visible = True
        self.parent = parent
        file_name_label = tk.Label(self, text="Enter data file information", font=('TkDefaultFont', 12, 'bold'))
        file_name_label.grid(row=0, column=0, pady=(14,16), padx=(6,0))

        self.filename_label = tk.Label(self, text="Data File")
        self.filename_label.grid(row=2, column=0, pady=(8,4))
        self.browse_files_button = tk.Button(self, text="Select Data File", command=lambda: select_data_file(self.filename_label))
        self.browse_files_button.grid(row=1, column=0)

        self.file_src_frame = srcFileFrame(self)
        self.file_src_frame.grid(row=4, column=0, pady=(16,8))
        self.rel_time_input = relTimeInputFrame(self)
        self.abs_time_input = absTimeInputFrame(self)
        self.abs_time_input.grid(row=6, column=0)

        self.calibration_vals_frame = calibrationValsFrame(self)
        self.calibration_vals_frame.grid(row=7, column=0)

        self.cleared_label = tk.Label(self, text="Cleared!")
        self.submitted_label = tk.Label(self, text="Submitted!")
        self.err_label = tk.Label(self, text="Error occured,\nplease see terminal for details", font=("Arial",14))

        self.file_data_submit_button = tk.Button(self, text="Submit file information", padx=8, pady=6, width=20, command=self.col_names_submit)
        self.file_data_submit_button.grid(row=10, column=0, pady=(16,4))
        self.file_data_clear_button = tk.Button(self, text="Clear Entries", padx=8, pady=6, width=20, command=self.clear_file_data)
        self.file_data_clear_button.grid(row=11, column=0, pady=4)

        self.open_plot_opts_button = tk.Button(self, text="Customize Plot Options", width=20, command=self.open_plot_opts)
        self.open_plot_opts_button.grid(row=14, pady=(16, 4)) 

    def open_plot_opts(self):
        self.parent.open_plot_opts_window()

    def blit_time_input_frame(self, is_relative_time):
        if is_relative_time:
            self.abs_time_input.grid_forget()
            self.rel_time_input.grid(row=6, column=0)
        else:
            self.rel_time_input.grid_forget()
            self.abs_time_input.grid(row=6, column=0)

    def col_names_submit(self):
        global input
        input.first_run = True
        set_input_altered_flag(True)
        input.file_src_type = self.file_src_frame.file_src_type
        if input.is_relative_time:
            input.rel_t0, input.rel_tf = self.rel_time_input.get_rel_time()
        else:
            input.abs_base_t0, input.abs_base_tf = self.abs_time_input.get_abs_time()

        if input.first_run:
            print(f"formatting {input.file} to BraTaDio convention...")
            format_raw_data(input.file_src_type, input.file, input.will_use_theoretical_vals)
            print("Format completed")
        
        self.submitted_label.grid(row=13, column=0)
        self.submitted_label.after(5000, lambda: self.submitted_label.grid_forget())

    def clear_file_data(self):
        global input
        input.abs_base_t0 = time(0, 0, 0)
        input.abs_base_tf = time(0, 0, 0)
        self.cleared_label.grid(row=12, column=0)
        self.filename_label.configure(text="Data File")
        self.abs_time_input.clear()
        self.rel_time_input.clear()
        self.submitted_label.grid_forget()

class Col2(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.col_position = 1
        self.is_visible = True
        self.plot_raw_data_var = tk.IntVar()
        self.plot_raw_data_check = tk.Checkbutton(self, text="Plot raw data\n(f and d)", font=('TkDefaultFont', 12, 'bold'), variable=self.plot_raw_data_var, onvalue=1, offvalue=2, command=self.receive_raw_checkboxes)
        self.plot_raw_data_check.grid(row=0, column=0, pady=(12,8), padx=(16,32))
        self.which_raw_channels_label = tk.Label(self, text="Select overtones for full data")

        # checkboxes for selecting which channels to plot for raw data
        self.raw_checks = create_checkboxes(self, 'raw')

        self.clear_raw_checks_button = tk.Button(self, text='clear all', width=8, command=self.clear_raw_checks)
        self.select_all_raw_checks_button = tk.Button(self, text='select all', width=8, command=self.select_all_raw_checks)

    def receive_raw_checkboxes(self):
        global input
        set_input_altered_flag(True)
        if self.plot_raw_data_var.get() == 1:
            input.will_plot_raw_data = True
            self.which_raw_channels_label.grid(row=1, column=0, pady=(0,26))
            self.select_all_raw_checks_button.grid(row=19, column=0, padx=(0,0), pady=(12,4))
            self.clear_raw_checks_button.grid(row=20, column=0, padx=(0,0), pady=(4,4))
            #self.calibration_data_button.grid(row=21, column=0, padx=(0,0), pady=(4,4))
            
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

class InteractivePlotOptions(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # options for the int plot
        self.interactive_plot_overtone_label = tk.Label(self, text="Select overtone to visualize:")
        self.interactive_plot_overtone_label.grid(row=0, column=0, pady=12)
        self.interactive_plot_overtone_select = tk.Entry(self, width=10)
        self.interactive_plot_overtone_select.grid(row=1, column=0)

        # define and place entry for range options
        self.which_range_label = tk.Label(self, text="Enter which range being selected\n(use identifier of your choosing\ni.e. numbers or choice of label)" )
        self.which_range_label.grid(row=2, column=0, pady=(2,4), padx=4)
        self.which_range_entry = tk.Entry(self, width=10)
        self.which_range_entry.grid(row=3, column=0, pady=(2,4))

        # button to submit range selected
        self.which_range_submit = tk.Button(self, text='Confirm Range', padx=10, pady=4, command=self.confirm_range)
        self.which_range_submit.grid(row=4, column=0, pady=4)
        input.range_frame_flag = True

    def confirm_range(self):
        global input
        input.which_range_selecting = self.which_range_entry.get()
        print(f"confirmed range: {input.which_range_selecting}")


class Col3(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.col_position = 2
        self.is_visible = True
        self.container = container
        self.plot_clean_data_var = tk.IntVar()
        self.plot_clean_data_check = tk.Checkbutton(self, text="Plot shifted data\n(Δf and Δd)", font=('TkDefaultFont', 12, 'bold'), variable=self.plot_clean_data_var, onvalue=1, offvalue=0, command=self.receive_clean_checkboxes)
        self.plot_clean_data_check.grid(row=0, column=0, pady=(12,8), padx=(32,16))
        self.which_clean_channels_label = tk.Label(self, text="Select overtones for\nbaseline corrected data")

        # checkboxes for selecting which channels to plot for clean data
        self.clean_checks = create_checkboxes(self, 'clean')

        self.clean_int_plot_var = tk.IntVar()
        self.clean_int_plot_frame = InteractivePlotOptions(self)
        self.clean_int_plot_check = tk.Checkbutton(self, text="Interactive plot", variable=self.clean_int_plot_var, onvalue=1, offvalue=0, command=self.clean_int_plot)

        self.clear_clean_checks_button = tk.Button(self, text='clear all', width=8, command=self.clear_clean_checks)
        self.select_all_clean_checks_button = tk.Button(self, text='select all', width=8, command=self.select_all_clean_checks)


    def receive_clean_checkboxes(self):
        global input
        set_input_altered_flag(True)
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
            self.clean_int_plot_check.grid(row=18, column=0, pady=12)

        else:
            input.will_plot_clean_data = False
            self.which_clean_channels_label.grid_forget()
            
            for cb in self.clean_checks:
                cb.checkbutton.grid_forget()

            self.select_all_clean_checks_button.grid_forget()
            self.clear_clean_checks_button.grid_forget()
            self.clean_int_plot_check.grid_forget()

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


    def clean_int_plot(self):
        global input
        print(self.clean_int_plot_var.get(), input.will_interactive_plot)
        if self.clean_int_plot_var.get() == 1:
            input.will_interactive_plot = True
            print(self.clean_int_plot_var.get(), input.will_interactive_plot)
            input.range_frame_flag = True
            self.parent.repack_frames()
            self.clean_int_plot_frame.grid(row=18, column=0)
        else:
            input.will_interactive_plot = False
            input.range_frame_flag = False
            self.parent.repack_frames()
            self.clean_int_plot_frame.grid_forget()
        print(self.clean_int_plot_var.get(), input.will_interactive_plot)


class Col4(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)

        self.col_position = 3
        self.model_window_open_flag = False
        self.is_visible = True
        self.parent = parent
        self.container = container
        self.first_run = True
        self.plot_options_label = tk.Label(self, text="Options for plots", font=('TkDefaultFont', 12, 'bold'))
        self.plot_options_label.grid(row=0, column=4, pady=(14,16), padx=(0,6))

        # miscellaneous plot options
        self.plot_dF_dD_together_var = tk.IntVar()
        self.plot_dF_dD_together_check = tk.Checkbutton(self, text="Plot Δf and Δd together", variable=self.plot_dF_dD_together_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.plot_dF_dD_together_check.grid(row=2, column=4)
        self.normalize_F_var = tk.IntVar()
        self.normalize_F_check = tk.Checkbutton(self, text="Normalize Δf with its\nrespective overtone", variable=self.normalize_F_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.normalize_F_check.grid(row=3, column=4)
        self.plot_dD_v_dF_var = tk.IntVar()
        self.plot_dD_v_dF_check = tk.Checkbutton(self, text="Plot Δd vs Δf", variable=self.plot_dD_v_dF_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.plot_dD_v_dF_check.grid(row=4, column=4)
        self.plot_temp_v_time_var = tk.IntVar()
        self.plot_temp_v_time_check = tk.Checkbutton(self, text="Plot temperature vs time", variable=self.plot_temp_v_time_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.plot_temp_v_time_check.grid(row=5, column=4)
        self.correct_slope_var = tk.IntVar()
        self.correct_slope_check = tk.Checkbutton(self, text="Slope Correction", variable=self.correct_slope_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.correct_slope_check.grid(row=6, column=4)

        self.open_model_window_button = tk.Button(self, text="Modeling", padx=8, pady=6, command=self.model_window_button)
        self.open_model_window_button.grid(row=10, column=4, pady=8)

        self.submit_button = tk.Button(self, text="Submit", padx=8, pady=6, width=20, command=self.submit)
        self.submit_button.grid(row=20, column=4, pady=4, padx=20)

        self.clear_range_data_button = tk.Button(self, text="Clear Saved Range Data", padx=8, pady=6, width=20, command=self.clear_range_data)
        self.clear_range_data_button.grid(row=21, column=4, pady=4)

        self.exit_button = tk.Button(self, text="Exit", padx=8, pady=6, width=20, command=exit)
        self.exit_button.grid(row=22, column=4, pady=4)

    def receive_optional_checkboxes(self):
        global input
        set_input_altered_flag(True)
        input.will_plot_dF_dD_together = True if self.plot_dF_dD_together_var.get() == 1 else False
        input.will_normalize_F = True if self.normalize_F_var.get() == 1 else False
        input.will_plot_dD_v_dF = True if self.plot_dD_v_dF_var.get() == 1 else False
        input.will_plot_temp_v_time = True if self.plot_temp_v_time_var.get() == 1 else False
        input.will_correct_slope = True if self.correct_slope_var.get() == 1 else False

    # when interactive plot window opens, grabs number of range from text field
    def confirm_range(self):
        global input
        input.which_range_selecting = self.which_range_entry.get()

        print(f"Confirmed range: {input.which_range_selecting}")

    def model_window_button(self):
        try:
            self.parent.test_model_window()
        except:
            self.parent.open_model_window()

    def submit(self):
        global input
        err_check()
        
        if input.will_interactive_plot:
            input.interactive_plot_overtones['clean'] = int(self.parent.frames[Col3].clean_int_plot_frame.interactive_plot_overtone_select.get())

        global INPUT_ALTERED_FLAG
        if INPUT_ALTERED_FLAG:
            analyze_data(input)
        else:
            print("No modifications made from previous iteration, no processing will be done")
        set_input_altered_flag(False, False)
        input.first_run = False

    def clear_range_data(self):
        set_input_altered_flag(True)
        rf_stats = open("selected_ranges/all_stats_rf.csv", 'w')
        dis_stats = open("selected_ranges/all_stats_dis.csv", 'w')
        sauerbray_stats = open("selected_ranges/Sauerbrey_stats.csv", 'w')
        sauerbrey_ranges = open("selected_ranges/Sauerbrey_ranges.csv", 'w')
        files = [rf_stats, dis_stats, sauerbray_stats, sauerbrey_ranges]
        for file in files:
            file.write('')


class ModelingWindow():
    def __init__(self, parent, container):
        super().__init__(container)
        self.is_visible = input.range_frame_flag
        self.parent = parent

    def open_modeling_window(self):
        self.model_window = tk.Toplevel(self)
        self.model_window.title('Modeling Options')
        self.models_frame = tk.Frame(self.model_window)
        self.models_frame.pack(side='left', anchor='n')

    def fill_modeling_window(self):
        # first column contains most plot customizations
        self.customize_label = tk.Label(self.models_frame, text="Modeling Options", font=('TkDefaultFont', 12, 'bold'))
        self.customize_label.grid(row=0, column=0, columnspan=3, padx=16, pady=12)
        self.range_label = tk.Label(self.models_frame, text="NOTE: Visit this section AFTER Submitting")
        self.range_label.grid(row=1, column=0, padx=10, pady=(0,8))

        # run linear regression button
        self.run_tf_liquid_analysis_button = tk.Button(self.models_frame, text="Run Analysis of\nThin Film in Liquid", padx=6, pady=4, width=20,
                                             command=lambda: thin_film_liquid_analysis((input.which_plot['clean'], input.will_use_theoretical_vals, input.latex_installed, input.fig_format)))
        self.run_tf_liquid_analysis_button.grid(row=10, column=0, pady=4)

        # run sauerbrey button
        self.run_sauerbrey_analysis_button = tk.Button(self.models_frame, text="Run Sauerbrey Mass Analysis", padx=6, pady=4, width=20,
                                             command=lambda: sauerbrey((input.will_use_theoretical_vals, input.calibration_data_from_file, input.fig_format)))
        self.run_sauerbrey_analysis_button.grid(row=9, column=0, pady=4)

        # avg change in freq and dis against overtone button
        self.avgs_analysis = tk.Button(self.models_frame, text="Plot Average Δf and Δd\n of Overtones", padx=6, pady=4, width=20,
                                             command=lambda: avgs_analysis(input.fig_format))
        self.avgs_analysis.grid(row=8, column=0, pady=4)

        # avg change in freq against overtone button
        self.run_tf_air_analysis_button = tk.Button(self.models_frame, text="Run Analysis of\nThin Film in Air", padx=6, pady=4, width=20,
                                             command=lambda: thin_film_air_analysis((input.which_plot['clean'], input.will_use_theoretical_vals, input.latex_installed, input.fig_format)))
        self.run_tf_air_analysis_button.grid(row=11, column=0, pady=4)

        # Gordon-Kanazawa model
        self.run_GK_button = tk.Button(self.models_frame, text="Run Gordon-Kanazawa Model", padx=6, pady=4, width=20,
                                             command=lambda: gordon_kanazawa((input.which_plot['clean'], input.will_use_theoretical_vals, input.fig_format)))
        self.run_GK_button.grid(row=12, column=0, pady=4)


    def test_modeling_window(self):
        self.model_window.deiconify()


class PlotOptsWindow():
    def __init__(self, parent, container):
        super().__init__(container) # initialize parent class for the child
        self.parent = parent

    def open_opts_window(self):
        opts_window = tk.Toplevel(self)
        opts_window.title('Customize Plots')
        self.opts_frame = tk.Frame(opts_window)
        self.opts_frame.pack(side='left', anchor='n')
        '''self.opts_col2 = tk.Frame(opts_window)
        self.opts_col2.pack(side='right', anchor='n')
        self.opts_confirm = tk.Frame(opts_window)
        self.opts_confirm.pack(side='bottom', anchor='e')'''

    def fill_opts_window(self):
        self.widgets = {}
        print(self.prev_opts)

        # first column contains most plot customizations
        self.customize_label = tk.Label(self.opts_frame, text="Plot Customization Options", font=('TkDefaultFont', 12, 'bold'))
        self.customize_label.grid(row=1, column=0, columnspan=6, padx=16, pady=12)

        self.font_choice_label = tk.Label(self.opts_frame, text="Enter font selection:")
        self.font_choice_label.grid(row=3, column=0, columnspan=3, pady=(20,4))
        self.font_choice_entry = tk.Entry(self.opts_frame, width=10)
        self.font_choice_entry.grid(row=3, column=3, columnspan=3, pady=(20,4))
        self.widgets['font'] = self.font_choice_entry

        self.label_text_size_label = tk.Label(self.opts_frame, text="Enter Label font size:")
        self.label_text_size_label.grid(row=4, column=0, columnspan=3, pady=(16,0))
        self.label_text_size_entry = tk.Entry(self.opts_frame, width=10)
        self.label_text_size_entry.grid(row=4, column=3, columnspan=3, pady=(16,0))
        self.widgets['label_text_size'] = self.label_text_size_entry

        self.title_text_size_label = tk.Label(self.opts_frame, text="Enter Title font size:")
        self.title_text_size_label.grid(row=5, column=0, columnspan=3, pady=(16,0))
        self.title_text_size_entry = tk.Entry(self.opts_frame, width=10)
        self.title_text_size_entry.grid(row=5, column=3, columnspan=3, pady=(16,0))
        self.widgets['title_text_size'] = self.title_text_size_entry

        self.value_text_size_label = tk.Label(self.opts_frame, text="Enter Value font size:")
        self.value_text_size_label.grid(row=6, column=0, columnspan=3, pady=(16,0))
        self.value_text_size_entry = tk.Entry(self.opts_frame, width=10)
        self.value_text_size_entry.grid(row=6, column=3, columnspan=3, pady=(16,0))
        self.widgets['value_text_size'] = self.value_text_size_entry

        self.legend_text_size_label = tk.Label(self.opts_frame, text="Enter Legend font size:")
        self.legend_text_size_label.grid(row=7, column=0, columnspan=3, pady=(16,0))
        self.legend_text_size_entry = tk.Entry(self.opts_frame, width=10)
        self.legend_text_size_entry.grid(row=7, column=3, columnspan=3, pady=(16,0))
        self.widgets['legend_text_size'] = self.legend_text_size_entry

        self.tick_direction_label = tk.Label(self.opts_frame, text="Choose tick direction:")
        self.tick_direction_label.grid(row=9, column=0, columnspan=6, pady=0)
        self.tick_direction_var = tk.IntVar()
        self.tick_direction_var.set(-1)
        self.tick_direction_in_radio = tk.Radiobutton(self.opts_frame, text="in", variable=self.tick_direction_var, value=0)
        self.tick_direction_in_radio.grid(row=10, column=0, columnspan=2)
        self.tick_direction_out_radio = tk.Radiobutton(self.opts_frame, text="out", variable=self.tick_direction_var, value=1)
        self.tick_direction_out_radio.grid(row=10, column=2, columnspan=2)
        self.tick_direction_inout_radio = tk.Radiobutton(self.opts_frame, text="both", variable=self.tick_direction_var, value=2)
        self.tick_direction_inout_radio.grid(row=10, column=4, columnspan=2)
        self.widgets['tick_dir'] = self.tick_direction_var

        # Options for changing the scale of x axis time
        self.scale_time_var = tk.IntVar()
        self.which_range_var = tk.IntVar()
        self.scale_time_check = tk.Checkbutton(self.opts_frame, text="Change scale of time? (default (s))", variable=self.scale_time_var, onvalue=1, offvalue=0, command=self.receive_scale_radios)
        self.scale_time_check.grid(row=12, column=0, columnspan=6, pady=(32,0))
        
        # default to seconds
        self.time_scale_frame = tk.Frame(self.opts_frame)
        self.which_time_scale_var = tk.IntVar()
        self.seconds_scale_check = tk.Radiobutton(self.time_scale_frame, text="Seconds", variable=self.which_time_scale_var, value=1, command=self.receive_scale_radios)
        self.seconds_scale_check.grid(row=0, column=0, columnspan=2)
        self.minutes_scale_check = tk.Radiobutton(self.time_scale_frame, text="Minutes", variable=self.which_time_scale_var, value=2, command=self.receive_scale_radios)
        self.minutes_scale_check.grid(row=0, column=2, columnspan=2)
        self.hours_scale_check = tk.Radiobutton(self.time_scale_frame, text="Hours", variable=self.which_time_scale_var, value=3, command=self.receive_scale_radios)
        self.hours_scale_check.grid(row=0, column=4, columnspan=2)
        self.widgets['time_scale'] = self.which_time_scale_var

        # Options for changing file format of saved scatter plot figures
        self.change_fig_format_var = tk.IntVar()
        self.change_fig_format_check = tk.Checkbutton(self.opts_frame, text="Change figure file format? (default .png)", variable=self.change_fig_format_var, onvalue=1, offvalue=0, command=self.receive_file_format_radios)
        self.change_fig_format_check.grid(row=16, column=0, columnspan=6, pady=(8,0))
        # default png
        self.file_format_frame = tk.Frame(self.opts_frame)
        self.which_file_format_var = tk.IntVar()
        self.png_check = tk.Radiobutton(self.file_format_frame, text=".png", variable=self.which_file_format_var, value=1, command=self.receive_file_format_radios)
        self.png_check.grid(row=0, column=0, columnspan=2)
        self.tiff_check = tk.Radiobutton(self.file_format_frame, text=".tiff", variable=self.which_file_format_var, value=2, command=self.receive_file_format_radios)
        self.tiff_check.grid(row=0, column=2, columnspan=2)
        self.pdf_check = tk.Radiobutton(self.file_format_frame, text=".pdf", variable=self.which_file_format_var, value=3, command=self.receive_file_format_radios)
        self.pdf_check.grid(row=0, column=4, columnspan=2)
        self.widgets['fig_format'] = self.which_file_format_var

        # option to index how many points user would like to plot (i.e. every 5th point)
        self.points_plotted_index_label = tk.Label(self.opts_frame, text="Points to plot index:\ni.e. plot every 5th point")
        self.points_plotted_index_label.grid(row=20, column=0, columnspan=3, pady=8)
        self.points_plotted_index_entry = tk.Entry(self.opts_frame, width=10)
        self.points_plotted_index_entry.grid(row=20, column=3, columnspan=3, pady=8)
        self.widgets['points_plotted_index'] = self.points_plotted_index_entry

        # option to set bounds of time, frequency, and dissipation
        self.bounds_frame = tk.Frame(self.opts_frame)
        bounds_label_text = "Enter bounds for data to be plotted\nenter 'auto' to use the default for that bound\n\n" \
        + "Note: units of time rely on units specified above,\n" \
        + "frequency bounds are in terms of Δf (Hz), not f,\n" \
        + "and dissipation bounds are in terms of (your number) E-6"
        self.bounds_label = tk.Label(self.bounds_frame, text=bounds_label_text)
        self.bounds_label.grid(row=0, column=0, columnspan=4, pady=8)
        self.time_lower_bound_label = tk.Label(self.bounds_frame, text="Time Lower: ")
        self.time_lower_bound_label.grid(row=1, column=0, padx=4, pady=4)
        self.time_lower_bound_entry = tk.Entry(self.bounds_frame, width=10)
        self.time_lower_bound_entry.grid(row=1, column=1, padx=4, pady=4)
        self.time_upper_bound_label = tk.Label(self.bounds_frame, text="Time Upper: ")
        self.time_upper_bound_label.grid(row=1, column=2, padx=4, pady=4)
        self.time_upper_bound_entry = tk.Entry(self.bounds_frame, width=10)
        self.time_upper_bound_entry.grid(row=1, column=3, padx=4, pady=4)
        self.widgets['time_lower_bound'] = self.time_lower_bound_entry
        self.widgets['time_upper_bound'] = self.time_upper_bound_entry

        self.frequency_lower_bound_label = tk.Label(self.bounds_frame, text="Frequency Lower: ")
        self.frequency_lower_bound_label.grid(row=2, column=0, padx=4, pady=4)
        self.frequency_lower_bound_entry = tk.Entry(self.bounds_frame, width=10)
        self.frequency_lower_bound_entry.grid(row=2, column=1, padx=4, pady=4)
        self.frequency_upper_bound_label = tk.Label(self.bounds_frame, text="Frequency Upper: ")
        self.frequency_upper_bound_label.grid(row=2, column=2, padx=4, pady=4)
        self.frequency_upper_bound_entry = tk.Entry(self.bounds_frame, width=10)
        self.frequency_upper_bound_entry.grid(row=2, column=3, padx=4, pady=4)
        self.widgets['frequency_lower_bound'] = self.frequency_lower_bound_entry
        self.widgets['frequency_upper_bound'] = self.frequency_upper_bound_entry

        self.dissipation_lower_bound_label = tk.Label(self.bounds_frame, text="Dissipation Lower: ")
        self.dissipation_lower_bound_label.grid(row=3, column=0, padx=4, pady=4)
        self.dissipation_lower_bound_entry = tk.Entry(self.bounds_frame, width=10)
        self.dissipation_lower_bound_entry.grid(row=3, column=1, padx=4, pady=4)
        self.dissipation_upper_bound_label = tk.Label(self.bounds_frame, text="Dissipation Upper: ")
        self.dissipation_upper_bound_label.grid(row=3, column=2, padx=4, pady=4)
        self.dissipation_upper_bound_entry = tk.Entry(self.bounds_frame, width=10)
        self.dissipation_upper_bound_entry.grid(row=3, column=3, padx=4, pady=4)
        self.widgets['dissipation_lower_bound'] = self.dissipation_lower_bound_entry
        self.widgets['dissipation_upper_bound'] = self.dissipation_upper_bound_entry
        
        self.bounds_frame.grid(row=21, column=0, columnspan=6, pady=(12,0))

        # second column color customizer
        self.ov_color_label = tk.Label(self.opts_frame, text="Customize Overtone Plot Colors", font=('TkDefaultFont', 12, 'bold'))
        self.ov_color_label.grid(row=1, column=6, padx=16, pady=12)
        
        self.ov1_color_button = tk.Button(self.opts_frame, text="1st overtone", width=10, command=lambda: self.choose_color(1))
        self.ov1_color_button.grid(row=3, column=6, pady=(16,4))
        self.ov3_color_button = tk.Button(self.opts_frame, text="3rd overtone", width=10, command=lambda: self.choose_color(3))
        self.ov3_color_button.grid(row=4, column=6, pady=4)
        self.ov5_color_button = tk.Button(self.opts_frame, text="5th overtone", width=10, command=lambda: self.choose_color(5))
        self.ov5_color_button.grid(row=5, column=6, pady=4)
        self.ov7_color_button = tk.Button(self.opts_frame, text="7th overtone", width=10, command=lambda: self.choose_color(7))
        self.ov7_color_button.grid(row=6, column=6, pady=4)
        self.ov9_color_button = tk.Button(self.opts_frame, text="9th overtone", width=10, command=lambda: self.choose_color(9))
        self.ov9_color_button.grid(row=7, column=6, pady=4)
        self.ov11_color_button = tk.Button(self.opts_frame, text="11th overtone", width=10, command=lambda: self.choose_color(11))
        self.ov11_color_button.grid(row=8, column=6, pady=4)
        self.ov13_color_button = tk.Button(self.opts_frame, text="13th overtone", width=10, command=lambda: self.choose_color(13))
        self.ov13_color_button.grid(row=9, column=6, pady=4)

        self.empty_entries_notif_label = tk.Label(self.opts_frame, text="WARNING: Empty entries to default to\npreviously entered options", font=('TkDefaultFont', 10, 'bold'))
        self.options_saved_label = tk.Label(self.opts_frame, text="Confirming selections\nsaves preferences\neven when software\nis closed")
        self.options_saved_label.grid(row=28, column=6, pady=(24,4))
        self.default_button = tk.Button(self.opts_frame, text="Default Values", width=14, command=self.set_default_values)
        self.default_button.grid(row=29, column=6, pady=4)
        self.confirm_button = tk.Button(self.opts_frame, text="Confirm Selections", width=14, command=self.confirm_opts)
        self.confirm_button.grid(row=30, column=6, pady=(4,16))

    def choose_color(self, ov_num):
        self.color_code = colorchooser.askcolor(title="Choose color for overtone", parent=self)
        self.options['colors'][f'ov{ov_num}'] = self.color_code[1]

    def set_text(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)
        
    def receive_scale_radios(self):
        global input
        set_input_altered_flag(True)
        if self.scale_time_var.get() == 1:
            self.time_scale_frame.grid(row=13, column=0, columnspan=6)
            if self.which_time_scale_var.get() == 1:
                input.x_timescale = 's'
            elif self.which_time_scale_var.get() == 2:
                input.x_timescale = 'min'
            elif self.which_time_scale_var.get() == 3:
                input.x_timescale = 'hr'
            else:
                input.x_timescale= 'u'
        else:
            self.time_scale_frame.grid_forget()
            input.x_timescale = 's'

    def receive_file_format_radios(self):
        global input
        set_input_altered_flag(True)
        if self.change_fig_format_var.get() == 1:
            self.file_format_frame.grid(row=17, column=0, columnspan=6)
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
    
    def set_default_values(self):
        with open('plot_opts/default_opts.json', 'r') as fp:
            default_opts = json.load(fp)

        for key in list(default_opts.keys())[1:]:
            if isinstance(self.widgets[key], tk.Entry):
                self.set_text(self.widgets[key], default_opts[key])

        self.tick_direction_var.set(1)
        self.time_scale_frame.grid(row=13, column=0, columnspan=6)
        if self.change_fig_format_var.get() == 0:
            self.change_fig_format_var.set(1)
        self.which_file_format_var.set(1)
        self.file_format_frame.grid(row=17, column=0, columnspan=6)
        if self.scale_time_var.get() == 0:
            self.scale_time_var.set(1)
        self.which_time_scale_var.set(1)
        
        self.options = default_opts

    def confirm_opts(self):
        set_input_altered_flag(True)
        print(self.prev_opts)
        
        # put widget values into dict
        warned_flag = False
        for key in list(self.options.keys())[1:]:
            if isinstance(self.widgets[key], tk.Entry):
                entry = self.widgets[key].get()
                if entry == '':
                    if not warned_flag:
                        self.empty_entries_notif_label.grid(row=31, column=6, pady=6)
                        warned_flag = True
                    self.options[key] = self.prev_opts[key]
                else:
                    try:
                        entry = int(entry)
                        self.options[key] = entry
                    except ValueError:
                        self.options[key] = entry

            elif isinstance(self.widgets[key], tk.IntVar):
                if key == 'time_scale':
                    if self.widgets[key].get() == 1:
                        self.options['time_scale'] = 's'
                    if self.widgets[key].get() == 2:
                        self.options['time_scale'] = 'min'
                    if self.widgets[key].get() == 3:
                        self.options['time_scale'] = 'hr'
                
                elif key == 'fig_format':
                    if self.widgets[key].get() == 1:
                        self.options['fig_format'] = 'png'
                    if self.widgets[key].get() == 2:
                        self.options['fig_format'] = 'tiff'
                    if self.widgets[key].get() == 3:
                        self.options['fig_format'] = 'pdf'

                elif key == 'tick_dir':
                    if self.widgets[key].get() == 0:
                        self.options['tick_dir'] = 'in'
                    if self.widgets[key].get() == 1:
                        self.options['tick_dir'] = 'out'
                    if self.widgets[key].get() == 2:
                        self.options['tick_dir'] = 'inout'

        if warned_flag:
            self.empty_entries_notif_label.after(5000, lambda: self.empty_entries_notif_label.grid_forget())
            warned_flag = False


            
        '''
        if self.which_time_scale_var.get() == 1:
            self.options['time_scale'] = 's'
        if self.which_time_scale_var.get() == 2:
            self.options['time_scale'] = 'min'
        if self.which_time_scale_var.get() == 3:
            self.options['time_scale'] = 'hr'

        if self.which_file_format_var.get() == 1:
            self.options['fig_format'] = 'png'
        if self.which_file_format_var.get() == 2:
            self.options['fig_format'] = 'tiff'
        if self.which_file_format_var.get() == 3:
            self.options['fig_format'] = 'pdf'

        if self.tick_direction_var.get() == 0:
            self.options['tick_dir'] = 'in'
        elif self.tick_direction_var.get() == 1:
            self.options['tick_dir'] = 'out'
        else:
            self.options['tick_dir'] = 'inout'

        self.options['points_plotted_index'] = int(self.points_plotted_index_entry.get())
        '''
        
        '''warned_flag = False
        for key in self.options.keys():
            if self.options[key] == '':
                self.options[key] = prev_opts[key]
                if not warned_flag:
                    self.empty_entries_notif_label.grid(row=31, column=6, pady=6)
                    warned_flag = True
                raise Exceptions.MissingPlotCustomizationException(key, "Please Specify Missing field. ")
        self.empty_entries_notif_label.after(5000, lambda: self.empty_entries_notif_label.grid_forget())
        warned_flag = False'''
        with open('plot_opts/plot_customizations.json', 'w') as fp:
            json.dump(self.options, fp)


menu = App()
menu.mainloop()