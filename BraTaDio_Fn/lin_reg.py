"""
Author: Brandon Pardi
Created: 12/30/2022, 1:53 pm
Last Modified: 1/4/2022, 3:17 pm
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
- grabs data into data frame and Transposes it for easier readability
- For peak frequency values needed for calculation, enter values into 'calibration_peak_frequencies.txt'
    - otherwise indicate in GUI to use theoretical values, theoretical values will be used

- LINEAR REGRESSION
    - x axis is the overtone times its corresponding average change in frequency (n*Df)
        - grabs the average Df values and multiplies each by its respective overtone
        - also grabs the x_err, in this case just the std_dev of the mean
    - y axis is the bandwidth shift Γ of each overtone (f*Dd)/2
        - grabs average frequency and average change in dissipation values from csv
            - note, frequency here refers to NOT baseline corrected frequency as it does in the x axis
        - calculates bandwidth defined above
        - propogates error of this calculation
    - plots the values with error bars
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


def linear(x, m, b):
    return m * x + b

def linear_regression():
    print("Performing linear plots...")

    # grab statistical data of overtones from files generated in interactive plot
    rf_df = pd.read_csv("selected_ranges/all_stats_rf.csv", index_col=0)
    dis_df = pd.read_csv("selected_ranges/all_stats_dis.csv", index_col=0)

    # grab all unique labels from dataset
    labels = rf_df['range_used'].unique()
    print(labels)

    # grab peak frequency values from either theoretical or calibration file as specified in gui
    with open("calibration_data/peak_frequencies.txt", 'r') as peak_file:
        freqs = peak_file.readlines()
        # grab freqs from peak freq list and converts them to a 2D numpy array of float values
        freqs = [[float(freq.split()[i].strip('\"')) for i in range(len(freqs[0].split()))] for freq in freqs]
        #freqs = np.asarray([np.asarray(freq_list) for freq_list in freqs])
        calibration_freq = np.asarray([np.average(freq) for freq in freqs])
        sigma_calibration_freq = np.asarray([np.std(freq) for freq in freqs])

    # grab and analyze data for each range and indicated by the label
    for label in labels:
        # plot will be mean of bandwidth shift vs overtone * mean of change in frequency
        # grab and calculate x values
        rf_df_range = rf_df.loc[rf_df['range_used'] == label]
        mean_delta_freq = rf_df_range['Dfreq_mean'].values
        n_mean_delta_freq = [Df * (2*i+1) for i, Df in enumerate(mean_delta_freq)] # 2i+1 corresponds to overtone number
        sigma_n_mean_delta_freq = rf_df_range['Dfreq_std_dev'].values
        print(f"*** rf for label: {label}:\n\tn*means: {n_mean_delta_freq}\n\tstddev: {sigma_n_mean_delta_freq}\n")

        # grab and calculate y values and propogate err
        dis_df_range = dis_df.loc[dis_df['range_used'] == label]
        mean_delta_dis = dis_df_range['Ddis_mean'].values
        sigma_mean_delta_dis = dis_df_range['Ddis_std_dev'].values
        print(f"*** df for label: {label}:\n\tn*means: {mean_delta_dis}\n\tstddev: {sigma_mean_delta_dis}\n")
        
        # calculate bandwidth shift and propogate error for this calculation
        data = [[mean_delta_dis, sigma_mean_delta_dis], [calibration_freq, sigma_calibration_freq]]
        print(data)
        delta_gamma = mean_delta_dis * calibration_freq / 2 # bandwidth shift, Γ
        sigma_delta_gamma = propogate_mult_err(delta_gamma, data)

        # print to verify results
        print(f"\tn_mean_delta_freq: {n_mean_delta_freq}; sigma_n_mean_delta_freq: {sigma_n_mean_delta_freq};\n\
        mean_delta_dis: {mean_delta_dis}; sigma_mean_delta_dis: {sigma_mean_delta_dis};\n\
        mean_freq: {calibration_freq}; sigma_peak_freq: {sigma_calibration_freq};\n\
        delta_gamma: {delta_gamma}; sigma_delta_gamma: {sigma_delta_gamma};")

        # performing the linear fit
        params, cov = curve_fit(linear, n_mean_delta_freq, delta_gamma)
        m, b = params

        # plot data
        lin_plot = plt.figure()
        plt.subplots_adjust(hspace=0.4)
        ax = lin_plot.add_subplot(1,1,1)
        ax.plot(n_mean_delta_freq, delta_gamma, 'o', markersize=8, label='data')
        ax.errorbar(n_mean_delta_freq, delta_gamma, xerr=sigma_n_mean_delta_freq, yerr=sigma_delta_gamma, fmt='.', label='err')
        
        # plot curve fit
        y_fit = linear(np.asarray(n_mean_delta_freq), m, b)
        ax.plot(n_mean_delta_freq, y_fit, 'r', label='linear fit')

        # format plot
        plt.sca(ax)
        plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.3)
        plt.xticks(fontsize=14, fontfamily='Arial')
        plt.yticks(fontsize=14, fontfamily='Arial')
        plt.xlabel(r"overtone * change in frequency, $\it{nΔf_n}$ (Hz)", fontsize=16, fontfamily='Arial')
        plt.ylabel(r"Bandwidth Shift, $\mathit{\Gamma}$$_n$", fontsize=16, fontfamily='Arial')
        plt.title("<placeholder title>", fontsize=16, fontfamily='Arial')
        
        lin_plot.tight_layout()
        plt.show()
    

if __name__ == "__main__":
    linear_regression()