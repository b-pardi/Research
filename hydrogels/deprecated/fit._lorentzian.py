import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd

# define the Lorentzian function
def lorentzian(x, x0, gamma, A):
    return A * gamma**2 / ((x - x0)**2 + gamma**2)

# generate some synthetic data
df = pd.read_csv("fiji_data/PAA intensity profile1.csv")
xdata = df['Distance_(pixels)'].values[190:224]
ydata = df['Gray_Value'].values[190:224]

plt.plot(xdata, ydata, 'bo', label='data')
plt.show()

# fit the data to the Lorentzian function
params, cov = curve_fit(lorentzian, xdata, ydata)

# plot the data and the fitted curve
plt.plot(xdata, ydata, 'bo', label='data')
plt.plot(xdata, lorentzian(xdata, params[0], params[1], params[2]), 'r-', label='fit')
plt.legend()
plt.show()