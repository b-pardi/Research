import pandas as pd
import numpy as np
import os
import sys

freqs = ['fundamental_freq', '3rd_freq', '5th_freq', '7th_freq', '9th_freq', '11th_freq', '13th_freq']
disps = ['fundamental_dis', '3rd_dis', '5th_dis', '7th_dis', '9th_dis', '11th_dis', '13th_dis']
    

# using the user defn file name and path (if provided) open file as dataframe
def open_df_from_file(file):
    fn = os.path.basename(file)
    print(fn)
    fn, ext = os.path.splitext(fn)
    
    try:
        if ext == '.csv':
            df = pd.read_csv(file)
        elif ext == '.txt':
            df = pd.read_csv(file, sep='\t')
        elif ext == '.xls':
            df = pd.read_excel(file, engine='xlrd')
        elif ext =='.xlsx':
            df = pd.read_excel(file, engine='openpyxl')
        else:
            print("invalid file format or path, please use either .csv, .xls, .xlsx, or .txt (with tab delimiter)")
            sys.exit(-1)
    except AssertionError as ae:
        print(f"Error occurred, ensure data file is not protected, and that it is less than 1 million rows\
              if file is protected, create new file and copy data to it")
    
    return df

# following 3 functions take input data from their respective machines,
# and converts to singular format usable by analysis script for consistency
def format_QCMd(df):
    if 'Frequency_0' in df.columns:
        df.rename(columns={'Time':'abs_time', 'Relative_time':'Time',
        'Frequency_0':freqs[0],'Dissipation_0':disps[0],
        'Frequency_1':freqs[1], 'Dissipation_1':disps[1],
        'Frequency_2':freqs[2], 'Dissipation_2':disps[2],
        'Frequency_3':freqs[3], 'Dissipation_3':disps[3],
        'Frequency_4':freqs[4], 'Dissipation_4':disps[4],
        'Temperature':'Temp'}, inplace=True)
    
    return df


def format_QCMi(df):
    print("QCM-i selected")
    slim_df = df[['Channel A QCM Time [sec]', # grab only relevant columns
             'Channel A Fundamental Dissipation [ ]', 'Channel A Fundamental Frequency [Hz]',
             'Channel A 3. Dissipation  [ ]', 'Channel A 3. Overtone [Hz]',
             'Channel A 5. Dissipation  [ ]', 'Channel A 5. Overtone [Hz]',
             'Channel A 7. Dissipation  [ ]', 'Channel A 7. Overtone [Hz]',
             'Channel A 9. Dissipation  [ ]', 'Channel A 9. Overtone [Hz]',
             'Channel A 11. Dissipation  [ ]', 'Channel A 11. Overtone [Hz]',
             'Channel A 13. Dissipation  [ ]', 'Channel A 13. Overtone [Hz]',
             'Channel A Temp [Celsius]']]
    
    # rename columns
    if 'Channel A QCM Time [sec]' in df.columns:
        fmt_df = slim_df.rename(columns={'Channel A QCM Time [sec]':'Time',
            'Channel A Fundamental Frequency [Hz]':freqs[0],'Channel A Fundamental Dissipation [ ]':disps[0],
            'Channel A 3. Overtone [Hz]':freqs[1], 'Channel A 3. Dissipation  [ ]':disps[1],
            'Channel A 5. Overtone [Hz]':freqs[2], 'Channel A 5. Dissipation  [ ]':disps[2],
            'Channel A 7. Overtone [Hz]':freqs[3], 'Channel A 7. Dissipation  [ ]':disps[3],
            'Channel A 9. Overtone [Hz]':freqs[4], 'Channel A 9. Dissipation  [ ]':disps[4],
            'Channel A 11. Overtone [Hz]':freqs[5], 'Channel A 11. Dissipation  [ ]':disps[5],
            'Channel A 13. Overtone [Hz]':freqs[6], 'Channel A 13. Dissipation  [ ]':disps[6],
            'Channel A Temp [Celsius]':'Temp'})

    return fmt_df

def format_Qsense(fmt_df, calibration_df):
    print("Qsense selected")

    if 'F_1:1' in fmt_df.columns:
        fmt_df.rename(columns={'Time_1':'Time',
        'F_1:1':freqs[0], 'D_1:1':disps[0],
        'F_1:3':freqs[1], 'D_1:3':disps[1],
        'F_1:5':freqs[2], 'D_1:5':disps[2],
        'F_1:7':freqs[3], 'D_1:7':disps[3],
        'F_1:9':freqs[4], 'D_1:9':disps[4],
        'F_1:11':freqs[5], 'D_1:11':disps[5],
        'F_1:13':freqs[6], 'D_1:13':disps[6],
        'Meas. Temp. Time':'Temp_Time', 'Tact':'Temp'}, inplace=True)

    fmt_df.loc[:, disps] = fmt_df.loc[:, disps].apply(lambda x: x*10e-6)

    if calibration_df.empty:
        print("Opting for theoretical values, calibration values will NOT be added to data")
        return fmt_df

    calibration_vals = calibration_df.values.flatten()
    calibration_vals = np.insert(calibration_vals, 0,0) # prepend 0 since time col is at start
    for col_i, val in enumerate(calibration_vals):
        fmt_df.iloc[:, col_i] += val

    return fmt_df

def format_raw_data(src_type, data_file, will_use_theoretical_vals):
    file_name, _ = os.path.splitext(data_file)
    file_name = os.path.basename(file_name)
    # check if file has already been formatted previously
    if data_file.__contains__("Formatted"):
        print(f"{file_name} has been formatted previously, using previously formatted file...")
        return
    

    data_df = open_df_from_file(data_file)
    print(f"*** Before formatting\n{data_df}")
    if src_type == 'QCM-d':
        formatted_df = format_QCMd(data_df)
    elif src_type == 'QCM-i':
        formatted_df = format_QCMi(data_df)
    elif src_type == 'Qsense':
        if not will_use_theoretical_vals:
            calibration_df = open_df_from_file("offset_data/COPY-PASTE_OFFSET_VALUES_HERE.csv")
        else:
            calibration_df = pd.DataFrame()
        formatted_df = format_Qsense(data_df, calibration_df)
    else:
        print("invalid option selected")
        sys.exit(1)
    
    print(file_name)
    print(f"*** After formatting\n{formatted_df}")
    formatted_df.to_csv(f"raw_data/Formatted-{file_name}.csv", index=False)


if __name__ == '__main__':
    format_raw_data('Qsense', 'qsense_unprotected_copy.xls')
