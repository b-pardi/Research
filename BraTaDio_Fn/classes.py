from tkinter import *
from datetime import time

class Menu:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.button = Button(master, text=" ", command=self.clicker)
        self.button.pack()
    
    def clicker(self):
        print("clicked")


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
                            '9th_freq': False, '9th_dis': False},

                    'clean': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': True, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': True}}
