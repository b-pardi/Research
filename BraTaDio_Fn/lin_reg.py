"""
Author: Brandon Pardi
Created: 12/30/2022, 1:53 pm
Last Modified: 1/12/2022, 2:50 pm
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


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
        if n_vals == 1:
            sigmas.append(np.sqrt(comp))
        else:
            sigmas.append(np.sqrt( comp/( n_vals-1 ) ))

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
        print(label, data)
        delta_gamma = mean_delta_dis * calibration_freq / 2 # bandwidth shift, Γ
        sigma_delta_gamma = propogate_mult_err(delta_gamma, data)

        print(f"*** for label: {label}: \n\tdelta_gamma: {delta_gamma}; sigma_delta_gamma: {sigma_delta_gamma}\n")

        # performing the linear fit
        params, cov = curve_fit(linear, n_mean_delta_freqs, delta_gamma)
        m, b = params
        sign = '-' if b < 0 else '+'

        # setup plot
        plt.rc('text', usetex=True)
        plt.rc('font', family='Arial')
        plt.rc('font', family='sans-serif')
        plt.rc('mathtext', fontset='stix', rm='serif')
        plt.rc('\DeclareUnicodeCharacter{0394}{\ensuremath{\Delta}}')
        plt.rc('\DeclareUnicodeCharacter{0398}{\ensuremath{\Gamma}}')
        lin_plot = plt.figure()
        plt.clf()
        plt.subplots_adjust(hspace=0.4)
        ax = lin_plot.add_subplot(1,1,1)
        plt.cla()

        # plot data
        ax.plot(n_mean_delta_freqs, delta_gamma, 'o', markersize=8, label=f'average values for range: {label}')
        ax.errorbar(n_mean_delta_freqs, delta_gamma, xerr=sigma_n_mean_delta_freqs, yerr=sigma_delta_gamma, fmt='.', label='error in calculations')
        
        # calculate linear fit data
        y_fit = linear(np.asarray(n_mean_delta_freqs), m, b)

        # shear compliance
        #shear_comp = -(b/(2*np.pi*5*1))*10^-3
        #print(shear_comp)

        # determine quality of the fit
        squaredDiffs = np.square(delta_gamma - y_fit)
        squaredDiffsFromMean = np.square(delta_gamma - np.mean(delta_gamma))
        rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
        print(f"R² = {rSquared}")

        # plot curve fit
        ax.plot(n_mean_delta_freqs, y_fit, 'r', label=f'Linear fit:\ny = {m:.4f}x {sign} {np.abs(b):.4f}\nrsq = {rSquared:.4f}')

        # format plot
        plt.sca(ax)
        plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.3)
        plt.xticks(fontsize=14, fontfamily='Arial')
        plt.yticks(fontsize=14, fontfamily='Arial') 
        plt.xlabel(r"Overtone * Change in frequency, $\mathit{n\Delta}$$\mathit{f}$$_n$ (Hz)", fontsize=16, fontfamily='Arial')
        plt.ylabel(r"Bandwidth shift, $\mathit{\Gamma}$$_n$", fontsize=16, fontfamily='Arial')
        plt.title(f"Bandwidth Shift vs N * Change in Frequency\nfor range: {label}", fontsize=16, fontfamily='Arial')

        # save figure
        lin_plot.tight_layout() # fixes issue of graph being cut off on the edges when displaying/saving
        plt.savefig(f"qcmd-plots/modeling/lin_regression_range_{label}", bbox_inches='tight', dpi=200)
        plt.rc('text', usetex=False)

if __name__ == "__main__":
    linear_regression()