# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 14:53:19 2021

@author: rober
"""

import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import csv

#Import CSV Data
with open("example_data.csv",'r') as i:           #open a file in directory of this script for reading 
    rawdata = list(csv.reader(i,delimiter=","))   #make a list of data in file
    
exampledata = np.array(rawdata[1:],dtype=np.float)    #convert to data array
xs = exampledata[:,0]
ys = exampledata[:,1]/1000000


plt.plot(xs, ys, '.')
plt.title("Original Data")

def monoExp(x, m, t, b):
    return m * np.exp(-t * x) + b

# perform the fit
p0 = (2000, .1, 50) # start with values near those we expect
params, cv = scipy.optimize.curve_fit(monoExp, xs, ys, p0)
m, t, b = params
# 
tauSec = (1 / t)

# determine quality of the fit
squaredDiffs = np.square(ys - monoExp(xs, m, t, b))
squaredDiffsFromMean = np.square(ys - np.mean(ys))
rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
print(f"R² = {rSquared}")

# plot the results
plt.plot(xs, ys, '.', label="data")
plt.plot(xs, monoExp(xs, m, t, b), '--', label="fitted", color='green')
plt.title("Fitted Exponential Curve")
plt.xlabel('Time, t (s)')
plt.ylabel('Normal Force, F (N)')
plt.show()
# inspect the parameters
print(f"Y = {m} * e^(-{t} * x) + {b}")
print(f"Tau = {tauSec} s")

plt.plot(xs, ys, '.', label="data", color='darkorange')


#Extrapolating

#xs2 = np.arange(200)
#ys2 = monoExp(xs2, m, t, b)

plt.plot(xs, ys, '.', label="data")
plt.plot(xs, ys, '--', label="fitted")
plt.xlabel(rawdata[0][0])
plt.ylabel(rawdata[0][1])
plt.title("Extrapolated Exponential Curve")



