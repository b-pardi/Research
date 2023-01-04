import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

'''
In the Lorentzian function, x is the indep. variable, x0 represents the center of the peak,
and gamma represents the half-width at half-maximum (HWHM) of the peak.
'''
def lorentzian(x, A, x0, gamma):
    return A * gamma**2 / (gamma**2 + (x - x0)**2)

# grab data
df = pd.read_csv("fiji_data/PAA intensity profile3.csv")
xdata = df['Distance_(pixels)'].values
xdata = xdata - xdata.min()
ydata = df['Gray_Value'].values
ydata = ydata - ydata.min()


# set up plots
span_plot = plt.figure()
span_plot.set_figwidth(10)
span_plot.set_figheight(6)
span_ax = span_plot.add_subplot(2,1,1) # main plot data
zoom_ax = span_plot.add_subplot(2,1,2) # zoomed data and fit
span_ax.set_title("Click and drag to select range")

# plotting the data
raw_plot, = span_ax.plot(xdata, ydata, '.', color='green', markersize=1, label='raw intensity data')
zoom_plot, = zoom_ax.plot(xdata, ydata, '.', color='green', markersize=2, label='spanned intensity data')

# function called by span selector when a selection is made
# is given the min and max from the span selected, and returns void
def onselect(xmin, xmax):
    # find indices of data points corresponding to selection
    imin, imax = np.searchsorted(xdata, (xmin, xmax))
    imax = min(len(xdata)-1, imax)

    # grab data corresponding to that region
    xspan = xdata[imin:imax]
    yspan = ydata[imin:imax]
    xspan = xspan - xspan.min()
    yspan = yspan - yspan.min()

    # plot the newly specified range
    zoom_plot.set_data(xspan, yspan)

    # perform curve fit on specified range
    params, covariance = curve_fit(lorentzian, xspan, yspan, p0=[-10,0,-1])
    A, x0, gamma = params
    print(f"A: {A}; x0: {x0}; HW@HM: {gamma}")

    # generate data for a smooth curve for this fit
    # note: xdata is input so we use it also for the fit data
    xfit = np.linspace(np.min(xdata), np.max(xdata), 1000)
    yfit = lorentzian(xfit, A, x0, gamma)


    # plot the fit data on top of the zoomed plot
    zoom_ax.plot(xfit, yfit, 'r-', label='Lorentzian fit')
    
    # set limits so plot is zoomed to fit
    zoom_ax.set_xlim(xspan.min(), xspan.max())
    zoom_ax.set_ylim(yspan.min(), yspan.max())
    span_plot.canvas.draw_idle()

    # plt.draw()


# Add the span selector widget
span = SpanSelector(span_ax, onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.3, facecolor='gray'))

plt.show()