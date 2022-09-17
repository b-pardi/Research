"""
Author: Brandon Pardi
Created: 9/14/2022, 12:45 pm
Last Modified: 9/16/2022 9:34pm
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
- like all of it really
- currently viscoelastic data does not exist yet.
'''

df = pd.read_csv("aggregate_data/taus-youngs.csv")
df = df.drop_duplicates()
df.to_csv("aggregate_data/taus-youngs.csv")

#print([df['Tau'][df['data_category'] == "soft"].values])


soft_df = df[df['data_category'] == "soft"]
stiff_df = df[df['data_category'] == "stiff"]
soft_viscoelastic_df = df[df['data_category'] == "soft_viscoelastic"]
stiff_viscoelastic_df = df[df['data_category'] == "stiff_viscoelastic"]

tau_data_dict = {
    'soft':soft_df['Tau'].values,
    'stiff':stiff_df['Tau'].values
}

'''
figure 1: Taus
figure 2: Youngs
'''
plt.figure(1)
sns.swarmplot(data=tau_data_dict)
sns.boxplot(x=tau_data_dict['soft'], boxprops={'facecolor':'None'})
plt.savefig("taus-youngs_plots/swarmplot.png")