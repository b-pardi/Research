import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit


df = pd.read_csv("aggregate_data/taus-youngs.csv")
print([df['Tau'][df['data_category'] == "soft"].values])
data_dict = {
    'tau_soft':[df['Tau'][df['data_category'] == "soft"].values],
    'tau_stiff':[df['Tau'][df['data_category'] == "soft"].values],
    'E_soft':[df['Tau'][df['data_category'] == "soft"].values],
    'E_stiff':[df['Tau'][df['data_category'] == "soft"].values]
}


data_df = pd.DataFrame(data_dict)
print(data_df.head())

plt.figure(1)
sns.swarmplot(data=data_df)
sns.boxplot(data=data_df, boxprops={'facecolor':'None'})
plt.savefig("taus-youngs_plots/swarmplot.png")