# Indenter Expert

# README
## Before Running Software:
- Install the latest version of python: https://www.python.org/downloads/
- ensure pip was installed correctly
    - run 'pip -V' in the command line interface (CLI) and it should return the version
- Please execute 'install_packages.py' BEFORE running this script
- Check the input variables section of 'indentation_data.py' and make sure all user defined inputs are correct
    - These Variables include:
    - Path to data (global or local), data_path
    - indicate what category of data for later swarm plots
    - 0: soft, 1: stiff, 2: soft viscoelastic, 3: stiff viscoelastic, data_category
    - If you would like to remove previously made plots before making more, set to True, will_remove_plots
    - If unable to find column index, check the skiprows value, rows_skipped
    - TIME PARAMETER FOR LENGTH OF CURVE, data this long after curve start will be removed, curve_time
    - finding start of curve for tau vals requires finding max value, to avoid outliars it will average x number of max force points this variable will determing how many to average, num_max_pts_to_avg
    - number of data points in the non-interacting regime used to find the std dev, for defining onset of interaction (start of curve), youngs_pts_to_avg
    - estimate of expected initial values for Tau, p0_tau
    - estimate of expected initial values for Young's Modulus, p0_E
    - constants for Youngs Modulus function, R and nu
    - DPI for quality of saved plots
- Many of these variables can be left unchanged, but the option to change is given for user options
- make sure all experimental data is in a folder entitled 'indentation_data', and that the script is in the same file path level as the folder OR use the global path outlined in the input variables section
    - data consists of multiple SEPARATE spreadsheets in .xlsx format, where each sheet is a separate experiment


## Steps to execute
### After ensuring everything is set up above, you can begin to run the software
1. execute script either in code editor that has an integrated run button, or by typing 'python indentation_data.py' in the CLI while navigated to the correct directory the script is located in
    - to navigate to directory in CLI, type cd "<path_to_script_location>", before executing python code
2. verify output graphs look appropriate in 'indentation_plots', and 'taus-youngs.csv' in the aggregate data folder was updated appropriately
3. change the name of the data directory to new batch of data, OR replace data in local directory to new batch
4. update category of experimental data as defined above
5. rinse and repeat

### After running script on all batches of experimental data, we can do meta analysis on all the recorded data
1. ensure 'taus-youngs.csv' contains analysis of all prior run experimental data
2. execute taus-youngs.py akin to how indentation_data executed earlier
3. view output in taus-youngs_plots folder


## When Running Software, Things to Note:
- script will name individual plots the same name as its corresponding sheet, followed by '-plot'
- var curve_time can be adjusted depending on the data set for the x length of the curve for tau values
- if program running slow, lower var DPI to ~80
- var names; df(s) short for dataframe(s), fvt_df: force vs time data frame, fvd_df: force vs displacement df, sd: squared distance,
- tau, youngs mod, and their rsq vals for each sheet are printed AND recorded in the legend of its respective plot,
- those values are also appended to 'taus-youngs.csv' for later swarmplot use
- when curve fitting data, software will warn user when curve fit is weak.


## Software Exceution Process
- grabs all sheets from 'indentation_data' folder and converts them to dataframes
- for taus, scrubs data to left of curve start (highest y values), and after <CURVE_TIME> to the right of curve start
    also removes points below the force value at tf
- for youngs mod values, removes everything after the max force point,
    as well as finds the std dev of the first <youngs_pts_to_avg> data points,
    and removes everything less than 3 times that value
- currently generates individual plots for each sheet, and one figure with each data set plotted and color coded
- box and whisker plots for E and tau will be generated in 'taus-youngs.py' when enough aggregate data is collected
- fits curve for each individual plot along with getting R^2 values
- writes tau and youngs mod values to 'taus-youngs.csv' for use with 'taus-youngs.py'
Now in taus-youngs.py after aggregate data collected:
- grabs data from 'taus-youngs.csv' and organizes it into multiple dataframes for grouping swarm and boxplots
    - also double checks for duplicate entries in the csv and rewrites to it if duplicated were found
- 4 swarm/box plots will be generated for each figure
    - 1 figure each for Tau, Tau_rsq, E, E_rsq
    - each figure will contain a plot for soft, stiff, soft_viscoelastic, stiff_viscoelastic
