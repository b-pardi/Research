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
    - Also on line 15 in analyze.py there is code that reads 'matplotlib.use('TkAgg')'
        - for use with spyder change 'TkAgg' to just 'Agg'

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

- For Sauerbrey equation
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

bug fixes:

format changes:

features:
- make modeling functions work for multiple ranges selected
- integrate commented out sauerbrey code to find the mass both ways

- sauerbrey mass overtone/linear fit
- OPTION TO plot all selected overtones together
- viscoelastic film modeling
- gordon-kanazawa

publication/documentation: 
- more explicit library acknowledgement sections
- instructions on adding more files to format

optimizations/refactoring: 
- only rerun calculations if changes in ui made
- have a requirements to list install dependencies that way
- remove unnecessary prints
- check data dir for existing file conversion
- make sauerbrey and avg df work for multiple ranges
- error messages become window popups
    - like when trying to submit with selections that there are no data for
    - have all exceptions be custom exception classes that generate a popup window with the err msg
- document and comment the hell out of the code
- remove latex features
- refactor analyze() to put each opt into its own function

waiting on data: 
- plot calibration values from data against overtone
    - calibration values come from the flatlining of points that we normally removed before the baseline
    - will be receiving more data soon with this air stabilization
    - interactive plot for RAW data to select the pre baseline baseline
    - bring up new window to enter range selections for each baseline (considering Bernardo's temperature jumps)

- calibration data from file option will need file formatting akin to experimental data formatting done in 'format_file.py' 

- qsense will need option to add calibration freqs to values because qsense records just change in frequency, qcmi and open qcm next record actual frequency
    - prompt user to put absolute frequencies of measured overtones into separate file, than in formatting script add those to each of the delta freq values


### CHANGE LOG
6/15
- fix sauerbrey saving ranges
- reimplement old sauerbrey eqn
- get sauerbrey and avgs to work with mult ranges
- implement saving of those outputs to a csv file

6/14
- added capability to enter time range selection in interactive plot
    - set TkAgg as backend for span selector window generation to allow for tkinter entry fields
    - text entry has a focus in/out handler for temporary text
    - update_text and onselect communicate with eachother
        - if using span selector, text field is updated with xmin,xmax values
        - if using text field, spans are set to match the entered values
    - added update text function to perform all the same tasks as the onselect function
    - refactored code so the above tasks are done in a separate function that onselect and update text both call
        - split into 2 functions, one to update plot and one to calc and save stat data
- thin film in liquid records output data used for plots into csv file "thin_film_liquid_output.csv"
- thin film in air records output data used for plots into csv file "thin_film_air_output.csv"

- Sauerbrey now has 2 methods of calculations
    - current way takes average Df from rf_stats and fits linear function to those values, multiplying slope by a theoretical or calculated C
    - additional way is being reimplemented where full freq range data is saved and picked up by sauerbrey function, and mass is plotted as a function of time by multiplying each df point by C

- bug fix input file selection not being saved
- updated readme for spyder users to make a modification to code

6/8
- fixed bug where axis weren't being labelled and no formatting was ocurring except for the last generated figure
    - setup_plot() now gets the passed in figure's number and selects it
    - figure saving now occurs outside of setup plot
- fixed bug where plot format options were only grabbed when restarting software
- replaced fundamental with 1st everywhere by altering the ordinal function
- changed color scheme of multiaxis to use the same color mapping of overtones as other plots
    - to help differentiate between freq and dis, freq uses right side up trianges, and dis uses upside down triangles
- modeling window opens from a separate button in column 4 rather than with the int plot checkbox
    - replaced destroy model window with test model window to check if it's already open when clicking button to not open duplicate windows

6/7
- refactor, made plot_customs a global variable since it is called in so many different functions
- refactor, all plots are named figure/axis objects, instead of using plt.figure(#) selecting the figure to modify before modifications are made. This is much more explicit and easy to follow rather than keeping track of which number belongs to which figure
    - adjust setup_plot functions accordingly
- sauerbrey report to 1 decimal


6/6
- fixed bug where if int plot in col 4 was checked, checking and unchecking other items in that column would open the model window 
- fixed bug with temperature plot time scale, changing units of time generated incorrect figures. temp df was in for loop of freq/dis analysis repeatedly subtracting baseline start and divisor
- adjusted multiaxis plot legend to report just the ordinal overtone number
- y axis labels in visualizations now show Df_n instead of just Df
    - adjustment made also to int plot and model plots
- refactored generate_interactive_plot() condensing code that chooses user specified overtone for visualizations
- changed units of dissipation linear fit in int plot to 1/{timescale}
- bug fix where units int plot linear fit were only reporting first letter (i.e. min was only showing m)
    - in main changed radio handler for time scale to set var to s, min, or hr, instead of just s, m, h and adjusting later
    - refactored code to accommodate this change
- raw plots now combined into 1 plot for all freq overtones and one for all dis overtones


6/5
- when selecting file, there is now a button to select which opens windows file explorer for user to select their file
    - removed code that called for separate file name and file path vars, replacing it with input.file which is simply the path/name.ext, vars that need just one of those are split as needed
    - removed file name and directory entries and corresponding handlers for them
    - refactored format_file.py to account for variable restructuring

- visualization plots now show when f is normalized in the axis label
- refactor s.t. normalized freq plot is not a separate chunk of code, rather just choosing labels for regular freq plot

- multiaxis plots now save all plots into one figure instead of separate for each overtone
- bug fix: legend placement was determined before all overtones plotted so it was misplaced
- bug fix: modeling plots were normalized when they shouldn't be
    - added unnormalized_df that is just a copy of the baseline shifted data_df but remultiplying the overtone ordinal value

- plot options put label that states options are saved even when closing software
- change asterisks to a dot
- nDf should be n * Df (dot not asterisk)
- thin film analysis y axis put proper fractions for labels
- hard coded to load qcmi.txt initially to minimize time takes for testing (will be removed on release)
- hard coded baseline time values for same purpose
- dis vs freq plot cleaned up legend
- fixed bug in multiaxis plot, now correctly save figure with user spec'd format
- fixed bug where all options in col 4 were calling destroy model window even when model window wasn't opened

5/25
- bug fix, C calculations for calibration data

5/24
- changed analyze to visualize when selecting overtone for int plots
- created new csv file in 'res' folder with theoretical frequency values
- added std dev to calibration data range selection
- updated calibration_frequencies function to grab frequencies from calibration data file
- adjusted prepare stats file function to have file path in name instead of hardcoding path, so can save calibration ranges to different folder than stats ranges
- bug fix, calibration/theoretical val radio buttons in modeling were not actually being sent properly to modeling functions, now that var is sent directly to function instead of via input object
- added button to clear old frequency data from selections in calibration_data.csv

- theoretical/calibration values option selection moved to column 1
- calibration menu option moved to nested option within column 1
- restructured theoretical/calibration selection as follows:
    - first prompted to use either theoretical or calibration values
        - if using theoretical, input object is updated and user can continue
        - if calibration selected, input object updated and user is then prompted with option to use from file or make selections
            - if file option selected, label informs user to copy values into file in calibration_data folder
            - if selections option selected, calibration menu button made available

- lower case dissipation for equation model plots
- changed modeling plots to black points and err bars
- removed 'analysis' from ov avgs

- added ability to calculate C based on calibration fundamental frequency for Sauerbrey model

5/18
- added thin film in liquid to title of plot
- Added functionality of Thin film in air analysis
    - plot Df/n (Hz) against n^2
        - offset m(sub)f is y intercept of linear fit
        - slope is Jprime
    - plot DGamma against n^2
        - slope is Jdoubleprime
    - see Johannsmann paper fig 17 eqn 46 for details

- added linear fit to interactive plot zoom section to measure drift
- fix bug where previous linear fits remains on screen during new selections
- add legend to report drift value (slope)
- adjusted value reporting to account for user selected time inputs with units in legend

- implemented avg plots for avg dissipation as well
- cite libraries as sources for paper
- make flowchart in inkscape

- added button in raw data column for calibration data window
- new class for calibration data window
- filled calibration data window with entries for constants and button for raw data int plot
- refactor to put all code setting up int plot into its own function
- refactor put clean data int plot into its own function
- added input fields to input which overtone analyzing and which range selecting for raw int plot
- raw_interactive_plot() function acts similarly to clean one but with different data and calculations
- save_calibration_data() function to save the averages of selections in raw int plot in similar fashion to range_statistics
- selections are averaged and saved in calibration_data.csv
- select_calibration_data() function to handle all processes relating to selection of raw data
- move conversion of files to confirm file data button 
- exception to check if selected overtone to analyze in int plot is selected in checkboxes
- interactive plot now open from calibration menu
- set yticks in dissipation plot to be scientific notation to clean it up

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
- refactored code moving all bandwidth shift calcs from thin_film_liquid_analysis() to new function process_bandwidth_calculations_for_linear_regression() for more reusable code for thin_film_air_analysis

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
