"""
Author: Brandon Pardi
Created: 9/14/2022, 12:45 pm
Last Modified: 9/18/2022 4:44pm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys


# error checking for opening csv file into df
try:
    df = pd.read_csv("aggregate_data/taus-youngs.csv")
except pd.errors.EmptyDataError as empty_err:
    print(f"Data frame empty!\nerr: {empty_err}")
    sys.exit(1)
except pd.errors.ParserError as parse_err:
    print(f"Could not parse CSV, check for improper delimiters\n(clear csv and try again)\n{parse_err}")
    sys.exit(1)

if df.shape != df.drop_duplicates().shape:
    df = df.drop_duplicates()
    df.to_csv("aggregate_data/taus-youngs.csv", index=False)

# grab data from the aggregate csv file collected from executions of indentation_data.py
tau_df = df[['Tau', 'data_category']]
tau_rsq_df = df[['T_rsq', 'data_category']]
E_df = df[['E', 'data_category']]
E_rsq_df = df[['E_rsq', 'data_category']]

''' GENERATE FIGURES FROM AGGREGATE DATA
figure 1: Taus
figure 2: Tau rsq
figure 3: Youngs Modulus
figure 4: Youngs mod rsq
'''

colors = ["red", "black"]
sns.set_palette(sns.color_palette(colors))

plt.figure(1)
swarm1 = sns.swarmplot(x='data_category', y='Tau', data=tau_df, hue='data_category')
box1 = sns.boxplot(x='data_category', y='Tau', data=tau_df, boxprops={'facecolor':'None'})
medians1 = tau_df.groupby(['data_category'])['Tau'].median()
plt.xticks(fontsize=14, fontfamily='Arial')
plt.yticks(fontsize=14, fontfamily='Arial')
plt.xlabel("Elasticity", fontsize=16, fontfamily='Arial')
plt.ylabel("Relaxation Time " + '$\it{τ}$' + " (" + '$\it{s}$' + ")", fontsize=16, fontfamily='Arial')
plt.savefig("taus-youngs_plots/TAUS-swarmplot.png", bbox_inches='tight')

plt.figure(2)
swarm2 = sns.swarmplot(x='data_category', y='T_rsq', data=tau_rsq_df, hue='data_category')
box2 = sns.boxplot(x='data_category', y='T_rsq', data=tau_rsq_df, boxprops={'facecolor':'None'})
medians2 = tau_rsq_df.groupby(['data_category'])['T_rsq'].median()
plt.xticks(fontsize=14, fontfamily='Arial')
plt.yticks(fontsize=14, fontfamily='Arial')
plt.xlabel("Elasticity", fontsize=16, fontfamily='Arial')
plt.ylabel("Relaxation Time " + '$\it{τ}$' + " R² value", fontsize=16, fontfamily='Arial')
plt.savefig("taus-youngs_plots/TAUS-RSQ-swarmplot.png", bbox_inches='tight')

plt.figure(3)
swarm3 = sns.swarmplot(x='data_category', y='E', data=E_df, hue='data_category')
box3 = sns.boxplot(x='data_category', y='E', data=E_df, boxprops={'facecolor':'None'})
medians3 = E_df.groupby(['data_category'])['E'].median()
plt.xticks(fontsize=14, fontfamily='Arial')
plt.yticks(fontsize=14, fontfamily='Arial')
plt.xlabel("Elasticity", fontsize=16, fontfamily='Arial')
plt.ylabel("Young's Modulus " + '$\it{E}$' + " (" + '$\it{kPa}$' + ")", fontsize=16, fontfamily='Arial')
plt.savefig("taus-youngs_plots/YOUNGS-swarmplot.png", bbox_inches='tight')

plt.figure(4)
swarm4 = sns.swarmplot(x='data_category', y='E_rsq', data=E_rsq_df, hue='data_category')
box4 = sns.boxplot(x='data_category', y='E_rsq', data=E_rsq_df, boxprops={'facecolor':'None'})
medians4 = E_rsq_df.groupby(['data_category'])['E_rsq'].median()
plt.xticks(fontsize=14, fontfamily='Arial')
plt.yticks(fontsize=14, fontfamily='Arial')
plt.xlabel("Elasticity", fontsize=16, fontfamily='Arial')
plt.ylabel("Young's Modulus " + '$\it{E}$' + " R² value", fontsize=16, fontfamily='Arial')
plt.savefig("taus-youngs_plots/YOUNGS-RSQ-swarmplot.png", bbox_inches='tight')