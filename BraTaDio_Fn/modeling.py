"""
Author: Brandon Pardi
Created: 12/30/2022, 1:53 pm
Last Modified: 3/16/2023, 8:19 pm
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import Exceptions
from analyze import determine_xlabel, get_plot_preferences, map_colors

# pass in 3 dimensional array of data values
    # inner most arrays are of individual values [val_x1, val_x2, ... val_xn]
    # mid level arrays are pairs of each component [val_x, stddex_x], [val_y, stddev_y], [...], ...
    # outer array is a list of these pairs [pair_x, pair_y, ...]
# returns propogated error of set of mean data
def propogate_mult_err(val, data):
    comp = np.zeros(len(data[0][0]), dtype=float)
    temp = 0
    for pair in data:
        for i in range(len(pair[0])):
            if pair[0][i] == 0:
                temp = 0
            else:
                temp = ( pair[1][i] / pair[0][i] ) # divide err by val
                temp = float(temp) # ensure correct data type of all vals in innermost array
                temp = np.power(temp, 2)
                comp[i] = temp

    err = val * np.sqrt( comp )
    return (err)

# pass in an array of mean values,
# 2d array of err vals where the ith inner err array correlates to the ith mean value
# n_vals is how many err vals each mean has
# n_means is how many means will be propogated (essentially number of overtones)
def propogate_mean_err(means, errs, n_vals):
    n_means = len(means)
    comp = 0
    sigmas = []
    # the new error is the square root of the sum of the squares of the errors and divide it by n_vals
    for i in range(n_means):
        for j in range(n_vals):
            comp += np.power( ( errs[j][i] ), 2 )
        if n_vals == 1:
            sigmas.append(np.sqrt(comp))
        else:
            sigmas.append(np.sqrt( comp/( n_vals-1 ) ))

    return sigmas

def linear(x, m, b):
    return m * x + b

def get_overtones_selected(which_plot):
    overtones = []
    
    for ov in which_plot.items():
        if ov[1] and ov[0].__contains__('freq'):
            overtones.append([ov[0][:-5]]) # append the overtone
    
    return overtones

def get_calibration_values(which_plot, use_theoretical_vals):
    delete_keys = []
    which_freq_plots = {}
    if use_theoretical_vals:
        # clean which_plot and remove the dis keys since we only need freq
        for key, val in which_plot.items():
            if key.__contains__('freq'):
                which_freq_plots[key] = val
        '''for key, val in which_plot.items():
            which_freq_plots[key] = val'''
        '''for key in delete_keys:
            del which_plot[key]'''
        print(which_freq_plots, which_plot)

        calibration_freq = []
        sigma_calibration_freq = []
        # theoretical calibration values for experiment, used in calculating bandwidth shift
        theoretical_values = [5.0e+06, 1.5e+07, 2.5e+07,
                            3.5e+07, 4.5e+07, 5.5e+07, 6.5e+07]
        
        # for items in which plot, if true,
        # insert the value from theoretical values
        # and 0 if false
        for i, ov in enumerate(which_freq_plots.items()):
            if ov[1]:
                calibration_freq.append(theoretical_values[i])
            else:
                calibration_freq.append(0)
            sigma_calibration_freq.append(0) # theoretical values will have no error

        print(f"Calibration Frequencies: {calibration_freq}")
        
    else:
        # grab peak frequency values from calibration file as specified in gui
        with open("calibration_data/peak_frequencies.txt", 'r') as peak_file:
            freqs = peak_file.readlines()
            # grab freqs from peak freq list and converts them to a 2D numpy array of float values
            freqs = [[float(freq.split()[i].strip('\"')) for i in range(len(freqs[0].split()))] for freq in freqs]
            #freqs = np.asarray([np.asarray(freq_list) for freq_list in freqs])
            calibration_freq = np.asarray([np.average(freq) for freq in freqs])
            sigma_calibration_freq = np.asarray([np.std(freq) for freq in freqs])
            print(f"*** peak frequencies: {calibration_freq}; sigma_peak_freq: {sigma_calibration_freq};\n")

    return (calibration_freq, sigma_calibration_freq)

# plot will be mean of bandwidth shift vs overtone * mean of change in frequency
def avg_and_propogate(label, sources, df, is_frequency):
    df_ranges = df.loc[df['range_used'] == label]

    # group data by range and then source
    # values get averaged across sources respective to their range
    # i.e. average( <num from range 'x' source1>, <num from range 'x' source2>, ... )
    delta_vals = []
    sigma_delta_vals = []
    if is_frequency:
        delta_col = 'Dfreq_mean'
        sigma_delta_col = 'Dfreq_std_dev'
    else:
        delta_col = 'Ddis_mean'
        sigma_delta_col = 'Ddis_std_dev'

    for source in sources: # grabs data grouped by label and further groups into source
        df_range = df_ranges.loc[df_ranges['data_source'] == source]
        delta_vals.append(df_range[delta_col].values)
        sigma_delta_vals.append(df_range[sigma_delta_col].values)
        
    # take average described above
    n_srcs = len(sources) # num sources -> number of ranges used for average
    mean_delta_vals = np.zeros(delta_vals[0].shape)
    for i in range(n_srcs):
        mean_delta_vals += delta_vals[i]
    
    mean_delta_vals /= n_srcs
    sigma_mean_delta_vals = propogate_mean_err(mean_delta_vals, sigma_delta_vals, n_srcs)
    
    return mean_delta_vals, sigma_mean_delta_vals

# takes in an array of data, and its corresponding error array,
# finds locations where elements are 0, and removes them from both
def remove_zero_elements(data_arr, err_arr):
    indices = np.where(data_arr==0.)
    data_arr = np.delete(data_arr, indices[0])
    err_arr = np.delete(err_arr, indices[0])

    return data_arr, err_arr

def setup_plot(use_tex=False):
    if use_tex:
        plt.rc('text', usetex=True)
        plt.rc('font', family='Arial')
        plt.rc('font', family='sans-serif')
        plt.rc('mathtext', fontset='stix', rm='serif')
        plt.rc('\DeclareUnicodeCharacter{0394}{\ensuremath{\Delta}}')
        plt.rc('\DeclareUnicodeCharacter{0398}{\ensuremath{\Gamma}}')
    plot = plt.figure()
    plt.clf()
    plt.subplots_adjust(hspace=0.4)
    ax = plot.add_subplot(1,1,1)
    plt.cla()
    return plot, ax

def plot_data(xdata, ydata, xerr, yerr, label, plot_type, use_tex=False, color=''):
    fig, ax = setup_plot(use_tex)
    
    # plotting modeled data slightly different than range data
    if plot_type == 'model':
        ax.plot(xdata, ydata, 'o', markersize=8, label=label)
        ax.errorbar(xdata, ydata, xerr=xerr, yerr=yerr, fmt='.', label='error in calculations')

    elif plot_type == 'equation':
        ax.plot(xdata, ydata, markersize=1, label=label, color=color)

    return fig, ax

def linearly_analyze(x, y, ax):
    # performing the linear fit
    params, cov = curve_fit(linear, x, y)
    m, b = params
    sign = '-' if b < 0 else '+' 

    # calculate linear fit data
    y_fit = linear(np.asarray(x), m, b)

    # determine quality of the fit
    squaredDiffs = np.square(y - y_fit)
    squaredDiffsFromMean = np.square(y - np.mean(y))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    # plot curve fit
    ax.plot(x, y_fit, 'r', label=f'Linear fit:\ny = {m:.4f}x {sign} {np.abs(b):.4f}\nrsq = {rSquared:.4f}')

def format_plot(ax, x_label, y_label, title):
    plot_customs = get_plot_preferences()
    font = plot_customs['font']
    plt.sca(ax)
    plt.legend(loc='best', fontsize=plot_customs['legend_text_size'], prop={'family': font}, framealpha=0.3)
    plt.xticks(fontsize=plot_customs['value_text_size'], fontfamily=font)
    plt.yticks(fontsize=plot_customs['value_text_size'], fontfamily=font) 
    plt.xlabel(x_label, fontsize=plot_customs['label_text_size'], fontfamily=font)
    plt.ylabel(y_label, fontsize=plot_customs['label_text_size'], fontfamily=font)
    plt.tick_params(axis='both', direction=plot_customs['tick_dir'])
    plt.title(title, fontsize=plot_customs['title_text_size'], fontfamily=font)

# grab plot labels determined by use of latex, and which function modeling
def get_labels(label, usetex, model):
    if model == 'linear':
        data_label = f"average values used for range: {label}"
        title = f"Bandwidth Shift vs N * Change in Frequency\nfor range: {label}"
        if usetex:
            x = r"Overtone * Change in frequency, $\mathit{n\Delta}$$\mathit{f}$$_n$ (Hz)"
            y = r"Bandwidth shift, $\mathit{\Gamma}$$_n$"
        else:
            x = 'Overtone * Change in frequency, $\it{n\Delta f_n}$'
            y = "Bandwidth shift, $\it{\Gamma_n}$"
    else:
        return None

    return data_label, x, y, title

def linear_regression(user_input):
    which_plot, use_theoretical_vals, latex_installed, fig_format = user_input
    print("Performing linear analysis...")

    # grab statistical data of overtones from files generated in interactive plot
    rf_df = pd.read_csv("selected_ranges/all_stats_rf.csv", index_col=0)
    dis_df = pd.read_csv("selected_ranges/all_stats_dis.csv", index_col=0)

    # grab all unique labels from dataset
    labels = rf_df['range_used'].unique()
    sources = rf_df['data_source'].unique()
    print(f"*** found labels: {labels}\n\t from sources: {sources}\n")

    calibration_freq, sigma_calibration_freq = get_calibration_values(which_plot, use_theoretical_vals)

    # grab and analyze data for each range and indicated by the label
    for label in labels:
        mean_delta_freqs, sigma_mean_delta_freqs = avg_and_propogate(label, sources, rf_df, True)
        n_mean_delta_freqs = [Df * (2*i+1) for i, Df in enumerate(mean_delta_freqs)] # 2i+1 corresponds to overtone number
        sigma_n_mean_delta_freqs = [sDf * (2*i+1) for i, sDf in enumerate(sigma_mean_delta_freqs)] 
        mean_delta_dis, sigma_mean_delta_dis = avg_and_propogate(label, sources, dis_df, False)        
        
        print(f"*** rf for label: {label}\n\tn*means: {n_mean_delta_freqs}\n\tstddev: {sigma_n_mean_delta_freqs}\n")
        print(f"*** dis for label: {label}:\n\tmeans: {mean_delta_dis}\n\tstddev: {sigma_mean_delta_dis}\n")

        # calculate bandwidth shift and propogate error for this calculation
        data = [[np.array(mean_delta_dis), np.array(sigma_mean_delta_dis)], [np.array(calibration_freq), np.array(sigma_calibration_freq)]]
        delta_gamma = np.array(mean_delta_dis * calibration_freq / 2) # bandwidth shift, Γ
        sigma_delta_gamma = propogate_mult_err(delta_gamma, data)

        # remove entries of freqs not being analyzed
        delta_gamma, sigma_delta_gamma = remove_zero_elements(delta_gamma, sigma_delta_gamma)
        n_mean_delta_freqs, sigma_n_mean_delta_freqs = remove_zero_elements(np.array(n_mean_delta_freqs), np.array(sigma_n_mean_delta_freqs))

        # plot data
        data_label, x_label, y_label, title = get_labels(label, latex_installed, 'linear')
        if n_mean_delta_freqs.shape != delta_gamma.shape:
            raise Exceptions.ShapeMismatchException((n_mean_delta_freqs.shape, delta_gamma.shape),"ERROR: Different number of overtones selected in UI than found in stats file")
        lin_plot, ax = plot_data(n_mean_delta_freqs, delta_gamma,
                                 sigma_n_mean_delta_freqs, sigma_delta_gamma,
                                 data_label, 'model', latex_installed)
        
        # take care of all linear fitting analysis    
        linearly_analyze(n_mean_delta_freqs, delta_gamma, ax) 

        # save figure
        format_plot(ax, x_label, y_label, title)
        lin_plot.tight_layout() # fixes issue of graph being cut off on the edges when displaying/saving
        plt.savefig(f"qcmd-plots/modeling/lin_regression_range_{label}.{fig_format}", format=fig_format, bbox_inches='tight', dpi=200)
        print("Linear Regression Complete")
        plt.rc('text', usetex=False)

def sauerbrey(user_input):
    use_theoretical_vals, df_normalized, x_timescale, fig_format = user_input
    print("Modeling Sauerbrey function...")
    df = pd.read_csv("selected_ranges/Sauerbrey_ranges.csv")
    labels = df['range_used'].unique()
    print(f"LABELS: {labels}")
    color_map, _ = map_colors(get_plot_preferences())


    for label in labels:
        df_range = df.loc[df['range_used'] == label]
        overtones = df['overtone'].unique()
        print(f"OVERTONES: {overtones}")

        for ov in overtones:
            df_ov_range = df_range.loc[df_range['overtone'] == ov]
            if use_theoretical_vals:
                C = 17.7
            else:
                C = 0 # will later contain experimental value

            # n = 1 for fundamental, for rest of overtones we pull the first char being the number
            n = 1 if ov == 'fundamental_freq' else int(ov[0])

            Df = df_ov_range['freq'].values
            time = df_ov_range['time'].values
            Dm = -C *  Df if df_normalized else -C * (Df/n)

            # plot and save
            x_label = determine_xlabel(x_timescale)
            y_label = 'Sauerbrey mass $\it{Δm}$ ' + r'($\frac{ng}{cm^2}$)'
            title = f"Sauerbrey eqn for range: {label}, overtone: {ov}"
            plot_label = "Sauerbrey eqn"
            Sauerbrey_plot, ax = plot_data(time, Dm, None, None, plot_label, 'equation', False, color_map[ov])
            format_plot(ax, x_label, y_label, title)
            Sauerbrey_plot.tight_layout()
            plt.savefig(f"qcmd-plots/Sauerbrey_label-ov_{label}-{ov}.{fig_format}", format=fig_format, bbox_inches='tight', dpi=200)
    print("Sauerbrey Analysis Complete")
    plt.rc('text', usetex=False)

    

if __name__ == "__main__":
    which_plot = {'raw': {'fundamental_freq': False, 'fundamental_dis': False, '3rd_freq': False, '3rd_dis': False,
                            '5th_freq': False, '5th_dis': False, '7th_freq': False, '7th_dis': False,
                            '9th_freq': False, '9th_dis': False, '11th_freq': False, '11th_dis': False,
                            '13th_freq': False, '13th_dis': False},

                    'clean': {'fundamental_freq': True, 'fundamental_dis': True, '3rd_freq': True, '3rd_dis': True,
                            '5th_freq': True, '5th_dis': True, '7th_freq': True, '7th_dis': True,
                            '9th_freq': True, '9th_dis': True, '11th_freq': True, '11th_dis': True,
                            '13th_freq': False, '13th_dis': False}}
    
    #linear_regression((which_plot['clean'], True, False))
    sauerbrey((which_plot['clean'], True, False))