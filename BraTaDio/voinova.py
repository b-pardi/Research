from math import pi, pow
from scipy.optimize import curve_fit
import matplotlib as plt
import numpy as np
import pandas as pd

''' VARIABLE NAMES/NUMBERING
0 corresponds to crystal
1 corresponds to film 1 (closest to crystal)
2 corresponds to film 2 (on top of film 1)
3 corresponds to bulk liquid on top of everything

formula originates from Voinova paper, however we are ignoring the sum for now as we work with 1 film
'''

rho0 = 2650 # density of quartz CONSTANT
h0 = 0 # thickness of quartz CONSTANT
eta3 = 0 # viscosity of bulk fluid
delta3 = 0 # coupled thickness of bulk fluid
h1 = 0 # thicknesss of adsorbed film
rho1 = 0 # density of adsorbed film
eta1 = 0 # viscosity of adsorbed film
mu1 = 0 # shear modulus of adsorbed film
omega = 0


def voinova_equation():
    Df = -1*( 1 / ( 2*pi*rho0*h0)) * ( (eta3 / delta3) +\
        ( h1*rho1*omega - 2*h1 * pow(eta3/delta3, 2) * \
        ( ( eta1 * pow(omega, 2) ) / ( pow(mu1, 2) + pow(omega, 2) * pow(eta1, 2) ) ) ) )
    
    return Df