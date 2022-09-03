"""
Author: Brandon Pardi
Created: 6/22/2022, 3:56 pm
Last Modified: 6/27/2022 10:31 am
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.optimize import curve_fit
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
- currently generates individual plots for each sheet, one figure with each data set plotted and color coded,
one figure with all data from all sheets in one BIG plot, and a box and whisker plot of Tau values from each sheet
- fits curve for each individual plot along with getting R^2 and Tau values

WIP
- none
"""

# TIME PARAMETER FOR LENGTH OF CURVE, data this long after curve start will be removed
curve_time = 60
# pixel density of plots, higher number -> more detail and more memory
# if program running slow, lower to ~80
DPI = 320

# find sheets in path, concat into 1 large data frame
data_path = Path.joinpath(Path.cwd(), "indentation_data1")
sheets = [file for file in data_path.iterdir() if file.suffix == ".xlsx"]

# check file grabbing
for sheet in sheets:
    assert os.path.isfile(sheet)

dfs = [pd.read_excel(file, skiprows=0) for file in sheets]
titles = []
scrubbed_dfs = []
taus = []
i = 0
for path in sheets:
    titles.append(os.path.basename(path))

# curve to fit
def monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b
# estimate of expected initial values
p0 = (2000, .1, 50)

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
    max_force = fvt_df['Fn (uN)'].max()
    max_force_ind = fvt_df[fvt_df['Fn (uN)'] == max_force].index

    # find 60 seconds after max force point
    t0 = fvt_df.loc[fvt_df['Fn (uN)'] == max_force, 'time(seconds)'].values[0]
    tf = t0 + curve_time

    # only need values to the right of max force point,
    # and left of 60 seconds after max force point
    fvt_df = fvt_df[max_force_ind[0]:]
    fvt_df = fvt_df.drop(fvt_df[fvt_df['time(seconds)'] > tf].index)
    fvt_df = fvt_df.reset_index(drop=True)

    xdata = fvt_df['time(seconds)']
    ydata = fvt_df['Fn (uN)']

    params, cv = curve_fit(monoExp, xdata, ydata, p0)
    m, t, b = params
    tau = 1 / t
    taus.append(tau)
    yfit = monoExp(xdata, m, t, b)

    # determine curve fit accuracy using R² diffs
    sd = np.square(ydata - yfit)
    sd_mean = np.square(ydata-np.mean(ydata))
    rsq = 1 - np.sum(sd) / np.sum(sd_mean)
    print(f"for data in '{titles[i]}':\nTau = {tau}\nR² = {rsq}")
    if rsq < 0.9:
        print("WARNING: weak curve fit")

    # PLOTTING THE DATA AND CURVE FIT
    # subtract t0 to shift curve left to start at 0,
    # mult by 1000000 to account for units being micro
    plt.figure(1, clear=True)
    plt.plot(xdata-t0, ydata*1000000, label="data")
    plt.plot(xdata-t0, yfit*1000000, '--', label='curve fit', color='black')
    text = f"R² = {rsq}\nTau = {tau}"
    plt.plot([], [], ' ', label = text)
    plt.legend(loc='upper right')
    plt.xlabel('Time (s)')
    plt.ylabel('Force (μn)')
    plt.figure(1).savefig(f"indentation_plots/{titles[i]}-plot.png", dpi=DPI)
    plt.figure(2)
    plt.plot(xdata-t0, ydata*1000000, label="data") 
    plt.plot(xdata-t0, yfit*1000000, '--', label='curve fit', color='black')
    scrubbed_dfs.append(fvt_df)
    i+=1

# this figure has all indiv sheets plotted onto it
plt.figure(2).savefig("indentation_plots/multiplot.png", dpi=DPI)

# Large dataframe of all data in sheets
comb_df = pd.concat(scrubbed_dfs)
temp_df = comb_df[comb_df['time(seconds)'].apply(lambda x: isinstance(x, str))]
if (temp_df.size > 0):
    comb_df = comb_df.drop(comb_df.index[temp_df.index])
comb_df = comb_df.sort_values(by='time(seconds)')
comb_df = comb_df.dropna().reset_index(drop=True)
xdata = comb_df['time(seconds)']
ydata = comb_df['Fn (uN)']
print(comb_df.head())
print(comb_df.tail())

# plots ALL data at once (not super useful with current sample data)
plt.figure(3)
plt.plot(xdata-t0, ydata*1000000, label="data")
plt.xlabel('Time (s)')
plt.ylabel('Force (μn)')
plt.figure(3).savefig("indentation_plots/BIGplot.png", dpi=DPI)

# box and whisker plot for Tau values
plt.figure(4)
plt.boxplot(taus, vert=True)
plt.figure(4).savefig("indentation_plots/Taus_BnW.png", dpi=DPI)