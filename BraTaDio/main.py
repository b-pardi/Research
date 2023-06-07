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

import Exceptions
from analyze import analyze_data, ordinal, select_calibration_data
from format_file import format_raw_data
from modeling import thin_film_liquid_analysis, thin_film_air_analysis, sauerbrey, avgs_analysis

'''
WIP
func/class for range select window (maybe just in col 4)
remove as many selfs as possible from classes (specifically col 1 and 4)
'''

'''Variable Initializations'''
class Input:
    def __init__(self): 
        self.file = 'qcmi_sample.txt'
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
        self.clean_interactive_plot_overtone = 0 # which overtone will be analyzed in the interactive plot
        self.range_frame_flag = False
        self.first_run = True
        self.latex_installed = False
        self.will_use_theoretical_vals = True
        self.calibration_data_from_file = False
        self.will_plot_temp_v_time = False
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
    
def browse_files(label):
    global input
    fp = filedialog.askopenfilename(initialdir=os.path.join(os.getcwd(), 'raw_data'),
                                          title="Select Data File",
                                          filetypes=(("Comma Separated Value files", "*.csv"),
                                                    ("Excel file 2007 and later", "*.xlsx"),
                                                    ("Excel file 1997-2003", "*.xls"),
                                                    ("Text file", "*.txt")))
    
    input.file = fp
    label.configure(text=f"File Selected: {os.path.basename(fp)}")

    return fp

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

    def open_calibration_data_window(self):
        self.calibration_window.open_calibration_window(self)
        self.calibration_window.fill_calibration_window(self)

    def run_calibration(self):
        self.calibration_window.run_calibration_input(self)

    def clear_ranges(self):
        self.calibration_window.clear_selections(self)

    def open_model_window(self):
        self.modeling_window.open_modeling_window(self)
        self.modeling_window.fill_modeling_window(self)

    def destroy_model_window(self):
        self.modeling_window.destroy_modeling_window(self)

    def choose_color(self, ov_num):
        self.plot_opts_window.choose_color(self, ov_num)

    def set_default_values(self):
        self.plot_opts_window.set_default_values(self)

    def confirm_opts(self):
        self.plot_opts_window.confirm_opts(self)

    def set_text(self, entry, text):
        self.plot_opts_window.set_text(self, entry, text)

    def confirm_range(self):
        self.modeling_window.confirm_range(self)

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
        self.browse_files_button = tk.Button(self, text="Select Data File", command=lambda: browse_files(self.filename_label))
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
        
        input.file_src_type = self.file_src_frame.file_src_type
        if input.is_relative_time:
            input.rel_t0, input.rel_tf = self.rel_time_input.get_rel_time()
        else:
            input.abs_base_t0, input.abs_base_tf = self.abs_time_input.get_abs_time()


        input.file = "raw_data/qcmi_sample.txt" # REMOVE FOR RELEASE
        if input.first_run:
            format_raw_data(input.file_src_type, input.file)
        
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

    def handle_radios(self):
        self.file_src_type = self.file_src_types[self.file_src_var.get()]
        if self.file_src_type == 'QCM-d':
            input.is_relative_time = False
        elif self.file_src_type == 'QCM-i' or self.file_src_type == 'Qsense':
            input.is_relative_time = True
        self.container.blit_time_input_frame(input.is_relative_time)

class calibrationValsFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        # prompt to use theoretical or calibration values for peak frequency
        self.theoretical_or_calibration_peak_freq_frame = tk.Frame(self)
        self.theoretical_or_calibration_peak_freq_frame.grid(row=7, column=0, columnspan=1, pady=(16,0))
        self.theoretical_or_calibration_peak_freq_var = tk.IntVar()
        self.theoretical_or_calibration_peak_freq_var.set(-1)
        self.theoretical_or_calibration_peak_freq_label = tk.Label(self.theoretical_or_calibration_peak_freq_frame,
                                                text="Use theoretical or calibration\npeak frequency values for calculations\n(note: values defined in 'calibration_data' folder")
        self.theoretical_or_calibration_peak_freq_label.grid(row=0, column=0, pady=(2,4), columnspan=2, padx=6)
        self.theoretical_peak_freq_radio = tk.Radiobutton(self.theoretical_or_calibration_peak_freq_frame, text='theoretical', variable=self.theoretical_or_calibration_peak_freq_var, value=1, command=self.handle_radios)
        self.theoretical_peak_freq_radio.grid(row=1, column=0, pady=(2,4))
        self.calibration_peak_freq_radio = tk.Radiobutton(self.theoretical_or_calibration_peak_freq_frame, text='calibration', variable=self.theoretical_or_calibration_peak_freq_var, value=0, command=self.handle_radios)
        self.calibration_peak_freq_radio.grid(row=1, column=1, pady=(2,4))

        self.will_get_from_file_label = tk.Label(self.theoretical_or_calibration_peak_freq_frame,
                                                text="Will the calibration values\ncome from a file or selected from data?")
        self.will_get_from_file_var = tk.IntVar()
        self.will_get_from_file_var.set(-1)
        self.from_file_radio = tk.Radiobutton(self.theoretical_or_calibration_peak_freq_frame, text='from file', variable=self.will_get_from_file_var, value=1, command=self.handle_radios)
        self.from_selections_radio = tk.Radiobutton(self.theoretical_or_calibration_peak_freq_frame, text='make selections', variable=self.will_get_from_file_var, value=0, command=self.handle_radios)
        self.from_file_label = tk.Label(self.theoretical_or_calibration_peak_freq_frame,
                                        text="Please copy/paste values into\ncalibration_data/calibration_from_machine.csv")
        self.calibration_data_button = tk.Button(self.theoretical_or_calibration_peak_freq_frame, text='Calibration Data Menu', width=20, command=self.container.parent.open_calibration_data_window)

    def handle_radios(self):
        global input
        input.will_use_theoretical_vals = self.theoretical_or_calibration_peak_freq_var.get()
        if not input.will_use_theoretical_vals:
            self.will_get_from_file_label.grid(row=2, column=0, pady=(2,4), columnspan=2, padx=6)
            self.from_file_radio.grid(row=3, column=0, pady=(2,4))
            self.from_selections_radio.grid(row=3, column=1, pady=(2,4))
            if self.will_get_from_file_var.get() == 1:
                self.calibration_data_button.grid_forget()
                self.from_file_label.grid(row=4, column=0, columnspan=2, pady=2)
                input.calibration_data_from_file = True
            elif self.will_get_from_file_var.get() == 0:
                self.from_file_label.grid_forget()
                self.calibration_data_button.grid(row=4, column=0, columnspan=2, pady=2)
                input.calibration_data_from_file = False
        else:
            self.will_get_from_file_label.grid_forget()
            self.from_file_radio.grid_forget()
            self.from_selections_radio.grid_forget()

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
    
class CalibrationWindow():
    def __init__(self, parent, container):
        super().__init__(container) # initialize parent class for the child
        self.parent = parent

    def open_calibration_window(self):
        calibration_window = tk.Toplevel(self)
        calibration_window.title('Input/Select Calibration Data')
        self.calibration_frame = tk.Frame(calibration_window)
        self.calibration_frame.pack(anchor='n')
        self.constants_frame = tk.Frame(calibration_window)
        self.constants_frame.pack(anchor='n')
        self.int_plot_frame = tk.Frame(calibration_window)
        self.int_plot_frame.pack(anchor='n')

    def fill_calibration_window(self):
        self.calibration_label = tk.Label(self.calibration_frame, text="Calibration Data", font=('TkDefaultFont', 12, 'bold'))
        self.calibration_label.grid(row=1, column=0, columnspan=3, padx=16, pady=12)
        instructions = "SELECT RAW OVERTONES BEING ANALYZED FIRST\nIn this menu, enter crystal constants below,\nas well as make your selection of the\ncalibration range data with the button below"
        self.instruction_label = tk.Label(self.calibration_frame, text=instructions)
        self.instruction_label.grid(row=2, column=0, padx=16, pady=12)

        # crystal constant entries and labels
        self.rho_label = tk.Label(self.constants_frame, text="ρq: ")
        self.rho_label.grid(row=0, column=0, pady=(2,4), padx=4)
        self.rho_entry = tk.Entry(self.constants_frame, width=10)
        self.rho_entry.grid(row=0, column=1, pady=(2,4))
        self.mu_label = tk.Label(self.constants_frame, text="µq: ")
        self.mu_label.grid(row=0, column=2, pady=(2,4), padx=4)
        self.mu_entry = tk.Entry(self.constants_frame, width=10)
        self.mu_entry.grid(row=0, column=3, pady=(2,4))
        self.kappa_label = tk.Label(self.constants_frame, text="κ: ")
        self.kappa_label.grid(row=1, column=0, pady=(2,4), padx=4)
        self.kappa_entry = tk.Entry(self.constants_frame, width=10)
        self.kappa_entry.grid(row=1, column=1, pady=(2,4))
        self.epsilon_label = tk.Label(self.constants_frame, text="ϵ: ")
        self.epsilon_label.grid(row=1, column=2, pady=(2,4), padx=4)
        self.epsilon_entry = tk.Entry(self.constants_frame, width=10)
        self.epsilon_entry.grid(row=1, column=3, pady=(2,4), padx=4)

        # raw data interactive plot
        self.raw_int_plot_overtone_label = tk.Label(self.int_plot_frame, text="select overtone to visualize:")
        self.raw_int_plot_overtone_label.grid(row=0, column=0, pady=(16,2))
        self.raw_int_plot_overtone_select = tk.Entry(self.int_plot_frame, width=10)
        self.raw_int_plot_overtone_select.grid(row=0, column=1, pady=(16,2))
        self.which_range_label = tk.Label(self.int_plot_frame, text="Enter which range being selected\n(use identifier of your choosing\ni.e. numbers or choice of label)" )
        self.which_range_label.grid(row=1, column=0, pady=(2,12), padx=8)
        self.which_range_entry = tk.Entry(self.int_plot_frame, width=10)
        self.which_range_entry.grid(row=1, column=1, pady=(2,12))

        self.clear_selections_button = tk.Button(self.int_plot_frame, text="Clear All Selections", padx=6, pady=4, width=20, command=self.clear_ranges)
        self.clear_selections_button.grid(row=2, column=0, columnspan=2, pady=12)  

        self.raw_int_plot_button = tk.Button(self.int_plot_frame, text="Calibration Data Selection", padx=6, pady=4, width=20, command=self.run_calibration)
        self.raw_int_plot_button.grid(row=3, column=0, columnspan=2, pady=12)

    def run_calibration_input(self):
        overtone_select = self.raw_int_plot_overtone_select.get()
        which_range = self.which_range_entry.get()
        print(f"opening calibration thingy: {overtone_select}")
        select_calibration_data(input, overtone_select, which_range)

    def clear_selections(self):
        with open("calibration_data/calibration_data.csv", 'w') as fp:
            fp.write('')

        self.rho_entry.delete(0,tk.END)
        self.mu_entry.delete(0,tk.END)
        self.kappa_entry.delete(0,tk.END)
        self.epsilon_entry.delete(0,tk.END)
        

class Col2(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
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
            #self.calibration_data_button.grid_forget()
        
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
        self.plot_clean_data_check = tk.Checkbutton(self, text="Plot shifted data", font=('TkDefaultFont', 12, 'bold'), variable=self.plot_clean_data_var, onvalue=1, offvalue=0, command=self.receive_clean_checkboxes)
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
        self.interactive_plot_var = tk.IntVar()
        self.interactive_plot_check = tk.Checkbutton(self, text="Interactive plot", variable=self.interactive_plot_var, onvalue=1, offvalue=0, command=self.receive_optional_checkboxes)
        self.interactive_plot_check.grid(row=6, column=4)
        
        # options for the int plot
        self.interactive_plot_opts = tk.Frame(self)
        self.interactive_plot_overtone_label = tk.Label(self.interactive_plot_opts, text="select overtone to visualize:")
        self.interactive_plot_overtone_label.grid(row=0, column=0)
        self.interactive_plot_overtone_select = tk.Entry(self.interactive_plot_opts, width=10)
        self.interactive_plot_overtone_select.grid(row=1, column=0)

        # Options for changing the scale of x axis time
        self.scale_time_var = tk.IntVar()
        self.which_range_var = tk.IntVar()
        self.scale_time_check = tk.Checkbutton(self, text="Change scale of time? (default (s))", variable=self.scale_time_var, onvalue=1, offvalue=0, command=self.receive_scale_radios)
        self.scale_time_check.grid(row=8, column=4, pady=(32,0))
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

        self.clear_range_data_button = tk.Button(self, text="Clear Saved Range Data", padx=8, pady=6, width=20, command=self.clear_range_data)
        self.clear_range_data_button.grid(row=21, column=4, pady=4)

        self.exit_button = tk.Button(self, text="Exit", padx=8, pady=6, width=20, command=exit)
        self.exit_button.grid(row=22, column=4, pady=4)

    def receive_scale_radios(self):
        global input
        if self.scale_time_var.get() == 1:
            self.time_scale_frame.grid(row=11, column=4)
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

        input.will_plot_dF_dD_together = True if self.plot_dF_dD_together_var.get() == 1 else False
        input.will_normalize_F = True if self.normalize_F_var.get() == 1 else False
        input.will_plot_dD_v_dF = True if self.plot_dD_v_dF_var.get() == 1 else False
        input.will_plot_temp_v_time = True if self.plot_temp_v_time_var.get() == 1 else False

        if self.interactive_plot_var.get() == 1:
            input.will_interactive_plot = True
            input.range_frame_flag = True
            self.parent.repack_frames()
            if self.model_window_open_flag == False:
                self.parent.open_model_window()
                self.model_window_open_flag = True
            self.interactive_plot_opts.grid(row=7, column=4)
        else:
            input.will_interactive_plot = False
            input.range_frame_flag = False
            self.parent.repack_frames()
            if self.model_window_open_flag == True:
                self.parent.destroy_model_window()
                self.model_window_open_flag = False
            self.interactive_plot_opts.grid_forget()

    def submit(self):
        global input
        err_check()
        if input.range_frame_flag:
            input.clean_interactive_plot_overtone = int(self.interactive_plot_overtone_select.get())

        analyze_data(input)
        input.first_run = False

    def clear_range_data(self):
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
        # open secondary window with range selections for interactive plot
        
        # define and place entry for range options
        self.which_range_label = tk.Label(self.models_frame, text="Enter which range being selected\n(use identifier of your choosing\ni.e. numbers or choice of label)" )
        self.which_range_label.grid(row=2, column=0, pady=(2,4), padx=4)
        self.which_range_entry = tk.Entry(self.models_frame, width=10)
        self.which_range_entry.grid(row=3, column=0, pady=(2,4))

        # button to submit range selected
        self.which_range_submit = tk.Button(self.models_frame, text='Confirm Range', padx=10, pady=4, command=self.confirm_range)
        self.which_range_submit.grid(row=4, column=0, pady=4)
        input.range_frame_flag = True

        # run linear regression button
        self.run_tf_liquid_analysis_button = tk.Button(self.models_frame, text="Run Analysis of\nThin Film in Liquid", padx=6, pady=4, width=20,
                                             command=lambda: thin_film_liquid_analysis((input.which_plot['clean'], input.will_use_theoretical_vals, input.latex_installed, input.fig_format)))
        self.run_tf_liquid_analysis_button.grid(row=10, column=0, pady=4)

        # run sauerbrey button
        self.run_sauerbrey_analysis_button = tk.Button(self.models_frame, text="Run Sauerbrey Mass Analysis", padx=6, pady=4, width=20,
                                             command=lambda: sauerbrey((input.will_use_theoretical_vals, input.calibration_data_from_file, input.fig_format)))
        self.run_sauerbrey_analysis_button.grid(row=9, column=0, pady=4)

        # avg change in freq and dis against overtone button
        self.avgs_analysis = tk.Button(self.models_frame, text="Run Average Δf and Δd\n of Overtones", padx=6, pady=4, width=20,
                                             command=lambda: avgs_analysis(input.fig_format))
        self.avgs_analysis.grid(row=8, column=0, pady=4)

        # avg change in freq against overtone button
        self.run_tf_air_analysis_button = tk.Button(self.models_frame, text="Run Analysis of\nThin Film in Air", padx=6, pady=4, width=20,
                                             command=lambda: thin_film_air_analysis((input.which_plot['clean'], input.will_use_theoretical_vals, input.latex_installed, input.fig_format)))
        self.run_tf_air_analysis_button.grid(row=11, column=0, pady=4)

    def destroy_modeling_window(self):
        self.model_window.destroy()
        
    # when interactive plot window opens, grabs number of range from text field
    def confirm_range(self):
        global input
        input.which_range_selecting = self.which_range_entry.get()

        print(f"Confirmed range: {input.which_range_selecting}")


class PlotOptsWindow():
    def __init__(self, parent, container):
        super().__init__(container) # initialize parent class for the child
        self.parent = parent

    def open_opts_window(self):
        opts_window = tk.Toplevel(self)
        opts_window.title('Customize Plots')
        self.opts_col1 = tk.Frame(opts_window)
        self.opts_col1.pack(side='left', anchor='n')
        self.opts_col2 = tk.Frame(opts_window)
        self.opts_col2.pack(side='right', anchor='n')
        self.opts_confirm = tk.Frame(opts_window)
        self.opts_confirm.pack(side='bottom')

    def fill_opts_window(self):
        # first column contains most plot customizations
        self.customize_label = tk.Label(self.opts_col1, text="Plot Customization Options", font=('TkDefaultFont', 12, 'bold'))
        self.customize_label.grid(row=1, column=0, columnspan=3, padx=16, pady=12)

        self.font_choice_label = tk.Label(self.opts_col1, text="Enter font selection:")
        self.font_choice_label.grid(row=3, column=0, pady=(20,4))
        self.font_choice_entry = tk.Entry(self.opts_col1, width=10)
        self.font_choice_entry.grid(row=3, column=1, pady=(20,4))

        self.label_text_size_label = tk.Label(self.opts_col1, text="Enter Label font size:")
        self.label_text_size_label.grid(row=4, column=0, pady=(16,0))
        self.label_text_size_entry = tk.Entry(self.opts_col1, width=10)
        self.label_text_size_entry.grid(row=4, column=1, pady=(16,0))

        self.title_text_size_label = tk.Label(self.opts_col1, text="Enter Title font size:")
        self.title_text_size_label.grid(row=5, column=0, pady=(16,0))
        self.title_text_size_entry = tk.Entry(self.opts_col1, width=10)
        self.title_text_size_entry.grid(row=5, column=1, pady=(16,0))

        self.value_text_size_label = tk.Label(self.opts_col1, text="Enter Value font size:")
        self.value_text_size_label.grid(row=6, column=0, pady=(16,0))
        self.value_text_size_entry = tk.Entry(self.opts_col1, width=10)
        self.value_text_size_entry.grid(row=6, column=1, pady=(16,0))

        self.legend_text_size_label = tk.Label(self.opts_col1, text="Enter Legend font size:")
        self.legend_text_size_label.grid(row=7, column=0, pady=(16,0))
        self.legend_text_size_entry = tk.Entry(self.opts_col1, width=10)
        self.legend_text_size_entry.grid(row=7, column=1, pady=(16,0))

        self.tick_direction_label = tk.Label(self.opts_col1, text="Choose tick direction:")
        self.tick_direction_label.grid(row=9, column=0, columnspan=3, pady=(16,0))
        self.tick_direction_var = tk.IntVar()
        self.tick_direction_in_radio = tk.Radiobutton(self.opts_col1, text="in", variable=self.tick_direction_var, value=1)
        self.tick_direction_in_radio.grid(row=10, column=0)
        self.tick_direction_out_radio = tk.Radiobutton(self.opts_col1, text="out", variable=self.tick_direction_var, value=0)
        self.tick_direction_out_radio.grid(row=10, column=1)
        self.tick_direction_inout_radio = tk.Radiobutton(self.opts_col1, text="both", variable=self.tick_direction_var, value=2)
        self.tick_direction_inout_radio.grid(row=10, column=2)


        # second column color customizer
        self.ov_color_label = tk.Label(self.opts_col2, text="Customize Overtone Plot Colors", font=('TkDefaultFont', 12, 'bold'))
        self.ov_color_label.grid(row=1, column=0, padx=16, pady=12)
        
        self.ov1_color_button = tk.Button(self.opts_col2, text="1st overtone", width=10, command=lambda: self.choose_color(1))
        self.ov1_color_button.grid(row=3, column=0, pady=(16,4))
        self.ov3_color_button = tk.Button(self.opts_col2, text="3rd overtone", width=10, command=lambda: self.choose_color(3))
        self.ov3_color_button.grid(row=4, column=0, pady=4)
        self.ov5_color_button = tk.Button(self.opts_col2, text="5th overtone", width=10, command=lambda: self.choose_color(5))
        self.ov5_color_button.grid(row=5, column=0, pady=4)
        self.ov7_color_button = tk.Button(self.opts_col2, text="7th overtone", width=10, command=lambda: self.choose_color(7))
        self.ov7_color_button.grid(row=6, column=0, pady=4)
        self.ov9_color_button = tk.Button(self.opts_col2, text="9th overtone", width=10, command=lambda: self.choose_color(9))
        self.ov9_color_button.grid(row=7, column=0, pady=4)
        self.ov11_color_button = tk.Button(self.opts_col2, text="11th overtone", width=10, command=lambda: self.choose_color(11))
        self.ov11_color_button.grid(row=8, column=0, pady=4)
        self.ov13_color_button = tk.Button(self.opts_col2, text="13th overtone", width=10, command=lambda: self.choose_color(13))
        self.ov13_color_button.grid(row=9, column=0, pady=(4, 200))

        self.options_saved_label = tk.Label(self.opts_confirm, text="Confirming selections saves preferences\neven when software is closed")
        self.options_saved_label.grid(row=18, column=0, pady=(24,4))
        self.default_button = tk.Button(self.opts_confirm, text="Default Values", width=20, command=self.set_default_values)
        self.default_button.grid(row=19, column=0, pady=4)
        self.confirm_button = tk.Button(self.opts_confirm, text="Confirm Selections", width=20, command=self.confirm_opts)
        self.confirm_button.grid(row=20, column=0, pady=(4,16))

    def choose_color(self, ov_num):
        self.color_code = colorchooser.askcolor(title="Choose color for overtone", parent=self)
        self.options['colors'][f'ov{ov_num}'] = self.color_code[1]

    def set_text(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)
        
    def set_default_values(self):
        with open('plot_opts/default_opts.json', 'r') as fp:
            default_opts = json.load(fp)
        self.set_text(self.font_choice_entry, default_opts['font'])
        self.set_text(self.label_text_size_entry, default_opts['label_text_size'])
        self.set_text(self.title_text_size_entry, default_opts['title_text_size'])
        self.set_text(self.value_text_size_entry, default_opts['value_text_size'])
        self.set_text(self.legend_text_size_entry, default_opts['legend_text_size'])
        
        self.options['tick_dir'] = default_opts['tick_dir']
        self.options['colors'] = default_opts['colors']

    def confirm_opts(self):
        self.options['font'] = self.font_choice_entry.get()
        self.options['label_text_size'] = self.label_text_size_entry.get()
        self.options['title_text_size'] = self.title_text_size_entry.get()
        self.options['value_text_size'] = self.value_text_size_entry.get()
        self.options['legend_text_size'] = self.legend_text_size_entry.get()

        if self.tick_direction_var.get() == 0:
            self.options['tick_dir'] = 'in'
        elif self.tick_direction_var.get() == 1:
            self.options['tick_dir'] = 'out'
        else:
            self.options['tick_dir'] = 'inout'

        for key in self.options.keys():
            if self.options[key] == '':
                raise Exceptions.MissingPlotCustomizationException(key, "Please Specify Missing field. ")

        with open('plot_opts/plot_customizations.json', 'w') as fp:
            json.dump(self.options, fp)


menu = App()
menu.mainloop()