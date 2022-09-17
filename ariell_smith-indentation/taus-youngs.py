import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit


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