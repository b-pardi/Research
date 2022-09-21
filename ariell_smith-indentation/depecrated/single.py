from pickletools import optimize
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path
import sys

df= pd.read_excel("indentation_data1/8.8kPa_S03_L01.Cycle0001.xls.xlsx", skiprows=0)
# only need time and force columns
fvt_df = df[['time(seconds)', 'Fn (uN)']]

# some entries contained 'na' for time so they will be removed
print(fvt_df.isna())
fvt_df = fvt_df.dropna(axis=0, how='any', inplace=False)

# account for units being micro
pd.options.mode.chained_assignment = None
fvt_df.loc[:,'Fn (uN)'] /= 1000000
pd.options.mode.chained_assignment = 'warn'

temp_df = fvt_df[fvt_df['time(seconds)'].apply(lambda x: isinstance(x, str))]
if (temp_df.size > 0):
    fvt_df = fvt_df.drop(fvt_df.index[temp_df.index])
fvt_df = fvt_df.astype(float)

# find the start of the curve (point of greatest force)
max_force = fvt_df['Fn (uN)'].max()
max_force_ind = fvt_df[fvt_df['Fn (uN)'] == max_force].index

# find 60 seconds after max force point
t0 = fvt_df.loc[fvt_df['Fn (uN)'] == max_force, 'time(seconds)'].values[0]
tf = t0 + 60

# only need values to the right of max force point,
# and left of 60 seconds after max force point
fvt_df = fvt_df[max_force_ind[0]:]
fvt_df = fvt_df.drop(fvt_df[fvt_df['time(seconds)'] > tf].index)
fvt_df = fvt_df.reset_index(drop=True)
print(fvt_df.head())
print(fvt_df.tail())
xdata = fvt_df['time(seconds)']
ydata = fvt_df['Fn (uN)']

# curve to fit
def monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b

# estimate of expected initial values
p0 = (2000, .1, 50)
# fit the curve, returns tuple with optimized parameters and covariance matrix
params, cv = curve_fit(monoExp, xdata, ydata, p0)
print(params)
m, t, b = params
tau = 1 / t
print(tau)
yfit = monoExp(xdata, m, t, b)

# determine curve fit accuracy using R² diffs
sd = np.square(ydata - yfit)
sd_mean = np.square(ydata-np.mean(ydata))
rsq = 1 - np.sum(sd) / np.sum(sd_mean)
print(f"R² = {rsq}")

# subtract t0 to shift curve left to start at 0
ax = plt.plot(xdata-t0, ydata, label="data")
ax = plt.plot(xdata-t0, yfit, '--', label='curve fit', color='black')
plt.xlabel('Time (s)')
plt.ylabel('Force (μn)')
plt.savefig("plot.png")
plt.show()
ax = plt.clf()
ax = fvt_df['Fn (uN)'].plot(kind = 'box',figsize=(6,6))
#plt.show()
plt.savefig("box.png")