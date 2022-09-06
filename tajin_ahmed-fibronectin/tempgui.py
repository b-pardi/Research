from tkinter import *
from datetime import datetime, time


### INPUT DEFINITIONS ###
file_name = "08102022_n=2_Fn at 500 ug per ml and full SF on func gold at 37C"
file_ext = '.csv'
# time is in (h, m, s)
abs_base_t0 = time(8, 35, 52)
abs_base_tf = time(9, 9, 19)
# column names
abs_time_col = 'Time'
rel_time_col = 'Relative_time'
num_freqs_tested = 5

# number after indicates which resonant frequency testing on (fundamental, 1st, 3rd, etc)
rf_cols = []
dis_cols = []
for i in range(num_freqs_tested):
    rf_cols.append(f'Frequency_{i}')
    dis_cols.append(f'Dissipation_{i}')
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
