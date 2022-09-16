import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit


df = pd.read_csv("aggregate_data/taus-youngs.csv")
#df = df.drop_duplicates()
print([df['Tau'][df['data_category'] == "soft"].values])


soft_df = df[df['data_category'] == "soft"]
stiff_df = df[df['data_category'] == "stiff"]
soft_viscoelastic_df = df[df['data_category'] == "soft_viscoelastic"]
stiff_viscoelastic_df = df[df['data_category'] == "stiff_viscoelastic"]

print(soft_df.head())

plt.figure(1)
sns.swarmplot(data=soft_df)
sns.boxplot(data=soft_df, boxprops={'facecolor':'None'})
plt.savefig("taus-youngs_plots/swarmplot.png")