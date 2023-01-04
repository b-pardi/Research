"""
Author: Brandon Pardi
Created: 6/22/2022, 3:56 pm
Last Modified: 9/16/2022 9:30pm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
from pathlib import Path
import os
import sys

"""
README
- Please execute 'install_packages.py' BEFORE running this script
- Check the input variables section and make sure all user defined inputs are correct
- make sure the data is in a folder entitled 'indentation_data', and that the script is in the same file path level as the folder
    OR use the global path outlined in the input variables section
- script will name individual plots the same name as its corresponding sheet, followed by '-plot'
- var curve_time can be adjusted depending on the data set for the x length of the curve for tau values
- if program running slow, lower var DPI to ~80
- var names; df(s) short for dataframe(s), fvt_df: force vs time data frame, fvd_df: force vs displacement df
    sd: squared distance,
- tau, youngs mod, and their rsq vals for each sheet are printed AND recorded in the legend of its respective plot,
- those values are also appended to 'taus-youngs.csv' for later swarmplot use

TASKS
- grabs all sheets from 'indentation_data' folder and converts them to dataframes
- for taus, scrubs data to left of curve start (highest y values), and after <CURVE_TIME> to the right of curve start
    also removes points below the force value at tf
- for youngs mod values, removes everything after the max force point,
    as well as finds the std dev of the first <youngs_pts_to_avg> data points,
    and removes everything less than 3 times that value
- currently generates individual plots for each sheet, and one figure with each data set plotted and color coded
- box and whisker plots for E and tau will be generated in 'taus-youngs.py' when enough aggregate data is collected
- fits curve for each individual plot along with getting R^2 values
- writes tau and youngs mod values to 'taus-youngs.csv' for use with 'taus-youngs.py'

WIP
- plot format

PLOT FORMATTING
- axis title, Arial size 16
- number size 14
- legend Arial size 16
- x indentation force, F(sub)i ; F is in italics
- make scale for numbers consistent across the board
"""

### INPUT VARIABLES ##

# data path for where data xls sheets are kept
# use this data path for data outside the main folder the script is in
#data_path = Path("your absolute path")
# use this one if keeping sheets in the directory with the script
data_path = Path.joinpath(Path.cwd(), "indentation_data_noisy")

# indicate what category of data for later swarm plots
# 0: soft, 1: stiff, 2: soft viscoelastic, 3: stiff viscoelastic
data_category = 1

# If you would like to remove previously made plots before making more, set to True
will_remove_plots = True

# If unable to find column index, check the skiprows value here!
rows_skipped = 0

# TIME PARAMETER FOR LENGTH OF CURVE, data this long after curve start will be removed
curve_time = 60

# finding start of curve for tau vals requires finding max value,
# to avoid outliars it will average x number of max force points
# this variable will determing how many to average
num_max_pts_to_avg = 7

# number of data points in the non-interacting regime used to find the std dev,
# for defining onset of interaction (start of curve)
youngs_pts_to_avg = 500

# estimate of expected initial values for Tau
p0_tau = (2000, .1, 50)

# estimate of expected initial values for Young's Modulus
p0_E = (5)

# constants for Youngs Modulus function
R = 0.00159 
nu = 0.5

# pixel density of plots, higher number -> more detail and more memory
# if program running slow, lower to ~80
DPI = 200

# find sheets in path, concat into 1 large data frame
sheets = [file for file in data_path.iterdir() if file.suffix == ".xlsx"]
# check file grabbing
for sheet in sheets:
    assert os.path.isfile(sheet)

# create file pointer for writing Tau values later
tau_youngs_file_RO = open("aggregate_data/taus-youngs.csv", 'r')
tau_youngs_file = open("aggregate_data/taus-youngs.csv", 'a')
header = "file_name,data_category,Tau,T_rsq,E,E_rsq,Tau_M,Tau_B\n"

# check if header already exists in csv (if new file it won't)
if header not in tau_youngs_file_RO.read():
    tau_youngs_file.write(header)
else:
    print("header already exists")

# remove old plots if indicated by user above
if will_remove_plots == True:
    plot_path = Path.joinpath(Path.cwd(), "indentation_plots")
    old_plots = [file for file in plot_path.iterdir() if file.suffix == ".png"]
    for plot in old_plots:
        plot.unlink()

# misc variable declaration
titles = []
Es = []
taus = []
time_margin = 0.05
force_margin = 0.0001
data_category_list = ['soft', 'stiff', 'soft_viscoelastic', 'stiff_viscoelastic']
i = 0

# get list of file names for indexing
for path in sheets:
    titles.append(os.path.basename(path))

# curve to fit tau
def tau_monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b

# curve to fit youngs modulus
def youngs_monoExp(x, E):
    return ((4/3) * R**(1/2) * x**(3/2) * E)/(1-nu**2)

# open all sheets into dfs
try:
    dfs = [pd.read_excel(file, skiprows=rows_skipped) for file in sheets]
except ValueError as ve:
    print(f"Could not read excel sheets! Make sure excel sheets are not currently open\n err: {ve}")
    sys.exit(1)

for df in dfs:
    # only need time and force columns for tau,
    # and z displacement and force columns for youngs
    fvt_df = df[['time(seconds)', 'Fn (uN)']]
    fvd_df = df[['z-stage (um)', 'Fn (uN)']]

    '''GENERAL CLEANING'''

    # some entries contained 'na' for time so they will be removed
    fvt_df = fvt_df.dropna(axis=0, how='any', inplace=False)
    fvd_df = fvd_df.dropna(axis=0, how='any', inplace=False)
    temp_df = fvt_df[fvt_df['time(seconds)'].apply(lambda x: isinstance(x, str))]
    if (temp_df.size > 0):
        fvt_df = fvt_df.drop(fvt_df.index[temp_df.index])

    # ensure units are all same
    fvt_df = fvt_df.astype(float)
    fvd_df = fvd_df.astype(float)

    # account for units being micro
    pd.options.mode.chained_assignment = None
    fvt_df.loc[:,'Fn (uN)'] /= 1000000
    pd.options.mode.chained_assignment = 'warn'


    '''TAU VALUE CLEANING'''

    # find the start of the curve for taus (point of greatest force)
    # use average of some largest y values to reduce chance of outliars,
    # and prevent curve from starting at incorrect place
    max_force_mean = fvt_df['Fn (uN)'].nlargest(num_max_pts_to_avg).mean()
    max_force = fvt_df.iloc[(fvt_df['Fn (uN)'] - max_force_mean).abs().argsort()[0],:]['Fn (uN)']
    max_force_ind = fvt_df[fvt_df['Fn (uN)'] == max_force].index

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
    fvt_df['time(seconds)'] -= fvt_df['time(seconds)'].min()


    '''YOUNGS MODULUS CLEANING'''

    # only need everything up til the max force point
    fvd_df = fvd_df[:max_force_ind[0]+1]
    # find std dev and keep everything more than 3 times it
    std_dev = fvd_df['Fn (uN)'].iloc[:youngs_pts_to_avg].std()
    counter = 0
    subi = 0
    while(counter < 10):
        cur = fvd_df.iloc[subi]['Fn (uN)']
        #print(cur)
        if cur >= 3 * std_dev:
            counter += 1
        else:
            counter = 0
        subi += 1
    
    fvd_df = fvd_df[subi - 8:]
    fvd_df = fvd_df.reset_index(drop=True)
    fvd_df['z-stage (um)'] -= fvd_df['z-stage (um)'].min()
    fvd_df['Fn (uN)'] -= fvd_df['Fn (uN)'].min()

    # put data df columns into lists
    xdata_tau = fvt_df['time(seconds)'].values
    xdata_E = fvd_df['z-stage (um)'].values
    ydata_tau = fvt_df['Fn (uN)'].values
    ydata_E = fvd_df['Fn (uN)'].values

    '''CURVE FITS'''

    # curve fit for tau
    tau_params, tau_cv = curve_fit(tau_monoExp, xdata_tau, ydata_tau, p0_tau)
    m, t, b = tau_params
    tau = 1 / t
    taus.append(tau)
    yfit_tau = tau_monoExp(xdata_tau, m, t, b)

    # curve fit for Youngs Modulus
    E_params, cv = curve_fit(youngs_monoExp, xdata_E, ydata_E, p0_E)
    E = E_params[0]
    Es.append(E)
    yfit_E = youngs_monoExp(xdata_E, E)
    youngsMod = f"Y = ((4/3)*{R}^(1/2) * x^(3/2) {E})/(3*(1-{nu}^2))"

    # determine curve fit accuracy using R² diffs
    # for tau
    sd_tau = np.square(ydata_tau - yfit_tau)
    sd_tau_mean = np.square(ydata_tau - np.mean(ydata_tau))
    T_rsq = 1 - np.sum(sd_tau) / np.sum(sd_tau_mean)
    if T_rsq < 0.9:
        print("WARNING: weak TAU curve fit")

    # for youngs modulus
    sd_E = np.square(ydata_E - yfit_E)
    sd_E_mean = np.square(ydata_E - np.mean(ydata_E))
    E_rsq = 1 - np.sum(sd_E) / np.sum(sd_E_mean)
    if E_rsq < 0.9:
        print("WARNING: weak YOUNGS curve fit")

    # display fit data
    print(f"for data in '{titles[i]}':\nTau = {tau}; R² = {T_rsq}\nE = {E}; R² = {E_rsq}")
    
    # write Tau and youngs values to a text file
    tau_text = f"Tau = {tau}\nR² = {T_rsq}\n"
    E_text = f"E = {E}\nR² = {E_rsq}\n"
    tau_youngs_file.write(f"{titles[i]},{data_category_list[data_category]},{tau},{T_rsq},{E},{E_rsq},{m},{b}\n")

    '''
    PLOTTING THE DATA AND CURVE FIT

        subtract t0 for taus to shift curve left to start at 0,
        subtract by mins dataset for youngs to shift to 0
        mult by 1000000 to account for units being micro
        figure 1 is indiv. plot for each Taus,
        figure 2 is indiv. plot for each Youngs mod,
        figure 3 is combined plot of all sheets in dir for Tau,
        figure 4 is combined plot of all sheets in dir for Youngs mod
    '''
    plt.figure(1, clear=True)
    plt.plot(xdata_tau, ydata_tau*1000000, 'o', label="data", linestyle='')
    plt.plot(xdata_tau, yfit_tau*1000000, '--', label='tau curve fit', color='black')
    plt.plot([], [], ' ', label = tau_text)
    plt.legend(loc='best', prop={'family': 'Arial'})
    plt.xticks(fontsize=14, fontfamily='Arial')
    plt.yticks(fontsize=14, fontfamily='Arial')
    plt.xlabel("Time (" + '$\it{s}$' + ")", fontsize=16, fontfamily='Arial')
    plt.ylabel("Indentation Force " + '$\it{F}$' + u'ᵢ' + " (" + '$\it{μn}$' + ")", fontsize=16, fontfamily='Arial')
    plt.figure(1).savefig(f"indentation_plots/{titles[i]}-TAU-plot.png", bbox_inches='tight', dpi=DPI)

    plt.figure(2, clear=True)
    plt.plot(xdata_E, ydata_E, 'o', label="E data", linestyle='')
    plt.plot(xdata_E, yfit_E, '--', label='E curve fit', color='black')
    plt.plot([], [], ' ', label = E_text)
    plt.legend(loc='best', prop={'family': 'Arial'})
    plt.xticks(fontsize=14, fontfamily='Arial')
    plt.yticks(fontsize=14, fontfamily='Arial')
    plt.xlabel('z-stage (' + '$\it{μn}$' + ')', fontsize=16, fontfamily='Arial')
    plt.ylabel("Indentation Force " + '$\it{F}$' + u'ᵢ' + " (" + '$\it{μn}$' + ")", fontsize=16, fontfamily='Arial')
    plt.figure(2).savefig(f"indentation_plots/{titles[i]}-YOUNGS-plot.png", bbox_inches='tight', dpi=DPI)

    plt.figure(3)
    plt.plot(xdata_tau, ydata_tau*1000000, 'o', label="data", linestyle='')
    plt.plot(xdata_tau, yfit_tau*1000000, '--', label='tau curve fit', color='black')

    plt.figure(4)
    plt.plot(xdata_E, ydata_E, 'o', label="E data", linestyle='')
    plt.plot(xdata_E, yfit_E, '--', label='E curve fit', color='black')
    
    i+=1

# this figure has all indiv sheets plotted onto it
plt.figure(3)
plt.xticks(fontsize=14, fontfamily='Arial')
plt.yticks(fontsize=14, fontfamily='Arial')
plt.xlabel("Time (" + '$\it{s}$' + ")", fontsize=16, fontfamily='Arial')
plt.ylabel("Indentation Force " + '$\it{F}$' + u'ᵢ' + " (" + '$\it{μn}$' + ")", fontsize=16, fontfamily='Arial')
plt.figure(3).savefig("indentation_plots/TAU-multiplot.png", bbox_inches='tight', dpi=DPI)

plt.figure(4)
plt.xticks(fontsize=14, fontfamily='Arial')
plt.yticks(fontsize=14, fontfamily='Arial')
plt.xlabel('z-stage (' + '$\it{μn}$' + ')', fontsize=16, fontfamily='Arial')
plt.ylabel("Indentation Force " + '$\it{F}$' + u'ᵢ' + " (" + '$\it{μn}$' + ")", fontsize=16, fontfamily='Arial')
plt.figure(4).savefig("indentation_plots/YOUNGS-multiplot.png", bbox_inches='tight', dpi=DPI)

# close tau file
tau_youngs_file.close()
