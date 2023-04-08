### MAIN README
- Please execute 'install_packages.py' BEFORE running this script
- when done with program, please click 'Abort' button instead of closing window
    - can cause terminal to freeze sometimes otherwise
- ensure sheets are in the 'raw_data' folder
    - OR specify file directory in gui
- consistency in data column placement and naming is required, however columns will be renamed
- if error occurs, it will be displayed in the terminal
- if uncaught error occurs, please notify me asap and describe what was done to reproduce
- specify in GUI:
    - file name (with exetension)
    - file path (if not in predefined raw_data directory)
    - indicate if new clean data file should be created
    - if plotting clean data, indicate baseline t0 and tf
    - CLICK SUBMIT FILE INFO
    - indicate which channels to plot for raw/clean data
    - indicate which special plot options
    - change scale of time if applicable
    - change file format if applicable

- For interactive plot:
    - for whichever overtone is to be analyzed in the interactive plot, 
    ensure that that overtone is selected in the baseline corrected data section as well,
    as it relies on the cleaned data processing done there
    - indicate which overtone will be analyzed
    - selected range is displayed in lower portion of figure, and data points written to 'range_{range selection}_rf/dis.txt'
    - save multiple ranges
        - if interactive plot selected, small new window opens
        - new window will show text entry to indiciate which range is being selected
        - input and confirm the range BEFORE making selection in the plot window
        - later analysis will use the range and file src for grouping and averaging data
        - input from entry box will correlate to which file for which range is being selected
    - when making selection in graph that already has data from that section, will overwrite data from ONLY that section
        - i.e. if you select data for range 'x' in file 'data1.csv', but a selection for that was already made and data is already there,
        even if there are other ranges in the file, only data for range 'x' file 'data1.csv' will be overwritten,
        and data for range 'y' in 'data1.csv' and range 'x' in 'data2.csv' will remain untouched
    - no matter which overtone is analyzed, the range selected there will apply to ALL overtones for statistical analysis
    - to run the statistical analysis, click the button in the smaller window where the range was indicated, after selecting a range in the plot
    
- For linear Analysis
    - make sure that all frequencies desired to be in the linear regression, are selected in the 'baseline corrected data' section
    - selections from interactive plot are calculated and will be exported to a csv file that are then used in the 'lin_reg.py' script
    - more information of linear regression in 'lin_reg.py'    

GUI features
- file name box (later maybe window to search for file)
- checkbox for each frequency being plotted
    - checkbox for raw and clean data
        - raw data plots are individual for overtone of each freq/dis
- abs base time t0, tf
- input for scale of time (seconds, minutes, hours)
- change saved figure file format
- alternate plot options:
    - plot dF and dD together
    - normalize F
    - dD vs dF
    - interactive plot -> linear analysis
- submit button runs data analysis while keeping gui window open



--------------------------------------------------------------


### DATA ANALYSIS README

- sends user input info to 'analyze.py' for processing
- opens defined data file and reads it into a dataframe
- renames columns as dictated below in Variable Declarations section
- checks which_plot to determine which channels are being analyzed, and adds to lists accordingly
- plots are frequencies and dissipations of each channel specified in 'main.py'
- if overwrite file selected, will create a copy of the data file with the baseline corrected points

Baseline Corrected Data:
    - find average resonant frequency of baseline, and lowers curve by that amount
    - removes points before start of baseline

Plot Options:
- plots raw data individually as specified in gui
- option for multi axis plot with change in frequency and dissipation vs time
- option to normalize data by dividing frequency by its respective overtone
- option to plot change in dissipation vs change in frequency
- option to change scale of x axis (time) to minutes, hours, or remain at seconds
- option to change saved figure file formats (png (default), tiff, pdf)

Interactive Plot:
- SPECIFY AND CONFIRM RANGE BEFORE MAKING SELECTION
- option for interactive plot that opens figure of selected overtone to further analyze
    - can select a range of points of plot to zoom in and save to file for later
    - interactive plot range will be used to specify statistical data for linear analysis
    - user indicates what range being selected, that range and the file containing current data,
    are used to group ranges for analysis


--------------------------------------------------------------


### LINEAR REGRESSION README

- Data for this script is statistical data curated from the raw input data acquired in 'main.py'
    - see README there for more information

- For italicized variables to work, please install a LaTex distribution (like https://www.tug.org/texlive/acquire-netinstall.html)

- script begins with various statistical data from 'all_stats_rf/dis.csv'
- For peak frequency values needed for calculation, enter values into 'calibration_peak_frequencies.txt'
    - otherwise indicate in GUI to use theoretical values, theoretical values will be used

- LINEAR REGRESSION
    - x axis is the overtone times its corresponding average change in frequency (n*Df)
        - grabs the average Df values and multiplies each by its respective overtone
        - also grabs the x_err, in this case just the std_dev of the mean
    - y axis is the bandwidth shift Γ of each overtone (f*Dd)/2
        - grabs average peak frequency and average change in dissipation values from calibration/theoretical data, and stats csv respectively
            - note, frequency here refers to NOT baseline corrected frequency as it does in the x axis
        - calculates bandwidth defined above
        - propogates error of this calculation
    - for x and y, values are grouped by ranges, and then data sources
        - values are averaged across multiple experimental data sets, based on the range
        - these averages are also propogated and the error calculated becomes the error bars in the plot
    - plots the values with error bars and shows equation with slope
    - NEED FORMULAS FOR Calculates G prime and JF (frequency dependent shear film compliance)

    - for bandwidth calculation, only use fundamental overtone peak frequency for all overtones

# ATTENTION:
If you wish to have greek letters italicized, latex is required to be installed on your system
if it is not, please comment out the 2 lines below


--------------------------------------------------------------


### WIP

- add option in col 5 to indicate if user has latex installed. if yes, linear regression model will remain as is with italicized capital greek letters, if not, disable rc params and user std matplotlib chars

- get calibration data for peak frequencies for linear regression (currently just using theoretical)


### CHANGE LOG

4/6
- adjusted range_statistics() so sauerbray ranges saved to csv file
- begun sauerbray function

4/2
- added options for sauerbray modeling
- added to statistics analysis functions to handle sauerbray range data

3/15-3/16
- linear regression now works with variable number of overtones being used, however needs verification with manually analyzed data
- fixed linear reg bug where freqs that are not being analyed and have 0 values were still being plotted
- major refactoring, putting most of linear regression function into separate functions
- added back end functionality to have different labels dependend on if user indicates if latex is installed
- modified propogation function to account for varying amts of overtone data (accounted for 0 entries)


3/11
- bug fix: 11th and 13th overtones were not working
- flushed out file conversion from qcmd, qcmi, qsense, to bratadio
- coupled span selectors in interactive plot
- refactor: put code from onselect to prepare the saving of statistical data, and the saving/formatting of the data into functions that get called from onselect
- optimize: rather than converting the file format every time submitted, first_run flag added to indicated if file needs conversion or not
- bug fix: when submitting from gui after the first time, would crash unable to open the csv from file
- added this changelog

3/8
- added gui options for different data file formats (qcmd, qcmi, qsense)
- added functionality for new data file formats

2/23
- formatting col5 to make more clean
- bug fix: added overtones
- bug fix: column 5 showing up
- more refactoring in favor of OOP for gui

2/16
- major refactoring-restructuring

1/12
- linear regression plot formatting changes
- linear reg model now averages across mult data sets for each range, added find nearest time

1/11
- can save stats ranges across diff files, avg across them needs work
- int plot saves mult ranges, lin reg uses mult ranges

1/4
- file restructuring
- format changes, updated readme
- adjusted for bandwidth shift, updated readme

1/2
- formatted interactive plot
- plotting statistical data of each frequency
- adjust stat data calcs to include all freqs based off int plot range

12/30
- updated for different format input data
- bug fix int plot overtone selection
- bug fix, selecting rf would alter selection for disp in int plot

12/29
- plot formatting

12/28
- functionality of selecting range to plot

12/16
- added statistical analysis to int plot ranges
- added functionality to save from multiple files in statistical calculations

12/14
- added rf and dis to plot selector

12/8
- changed range selector to text entry

11/30
- added functionality to select-save mult ranges for statistical analysis from interactive plot

12/29
- file structure adjusted
- gui runs async from data, added interactive plot

11/29
- refactor so dont need to close gui to run analysis

10/27
- gui and plotting format changes
- small format changes to ind and qcmd

10/12 
- fixed x time scale bug

10/3
- multi axis plot for dD and dF added

10/1
- added option to plot dD vs dF
- bug fix on which channel plotted, raw data plotting
- func for plotting (refactor)
- overwrite clean data now works
- clean plt - only plots channels selected (not all)
- function to get channels (refactor)

9/30
- add alt opt to gui
- begun error checking function
- system for deleting channels
- ui dev progress

9/28
- updated plot formatting

9/27
- improved backend com,
- backend linked to front. can plot all clean data

9/24
- changed gui labels
