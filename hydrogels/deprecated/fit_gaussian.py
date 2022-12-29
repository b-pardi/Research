

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd

# generate some synthetic data
df = pd.read_csv("fiji_data/PAA intensity profile3.csv")
x = df['Distance_(pixels)'].values[300:650]
y = df['Gray_Value'].values[300:650]
# parameters: mu, sigma, ampl
# p0 = center of peak, bell width, peak height
#x = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
#y = [1,1,2,1,0,2,2,3,1,0,1,-3,-4,-4,-7,-8,-12,-12,-10,-10,-8,-6,-4,-2,0,1,2,1,1,0,1]
#p0=[12,5,-10]
#y = [-1,-1,-2,-1,0,-2,-2,-3,-1,0,1,3,4,4,7,8,12,12,10,10,8,6,4,2,0,-1,-2,-1,-1,0,-1]
#p0=[12,5,10]

def gaussian(x, a, b, c, d):
    return a * np.exp(-(x - b) ** 2 / (2 * c ** 2)) + d
 
# Fit the experimental data to the Gaussian curve
# init params
mean = sum(x * y) / sum(y)
sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
p0 = [max(y), mean, sigma, 0]
params, _ = curve_fit(gaussian, x, y, p0=p0)
print(params)
# Generate a set of x values for the fitted curve
x_fit = np.linspace(x.min(), x.max(), 100)

# Calculate the y values for the fitted curve
y_fit = gaussian(x_fit, *params)
print(y_fit)

# Plot the experimental data and the fitted curve
plt.plot(x, y, 'bo', label='Experimental data')
plt.plot(x_fit, y_fit, 'r', label='Fitted curve')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.show()