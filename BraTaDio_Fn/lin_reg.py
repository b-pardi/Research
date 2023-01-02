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

    #with open(f"selected_ranges/all_stats_rf.csv", 'w') as rf_stat_file:
    rf_df = pd.read_csv("selected_ranges/all_stats_rf.csv", index_col=0).transpose()
    dis_df = pd.read_csv("selected_ranges/all_stats_dis.csv", index_col=0).transpose()

    print(dis_df.head())
    print(rf_df.head())


if __name__ == "__main__":
    linear_regression()