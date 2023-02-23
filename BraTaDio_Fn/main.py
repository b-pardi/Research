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
from lin_reg import *


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
        self.range_window_flag = False
        self.which_plot = {'raw': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': False, '11th_freq': False, 'th_dis': False,
                            '13th_freq': False, '13th_dis': False},

                    'clean': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': True, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': True}}

input = Input()

# menu class inherits Tk class 
class Menu(Tk):
    def __init__(self):
        super().__init__() # instantiate the parent class

        self.title = 'BraTaDio QCMd Expert'
        self.iconphoto(False, PhotoImage(file="res/m3b_comp.png"))
    
        # defining containers
        container = Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # initializing frames
        self.frames = {}
        self.col1 = Col1
        self.col2 = Col2
        self.col3 = Col3
        self.col4 = Col4

        # define and pack frames
        for i, f in enumerate({Col1, Col2, Col3, Col4}):
            frame = f(self, container)
            self.frames[f] = frame
            frame.grid(row=0, column=i, sticky = 'nsew')


class Col1(Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        file_name_label = Label(self, text="Enter data file information", font=('TkDefaultFont', 12, 'bold'))
        file_name_label.grid(row=0, column=0, pady=(14,16), padx=(6,0))
        
        self.file_name_entry = Entry(self, width=40, bg='white', fg='gray')
        self.file_name_entry.grid(row=2, column=0, columnspan=1, padx=8, pady=4)
        #self.file_name_entry.insert(0, "File name here (W/ EXTENSION)")
        self.file_name_entry.insert(0, "sample2.csv")
        self.file_name_entry.bind("<FocusIn>", self.handle_fn_focus_in)
        self.file_name_entry.bind("<FocusOut>", self.handle_fn_focus_out)

        self.file_path_entry = Entry(self, width=40, bg='white', fg='gray')
        self.file_path_entry.grid(row=3, column=0, columnspan=1, padx=8, pady=4)
        self.file_path_entry.insert(0, "Enter path to file (leave blank if in 'raw data' folder)")
        self.file_path_entry.bind("<FocusIn>", self.handle_fp_focus_in)
        self.file_path_entry.bind("<FocusOut>", self.handle_fp_focus_out)

        file_overwrite_var = IntVar()
        file_overwrite_check = Checkbutton(self, text='New file with processed data?', variable=file_overwrite_var, onvalue=1, offvalue=0, pady=10)
        file_overwrite_check.grid(row=5, column=0)

        baseline_frame = Frame(self)
        baseline_time_label = Label(self, text="Enter absolute baseline time")
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

        cleared_label = Label(self, text="Cleared!")
        submitted_label = Label(self, text="Submitted!")
        err_label = Label(self, text="Error occured,\nplease see terminal for details", font=("Arial",14))

        file_data_submit_button = Button(self, text="Submit file information", padx=8, pady=6, width=20, command=self.col_names_submit)
        file_data_submit_button.grid(row=10, column=0, pady=(16,4))
        file_data_clear_button = Button(self, text="Clear Entries", padx=8, pady=6, width=20, command=self.clear_file_data)
        file_data_clear_button.grid(row=11, column=0, pady=4)
        
    def handle_fn_focus_in(self, _):
        if self.file_name_entry.get() == "File name here (W/ EXTENSION)":
            self.file_name_entry.delete(0, END)
            self.file_name_entry.config(fg='black')

    def handle_fn_focus_out(self, _):
        if self.file_name_entry.get() == "":
            self.file_name_entry.delete(0, END)
            self.file_name_entry.config(fg='gray')
            self.file_name_entry.insert(0, "File name here (W/ EXTENSION)")

    def handle_fp_focus_in(self, _):
        if self.file_path_entry.get() == "Enter path to file (leave blank if in 'raw data' folder)":
            self.file_path_entry.delete(0, END)
            self.file_path_entry.config(fg='black')

    def handle_fp_focus_out(self, _):
        if self.file_path_entry.get() == "":
            self.file_path_entry.delete(0, END)
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

    def clear_file_data(self):
        global input
        input.abs_base_t0 = time(0, 0, 0)
        input.abs_base_tf = time(0, 0, 0)
        self.cleared_label.grid(row=12, column=0)
        self.file_name_entry.delete(0, END)
        self.file_path_entry.delete(0, END)
        self.hours_entry_t0.delete(0, END)
        self.minutes_entry_t0.delete(0, END)
        self.seconds_entry_t0.delete(0, END)
        self.hours_entry_tf.delete(0, END)
        self.minutes_entry_tf.delete(0, END)
        self.seconds_entry_tf.delete(0, END)
        self.file_overwrite_var.set(0)
        self.submitted_label.grid_forget()

class Col2(Frame):
    def __init__(self, parent, container):
        super().__init__(container)


class Col3(Frame):
    def __init__(self, parent, container):
        super().__init__(container)


class Col4(Frame):
    def __init__(self, parent, container):
        super().__init__(container)


'''Function Defintions for UI events'''








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
col1 = Frame(root)
col2 = Frame(root)
col3 = Frame(root)
fr2 = Frame(col3)
fr3 = Frame(col3)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

col1.grid(row=0, column=1, sticky='nsew', padx=(4,4), pady=(4,10))
col2.grid(row=0, column=2, sticky='nsew', padx=(4,4), pady=(4,10))
col3.grid(row=0, column=3, sticky='nsew', padx=(4,10), pady=(4,10))
fr2.grid(row=8, column=4)
fr3.grid(row=15, column=4)


# conclude UI event loop
root.mainloop()

