"""
Author: Brandon Pardi
Created: 12/30/2022, 1:53 pm
Last Modified: 1/4/2022, 3:17 pm
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

'''
README

- Data for this script is statistical data curated from the raw input data acquired in 'main.py'
    - see README there for more information

- script begins with various statistical data from 'all_stats_rf/dis.csv'
- grabs data into data frame and Transposes it for easier readability

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

def linear_regression():
    print("Performing linear plots...")

    # grab statistical data of overtones from files generated in interactive plot
    rf_df = pd.read_csv("selected_ranges/all_stats_rf.csv", index_col=0).transpose()
    dis_df = pd.read_csv("selected_ranges/all_stats_dis.csv", index_col=0).transpose()

    print(rf_df.head())
    print(dis_df.head())

    # plot will be mean of bandwidth shift vs overtone * mean of change in frequency
    # grab and calculate x values
    mean_delta_freq = rf_df.loc['Dfreq_mean'].values
    n_mean_delta_freq = [Df * (2*i+1) for i, Df in enumerate(mean_delta_freq)] # 2i+1 corresponds to overtone number
    sigma_n_mean_delta_freq = rf_df.loc['Dfreq_std_dev']

    # grab and calculate y values and propogate err
    mean_delta_dis = dis_df.loc['Ddis_mean'].values
    sigma_mean_delta_dis = dis_df.loc['Ddis_std_dev'].values
    mean_freq = rf_df.loc['freq_mean'].values
    sigma_mean_freq = rf_df.loc['freq_std_dev'].values
    delta_gamma = mean_delta_dis * mean_freq / 2 # bandwidth shift, Γ
    x_comp = ( sigma_mean_delta_dis / mean_delta_dis )
    y_comp = ( sigma_mean_freq / mean_freq )
    sigma_delta_gamma = delta_gamma * np.sqrt( np.power(x_comp,2) + np.power(y_comp,2) )

    # print to verify results
    print(f"\tn_mean_delta_freq: {n_mean_delta_freq}; sigma_n_mean_delta_freq: {sigma_n_mean_delta_freq};\n\
    mean_delta_dis: {mean_delta_dis}; sigma_mean_delta_dis: {sigma_mean_delta_dis};\n\
    mean_freq: {mean_freq}; sigma_mean_freq: {sigma_mean_freq};\n\
    x_comp: {x_comp}; y_comp: {y_comp};\n\
    delta_gamma: {delta_gamma}; sigma_delta_gamma: {sigma_delta_gamma};")

    # plot data
    lin_plot = plt.figure()
    plt.subplots_adjust(hspace=0.4)
    ax = lin_plot.add_subplot(1,1,1)
    ax.plot(n_mean_delta_freq, delta_gamma, 'o', markersize=8, label='data')
    ax.errorbar(n_mean_delta_freq, delta_gamma, xerr=sigma_n_mean_delta_freq, yerr=sigma_delta_gamma, fmt='.', label='err')
    
    # format plot
    plt.sca(ax)
    plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.3)
    plt.xticks(fontsize=14, fontfamily='Arial')
    plt.yticks(fontsize=14, fontfamily='Arial')
    plt.xlabel(r"overtone * change in frequency, $\it{nΔf}$ (Hz)", fontsize=16, fontfamily='Arial')
    plt.ylabel(r"Bandwidth Shift, $\mathit{\Gamma}$$_n$ ($\mathregular{ng/cm^2}$)", fontsize=16, fontfamily='Arial')
    plt.title("<placeholder title>", fontsize=16, fontfamily='Arial')
    
    lin_plot.tight_layout()
    plt.show()
    


if __name__ == "__main__":
    linear_regression()