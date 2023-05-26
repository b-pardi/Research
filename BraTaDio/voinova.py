from math import pi, pow
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze import get_num_from_string

''' VARIABLE NAMES/NUMBERING
0 corresponds to crystal
1 corresponds to film 1 (closest to crystal)
2 corresponds to film 2 (on top of film 1)
3 corresponds to bulk liquid on top of everything

formula originates from Voinova paper, however we are ignoring the sum for now as we work with 1 film
we are replacing omega with 2pi * nf0
'''

def voinova_equation(n, delta3, mu1, h1):
    rho0 = 2650 # density of quartz CONSTANT
    h0 = 3.3698e-4 # thickness of quartz CONSTANT
    eta3 = 10e-2 # viscosity of bulk fluid CONSTANT
    rho1 = 10e3 # density of adsorbed film CONSTANT
    eta1 = 10e-2 # viscosity of adsorbed film CONSTANT
    f0 = 4998264.628859391 # calibration fundamental frequency value (will be experimentally determined later)
    omega = 2 * pi * n * f0

    Df = -1*( 1 / ( 2*pi*rho0*h0)) * ( (eta3 / delta3) +\
        ( h1*rho1*omega - 2*h1 * (eta3/delta3)**2 * \
        ( ( eta1 * (omega)**2 ) /\
          ( mu1**2 + omega**2 * eta1**2 ) ) ) )
    
    return Df

def get_data():
    df = pd.read_csv("selected_ranges/all_stats_rf.csv")
    df = df[(df!= 0).all(1)] # remove freq rows with 0 (unselected rows)
    print(df.head)
    xdata = df['overtone'].values
    xdata = [get_num_from_string(x) for x in xdata]
    ydata = df['Dfreq_mean'].values
    return xdata, ydata

def model():
    n, Df = get_data() # experimental data
    print('APPLE',n, Df)

    delta3 = 16e-6 # coupled thickness of bulk fluid PARAMETER
    h1 = 4.45e-9 # thicknesss of adsorbed film PARAMETER
    mu1 = 5.3e6 # shear modulus of adsorbed film PARAMETER

    p0 = (delta3, h1, mu1) # vars are initialized with initial guesses

    params, _ = curve_fit(voinova_equation, n, Df, p0=p0)
    delta3_fit, h1_fit, mu1_fit = params

    Df_fit = []
    for ov in n:
        Df_fit.append(voinova_equation(ov, delta3_fit, h1_fit, mu1_fit))
    print('BANANA', Df_fit)

    plt.scatter(n, Df, label='data')
    plt.plot(n, Df_fit, label='fit')
    plt.title("Voinova Model")
    plt.xlabel("n")
    plt.ylabel("Df")
    plt.legend()
    plt.savefig("qcmd-plots/modeling/voinova.png", bbox_inches='tight', dpi=400)
    plt.show()

if __name__ == "__main__":
    model()