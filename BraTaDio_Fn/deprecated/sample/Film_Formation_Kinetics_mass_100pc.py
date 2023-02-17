# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 20:10:32 2021

@author: rober
"""

#import libraries
import numpy as np
import csv
import matplotlib.pylab as plt
from scipy.optimize import curve_fit
from scipy import integrate as intg
import statistics
import math
from scipy import optimize
#Import CSV Data

with open("100pc_Nonetreated_SF.csv",'r') as i:           #open a file in directory of this script for reading 
    rawdata = list(csv.reader(i,delimiter=","))   #make a list of data in file

    i = 0
    while i < len(rawdata):
        
        del rawdata[i][0]
        del rawdata[i][0]
        i +=1
           
exampledata = np.array(rawdata[:])    #convert to data array
exampledata2=np.array(exampledata[1:],dtype=np.float)

vector = np.vectorize(np.float)

Time=  exampledata2[4527:,0]
Time = (Time-exampledata2[4527,0])/60
Time = vector(Time)
Frequency_Change = exampledata2[4527:,2]
Baseline= statistics.mean(exampledata2[4512:4527,2])
Frequency_Change = Frequency_Change - Baseline
Surface_Density = Frequency_Change*(-17.7/3)
Surface_Density= vector(Surface_Density)
fig,ax=plt.subplots()
Time=Time[0::100]
Surface_Density= Surface_Density[0::100]
print(Surface_Density)

ax.scatter(Time,Surface_Density,color='r',marker='o',label='100% Nontreated SF')
ax.plot(Time,Surface_Density,color='r')



with open("100pc_SF+HAase.csv",'r') as i:           #open a file in directory of this script for reading 
    rawdata = list(csv.reader(i,delimiter=","))   #make a list of data in file

    i = 0
    while i < len(rawdata):
        
        del rawdata[i][0]
        del rawdata[i][0]
        i +=1
           
exampledata = np.array(rawdata[:])    #convert to data array
exampledata2=np.array(exampledata[1:],dtype=np.float)

vector = np.vectorize(np.float)

Time=  exampledata2[2549:,0]
Time = (Time-exampledata2[2549,0])/60
Time = vector(Time)
Frequency_Change = exampledata2[2549:,2]
Baseline= statistics.mean(exampledata2[2534:2549,2])
Frequency_Change = Frequency_Change - Baseline
Surface_Density = Frequency_Change*(-17.7/3)
Surface_Density= vector(Surface_Density)
Time=Time[0::100]
Surface_Density= Surface_Density[0::100]

print(Surface_Density)


ax.scatter(Time,Surface_Density,color='k',marker='o',label= '100% SF+HAase')
ax.plot(Time,Surface_Density,color='k')

print(type(Time))




with open("100pc_SF+Trypsin.csv",'r') as i:           #open a file in directory of this script for reading 
    rawdata = list(csv.reader(i,delimiter=","))   #make a list of data in file

    i = 0
    while i < len(rawdata):
        
        del rawdata[i][0]
        del rawdata[i][0]
        i +=1
           
exampledata = np.array(rawdata[:])    #convert to data array
exampledata2=np.array(exampledata[1:],dtype=np.float)

vector = np.vectorize(np.float)

Time=  exampledata2[3927:,0]
Time = (Time-exampledata2[3927,0])/60
Time = vector(Time)
Frequency_Change = exampledata2[3927:,2]
Baseline= statistics.mean(exampledata2[3912:3927,2])
Frequency_Change = Frequency_Change - Baseline
Surface_Density = (Frequency_Change)*(-17.7/3)
Surface_Density= vector(Surface_Density)



Time=Time[0::100]
Surface_Density= Surface_Density[0::100]

print(Surface_Density)


ax.scatter(Time,Surface_Density,color='b',marker='o',label= '100% SF+Trypsin')
ax.plot(Time,Surface_Density,color='b')























# def func(t,tau):                                   #input x in nm and b in nm^-1
#     a= 1-np.exp((-(t/tau)))
#     return 580*a
# a,d = optimize.curve_fit(func,Time,Surface_Density,maxfev=1000000000,bounds=(0,[2000]))
# theoretical_data_points=[func(i,*a) for i in Time]
# print(a)
# #ax.plot(Time,func(Time,*a))
# r_squared=coefficient_of_determination(Surface_Density,theoretical_data_points)
# print("Rsquared=",r_squared)

ax.set_ylabel("Chage in surface mass density, \n $\Delta$$\Gamma$ (ng/cm$^2$)",color="black",fontsize=14)
ax.set_xlabel("Time, $t$ (min)",color="black",fontsize=14)
ax.set_ylim(-50, 2100)
ax.set_xlim(0, 58)
plt.xticks(fontsize = 12)
from matplotlib.ticker import AutoMinorLocator
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.tick_params(which='minor',bottom=True,top=True,right=True,left=True)
ax.tick_params(which="minor",axis='both',direction='in')
ax.tick_params(which="major",axis='both',direction='in')
plt.tick_params(axis='both',direction='in')
ax.tick_params(bottom=True, top=True,left=True,right=True)
plt.yticks(fontsize = 12)
plt.legend(bbox_to_anchor=(1,0.5),loc='center left')

plt.show()

fig.savefig('Film_Formation_Kinetics_mass_100pc.pdf',
                        format='pdf',
                        dpi=100,
                        bbox_inches='tight')
# #Define Constants
# a0 = 2.5    #W m^-2 nm^-1
# a1 = 0.5    #W m^-2 nm^-1

# funcdata = func(xdata, 1.37)                 #Generate & Plot data for comparison
# plt.plot(xdata,funcdata,label="Model")   
# plt.legend()

# #Curve fit data to model
# popt, pcov = curve_fit(func,xdata,ydata,bounds=(0,4))
# perr = np.sqrt(np.diag(pcov))

# #Integrals
# TotalInt = intg.trapz(ydata,xdata)                     #Compute numerical integral
# TotalInt_func = intg.quad(func,0,4, args=(1.375))[0]        #Compute integral of function
# low_Frac = intg.quad(func,0,2, args=(1.375))[0]/TotalInt_func
# high_Frac = intg.quad(func,2,4, args=(1.375))[0]/TotalInt_func