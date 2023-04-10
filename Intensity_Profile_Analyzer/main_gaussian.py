"""
Author: Brandon Pardi
Created: 12/28/2022, 3:45 pm
Last Modified: 1/4/2022 1:24 pm
"""

import numpy as np
import pandas as pd
import os
import sys
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

# path to where folder is located, copy from file explorer window
# make sure not to delete the 'r' here when updating data file path
#           ↓
FILE_PATH = r"C:\Users\Brandon\Documents\00 School Files 00\University\Research\Intensity_Profile_Analyzer\fiji_data" 
FILE_NAME = "2022_12_30_example of stiff Poisson ratio_ BP.xlsx" # specify file (with extension) to be opened
COLUMNS = (3,4) # specify which column in the file are being analyzed
SHEET = 'Sheet2' # if file has multiple sheets, indicate here, else leave blank

def gaussian(x, a, b, c, d):
    return a * np.exp(-(x - b) ** 2 / (2 * c ** 2)) + d

# function to find array value closest to passed in value
# used to find values in data closes to the results of the curve fit
def find_nearest(array, value):
    array = np.asarray(array)
    index = (np.abs(array - value)).argmin()
    return array[index], index

# grab data
def grab_data(file):
    _, ext = os.path.splitext(file)
    global SHEET
    if SHEET == '':
        SHEET = None
    print(ext)
    if ext == '.csv':
        df = pd.read_csv(file, SHEET)
    elif ext == '.xlsx':
        xlsx = pd.ExcelFile(file)
        df = pd.read_excel(xlsx, SHEET)
    else:
        print("\nPlease enter file with valid format\n",
              "valid formats are .csv or .xlsx\n",
              f"found {ext}")
        sys.exit(1)

    return df

def assign_colors(df):
    data_source = df.columns.values[COLUMNS[0]-COLUMNS[0]%4]
    strain_direction = df.iloc[0,COLUMNS[0]-1] # determine if longitudinal or lateral strain measurements
    print(f"{data_source} - {strain_direction}")

    color = ('','') # assign color values depending on strain direction
    if strain_direction == 'width':
        # lighter and darker colors for raw and zoomed data
        color = ('#6495ED','#4169E1') # oranges
    elif strain_direction == 'length':
        color = ('#FA8128','#C95B0C') # blues

    return color, data_source, strain_direction

# plot formatting
def format_plot(data_source, strain_direction):
    # declare plot and subplots
    span_plot = plt.figure()
    plt.subplots_adjust(hspace=0.4)
    span_plot.set_figwidth(10)
    span_plot.set_figheight(6)
    ax = span_plot.add_subplot(1,1,1) # the 'big' subplot for shared axis
    span_ax = span_plot.add_subplot(2,1,1) # main plot data
    zoom_ax = span_plot.add_subplot(2,1,2) # zoomed data and fit

    # formatting and labels
    span_ax.set_title(f"Pixel Intensity of Hydrogel img: {data_source}\nClick and drag to select range")
    zoom_ax.set_title("\nSelection Data", fontsize=16, fontfamily='Arial')
    plt.sca(span_ax)
    plt.xticks(fontsize=12, fontfamily='Arial')
    plt.yticks(fontsize=12, fontfamily='Arial')
    plt.sca(zoom_ax)
    plt.xticks(fontsize=12, fontfamily='Arial')
    plt.yticks(fontsize=12, fontfamily='Arial')

    # Turn off axis lines and ticks of the big subplot
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)

    # Set common labels
    ax.set_xlabel(f"{strain_direction.title()} distance, (px)", fontsize=16, fontfamily='Arial')
    ax.set_ylabel("Brightness Intensity Value, " + "$\it{I}$" + " (AR U)", fontsize=16, fontfamily='Arial', labelpad=15)

    return span_plot, ax, span_ax, zoom_ax

def gaussian_analyze(xspan, yspan):
    # initial paramaters for gaussian fit
    mean = sum(xspan * yspan) / sum(yspan)
    sigma = np.sqrt(sum(yspan * (xspan - mean) ** 2) / sum(yspan))
    p0 = [max(yspan), mean, sigma, 0]

    # perform curve fit on specified range
    params, covariance = curve_fit(gaussian, xspan, yspan, p0=p0)
    #print(f"Gauss fit paramaters: {params}")

    # generate data for a smooth curve for this fit
    # note: xdata is input so we use it also for the fit data
    xfit = np.linspace(np.min(xdata), np.max(xdata), 1000)
    yfit = gaussian(xfit, *params)

    # grab applicable data from fit
    x0_gauss, x0_ind_gauss = find_nearest(xspan, params[1]) # xpoint in data closest to curves peak
    y0_gauss = yspan[x0_ind_gauss]
    print(f"*** Gaussian Fit method: x0 - {x0_gauss}; y0 - {y0_gauss} ***")

    return xfit, yfit, x0_gauss, y0_gauss

def avg_min(xspan, yspan):
    # alternative method of finding min point, grouping and averaging
    mins = np.partition(yspan, 4)[0:5]
    avg_min_val = mins.mean() # multiple occurences of this may occur in list
    y0_avg, _ = find_nearest(yspan, avg_min_val)
    
    # take median value of all occurences of the found average
    y0_avg_indices = np.where(yspan==y0_avg)[0]
    y0_avg_ind = int(np.median(y0_avg_indices))
    x0_avg = xspan[y0_avg_ind]

    print(f"*** Average Values method: x0 - {x0_avg}; y0 - {y0_avg} ***\n")

    return x0_avg, y0_avg


# set up plots
def plot_analyze(data_source, strain_direction):
    span_plot, ax, span_ax, zoom_ax = format_plot(data_source, strain_direction)
    
    # plotting the data
    raw_plot, = span_ax.plot(xdata, ydata, '.', color=color[0], markersize=1, label='raw intensity data')
    zoom_plot, = zoom_ax.plot(xdata, ydata, '.', color=color[1], markersize=2, label='spanned intensity data')

    # function called by span selector when a selection is made
    # is given the min and max from the span selected, and returns void
    def onselect(xmin, xmax):
        zoom_ax.clear()
        zoom_ax.set_title("\nSelection Data", fontsize=16, fontfamily='Arial')
        plt.sca(zoom_ax)
        plt.xticks(fontsize=12, fontfamily='Arial')
        plt.yticks(fontsize=12, fontfamily='Arial')

        # find indices of data points corresponding to selection
        imin, imax = np.searchsorted(xdata, (xmin, xmax))
        imax = min(len(xdata)-1, imax)

        # grab data corresponding to that region
        xspan = xdata[imin:imax]
        yspan = ydata[imin:imax]

        # plot the newly specified range
        zoom_ax.plot(xspan, yspan, '.', color=color[1], markersize=4, label='spanned intensity data')
        
        xfit, yfit, x0_gauss, y0_gauss = gaussian_analyze(xspan, yspan)

        # plot the fit data on top of the zoomed plot
        zoom_ax.plot(xfit, yfit, 'black', label='gaussian fit')
        
        x0_avg, y0_avg = avg_min(xspan, yspan)

        # plot the different found min points
        zoom_ax.scatter(x=x0_gauss, y=y0_gauss, c='red', label=f'gaussian minima: {x0_gauss}, {y0_gauss}', zorder=4)
        zoom_ax.scatter(x=x0_avg, y=y0_avg, c='purple', label=f'average minima: {x0_avg}, {y0_avg}', zorder=5)

        # set limits so plot is zoomed to fit
        zoom_ax.set_xlim(xspan.min()-5, xspan.max()+5)
        zoom_ax.set_ylim(min(yspan.min(),yfit.min())-5, max(yspan.max(), yfit.max())+5)
        plt.legend()
        span_plot.canvas.draw_idle()
        
    # Add the span selector widget
    span = SpanSelector(span_ax, onselect, 'horizontal', useblit=True, interactive=True,
                        props=dict(alpha=0.3, facecolor='gray'))

    plt.show()


if __name__ == '__main__':
    #FILE_PATH = FILE_PATH.replace('\\', '/')
    print(FILE_PATH)
    file = os.path.join(FILE_PATH, FILE_NAME)
    df = grab_data(file)
    color, data_source, strain_direction = assign_colors(df)

    # grab data from sheet into numpy array, while removing na values from end of list
    xdata = df.iloc[2:,COLUMNS[0]-1].dropna().values
    ydata = df.iloc[2:,COLUMNS[1]-1].dropna().values

    plot_analyze(data_source, strain_direction)