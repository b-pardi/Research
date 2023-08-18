"""
Author: Brandon Pardi
Created: 12/30/2022, 1:53 pm
Last Modified: 3/16/2023, 8:19 pm
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, least_squares

import Exceptions
from analyze import get_plot_preferences, get_num_from_string, prepare_stats_file, range_statistics

PI = np.pi

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

def elastic_modulus_stiffening(n):
    # constants
    mu_q = 2.93e10      # N/m^2 elastic modulus of quarts
    epsilon = -9.24e-2  # C/m^2 piezoelectric stress coefficient
    kappa = 3.982e-11   # F/m   effecting dielectric constant for quartz
    
    # variables
    # n is the overtone number

    # elastic modulus of quarts accounting for piezoelectric stiffening
    mu_qn = mu_q + ( epsilon ** 2 / kappa )\
            - ( (8 * epsilon ** 2) / (PI ** 2 * n ** 2 * kappa) )
    
    return mu_qn

def crystal_thickness_eqn(n, h_q):
    # constants
    rho_q = 2649.7      # kg/m^3 density of quarts

    # variables
    # f_Rn resonant frequency
    # n is overtone number
    mu_qn = elastic_modulus_stiffening(n)

    # fitting paramaters
    # h_q mm crystal thickness

    f_Rn = ( n / ( 2 * h_q )) * np.sqrt( mu_qn / rho_q )
    return f_Rn

def gk_eqn(mu_Df_n, f0):
    # constants
    rhoQ = 2650 # (kg/m^3) density of quartz
    muQ = 3.3698e-4 # (m) thickness of quartz
    # fitting parameters
    ''' eta*rho = kinematic_viscosity
        rhoL (kg/m^3) 
        etaL (Pa*s) dynamic viscosity
    '''
    kinematic_viscosity = ( np.power(mu_Df_n, 2) * PI * muQ * rhoQ ) / np.power(f0, 3)
    return kinematic_viscosity

def get_overtones_selected(which_plot):
    overtones = []
    
    for ov in which_plot.items():
        if ov[1] and ov[0].__contains__('freq'):
            overtones.append([ov[0][:-5]]) # append the overtone
    
    return overtones

def get_calibration_values(which_plot, use_theoretical_vals):
    which_freq_plots = {}
    calibration_freq = []
    sigma_calibration_freq = []
    print(use_theoretical_vals)

    # clean which_plot and remove the dis keys since we only need freq
    for key, val in which_plot.items():
        if key.__contains__('freq'):
            which_freq_plots[key] = val

    if use_theoretical_vals:        
        # theoretical calibration values for experiment, used in calculating bandwidth shift
        theoretical_values_df = pd.read_csv("offset_data/theoretical_frequencies.csv", index_col=False)
        theoretical_values = theoretical_values_df.filter(like="freq").values.flatten()
        print(f"theo vals: {theoretical_values}")

        for i, ov in enumerate(which_freq_plots.items()): # for items in which plot,
            if ov[1]:  # if true, insert the value from theoretical values
                calibration_freq.append(theoretical_values[i])
            else: # and 0 if false
                calibration_freq.append(0)
            sigma_calibration_freq.append(0) # theoretical values will have no error

        print(f"*** Theoretical Calibration Frequencies: {calibration_freq}")
        
    else:
        # grab peak frequency values from calibration file as specified in gui
        all_overtones = [get_num_from_string(ov) for ov in which_freq_plots.keys()] # get all overtones to insert 0s into overtones not selected\
        selected_overtones = [get_num_from_string(ov[0]) if ov[1] else 0 for ov in which_freq_plots.items()]
        exp_vals_df = pd.read_csv("offset_data/COPY-PASTE_OFFSET_VALUES_HERE.csv", index_col=False).filter(like="freq")
        i = 0
        while(i < len(all_overtones)): # all ovs always >= selected overtones
            print(selected_overtones, all_overtones[i], selected_overtones[i])
            if i < len(selected_overtones) and all_overtones[i] == selected_overtones[i]:
                print(exp_vals_df.head())
                print(exp_vals_df.iloc[0,i])
                calibration_freq.append(exp_vals_df.iloc[0,i])
                #sigma_calibration_freq.append(exp_vals_df.iloc[i,2])
            else:
                print('not')
                calibration_freq.append(0)
            sigma_calibration_freq.append(0) # calibration vals have no err
            i+=1

        print(f"*** Experimental Calibration Frequencies: {calibration_freq}")
        
    return (calibration_freq, sigma_calibration_freq)

# plot will be mean of bandwidth shift vs overtone * mean of change in frequency
def avg_and_propogate(label, sources, df, is_frequency):
    df_ranges = df.loc[df['range_name'] == label]

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

def plot_data(xdata, ydata, xerr, yerr, label, has_err, color='black'):
    fig, ax = setup_plot(False)
    
    # plotting modeled data slightly different than range data
    if has_err:
        if label:
            ax.plot(xdata, ydata, 'o', markersize=4, label=label, color=color)
            ax.errorbar(xdata, ydata, xerr=xerr, yerr=yerr, fmt='.', label='std dev', color=color)
        else:
            ax.plot(xdata, ydata, 'o', markersize=4, color=color)
            ax.errorbar(xdata, ydata, xerr=xerr, yerr=yerr, fmt='.', color=color)
    else:
        ax.plot(xdata, ydata, 'o', markersize=4, label=label, color=color)

    return fig, ax

def linearly_analyze(x, y, ax, label_prefix='', label_postfix=''):
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

    # for reporting Sauerbrey mass given slope

    # put label together
    if label_prefix == '' and label_postfix == '':
        label = f'Linear fit:\ny = {m:.4f}x {sign} {np.abs(b):.4f}'
    else:
        label = label_prefix + f"{m:.4e} " + label_postfix
    
    # plot curve fit
    ax.plot(x, y_fit, 'r', label=label)

    return m, b

def format_plot(ax, x_label, y_label, title, xticks=np.asarray(None)):
    plot_customs = get_plot_preferences()
    font = plot_customs['font']
    if xticks.any():
        ax.set_xticks(xticks)
    plt.sca(ax)
    plt.legend(loc='best', fontsize=plot_customs['legend_text_size'], prop={'family': font}, framealpha=0.3)
    plt.xticks(fontsize=plot_customs['value_text_size'], fontfamily=font)
    plt.yticks(fontsize=plot_customs['value_text_size'], fontfamily=font) 
    plt.xlabel(x_label, fontsize=plot_customs['label_text_size'], fontfamily=font)
    plt.ylabel(y_label, fontsize=plot_customs['label_text_size'], fontfamily=font)
    plt.tick_params(axis='both', direction=plot_customs['tick_dir'])
    plt.title(title, fontsize=plot_customs['title_text_size'], fontfamily=font)

# grab plot labels determined by use of latex, and which function modeling
def get_labels(label, type, subtype='', usetex=False):
    if type == 'film_liquid':
        data_label = None
        title = "Thin Film in Liquid " + r"$\frac{\mathit{\Delta}\mathit{\Gamma}}{\mathit{-\Delta}f} \approx J^{\prime}_{f}\omega\eta_{bulk}$" + f"  for range: {label}"
        x = r"Overtone $\cdot$ Change in frequency, $\mathit{n\cdot\Delta}$$\mathit{f}$$_n$ (Hz)"
        y = r"Bandwidth shift, $\mathit{\Delta\Gamma}$$_n$"

    elif type == 'film_air':
        data_label = None
        title = "Thin Film in Air " + f"for range: {label}"
        x = r"$\mathit{n^2}$"
        if subtype == 'gamma': # $\frac{ng}{cm^2}$
            y = r"Normalized bandwidth shift, $\frac{\mathit{\Delta}\mathit{\Gamma_{n}}}{\mathit{n}}$ Hz"
        elif subtype == 'freq':
            y = r"Normalized change in frequency, $\frac{\mathit{\Delta}f_{n}}{\mathit{n}}$ Hz"
        else:
            y = 'placeholder'
    
    elif type == 'crystal':
        data_label = None
        title = "Crystal Thickness"
        y = r"Resonant frequency, $\it{f_{Rn}}$ (Hz)"
        x = 'Overtone order, $\it{n}$'

    elif type == 'sauerbrey':
        data_label = f"average"
        title = f"Average Change in Frequency for Sauerbrey Mass\nfor Range: {label}"
        x = 'Overtone order, $\it{n}$'
        if subtype == 'fit':
            y = r'Average change in frequency, $\it{Δf_{n}}$ ' + '(Hz)'
        if subtype == 'avgs':
            y = r'Sauerbrey mass, $\it{m_{n}}$ ($\frac{ng}{cm^2}$)'

    elif type == 'avgs':
        data_label = f"average"
        x = 'Overtone order, $\it{n}$'
        if subtype == 'freq':
            title = f"Average Change in Frequency\nfor Range: {label}"
            y = r'Average change in frequency, $\it{Δf_{n}}$ ' + '(Hz)'
        if subtype == 'dis':
            title = f"Average Change in Dissipation\nfor Range: {label}"
            y = r'Average change in dissipation, $\it{ΔD_{n}}$'
    
    else:
        return None

    return data_label, x, y, title

def process_bandwidth_calculations_for_linear_regression(which_plot, sources, rf_df, dis_df, label, use_theoretical_vals):
    calibration_freq, sigma_calibration_freq = get_calibration_values(which_plot, use_theoretical_vals)

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

    return n_mean_delta_freqs, delta_gamma, sigma_n_mean_delta_freqs, sigma_delta_gamma


def thin_film_liquid_analysis(user_input):
    which_plot, use_theoretical_vals, latex_installed = user_input
    plot_customs = get_plot_preferences()
    fig_format = plot_customs['fig_format']
    dpi = plot_customs['fig_dpi']
    print("Performing thin film in liquid analysis...")

    # grab statistical data of overtones from files generated in interactive plot
    rf_df = pd.read_csv("selected_ranges/clean_all_stats_rf.csv", index_col=0)
    dis_df = pd.read_csv("selected_ranges/clean_all_stats_dis.csv", index_col=0)

    # grab all unique labels from dataset
    labels = rf_df['range_name'].unique()
    sources = rf_df['data_source'].unique()
    print(f"*** found labels: {labels}\n\t from sources: {sources}\n")
    
    # grab and analyze data for each range and indicated by the label
    for label in labels:
        n_mean_delta_freqs, delta_gamma, sigma_n_mean_delta_freqs, sigma_delta_gamma = process_bandwidth_calculations_for_linear_regression(
            which_plot, sources, rf_df, dis_df, label, use_theoretical_vals)
    
        # plot data
        data_label, x_label, y_label, title = get_labels(label, 'film_liquid', '', latex_installed)
        
        if n_mean_delta_freqs.shape != delta_gamma.shape:
            raise Exceptions.ShapeMismatchException((n_mean_delta_freqs.shape, delta_gamma.shape),"ERROR: Different number of overtones selected in UI than found in stats file")
        lin_plot, ax = plot_data(n_mean_delta_freqs, delta_gamma, sigma_n_mean_delta_freqs,
                                 sigma_delta_gamma, data_label, True)
        
        # take care of all linear fitting analysis    
        m, b = linearly_analyze(n_mean_delta_freqs, delta_gamma, ax, 'Shear dependent compliance: ', r'$\frac{1}{Pa}$')
        delta_gamma_fit = linear(n_mean_delta_freqs, m, b)

        # save calculations to file
        stats_out_fn = 'selected_ranges/thin_film_liquid_output.csv'                
        header = f"n*Df,bandwidth_shift,bandwidth_shift_FIT,range_name,data_source\n"
        prepare_stats_file(header, label, sources[0], stats_out_fn)
        with open(stats_out_fn, 'a') as stat_file:
            for i in range(len(delta_gamma)):
                stat_file.write(f"{n_mean_delta_freqs[i]:.8E},{delta_gamma[i]:.8E},{delta_gamma_fit[i]:.8E},{label},{sources[0]}\n")

        # save figure
        format_plot(ax, x_label, y_label, title)
        lin_plot.tight_layout() # fixes issue of graph being cut off on the edges when displaying/saving
        plt.savefig(f"qcmd-plots/modeling/thin_film_liquid_{label}.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)
        print("Thin film in liquid analysis complete")
        plt.rc('text', usetex=False)

def thin_film_air_analysis(user_input):
    which_plot, use_theoretical_vals, latex_installed = user_input
    plot_customs = get_plot_preferences()
    fig_format = plot_customs['fig_format']
    dpi = plot_customs['fig_dpi']
    print("Performing thin film in liquid analysis...")

    # grab statistical data of overtones from files generated in interactive plot
    rf_df = pd.read_csv("selected_ranges/clean_all_stats_rf.csv", index_col=0)
    dis_df = pd.read_csv("selected_ranges/clean_all_stats_dis.csv", index_col=0)

    # grab all unique labels from dataset
    labels = rf_df['range_name'].unique()
    sources = rf_df['data_source'].unique()
    print(rf_df.index)
    overtones_df = rf_df[(rf_df!= 0).all(1)] # remove rows with 0 (unselected rows)
    overtones = overtones_df.index.unique()
    overtones = np.asarray([get_num_from_string(ov) for ov in overtones]) # get just the number from overtone labels
    print(f"*** found labels: {labels}\n\t from sources: {sources}\nfor overtones: {overtones}")
    
    # grab and analyze data for each range and indicated by the label
    for label in labels:
        n_mean_delta_freqs, delta_gamma, sigma_n_mean_delta_freqs, sigma_delta_gamma = process_bandwidth_calculations_for_linear_regression(which_plot, sources, rf_df, dis_df, label, use_theoretical_vals)
        
        # for thin film in air, Df and DGamma are normalized
        print("AAA", delta_gamma, overtones)
        delta_gamma_norm = delta_gamma / overtones
        sigma_delta_gamma_norm = sigma_delta_gamma / overtones
        # Df is divided twice since process function returns n*DGamma
        delta_freqs_norm = n_mean_delta_freqs / overtones / overtones
        sigma_delta_freqs_norm = sigma_n_mean_delta_freqs / overtones / overtones
        # plotting against overtones^2
        sq_overtones = overtones * overtones
        print(f"delta_gamma: {delta_gamma}\ndelta_gamma_normalized: {delta_gamma_norm}\nn^2: {sq_overtones}")

        # error checking
        if n_mean_delta_freqs.shape != delta_gamma.shape:
            raise Exceptions.ShapeMismatchException((n_mean_delta_freqs.shape, delta_gamma.shape),"ERROR: Different number of overtones selected in UI than found in stats file")

        # plot data for DGamma/n v n^2
        data_label, x_label, y_label, title = get_labels(label, 'film_air', 'gamma', latex_installed)     
        lin_plot, ax = plot_data(sq_overtones, delta_gamma_norm, None,
                                 sigma_delta_gamma_norm, data_label, True)
        
        # take care of all linear fitting analysis    
        dG_m, dG_b = linearly_analyze(sq_overtones, delta_gamma_norm, ax) 
        delta_gamma_norm_fit = linear(sq_overtones, dG_m, dG_b)

        # save figure
        format_plot(ax, x_label, y_label, title)
        lin_plot.tight_layout() # fixes issue of graph being cut off on the edges when displaying/saving
        plt.savefig(f"qcmd-plots/modeling/thin_film_air_GAMMA_{label}.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)
        
        # repeat above plotting/saving for Df/n v n^2
        data_label, x_label, y_label, title = get_labels(label, 'film_air', 'freq', latex_installed)     
        lin_plot, ax = plot_data(sq_overtones, delta_freqs_norm, None,
                                 sigma_delta_freqs_norm, data_label, True)
        
        # take care of all linear fitting analysis    
        linearly_analyze(sq_overtones, delta_freqs_norm, ax) 
        delta_freq_norm_fit = linear(sq_overtones, dG_m, dG_b)

        # save calculations to file
        stats_out_fn = 'selected_ranges/thin_film_air_output.csv'                
        header = f"sq_overtones,delta_gamma_norm,delta_gamma_norm_fit,delta_freqs_norm,delta_freq_norm_fit,range_name,data_source\n"
        prepare_stats_file(header, label, sources[0], stats_out_fn)
        with open(stats_out_fn, 'a') as stat_file:
            for i in range(len(sq_overtones)):
                stat_file.write(f"{sq_overtones[i]},{delta_gamma_norm[i]:.8E},{delta_gamma_norm_fit[i]:.8E},{delta_gamma_norm[i]:.8E},{delta_freq_norm_fit[i]:.8E},{label},{sources[0]}\n")

        # save figure
        format_plot(ax, x_label, y_label, title)
        lin_plot.tight_layout() # fixes issue of graph being cut off on the edges when displaying/saving
        plt.savefig(f"qcmd-plots/modeling/thin_film_air_FREQ_{label}.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)

        print("Thin film in air analysis complete")
        plt.rc('text', usetex=False)

def gordon_kanazawa(user_input):
    which_plot, will_use_theoretical_vals = user_input
    fig_format = get_plot_preferences()['fig_format']
    print("Analyzing Gordon-Kanazawa Equation...")

    # get offset of fundamental frequency
    if will_use_theoretical_vals:
        f0 = 4998264.628859391 # (HZ) calibration fundamental frequency value (will be experimentally determined later)
    else:
        f0_which_plot = which_plot
        f0_which_plot['fundamental_freq'] = True
        f0 = np.asarray(get_calibration_values(f0_which_plot, will_use_theoretical_vals)[0])[0] # get offset data
    print(f"***f0 = {f0}")

    # for saving output data
    header = "overtone,mu_Df,mu_Df_n,kinematic_viscosity,range_name,data_source\n"
    stats_out_fn = 'selected_ranges/gordon-kanazawa_output.csv'                

    # grab data from file
    stats_df = pd.read_csv("selected_ranges/clean_all_stats_rf.csv")
    stats_df = stats_df[(stats_df!= 0).all(1)] # remove freq rows with 0 (unselected rows)
    labels = stats_df['range_name'].unique()
    print(labels)
    overtone_labels = stats_df['overtone'].unique() # overtone number (x)
    overtones = np.asarray([get_num_from_string(ov) for ov in overtone_labels]) # get just the number from overtone labels
    source = stats_df['data_source'].unique()[0]

    for label in labels:
        stats_df_range = stats_df.loc[stats_df['range_name'] == label]
        mu_Df = stats_df_range['Dfreq_mean'].values # grab averages and normalize
        mu_Df_n = mu_Df / overtones # grab averages and normalize
        sigma_mu_Df_n = stats_df_range['Dfreq_std_dev'].values
        kinematic_viscosity = gk_eqn(mu_Df_n, f0)
        print(f"** Kinematic Viscocity for {label}: {kinematic_viscosity}")
        prepare_stats_file(header, label, source, stats_out_fn)
        with open(stats_out_fn, 'a') as stat_file:
            for i in range(len(kinematic_viscosity)):
                stat_file.write(f"{overtones[i]},{mu_Df[i]},{mu_Df_n[i]},{kinematic_viscosity[i]},{label},{source}\n")

    print("Gordon-Kanazawa Analysis Complete")


def crystal_thickness(user_input):
    which_plot, will_use_theoretical_vals = user_input
    plot_customs = get_plot_preferences()
    fig_format = plot_customs['fig_format']
    dpi = plot_customs['fig_dpi']
    
    overtones = get_overtones_selected(which_plot) # get overtones
    overtones = [get_num_from_string(n[0]) for n in overtones]
    offset_vals = np.asarray(get_calibration_values(which_plot, will_use_theoretical_vals)[0]) # get offset data
    offset_vals = offset_vals[offset_vals != 0]

    print('*****', will_use_theoretical_vals, '\n', overtones, '\n', offset_vals)
    # performing the for crystal thickness equation fit 
    params, cov = curve_fit(crystal_thickness_eqn, overtones, offset_vals)
    h_q = params[0]

    # calculate fit data
    y_fit = crystal_thickness_eqn(np.asarray(overtones), h_q)

    # determine quality of the fit
    squaredDiffs = np.square(offset_vals - y_fit)
    squaredDiffsFromMean = np.square(offset_vals - np.mean(offset_vals))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    # plotting data with fit
    data_label, x_label, y_label, title = get_labels('','crystal')
    crystal_fig, crystal_ax = plot_data(overtones, offset_vals, None, None, data_label, False)
    crystal_label = f"Crystal thickness: {h_q*1000:.4f} (mm)\n" + r'$R^2$: ' + f"{rSquared:.4f}"
    crystal_ax.plot(overtones, y_fit, 'r', label=crystal_label, zorder=-1)
    format_plot(crystal_ax, x_label, y_label, title, np.asarray(overtones))

    crystal_fig.tight_layout()
    crystal_fig.savefig(f"qcmd-plots/modeling/crystal_thickness.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)

    stats_out_fn = 'selected_ranges/crystal_thickness_output.csv'                
    header = f"overtone,offset_vals,offset_vals_FIT,crystal_thickness(mm)\n"
    with open(stats_out_fn, 'w') as stat_file:
        stat_file.write(header)
        for i in range(len(overtones)):
            stat_file.write(f"{overtones[i]},{offset_vals[i]:.8E},{y_fit[i]:.8E},{h_q*1000:.8E}\n")


def sauerbrey_avgs(mu_Df, delta_mu_Df, C, overtones, label, fig_format, dpi):
    # method 2 avg rf * C for each overtone
    mu_Dm = mu_Df * C / overtones
    delta_mu_Dm = np.abs(delta_mu_Df * C / overtones)

    if mu_Df.shape != overtones.shape:
        raise Exceptions.ShapeMismatchException((mu_Df.shape, overtones.shape),"ERROR: Different number of overtones selected in UI than found in stats file")
    
    data_label, x_label, y_label, title = get_labels(label, 'sauerbrey', 'avgs')
    avg_Dm_fig, avg_Dm_ax = plot_data(overtones, mu_Dm, None, delta_mu_Dm, data_label, True)
    format_plot(avg_Dm_ax, x_label, y_label, title, overtones)
    avg_Dm_fig.tight_layout()
    plt.savefig(f"qcmd-plots/modeling/Sauerbrey_avgs_range_{label}.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)

    return mu_Dm, delta_mu_Dm

def sauerbrey_fit(df, overtones, label, C, fig_format, dpi):
    # grabbing data from df
    df_range = df.loc[df['range_name'] == label]
    # method 1 of Sauerbrey mass (linear fit slope * C)
    mu_Df = df_range['Dfreq_mean'].values # average change in frequency (y)
    delta_mu_Df = df_range['Dfreq_std_dev'].values # std dev of y

    if mu_Df.shape != overtones.shape:
        raise Exceptions.ShapeMismatchException((mu_Df.shape, overtones.shape),"ERROR: Different number of overtones selected in UI than found in stats file")
    
    # plotting average frequencies
    data_label, x_label, y_label, title = get_labels(label, 'sauerbrey', 'fit')
    avg_Df_fig, avg_Df_ax = plot_data(overtones, mu_Df, None, delta_mu_Df, data_label, True)

    # take care of all linear fitting analysis    
    m, b = linearly_analyze(overtones, mu_Df, avg_Df_ax)
    mu_Df_fit = linear(overtones, m, b)

    format_plot(avg_Df_ax, x_label, y_label, title, overtones)
    avg_Df_fig.tight_layout()
    plt.legend().get_texts()[1].set_text("Sauerbrey mass: " + f"{m*C:.1f}" + r" ($\frac{ng}{cm^2}$)")
    plt.savefig(f"qcmd-plots/modeling/Sauerbrey_fit_range_{label}.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)

    return mu_Df, delta_mu_Df, mu_Df_fit

def sauerbrey(user_input):
    use_theoretical_vals, calibration_data_from_file = user_input
    plot_customs = get_plot_preferences()
    fig_format = plot_customs['fig_format']
    dpi = plot_customs['fig_dpi']
    print("Analyzing Sauerbrey equation...")

    # grabbing df from csv
    df = pd.read_csv("selected_ranges/clean_all_stats_rf.csv")
    df = df[(df!= 0).all(1)] # remove freq rows with 0 (unselected rows)
    labels = df['range_name'].unique()
    overtones = df['overtone'].unique() # overtone number (x)
    overtones = np.asarray([get_num_from_string(ov) for ov in overtones]) # get just the number from overtone labels
    sources = df['data_source'].unique()
    print(f"LABELS: {labels}; OVERTONES: {overtones}")

    # calculate C for Sauerbrey mass formula if user opts to use calibration vals
    C = -17.7 # default theoretical value
    if not use_theoretical_vals:
        if calibration_data_from_file: # if user opted to put in their own calibration values from the machine 
            pass
        else: # if user made selection data
            calibration_df = pd.read_csv("offset_data/COPY-PASTE_OFFSET_VALUES_HERE.csv")
            f0 = calibration_df.loc[0]['fundamental_freq']
            print(f"f0: {f0}")

        quarts_wave_velocity = 3340
        quartz_density = 2650
        C = -1 * ( quarts_wave_velocity * quartz_density ) / ( 2 * ( f0 ** 2 )  )
        C *= 1e8
    print(f"C: {C}")

    for label in labels:
        mu_Df, delta_mu_Df, mu_Df_fit = sauerbrey_fit(df, overtones, label, C, fig_format, dpi)
        mu_Dm, delta_mu_Dm = sauerbrey_avgs(mu_Df, delta_mu_Df, C, overtones, label, fig_format, dpi)

        # save calculations to file
        stats_out_fn = 'selected_ranges/sauerbrey_output.csv'                
        header = f"overtone,avg_Df,avg_Df_err,avg_Df_FIT,avg_Dm,avg_Dm_err,C,range_name,data_source\n"
        prepare_stats_file(header, label, sources[0], stats_out_fn)
        with open(stats_out_fn, 'a') as stat_file:
            for i in range(len(mu_Df)):
                stat_file.write(f"{overtones[i]},{mu_Df[i]:.8E},{delta_mu_Df[i]:.8E},{mu_Df_fit[i]:.8E},{mu_Dm[i]:.8E},{delta_mu_Dm[i]:.8E},{C:.8E},{label},{sources[0]}\n")
        
    print("Sauerbrey analysis complete")
    plt.rc('text', usetex=False)

def avgs_analysis():
    plot_customs = get_plot_preferences()
    fig_format = plot_customs['fig_format']
    dpi = plot_customs['fig_dpi']
    print("Analyzing average change in frequency and dissipation...")

    # grabbing df from csv
    rf_df = pd.read_csv("selected_ranges/clean_all_stats_rf.csv")
    rf_df = rf_df[(rf_df!= 0).all(1)] # remove freq rows with 0 (unselected rows)
    dis_df = pd.read_csv("selected_ranges/clean_all_stats_dis.csv")
    dis_df = dis_df[(dis_df!= 0).all(1)] # remove dis rows with 0 (unselected rows)
    labels = rf_df['range_name'].unique()
    overtones = rf_df['overtone'].unique() # overtone number (x)
    overtones = np.asarray([get_num_from_string(ov) for ov in overtones]) # get just the number from overtone labels
    print(f"LABELS: {labels}; OVERTONES: {overtones}")

    for label in labels:
        # grabbing data from df
        rf_df_range = rf_df.loc[rf_df['range_name'] == label]
        dis_df_range = dis_df.loc[dis_df['range_name'] == label]
        mu_Df = rf_df_range['Dfreq_mean'].values # average change in frequency (y)
        delta_mu_Df = rf_df_range['Dfreq_std_dev'].values # std dev of y
        mu_Dd = dis_df_range['Ddis_mean'].values # average change in dissipation (y)
        delta_mu_Dd = dis_df_range['Ddis_std_dev'].values # std dev of y

        if mu_Df.shape != overtones.shape:
            raise Exceptions.ShapeMismatchException((mu_Df.shape, overtones.shape),"ERROR: Different number of overtones selected in UI than found in stats file")
        
        # plotting average frequencies
        print(fig_format)
        data_label, x_label, y_label, title = get_labels(label, 'avgs', 'freq')
        avg_Df_range_plot, ax = plot_data(overtones, mu_Df, None, delta_mu_Df, data_label, True)
        format_plot(ax, x_label, y_label, title, overtones)
        avg_Df_range_plot.tight_layout()
        plt.savefig(f"qcmd-plots/modeling/Avg_Df_range_{label}.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)

        # plotting average dissipations
        data_label, x_label, y_label, title = get_labels(label, 'avgs', 'dis')
        avg_Dd_range_plot, ax = plot_data(overtones, mu_Dd, None, delta_mu_Dd, data_label, True)
        format_plot(ax, x_label, y_label, title, overtones)
        avg_Dd_range_plot.tight_layout()
        plt.savefig(f"qcmd-plots/modeling/Avg_Dd_range_{label}.{fig_format}", format=fig_format, bbox_inches='tight', transparent=True, dpi=dpi)

    print("Average change in frequency and dissipation analysis complete")
    plt.rc('text', usetex=False)


# main used for testing
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
    gordon_kanazawa((which_plot['clean'], True))