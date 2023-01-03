"""
Author: Brandon Pardi
Created: 12/30/2022, 1:53 pm
Last Modified: 12/30/2022, 1:53 pm
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def linear_regression():
    print("Performing linear plots...")

    # grab statistical data of overtones from files generated in interactive plot
    rf_df = pd.read_csv("selected_ranges/all_stats_rf.csv", index_col=0).transpose()
    dis_df = pd.read_csv("selected_ranges/all_stats_dis.csv", index_col=0).transpose()

    print(rf_df.head())
    print(dis_df.head())

    # plot will be mean of change in dissipation vs overtone * mean of change in frequency
    xdata = rf_df.iloc[0].values
    xdata = [Df * (2*i+1) for i, Df in enumerate(xdata)] # 2i+1 corresponds to overtone number
    ydata = dis_df.iloc[0].values
    ydata = [pt * 1000000 for pt in ydata]
    print(xdata)
    print(ydata)

    # plot data
    lin_plot = plt.figure()
    plt.subplots_adjust(hspace=0.4)
    ax = lin_plot.add_subplot(1,1,1)
    ax.plot(xdata, ydata, 'o', markersize=8, label='data')
    
    # format plot
    plt.sca(ax)
    plt.legend(loc='best', fontsize=14, prop={'family': 'Arial'}, framealpha=0.3)
    plt.xticks(fontsize=14, fontfamily='Arial')
    plt.yticks(fontsize=14, fontfamily='Arial')
    plt.xlabel("overtone * change in frequency, " + '$\it{nΔt}$' + " (Hz)", fontsize=16, fontfamily='Arial')
    plt.ylabel("Change in dissipation, " + '$\it{Δd}$' + " (" + r'$10^{-6}$' + ")", fontsize=16, fontfamily='Arial')
    plt.title("<placeholder title>", fontsize=16, fontfamily='Arial')
    
    lin_plot.tight_layout()
    plt.show()
    


if __name__ == "__main__":
    linear_regression()