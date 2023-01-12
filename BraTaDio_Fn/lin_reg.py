"""
Author: Brandon Pardi
Created: 12/30/2022, 1:53 pm
Last Modified: 1/12/2022, 2:50 pm
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

'''
README

- Data for this script is statistical data curated from the raw input data acquired in 'main.py'
    - see README there for more information

- script begins with various statistical data from 'all_stats_rf/dis.csv'
- For peak frequency values needed for calculation, enter values into 'calibration_peak_frequencies.txt'
    - otherwise indicate in GUI to use theoretical values, theoretical values will be used

- LINEAR REGRESSION
    - x axis is the overtone times its corresponding average change in frequency (n*Df)
        - grabs the average Df values and multiplies each by its respective overtone
        - also grabs the x_err, in this case just the std_dev of the mean
    - y axis is the bandwidth shift Γ of each overtone (f*Dd)/2
        - grabs average peak frequency and average change in dissipation values from calibration/theoretical data, and stats csv respectively
            - note, frequency here refers to NOT baseline corrected frequency as it does in the x axis
        - calculates bandwidth defined above
        - propogates error of this calculation
    - for x and y, values are grouped by ranges, and then data sources
        - values are averaged across multiple experimental data sets, based on the range
        - these averages are also propogated and the error calculated becomes the error bars in the plot
    - plots the values with error bars and shows equation with slope
    - NEED FORMULAS FOR Calculates G prime and JF (frequency dependent shear film compliance)
    
'''

# pass in 3 dimensional array of data values
    # inner most arrays are of individual values [val_x1, val_x2, ... val_xn]
    # mid level arrays are pairs of each component [val_x, stddex_x], [val_y, stddev_y], [...], ...
    # outer array is a list of these pairs [pair_x, pair_y, ...]
# returns propogated error of set of mean data
def propogate_mult_err(val, data):
    comp = 0
    for pair in data:
        temp = ( pair[1] / pair[0] ) # divide err by val
        temp = [float(x) for x in temp] # ensure correct data type of all vals in innermost array
        temp = np.power(temp, 2)
        comp += temp

    err = val * np.sqrt( comp )
    return (err)

# pass in an array of mean values,
# 2d array of err vals where the ith inner err array correlates to the ith mean value
# n_vals is how many err vals each mean has
# n_means is how many means will be propogated (essentially number of overtones)
def propogate_mean_err(means, errs, n_vals):
    n_means = len(means)
    comp = 0
    sigmas = []
    # the new error is the square root of the sum of the squares of the errors and divide it by n_vals
    for i in range(n_means):
        for j in range(n_vals):
            comp += np.power( ( errs[j][i] ), 2 )
        res = np.sqrt( comp/( n_vals-1 ) )
        sigmas.append(res)

    return sigmas

def linear(x, m, b):
    return m * x + b

def linear_regression():
    print("Performing linear analysis...")

    # grab statistical data of overtones from files generated in interactive plot
    rf_df = pd.read_csv("selected_ranges/all_stats_rf.csv", index_col=0)
    dis_df = pd.read_csv("selected_ranges/all_stats_dis.csv", index_col=0)

    # grab all unique labels from dataset
    labels = rf_df['range_used'].unique()
    sources = rf_df['data_source'].unique()
    print(f"*** found labels: {labels}\n\t from sources: {sources}\n")

    # grab peak frequency values from either theoretical or calibration file as specified in gui
    with open("calibration_data/peak_frequencies.txt", 'r') as peak_file:
        freqs = peak_file.readlines()
        # grab freqs from peak freq list and converts them to a 2D numpy array of float values
        freqs = [[float(freq.split()[i].strip('\"')) for i in range(len(freqs[0].split()))] for freq in freqs]
        #freqs = np.asarray([np.asarray(freq_list) for freq_list in freqs])
        calibration_freq = np.asarray([np.average(freq) for freq in freqs])
        sigma_calibration_freq = np.asarray([np.std(freq) for freq in freqs])
        print(f"*** peak frequencies: {calibration_freq}; sigma_peak_freq: {sigma_calibration_freq};\n")

    # grab and analyze data for each range and indicated by the label
    for label in labels:
        # plot will be mean of bandwidth shift vs overtone * mean of change in frequency
        # grab and calculate x values
        rf_df_ranges = rf_df.loc[rf_df['range_used'] == label]

        # group data by range and then source
        # values get averaged across sources respective to their range
        # i.e. average( <num from range 'x' source1>, <num from range 'x' source2>, ... )
        delta_freqs = []
        sigma_delta_freqs = []
        for source in sources: # grabs data grouped by label and further groups into source
            rf_df_range = rf_df_ranges.loc[rf_df_ranges['data_source'] == source]
            delta_freqs.append(rf_df_range['Dfreq_mean'].values)
            sigma_delta_freqs.append(rf_df_range['Dfreq_std_dev'].values)
        
        # take average described above
        n_srcs = len(sources) # num sources -> number of ranges used for average
        mean_delta_freqs = np.zeros(delta_freqs[0].shape)
        for i in range(n_srcs):
            mean_delta_freqs += delta_freqs[i]

        mean_delta_freqs /= n_srcs
        n_mean_delta_freqs = [Df * (2*i+1) for i, Df in enumerate(mean_delta_freqs)] # 2i+1 corresponds to overtone number
        sigma_n_mean_delta_freqs = propogate_mean_err(mean_delta_freqs, sigma_delta_freqs, n_srcs)
        
        print(f"*** rf for label: {label}\n\tn*means: {n_mean_delta_freqs}\n\tstddev: {sigma_n_mean_delta_freqs}\n")

        # grab and calculate y values and propogate err (same process as frequency)
        dis_df_ranges = dis_df.loc[dis_df['range_used'] == label]
        delta_dis = []
        sigma_delta_dis = []
        for source in sources: # grab vals
            dis_df_range = dis_df_ranges.loc[dis_df_ranges['data_source'] == source]
            delta_dis.append(dis_df_range['Ddis_mean'].values)
            sigma_delta_dis.append(dis_df_range['Ddis_std_dev'].values)
        
        # avg and propogate vals
        mean_delta_dis = np.zeros(delta_dis[0].shape)
        for i in range(n_srcs):
            mean_delta_dis += delta_dis[i]

        mean_delta_dis /= n_srcs
        sigma_mean_delta_dis = propogate_mean_err(mean_delta_dis, sigma_delta_dis, n_srcs)

        print(f"*** dis for label: {label}:\n\tn*means: {mean_delta_dis}\n\tstddev: {sigma_mean_delta_dis}\n")
        
        # calculate bandwidth shift and propogate error for this calculation
        data = [[mean_delta_dis, sigma_mean_delta_dis], [calibration_freq, sigma_calibration_freq]]
        delta_gamma = mean_delta_dis * calibration_freq / 2 # bandwidth shift, Γ
        sigma_delta_gamma = propogate_mult_err(delta_gamma, data)

        print(f"*** for label: {label}: \n\tdelta_gamma: {delta_gamma}; sigma_delta_gamma: {sigma_delta_gamma}\n")

        # performing the linear fit
        params, cov = curve_fit(linear, n_mean_delta_freqs, delta_gamma)
        m, b = params
        sign = '-' if b < 0 else '+'

        # setup plot
        lin_plot = plt.figure()
        plt.subplots_adjust(hspace=0.4)
        ax = lin_plot.add_subplot(1,1,1)

        # plot data
        ax.plot(n_mean_delta_freqs, delta_gamma, 'o', markersize=8, label=f'average values for range: {label}')
        ax.errorbar(n_mean_delta_freqs, delta_gamma, xerr=sigma_n_mean_delta_freqs, yerr=sigma_delta_gamma, fmt='.', label='error in calculations')
        
        # plot curve fit
        y_fit = linear(np.asarray(n_mean_delta_freqs), m, b)
        ax.plot(n_mean_delta_freqs, y_fit, 'r', label=f'Linear fit:\ny = {m:.4f}x {sign} {np.abs(b):.4f}')

        # format plot
        plt.sca(ax)
        plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.3)
        plt.xticks(fontsize=14, fontfamily='Arial')
        plt.yticks(fontsize=14, fontfamily='Arial')
        plt.xlabel(r"overtone * change in frequency, $\it{nΔf_n}$ (Hz)", fontsize=16, fontfamily='Arial')
        plt.ylabel(r"Bandwidth Shift, $\mathit{\Gamma}$$_n$", fontsize=16, fontfamily='Arial')
        plt.title(f"Bandwidth Shift vs N * Change in Frequency\nfor range: {label}", fontsize=16, fontfamily='Arial')
        
        # save figure
        lin_plot.tight_layout() # fixes issue of graph being cut off on the edges when displaying/saving
        plt.savefig(f"qcmd-plots/modeling/lin_regression_range_{label}", bbox_inches='tight', dpi=200)
    

if __name__ == "__main__":
    linear_regression()