from tkinter import *
from datetime import datetime, time


### INPUT DEFINITIONS ###
file_name = "08102022_n=2_Fn at 500 ug per ml and full SF on func gold at 37C"
file_ext = '.csv'
abs_base_t0 = time(8, 35, 52)
abs_base_tf = time(9, 9, 19)
# column names
abs_time_col = 'Time'
rel_time_col = 'Relative_time'
num_freqs_tested = 5

# number after indicates which resonant frequency testing on (fundamental, 1st, 3rd, etc)
'''rf_col_fund = 'Frequency_0'
dis_col_fund = 'Dissipation_0'
rf_col_3 = 'Frequency_1'
dis_col_3 = 'Dissipation_1'
rf_col_5 = 'Frequency_2'
dis_col_5 = 'Dissipation_2'
rf_col_7 = 'Frequency_3'
dis_col_7 = 'Dissipation_3'
rf_col_9 = 'Frequency_4'
dis_col_9 = 'Dissipation_4' '''

col_names = []

root = Tk()

def col_names_submit():
    col_names.append(rf_col_fund_entry.get())
    col_names.append(dis_col_fund_entry.get())

def clear_cols():
    col_names = []
    cleared_label.grid(row=12, column=0)
    rf_col_fund_entry.delete(0, END)
    dis_col_fund_entry.delete(0, END)


col_names_label = Label(root, text="Enter column names as they appear in excel")
spacing = Label(root, text="         ")
col_names_label.grid(row=0, column=0)
spacing.grid(row=1, column=0)
cleared_label = Label(root, text="Cleared!")

rf_col_fund_entry = Entry(root, width=40)
rf_col_fund_entry.grid(row=2, column=0, columnspan=1, padx=8, pady=4)
rf_col_fund_entry.insert(1, "fundamental resonant frequency")
dis_col_fund_entry = Entry(root, width=40)
dis_col_fund_entry.grid(row=3, column=0, columnspan=1, padx=8, pady=4)
dis_col_fund_entry.insert(0, "fundamental dissipation")

col_names_submit_button = Button(root, text="Submit column names", padx=12, pady=8, command=col_names_submit)
col_names_submit_button.grid(row=10, column=0)
clear_button = Button(root, text="Clear Entries", padx=12, pady=8, command=clear_cols)
clear_button.grid(row=11, column=0)

root.mainloop()

rf_col_fund = col_names[0]
dis_col_fund = col_names[1]
print(col_names)
