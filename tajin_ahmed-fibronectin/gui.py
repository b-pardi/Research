from tkinter import *
import sys
from datetime import datetime, time


'''
GUI notes
- file name box (later maybe window to search for file)
- checkbox for each frequency being plotted
    - checkbox for raw and clean data
        - raw data plots are individual for overtone of each freq/dis
        - cleaned plots will be overlapped (all overtones of freq and all of dis)
- abs base time t0, tf
- checkbox for other formulas (normalize data)

- look into:
    - interactive plots (plotly)
'''


### INPUT DEFINITIONS ###
file_name = "08102022_n=2_Fn at 500 ug per ml and full SF on func gold at 37C"
file_ext = '.csv'
abs_base_t0 = time(8, 35, 52)
abs_base_tf = time(9, 9, 19)
# column names
abs_time_col = 'Time'
rel_time_col = 'Relative_time'
num_freqs_tested = 5

'''Variable Initializations'''
file_info = []

'''Function Defintions for UI events'''
def col_names_submit():
    file_info.append(file_name_entry.get())
    file_info.append(file_path_entry.get())

def clear_file_data():
    global file_info
    file_info = []
    cleared_label.grid(row=12, column=0)
    file_name_entry.delete(0, END)
    file_path_entry.delete(0, END)

def handle_fn_focus_in(_):
    file_name_entry.delete(0, END)
    file_name_entry.config(fg='black')

def handle_fn_focus_out(_):
    file_name_entry.delete(0, END)
    file_name_entry.config(fg='gray')
    file_name_entry.insert(0, "File name here")

def handle_fp_focus_in(_):
    file_path_entry.delete(0, END)
    file_path_entry.config(fg='black')

def handle_fp_focus_out(_):
    file_path_entry.delete(0, END)
    file_path_entry.config(fg='gray')
    file_path_entry.insert(0, "Enter path to file (leave blank if in same dir)")    


'''Enter event loop for UI'''
root = Tk()

# define and place file info labels and buttons
file_name_label = Label(root, text="Enter data file information ")
spacing = Label(root, text="         ")
file_name_label.grid(row=0, column=0)
spacing.grid(row=1, column=0)
cleared_label = Label(root, text="Cleared!")

file_name_entry = Entry(root, width=40, bg='white', fg='gray')
file_name_entry.grid(row=2, column=0, columnspan=1, padx=8, pady=4)
file_name_entry.insert(0, "File name here")
file_name_entry.bind("<FocusIn>", handle_fn_focus_in)
file_name_entry.bind("<FocusOut>", handle_fn_focus_out)

file_path_entry = Entry(root, width=40, bg='white', fg='gray')
file_path_entry.grid(row=3, column=0, columnspan=1, padx=8, pady=4)
file_path_entry.insert(0, "Enter path to file (leave blank if in same dir)")
file_path_entry.bind("<FocusIn>", handle_fp_focus_in)
file_path_entry.bind("<FocusOut>", handle_fp_focus_out)

file_data_submit_button = Button(root, text="Submit file information", padx=12, pady=8, command=col_names_submit)
file_data_submit_button.grid(row=10, column=0)
file_data_clear_button = Button(root, text="Clear Entries", padx=12, pady=8, command=clear_file_data)
file_data_clear_button.grid(row=11, column=0)

# define and place checkboxes


# conclude UI event loop
root.mainloop()

''' Grab data from UI temp into variables for data analysis'''

# assign file info data
if len(file_info) == 0:
    print("please define file information!")
    sys.exit(1)
elif len(file_info) == 1:
    file_name = file_info[0]
else:
    file_name = file_info[0]
    file_path = file_info[1]

print(file_info)
