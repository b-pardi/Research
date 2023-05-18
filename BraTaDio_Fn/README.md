### MAIN README
- Please execute 'install_packages.py' BEFORE running this script
- when done with program, please click 'Abort' button instead of closing window
    - can cause terminal to freeze sometimes if just closing windows
- ensure sheets are in the 'raw_data' folder
    - OR specify file directory in gui
- consistency in data column placement and naming is required, however columns will be renamed
- if error occurs, it will be displayed in the terminal
- if uncaught error occurs, please notify developer asap and describe what was done to reproduce
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

- IF USING SPYDER
    - by default, plt will show plots in console box and span selector will not work
    - follow these steps to make selection plots open in new window:
        Tools > Preferences > IPython console > Graphics > Graphics Backend > Apply & OK

- For interactive plot:
    - for whichever overtone is to be analyzed in the interactive plot, 
    ensure that that overtone is selected in the baseline corrected data section as well, as it relies on the cleaned data processing done there
    - indicate which overtone will be analyzed
    - selected range is displayed in right side of figure, and data points written to files in selected_ranges folder for sauerbray equation, and statistical calculations written for linear regression modeling
    - if analyzing new data file, be sure to clear range data selections via the button in column 4 before making new selections
    - save multiple ranges
        - if interactive plot selected, new column opens
        - new column will show text entry to indiciate which range is being selected
        - input and confirm the range BEFORE making selection in the plot window
        - later analysis will use the range and file src for grouping and averaging data
        - input from entry box will correlate to which file for which range is being selected
    - when making selection in graph that already has data from that section, will overwrite data from ONLY that section
        - i.e. if you select data for range 'x' in file 'data1.csv', but a selection for that was already made and data is already there,
        even if there are other ranges in the file, only data for range 'x' file 'data1.csv' will be overwritten,
        and data for range 'y' in 'data1.csv' and range 'x' in 'data2.csv' will remain untouched
    - no matter which overtone is analyzed, the range selected there will apply to ALL overtones for statistical analysis
    - to run the statistical analysis, click the button in the smaller window where the range was indicated, after all desired range selections are made, and after indicating to use theoretical or calibration/experimental values required in analysis
        - indicating calibration/exerimental values will require additional input as specified in the application window
    
- For linear Analysis
    - make sure that all frequencies desired to be in the linear regression, are selected in the 'baseline corrected data' section
    - selections from interactive plot are calculated and will be exported to a csv file that are then used in the 'lin_reg.py' script

- For Sauerbray equation
    - 1 plot per overtone per range selected will be generated
        - i.e. if you make a selection for range x and one for range y, and you have selected frequency overtones 3, 5, and 7, you will get a plot for range x overtone 3, range y overtone 3, range x overtone 5, and so on
    - color map scheme for Sauerbray plots will match color map of baseline corrected data plots
    - equation being applied for Sauerbray is Dm = -C * (Df/n) where Df is an individual change in frequency point in the range selected, n is the corresponding overtone of that point, and C is either experimentally calculated, or the theoretical value 17.7 as chosen in the window


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

## ATTENTION:
If you wish to have greek letters italicized, latex is required to be installed on your system
if it is not, please comment out the 2 lines below


--------------------------------------------------------------


### WIP

- implement avg Df plots for avg dissipation as well

- Thin film in air analysis
    - plot Df/n (Hz) against n^2
        - offset m(sub)f is y intercept of linear fit
        - slope is Jprime
    - plot DGamma against n^2
        - slope is Jdoubleprime
    - see Johannsmann paper fig 17 eqn 46 for details

- bandwidth shift add delta infront of the gamma
- overtone * change in frequency of overtone
- change * to a dot
- shift and n to lowercase in title, frequency lower case

- make sauerbrey and avg df work for multiple ranges

- ASK ROBERTO:
    - can Sauerbrey equation plotting (full range not the averages) go in the column 4 plot options section? Would simplify code (wouldn't need to save all points to csv) and makes sense because the full range plot doesn't require the interactive plot like the shear dependent compliance analysis and sauerbrey range analysis

- get calibration data for peak frequencies for linear regression (currently just using theoretical)
    - C = Vq * Pq / 2F0^2

- long term
    - document and comment the hell out of the code
    - maybe add marker size/type customizations
    - remove latex features
    - refactor analyze() to put each opt into its own function



### CHANGE LOG

5/17
- changed func name avg_Df to avgs_analysis to prepare for adding avg Dd functionality
- bandwidth shift
    - removed 1st and 3rd items from legend
    - removed rsq value from legend
    - changed title to DGamma/-Dfreq ~ J`(sub)f(omega)(eta(sub)bulk)

- avg Df and Sauerbrey
    - changed y axis labels
    - adjusted legend
    - x tick marks show odd numbers (corresponding to the overtone vals)

- fixed modeling options window title
- changed order of modeling buttons
- changed modeling button names
- added button for thin film in air analysis
- changed linear_regression function to thin_film_liquid_analysis to differentiate between the soon added thin_film_air_analysis

5/16
- modeling options moved from 5th column of main UI to a new window that opens upon selecting the interactive plot
- added functionality to close modeling window when unchecking interactive plot box
- added button to analyze avg change in frequency against overtone numbers
- added functionality to plot average change in frequency against overtone numbers (akin to Sauerbrey equation just without the actual equation)
- fix bug where non selected frequencies that have 0 rows in range data are still plotted
- fixed labels for avg change in frequency plots
- fixed bug in renaming dataframe to bratadio format
- fixed bug when grabbing overtone selection for int plot, was checking if model window is visible when it didn't have that attribute, changed to input.range_frame_flag


5/14
- progress on moving column 5 (modeling) to new window instead

5/6
- change QCM-D -> Open QCM Next
- change linear analysis to Shear dependent compliance analysis
- change corrected data to shifted data
- switch order of buttons in modeling column
- added file checking/creation of sauerbray stats to prepare_stats_file in interactive plot
- added saurbrey statistical calculations to range_statistics() in interactive plot
- added sauerbrey stats file to clear range data function button
- for sauerbrey analysis:
    - for eqn plotting just do the whole range of the overtone
    - similar to linear regression, plot avg Dm values in each overtone for each range selected, with err for std dev
    - 1 plot per range selected, each range analyze all overtones
    - Dm v overtone, n
    - removed code to plot sauerbray range eqn points (opting for averages described above)

4/30
- integrated plot customizations from json file into analyze.py
- added legend text size option
- added inout option to tick directions
- fixed set with copy warning for multiaxis plot
- fixed legend placement for multiaxis plot
- added error checking to ensure all plot opt fields are filled out
- modeling.py functions now utilize plot customizations

4/29
- began plot customizations class and figured out inheritance issue (instantiated in App class)
- added color wheel customization to plot opts window for each overtone
- added json dump function to save plot preferences
- added all other plot customization options to window
- added default values option to set options to default, also means having a default values json file
- fixed bug so plot customizations dictionary is initialized to previously saved values instead of resetting everytime

4/27
- error check for linear regression if different number overtones selected than saved in stats files
- bug fix: plots saved in modeling.py now also utilize user selected figure format
- bug fix: after submitting and running linear regression, would alter keys in which_plot in the double digit overtones, causing the underscore to be removed and not be found in dataframe (i.e. 11th_dis -> 11thdis). Culprit in overtone selection in modeling.py
- started custom Error classes to handle shape mismatch
- remove legend in temp v time
- changed overtone labels to just number of overtone using get_num_from_string() function
- removed Delta from Delta t in time labels
- bug fix normalizing overtone, used num from string function instead of hardcoding

4/22
- removed option for calibration/theoretical vals for Sauerbray, as option currently for Linear Regression will also apply for Sauerbray, so 2 separate options unnecessary

4/18
- updated README
- error check to see if Df already normalized before doing Sauerbray, if it is we don't divide by the overtone as to not do it twice
- updated plot formatting for Sauerbray
- fixed bug legend not showing in Sauerbray plots
- fixed bug when plotting only raw data
- fixed bug in Linear regression model

4/17
- refactored code to clean up analyze.py, moving nested functions outside of analyze() and shortening it. more refactoring of the like needed
- fixed normalization bug, needed to divide baseline df by overtone as well
- fixed bug in naming multiaxis plot, name pulled from wrong list of freqs
- fixed bug when plotting more freq overtones than dis or vice versa
- fixed bug in sauerbray eqn where graph shape was correct but numbers were off, was doing unnecessary unit conversion
- applied color map used in analyze.py to sauerbray eqn plots
- added opt to plot temp as f(time)
- adjusted data formatting section to support above (qsense does not have temperature data)
- added error checking for it data has temperature values
- added error checking for if dataframe empty (if user selects a overtone to plot that doesn't actually have data in it)

4/10
- fixed sauerbray eqn plots. Now will plot all overtones selected with all ranges having selections

4/9
- added option to empty range selection files to clear previous experiment data
- fixed sauerbray ranges writing header twice
- sauerbray analysis function progress, can read in and iterate over data as well as plot, however bug introduces 0 arrays so needs fix

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
