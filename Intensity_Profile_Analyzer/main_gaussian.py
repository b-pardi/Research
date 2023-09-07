"""
Author: Brandon Pardi
Created: 12/28/2022, 3:45 pm
Last Modified: 1/4/2022 1:24 pm
"""

import numpy as np
import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

FILE= ""


def set_fp(fp):
    global FILE
    FILE = fp

def set_cols(cols):
    global COLUMNS
    COLUMNS = cols

def set_sheet(sheet):
    global SHEET
    SHEET = sheet

def browse_files(default_dir, btn_title):
    initdir = os.path.join(os.getcwd(), default_dir)
    fp = filedialog.askopenfilename(initialdir=initdir, title=btn_title, filetypes=(
        ("Excel file 2007 and later", "*.xlsx"),
        ("Comma Separated Value files", "*.csv"),
        ("Excel file 1997-2003", "*.xls"),
        ("Text file", "*.txt")
    ))

    return fp

def select_file(label):
    default_fp = 'fiji_data' # local default path
    fp = browse_files(default_fp, 'Select data file')
    label.configure(text=f"File chosen: {os.path.basename(fp)}")
    print(f"*** {fp} Chosen")
    set_fp(fp)

# Get the above variables for use in analysis
def window():
    root = tk.Tk()
    root.title("Data Entry for IPA")
    container = tk.Frame(root)
    container.pack(side='top', fill='both', expand=True)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)

    select_file_label = tk.Label(container, text="Data File")
    select_file_label.grid(row=2, column=0, pady=8)
    select_file_button = tk.Button(container, text="Select Data File", width=15, command=lambda: select_file(select_file_label))
    select_file_button.grid(row=1,column=0,pady=16)

    columns_label = tk.Label(container, text="Enter columns being analyzed\n(separate by a comma i.e. x,y)")
    columns_label.grid(row=3, column=0)
    columns_entry = tk.Entry(container)
    columns_entry.grid(row=4, column=0,pady=(8,16))

    sheet_label = tk.Label(container, text="If your file has multiple sheets,\nindicate which one to analyze here\nelse leave blank")
    sheet_label.grid(row=5, column=0)
    sheet_entry = tk.Entry(container)
    sheet_entry.grid(row=6, column=0,pady=(8,16))

    submit_button = tk.Button(container, text="Submit", width=10, command=lambda: set_and_run(columns_entry, sheet_entry))
    submit_button.grid(row=19, column=0,pady=(16,0))
    close_button = tk.Button(container, text="Close", width=10, command=root.destroy)
    close_button.grid(row=20, column=0, pady=8)

    root.mainloop()

def set_and_run(columns_entry, sheet_entry):
    global FILE
    file = FILE

    columns = columns_entry.get()
    columns = columns.split(',')
    columns = [int(c) for c in columns]

    sheet = sheet_entry.get()
    print(file, columns, sheet)
    analyze_data(file, columns, sheet)


def gaussian(x, a, b, c, d):
    return a * np.exp(-(x - b) ** 2 / (2 * c ** 2)) + d

# function to find array value closest to passed in value
# used to find values in data closes to the results of the curve fit
def find_nearest(array, value):
    array = np.asarray(array)
    index = (np.abs(array - value)).argmin()
    return array[index], index

# grab data
def grab_data(file,sheet):
    _, ext = os.path.splitext(file)
    if sheet == '':
        sheet = None
    print(ext)
    if ext == '.csv':
        df = pd.read_csv(file, sheet)
    elif ext == '.xlsx':
        xlsx = pd.ExcelFile(file)
        df = pd.read_excel(xlsx, sheet)
    else:
        print("\nPlease enter file with valid format\n",
              "valid formats are .csv or .xlsx\n",
              f"found {ext}")
        sys.exit(1)

    return df

def assign_colors(df, columns):
    data_source = df.columns.values[columns[0]-columns[0]%4]
    strain_direction = df.iloc[0,columns[0]-1] # determine if longitudinal or lateral strain measurements
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

def gaussian_analyze(xspan, yspan, xdata):
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
def plot_analyze(data_source, strain_direction, xdata, ydata, color):
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
        
        xfit, yfit, x0_gauss, y0_gauss = gaussian_analyze(xspan, yspan, xdata)

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


def analyze_data(file, columns, sheet):
    df = grab_data(file, sheet)

    print(df)
    color, data_source, strain_direction = assign_colors(df,columns)

    # grab data from sheet into numpy array, while removing na values from end of list
    xdata = df.iloc[2:,columns[0]-1].dropna().values
    ydata = df.iloc[2:,columns[1]-1].dropna().values
    print(xdata,ydata)

    plot_analyze(data_source, strain_direction, xdata, ydata, color)


if __name__ == '__main__':
    window()