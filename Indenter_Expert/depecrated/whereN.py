import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

# find sheets in path, concat into 1 large data frame
data_path = Path.joinpath(Path.cwd(), "indentation_data")
sheets = [file for file in data_path.iterdir() if file.suffix == ".xlsx"]
titles = []
for path in sheets:
    titles.append(os.path.basename(path))
dfs = [pd.read_excel(file, skiprows=7) for file in sheets]

i = 0
for df in dfs:
    # only need time and force columns
    fvt_df = df[['time(seconds)', 'Fn (uN)']]

    # some entries contained 'na' for time so they will be removed
    fvt_df.dropna(axis=0, how='any', inplace=False)
    temp_df = fvt_df[fvt_df['time(seconds)'].apply(lambda x: isinstance(x, str))]
    if (temp_df.size > 0):
        print(titles[i])
        print(temp_df)
        print(temp_df.index)
        fvt_df = fvt_df.drop(fvt_df.index[temp_df.index])
        temp_df = fvt_df[fvt_df['time(seconds)'].apply(lambda x: isinstance(x, str))]
        print(temp_df)
    i += 1
