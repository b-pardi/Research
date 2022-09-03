import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import sys

root = tk.Tk()
var = tk.IntVar()

""" BASIC ANALYSIS """
def basic_analysis(sales_df):
    # returns first n rows of data frame
    print(sales_df.head(10))

    # gives number of rows and columns of df (rows x cols)
    print(sales_df.shape)

    # returns information about the table such as null vales, data types, memory usage
    print(sales_df.info())

    # gives common statistical values for each integer column such mean, dev, count, etc
    print(sales_df.describe())

    print("\n\n\n")

    # analyzing just one column
    print(f"{sales_df['Unit_Cost'].describe()} \nmean: {sales_df['Unit_Cost'].mean()}")


""" PLOTTING """
def simple_graphs(sales_df):
    # ion enables interactive mode, so need not use plt.show() after every plot
    plt.ion()

    ax = sales_df["Unit_Cost"].plot(kind = 'box', vert=False, figsize=(14,6))
    next_button = tk.Button(root, text="Next Graph", command=lambda: var.set(1))
    next_button.pack()
    next_button.wait_variable(var)
    # clf clears the plots
    ax = plt.clf()

    ax = sales_df["Unit_Cost"].plot(kind = 'density', figsize=(14,6))
    ax.axvline(sales_df["Unit_Cost"].mean(), color='red')
    ax.axvline(sales_df['Unit_Cost'].median(), color='blue')
    ax.set_ylabel("num units")
    ax.set_xlabel("dollars")
    next_button.wait_variable(var)
    ax = plt.clf()

    ax = sales_df["Unit_Cost"].plot(kind = 'hist', figsize=(14,6))
    ax.set_ylabel("num sales")
    ax.set_xlabel("dollars")

    end_label = tk.Label(root, text="End of sample graphs")
    end_label.pack()
    end_button = tk.Button(root, text="clear graphs before next option", command=lambda: var.set(1))
    end_button.pack()
    end_button.wait_variable(var)
    ax = plt.clf()


""" CATEGORICAL ANALYSIS """

def cat_analysis(sales_df):
    plt.ion()
    sales_df["Age_Group"].value_counts()
    ax = sales_df["Age_Group"].value_counts().plot(kind = "pie", figsize=(6,6))
    next_button = tk.Button(root, text="Next Graph", command=lambda: var.set(1))
    next_button.pack()
    next_button.wait_variable(var)
    ax = plt.clf()

    ax = sales_df["Age_Group"].value_counts().plot(kind="bar", figsize=(14,6))
    plt.title("Age Distribution")
    ax.set_ylabel("number of sales")
    
    end_label = tk.Label(root, text="End of sample categorical analysis")
    end_label.pack()
    end_button = tk.Button(root, text="clear graphs before next option", command=lambda: var.set(1))
    end_button.pack()
    end_button.wait_variable(var)
    ax = plt.clf()

""" CORRELATION """
def correlate(sales_df):
    corr = sales_df.corr()
    print(corr)
    plt.ion()

    fig = plt.figure(figsize=(8,8))
    # matshow displays an array as a matrix in a NEW figure window
    # maps correlation values to color (cmap changes colors), red neg corr, blue pos corr
    plt.matshow(corr, cmap='RdBu', fignum=fig.number)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation="vertical")
    plt.yticks(range(len(corr.columns)), corr.columns)
    next_button = tk.Button(root, text="Next Graph", command=lambda: var.set(1))
    next_button.pack()
    next_button.wait_variable(var)
    plt.clf()

    ax = sales_df.plot(kind = "scatter", x="Revenue", y = "Profit", figsize=(6,6))
    ax.set_ylabel("profit")
    ax.set_xlabel("revenue")
    next_button.wait_variable(var)
    ax = plt.clf()

    ax = sales_df[["Profit", "Age_Group"]].boxplot(by="Age_Group",figsize=(12,6))
    ax.set_ylabel("profit")
    plt.savefig("tempfig.png")
    next_button.wait_variable(var)
    ax = plt.clf()

    boxplt_cols = ['Year', 'Customer_Age', 'Order_Quantity', 'Unit_Cost', 'Unit_Price', 'Profit']
    sales_df[boxplt_cols].plot(kind='box', subplots = True, layout=(2,3), figsize=(12,8))

    end_label = tk.Label(root, text="End of sample correlation")
    end_label.pack()
    end_button = tk.Button(root, text="clear graphs before next option", command=lambda: var.set(1))
    end_button.pack()
    end_button.wait_variable(var)
    ax = plt.clf()   

def col_wrang(sales_df):
    # make a new columns using data from other columns
    sales_df["Revenue_per_Age"] = sales_df["Revenue"] / sales_df["Customer_Age"]
    print(sales_df["Revenue_per_Age"].head())

def filtering(sales_df):
    # selecting more specific data
    print(sales_df.loc[sales_df['State'] == 'Kentucky'])
    print(sales_df.loc[sales_df['Age_Group'] == 'Adults (35-64)', 'Revenue'].mean())
    print(sales_df.loc[(sales_df['Age_Group'] == 'Adults (35-64)') & (sales_df['Country'] == 'United States'), 'Revenue'].mean())
    
    print(sales_df.loc[sales_df['Country'] == 'France', 'Revenue'].head())
    sales_df.loc[sales_df['Country'] == 'France', 'Revenue'] *= 1.1
    print(sales_df.loc[sales_df['Country'] == 'France', 'Revenue'].head())

if __name__ == "__main__":
    # read data from csv into a dataframe
    sales_df = pd.read_csv("sales_data.csv")

    # open a basic GUI
    choose_label = tk.Label(root, text="Choose an option below")
    opt1 = tk.Button(root, text="basic data analysis", padx=30, pady=5, command=lambda: basic_analysis(sales_df))
    opt2 = tk.Button(root, text="simple graphs/charts", padx=30, pady=5, command=lambda: simple_graphs(sales_df))
    opt3 = tk.Button(root, text="categorical analysis", padx=30, pady=5, command=lambda: cat_analysis(sales_df))
    opt4 = tk.Button(root, text="correlation", padx=30, pady=5, command=lambda: correlate(sales_df))
    opt5 = tk.Button(root, text="column wrangling", padx=30, pady=5, command=lambda: col_wrang(sales_df))
    opt6 = tk.Button(root, text="selection and indexing", padx=30, pady=5, command=lambda: filtering(sales_df))
    kill = tk.Button(root, text="END PROGRAM", command=sys.exit)
    choose_label.pack()
    opt1.pack()
    opt2.pack()
    opt3.pack()
    opt4.pack()
    opt5.pack()
    opt6.pack()
    kill.pack()
    root.mainloop()
    
'''
    print("* OPTIONS *")

    choice = input("""
1: basic data analysis
2: simple graphs/charts
3: categorical analysis
4: correlation
5: column wrangling
6: selection and indexing
--------------------------------
""")

    if (choice == "1"):
        basic_analysis(sales_df)

    elif(choice == "2"):
        simple_graphs(sales_df)

    elif(choice == "3"):
        cat_analysis(sales_df)

    elif(choice == "4"):
        correlate(sales_df)

    elif(choice == "5"):
        col_wrang(sales_df)

    elif(choice == "6"):
        filtering(sales_df)

    else:
        print("Please select valid option")
'''