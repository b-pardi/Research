"""
Author: Brandon Pardi
Created: 6/22/2022, 3:56 pm
Last Modified: 9/15/2022 12:30pm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
from scipy import stats
from pathlib import Path
import os

"""
README
- Please execute 'install_packages.py' BEFORE running this script
- make sure the data is in a folder entitled 'indentation_data', and that the script is in the same file path level as the folder
- script will name individual plots the same name as its corresponding sheet, followed by '-plot'
- var curve_time can be adjusted depending on the data set for the x length of the curve
- if program running slow, lower var DPI to ~80
- var names; df(s) short for dataframe(s), fvt_df: force vs time data frame,
sd: squared distance, comb_df: combined dataframe
- tau and R vals for each sheet are printed AND recorded in the legend of its respective plot

TASKS
- grabs all sheets from 'indentation_data' folder and converts them to dataframes
- scrubs data to left of curve start (highest y values), and after <CURVE_TIME> to the right of curve start
- removes points below the force value at tf
- currently generates individual plots for each sheet, one figure with each data set plotted and color coded,
one figure with all data from all sheets in one BIG plot, and a box and whisker plot of Tau values from each sheet
- fits curve for each individual plot along with getting R^2 and Tau values
- writes tau values to 'taus.txt'

WIP
- plot format
- reevaluate how to find start of curve (derivative of data)
    - avg of x number highest points
    - gaussian fit to 
- error bars (different script)
- youngs modulus

PLOT FORMATTING
- axis title, Arial size 16
- number size 14
- legend ?
- x indentation force, F(sub)i ; F is in italics
- make scale for numbers consistent across the board
"""

### INPUT VARIABLES ##

# use this data path for data outside the main folder the script is in
#data_path = Path("your absolute path")

# indicate what category of data for later swarm plots
# 0: soft, 1: stiff, 2: soft viscoelastic, 3: stiff viscoelastic
data_category = 0

# If you would like to remove previously made plots before making more, set to True
will_remove_plots = True

# If unable to find column index, check the skiprows value here!
rows_skipped = 0

# TIME PARAMETER FOR LENGTH OF CURVE, data this long after curve start will be removed
curve_time = 60

# finding start of curve requires finding max value,
# to avoid outliars it will average x number of max force points
# this variable will determing how many to average
num_max_pts_to_avg = 5

gauss_x_range = 200

# estimate of expected initial values
p0 = (2000, .1, 50)

# pixel density of plots, higher number -> more detail and more memory
# if program running slow, lower to ~80
DPI = 160

# find sheets in path, concat into 1 large data frame
data_path = Path.joinpath(Path.cwd(), "indentation_data_noisy")

sheets = [file for file in data_path.iterdir() if file.suffix == ".xlsx"]

# check file grabbing
for sheet in sheets:
    assert os.path.isfile(sheet)

# create file pointer for writing Tau values later
tau_youngs_file = open("aggregate_data/taus-youngs.csv", 'w')
tau_youngs_file.write("file_name,data_category,Tau,T_rsq,E,E_rsq\n")

if will_remove_plots == True:
    plot_path = Path.joinpath(Path.cwd(), "indentation_plots")
    old_plots = [file for file in plot_path.iterdir() if file.suffix == ".png"]
    for plot in old_plots:
        plot.unlink()

dfs = [pd.read_excel(file, skiprows=rows_skipped) for file in sheets]
titles = []
scrubbed_dfs = []
taus = []
time_margin = 0.05
force_margin = 0.0001
data_category_list = ['soft', 'stiff', 'soft_viscoelastic', 'stiff_viscoelastic']
i = 0
for path in sheets:
    titles.append(os.path.basename(path))

# curve to fit
def monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b

# curve fit for finding max value
def gauss(x, H, A, x0, sigma):
    return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

for df in dfs:
    # debugging
    #print(f"currently checking: '{titles[i]}':")

    # only need time and force columns
    fvt_df = df[['time(seconds)', 'Fn (uN)']]

    # some entries contained 'na' for time so they will be removed
    fvt_df = fvt_df.dropna(axis=0, how='any', inplace=False)
    temp_df = fvt_df[fvt_df['time(seconds)'].apply(lambda x: isinstance(x, str))]
    if (temp_df.size > 0):
        fvt_df = fvt_df.drop(fvt_df.index[temp_df.index])

    # ensure units are all same
    fvt_df = fvt_df.astype(float)

    # account for units being micro
    pd.options.mode.chained_assignment = None
    fvt_df.loc[:,'Fn (uN)'] /= 1000000
    pd.options.mode.chained_assignment = 'warn'

    # find the start of the curve (point of greatest force)
    # use average of x largest y values to reduce chance of outliars,
    # and prevent curve from starting at incorrect place
    max_force_mean = fvt_df['Fn (uN)'].nlargest(num_max_pts_to_avg).mean()
    max_force = fvt_df.iloc[(fvt_df['Fn (uN)'] - max_force_mean).abs().argsort()[0],:]['Fn (uN)']
    max_force_ind = fvt_df[fvt_df['Fn (uN)'] == max_force].index
    #max_force = fvt_df['Fn (uN)'].max()
    print(f"max force chosen: {max_force} @{max_force_ind[0]}")
    '''gauss_x = fvt_df.loc[max_force_ind-gauss_x_range:max_force_ind+gauss_x_range]['time(seconds)'].values
    gauss_y = fvt_df.loc[max_force_ind-gauss_x_range:max_force_ind+gauss_x_range]['Fn (uN)'].values
    gauss_param, gauss_cv = curve_fit(gauss, gauss_x, gauss_y)'''

    # find 60 seconds after max force point (tf)
    t0 = fvt_df.loc[fvt_df['Fn (uN)'] >= max_force-force_margin, 'time(seconds)'].values[0]
    tf = t0 + curve_time

    # find the force at tf
    tf_df = fvt_df['time(seconds)'].between(tf-time_margin, tf+time_margin)
    tf_df = tf_df[tf_df]
    tf_ind = tf_df.index[0]
    f_tf = fvt_df['Fn (uN)'].loc[tf_ind]

    # only need values to the right of max force point,
    # and left of 60 seconds after max force point
    fvt_df = fvt_df[max_force_ind[0]:]
    fvt_df = fvt_df.drop(fvt_df[fvt_df['time(seconds)'] > tf].index)
    # remove values that fall too far below force value at end of curve 
    fvt_df = fvt_df.drop(fvt_df[fvt_df['Fn (uN)'] < f_tf - force_margin].index)
    fvt_df = fvt_df.reset_index(drop=True)

    xdata = fvt_df['time(seconds)']
    ydata = fvt_df['Fn (uN)']

    exp_params, exp_cv = curve_fit(monoExp, xdata, ydata, p0)
    m, t, b = exp_params
    tau = 1 / t
    taus.append(tau)
    yfit = monoExp(xdata, m, t, b)

    # determine curve fit accuracy using R² diffs
    sd = np.square(ydata - yfit)
    sd_mean = np.square(ydata-np.mean(ydata))
    T_rsq = 1 - np.sum(sd) / np.sum(sd_mean)
    print(f"for data in '{titles[i]}':\nTau = {tau}\nR² = {T_rsq}")
    if T_rsq < 0.9:
        print("WARNING: weak curve fit")
    
    # write Tau values to a text file
    text = f"R² = {T_rsq}\nTau = {tau}\n"
    tau_youngs_file.write(f"{titles[i]},{data_category_list[data_category]},{tau},{T_rsq},na,na\n")

    '''PLOTTING THE DATA AND CURVE FIT'''
    # subtract t0 to shift curve left to start at 0,
    # mult by 1000000 to account for units being micro
    # figure 1 is indiv. plot for each sheet, figure 2 is combined plot of all sheets in dir.
    plt.figure(1, clear=True)
    plt.plot(xdata-t0, ydata*1000000, label="data")
    # curve fit plots in try/except because of some data does not fit curve properly
    try:
        plt.plot(xdata-t0, yfit*1000000, '--', label='curve fit', color='black')
    except Exception as exc:
        print(f"Curve fit failed! Data in: {titles[i]}\n err: {exc}")
    plt.plot([], [], ' ', label = text)
    plt.legend(loc='upper right')
    plt.xlabel('Time (s)')
    plt.ylabel('Force (μn)')
    plt.figure(1).savefig(f"indentation_plots/{titles[i]}-plot.png", dpi=DPI)

    plt.figure(2)
    plt.plot(xdata-t0, ydata*1000000, label="data")
    try:
        plt.plot(xdata-t0, yfit*1000000, '--', label='curve fit', color='black')
    except Exception as exc:
        print(f"Curve fit failed! Data in: {titles[i]}\n err: {exc}")
    scrubbed_dfs.append(fvt_df)
    i+=1

# this figure has all indiv sheets plotted onto it
plt.figure(2).savefig("indentation_plots/multiplot.png", dpi=DPI)

# box and whisker plot for Tau values
plt.figure(4)
plt.boxplot(taus, vert=True)
plt.xlabel('Tau')
plt.figure(4).savefig("indentation_plots/Taus_BnW.png", dpi=DPI)

# close tau file
tau_youngs_file.close()
