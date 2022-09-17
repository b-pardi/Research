#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 22:09:00 2022

@author: joyce
"""

import os
import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import scipy.optimize

# choose directory where files are stored
directory1="C:/Users/Brandon/Documents/00 School Files 00/University/Research/ariell_smith-indentation/indentation_data_noisy/PAA_8.8kpa_S02_L03_C02.xlsx"
lenofdir1 = len(directory1)  # find the length of the directory

directory2="C:/Users/Brandon/Documents/00 School Files 00/University/Research/ariell_smith-indentation/indentation_data2PAA_40kpa_S01_L01_C03..xlsx"
lenofdir2 = len(directory2)  # find the length of the directory



# joins directory with the file name
xls_files1 = glob.glob(os.path.join(directory1, "*.xlsx"))
xls_files2 = glob.glob(os.path.join(directory2, "*.xlsx"))


alldataframes = []  # empty data frame to add all the data to
rSquaredallvals = []
Eallvals1 = []
Eallvals2 = []
filenames = []
Eallvalsaverage = []
avg = []
Eavg = []
EStd = []
stddev = []
R = 0.00159  # [m]
nu = 0.5


def monoExp(x, E):
    return ((4/3) * R**(1/2) * x**(3/2) * E)/(1-nu**2)


for f in xls_files1:
    # reads all excel files and finds zstage column and fn
    df = pd.read_excel(f, usecols=["z-stage (um)", "Fn (uN)"], skiprows=(7))
    max = df["Fn (uN)"].idxmax() # finds the index of the max of fn column
    # takes the first 100 rows of zstage and finds the standard deviation
    stddev = df["Fn (uN)"].iloc[0:500].std()
    dfmax = df.iloc[0:max+1]  # +1 so it includes the final data
    counter = 0  # starts counter at zero
    index = 0  # starts index at zero
    while(counter < 10):
        cur = df.iloc[index]["Fn (uN)"]
        if cur >= stddev * 3:  # if the number is less than or equal to 2 times the standard deviation
            counter += 1
        else:
            counter = 0
        index += 1
    # shifts starting index to the first of the 10 in a row where sd*2 is filfilled
    startIndex = index - 8
    dfFinal = dfmax.iloc[startIndex:]
    dfFinal -= dfmax.iloc[startIndex]  # zeros out the graph
    alldataframes.append(dfFinal)  # adds df to the collective df

    xs = dfFinal["z-stage (um)"]
    ys = dfFinal["Fn (uN)"]

    # perform the fit
    p0 = (0)  # start with values near those we expect
    params, cv = scipy.optimize.curve_fit(monoExp, xs, ys, p0)
    E = params

    # determine quality of the fit
    squaredDiffs = np.square(ys - monoExp(xs, E))
    squaredDiffsFromMean = np.square(ys - np.mean(ys))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    youngsMod = f"Y = ((4/3)*{R}^(1/2) * x^(3/2) {E})/(3*(1-{nu}^2))"

    # inspect the parameters
    print(E)

    filenames.append(f[lenofdir1:-5])
    rSquaredallvals.append(rSquared)
    Eallvals1.append(E[0]) # Append current E to variable
    
alldataframes = []  # empty data frame to add all the data to
rSquaredallvals = []
Eallvals2 = []
filenames = []
Eallvalsaverage = []
avg = []
Eavg = []
EStd = []
stddev = []
R = 0.00159  # [m]
nu = 0.5
    
for f in xls_files2:
    # reads all excel files and finds zstage column and fn
    df = pd.read_excel(f, usecols=["z-stage (um)", "Fn (uN)"],)
    max = df["Fn (uN)"].idxmax() # finds the index of the max of fn column
    # takes the first 100 rows of zstage and finds the standard deviation
    stddev = df["Fn (uN)"].iloc[0:500].std()
    dfmax = df.iloc[0:max+1]  # +1 so it includes the final data
    counter = 0  # starts counter at zero
    index = 0  # starts index at zero
    while(counter < 10):
        cur = df.iloc[index]["Fn (uN)"]
        if cur >= stddev * 3:  # if the number is less than or equal to 2 times the standard deviation
            counter += 1
        else:
            counter = 0
        index += 1
    # shifts starting index to the first of the 10 in a row where sd*2 is filfilled
    startIndex = index - 8
    dfFinal = dfmax.iloc[startIndex:]
    dfFinal -= dfmax.iloc[startIndex]  # zeros out the graph
    alldataframes.append(dfFinal)  # adds df to the collective df

    xs = dfFinal["z-stage (um)"]
    ys = dfFinal["Fn (uN)"]

    # perform the fit
    p0 = (0)  # start with values near those we expect
    params, cv = scipy.optimize.curve_fit(monoExp, xs, ys, p0)
    E = params

    # determine quality of the fit
    squaredDiffs = np.square(ys - monoExp(xs, E))
    squaredDiffsFromMean = np.square(ys - np.mean(ys))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    youngsMod = f"Y = ((4/3)*{R}^(1/2) * x^(3/2) {E})/(3*(1-{nu}^2))"

    # inspect the parameters
    print(E)

    filenames.append(f[lenofdir2:-5])
    rSquaredallvals.append(rSquared)
    Eallvals2.append(E[0]) # Append current E to variable




my_dict = {'soft':Eallvals1, 'stiff': Eallvals2,}

fig,ax = plt.subplots()
ax.boxplot(my_dict.values())
ax.set_xticklabels(my_dict.keys())
ax.set_ylabel("Young's modulus (kPa)",fontsize = 16)
plt.figure(1)
plt.boxplot(my_dict.values())
plt.savefig("YOUNGS-plot")
