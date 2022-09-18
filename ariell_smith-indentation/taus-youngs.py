"""
Author: Brandon Pardi
Created: 9/14/2022, 12:45 pm
Last Modified: 9/18/2022 4:44pm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit


'''
README
- grabs data from 'taus-youngs.csv' and organizes it into multiple dataframes for grouping swarm and boxplots
    - see README for 'indentation_data.py to see how the csv is generated
    - also doubles checks for duplicate entries in the csv and rewrites to it if duplicated were found
- 4 swarm/box plots will be generated for each figure
    - 1 figure each for Tau, Tau_rsq, E, E_rsq
    - each figure will contain a plot for soft, stiff, soft_viscoelastic, stiff_viscoelastic

WIP
- currently viscoelastic data does not exist yet.
'''

df = pd.read_csv("aggregate_data/taus-youngs.csv")
df = df.drop_duplicates()
#df.to_csv("aggregate_data/taus-youngs.csv")

tau_df = df[['Tau', 'data_category']]
tau_rsq_df = df[['T_rsq', 'data_category']]
E_df = df[['E', 'data_category']]
E_rsq_df = df[['E_rsq', 'data_category']]

'''
figure 1: Taus
figure 2: Tau rsq
figure 3: Youngs Modulus
figure 4: Youngs mod rsq
'''

plt.figure(1)
sns.swarmplot(x='data_category', y='Tau', data=tau_df)
sns.boxplot(x='data_category', y='Tau', data=tau_df, boxprops={'facecolor':'None'})
plt.savefig("taus-youngs_plots/TAUS-swarmplot.png")

plt.figure(2)
sns.swarmplot(x='data_category', y='T_rsq', data=tau_rsq_df)
sns.boxplot(x='data_category', y='T_rsq', data=tau_rsq_df, boxprops={'facecolor':'None'})
plt.savefig("taus-youngs_plots/TAUS-RSQ-swarmplot.png")

plt.figure(3)
sns.swarmplot(x='data_category', y='E', data=E_df)
sns.boxplot(x='data_category', y='E', data=E_df, boxprops={'facecolor':'None'})
plt.savefig("taus-youngs_plots/YOUNGS-swarmplot.png")

plt.figure(4)
sns.swarmplot(x='data_category', y='E_rsq', data=E_rsq_df)
sns.boxplot(x='data_category', y='E_rsq', data=E_rsq_df, boxprops={'facecolor':'None'})
plt.savefig("taus-youngs_plots/YOUNGS-RSQ-swarmplot.png")