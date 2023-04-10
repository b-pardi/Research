# Intensity Profile Analyzer
## For use with Fiji software to further analyze the outputs of pixel intensity profile data

## Before Running Script
- execute 'install_packages.py'
- specify file name, file path, which pair of columns in file are being analyzed, and which sheet in file to look at
    - (First 3 variables in script 'FILE_NAME', 'COLUMNS', and SHEET)
    - if only 1 sheet in file, make sheets variable empty, i.e. it should look like SHEETS = ''
    - Note: Columns are NOT 0 indexed, meaning the first column is a 1 not 0
    - also make sure not to remove the r in front of the quotes for the FILE_PATH string

## Executing script
- run the script in one of two ways
    - in the command line interface (CLI) navigate to the working directory where the script is located on your computer typing: cd 'PATH_TO_FOLDER_WITH_SCRIPT' then type: python main_gaussian.py
    - OR
    - in whatever code editor of your choice, hit the play/run button while the script is open in the editor
- window will open with 2 plots in it
    - plot title indicates image that data originates from
    - x axis indicates strain direction (length or width)
    - top plot is original data, click and drag in this plot to select data
    - for optimal approximation, data selection should include the entirety of the dip
        - i.e. the plateaus on either side of the dip should be within the span for proper fit
    - lower plot will show the selected data zoomed in to fit
    - will also show the curve fit, and approximate minimum points
- to account for data that doesn't fit curve properly, second method implemented also to find minimum by averaging the lowest 5 values and taking the median index of occurences of that average value
    - this will be useful when data is not as clean and the guassian function doesn't fit properly
- user will choose which of these min vals is more appropriate
- in addition to displaying fit and minima in plots, values also printed in terminal

### IF USING SPYDER
- by default, plt will show plots in console box and span selector will not work
- follow these steps to make selection plots open in new window:
    Tools > Preferences > IPython console > Graphics > Graphics Backend > Apply & OK
