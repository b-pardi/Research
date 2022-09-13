# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:24:43 2020

@author: rober
"""
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns
import matplotlib.ticker as ticker


path = os.getcwd()

# making data frame  
print(path)
df = pd.read_excel(r'C:\Users\\ariel\OneDrive\Desktop\2021-08-06-Hydrogels_AriellSmith_updated.xlsx')


#plotting the data in a scatter plot
#d_fn = sns.scatterplot(x = 'ASC_pH6.8_constant strain_frequency .1-200 [rad/s]_01.24.2022', y = 'Storage Modulus_ASC_pH 6.8 [Pa]', data = df, color = 'black', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.8 ASC')
#d_fn = sns.scatterplot(x = 'ASC_pH6.8_constant strain_frequency .1-200 [rad/s]_01.24.2022', y = 'Loss Modulus_ASC_pH6.8 [Pa]', data = df, color = '', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.8 ASC')
#d_fn = sns.scatterplot(x = 'ASC_pH6.8_.1-100% strain_constant frequency  6.28 rad/s _01.24.2022', y = 'Storage Modulus [Pa]_ASC 6.8', data = df, color = 'b', marker = 'o', edgecolor = 'b', label = 'G\u2032, pH 6.8 ASC')
#d_fn = sns.scatterplot(x = 'ASC_pH6.8_.1-100% strain_constant frequency  6.28 rad/s _01.24.2022', y = 'Loss Modulus [Pa]_ASC 6.8', data = df, color = '', marker = 'o', edgecolor = 'b', label = 'G\u2032\u2032, pH 6.8 ASC')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.8_constant strain_frequency .1-200 [rad/s]_12.16.2021', y = 'Storage Modulus_Card-Card 6.8 [Pa]', data = df, color = 'Red', marker = 'o', edgecolor = 'Red', label = 'G\u2032, pH 6.8 Card-Card')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.8_constant strain_frequency .1-200 [rad/s]_12.16.2021', y = 'Loss Modulus_Card-Card 6.8 [Pa]', data = df, color = '', marker = 'o', edgecolor = 'red', label = 'G\u2032\u2032, pH 6.8 Card-Card')
#d_fn = sns.scatterplot(x = 'ASCc_pH6.8_constant strain_frequency .1-200 [rad/s]_02.01.2021', y = 'Storage Modulus_ ASCc 6.8[Pa]', data = df, color = 'black', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.8 ASCc')
#d_fn = sns.scatterplot(x = 'ASCc_pH6.8_constant strain_frequency .1-200 [rad/s]_02.01.2021', y = 'Loss Modulus_ACSc 6.8 [Pa]', data = df, color = '', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.8 ASCc')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.28_.1-100% strain_constant frequency 6.28 rad/s ', y = 'Storage Modulus_Card-Card 6.28 [Pa]', data = df, color = 'b', marker = 'o', edgecolor = 'b', label = 'G\u2032, pH 6.28 Card-Card')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.28_.1-100% strain_constant frequency 6.28 rad/s ', y = 'Loss Modulus_Card-Card 6.28 [Pa]', data = df, color = '', marker = 'o', edgecolor = 'b', label = 'G\u2032\u2032, pH 6.28 Card-Card')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.28_.1-100% strain_constant frequency 6.28 rad/s', y = 'Storage Modulus_ Card-Card 6.28 [Pa]', data = df, color = 'Red', marker = 'o', edgecolor = 'Red', label = 'G\u2032, pH 5.5 Card-Card')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.28_.1-100% strain_constant frequency 6.28 rad/s', y = 'Loss Modulus_ Card-Card 6.28 [Pa]', data = df, color = '', marker = 'o', edgecolor = 'red', label = 'G\u2032\u2032, pH 5.5 Card-Card')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.8_constant strain_frequency .1-200 [rad/s]_02.01.2021', y = 'Storage Modulus_ Card-Card 6.8_2 [Pa]', data = df, color = 'Red', marker = 'o', edgecolor = 'Red', label = 'G\u2032, pH 6.8 Card-Card')
#d_fn = sns.scatterplot(x = 'Card-Card_pH6.8_constant strain_frequency .1-200 [rad/s]_02.01.2021', y = 'Loss Modulus_Card-Card 6.8_2 [Pa]', data = df, color = '', marker = 'o', edgecolor = 'red', label = 'G\u2032\u2032, pH 6.8 Card-Card')
######################## test conducted at SJSU on 4.15.2022################
#d_fn = sns.scatterplot(x = 'Card_card_pH6.88_sample 1_04.15.2022', y = 'Storage Modulus_ Card-Card 6.88_sample1[Pa]', data = df, color = 'red', marker = 'o', edgecolor = 'red', label = 'G\u2032, pH 6.88 Card-Card')
#d_fn = sns.scatterplot(x = 'Card_card_pH6.88_sample 1_04.15.2022', y = 'Loss Modulus_Card-Card 6.88_sample1[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'red', label = 'G\u2032\u2032, pH 6.88 Card-Card')
#d_fn = sns.scatterplot(x = 'Card_card_pH6.78_sample 2_04.15.2022', y = 'Storage Modulus_ Card-Card 6.78_sample2[Pa]', data = df, color = 'red', marker = 'o', edgecolor = 'red', label = 'G\u2032, pH 6.78 Card-Card')
#d_fn = sns.scatterplot(x = 'Card_card_pH6.78_sample 2_04.15.2022', y = 'Loss Modulus_Card-Card 6.78_sample2[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'red', label = 'G\u2032\u2032, pH 6.78 Card-Card')
#d_fn = sns.scatterplot(x = 'Card_card_pH6.83_sample 3_04.15.2022', y = 'Storage Modulus_ Card-Card 6.83_sample3[Pa]', data = df, color = 'Red', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.83 Card-Card')
#d_fn = sns.scatterplot(x = 'Card_card_pH6.83_sample 3_04.15.2022', y = 'Loss Modulus_Card-Card 6.83_sample3[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.83 Card-Card')
#d_fn = sns.scatterplot(x = 'Card_card_pH6.77_sample 4_04.15.2022', y = 'Storage Modulus_ Card-Card 6.77_sample4[Pa]', data = df, color = 'red', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.77 Card-Card')
#d_fn = sns.scatterplot(x = 'Card_card_pH6.77_sample 4_04.15.2022', y = 'Loss Modulus_Card-Card 6.77_sample4[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.77 Card-Card')
#d_fn = sns.scatterplot(x = 'ASC-c_pH6.85_sample 5_test1_04.15.2022', y = 'Storage Modulus_ ASC-c 6.85_test 1_sample5[Pa]', data = df, color = 'blue', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.85 ASCc')
#d_fn = sns.scatterplot(x = 'ASC-c_pH6.85_sample 5_test1_04.15.2022', y = 'Loss Modulus_ ASC-c 6.85_test 1_sample5[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'blue', label = 'G\u2032\u2032, pH 6.85 ASCc')
#d_fn = sns.scatterplot(x = 'ASC-c_pH6.85_sample 6_test2_04.15.2022', y = 'Storage Modulus_ ASC-c 6.85_test 2_sample6[Pa]', data = df, color = 'black', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.85 ASCc')
#d_fn= sns.scatterplot(x = 'ASC-c_pH6.85_sample 6_test2_04.15.2022', y = 'Loss Modulus_ ASC-c 6.85_test 2_sample6[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.85 ASCc')
#d_fn = sns.scatterplot(x = 'ASC-c_pH6.85_sample 7_test1_part2_04.15.2022', y = 'Storage Modulus_ ASC-c 6.85_test 1_part 2_sample7[Pa]', data = df, color = 'black', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.85 ASCc')
#d_fn = sns.scatterplot(x = 'ASC-c_pH6.85_sample 7_test1_part2_04.15.2022', y = 'Loss Modulus_ ASC-c 6.85_test 1_part 2_sample7[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.85 ASCc')
#d_fn = sns.scatterplot(x = 'ASC-c_pH6.78_sample 8_test2_part2_04.15.2022', y = 'Storage Modulus_ ASC-c 6.85_test 2_part 2_sample8[Pa]', data = df, color = 'blue', marker = 'o', edgecolor = 'blue', label = 'G\u2032, pH 6.78 ASCc')
#d_fn = sns.scatterplot(x = 'ASC-c_pH6.78_sample 8_test2_part2_04.15.2022', y = 'Loss Modulus_ ASC-c 6.85_test 2_part 2_sample8[Pa]', data = df, color = 'none', marker = 'o', edgecolor = 'blue', label = 'G\u2032\u2032, pH 6.78 ASCc')
## FOR BRANDON##
'''SET 1'''
d_fn = sns.scatterplot(x = 'Average_Card-card_All sample_test 1 _04.15.2022', y = 'Average_Card-card_storage modulus_04.15.2022', data = df, color = 'red', marker = 'o', edgecolor = 'red', label = 'G\u2032, pH 6.8 Card-Card')
d_fn = sns.scatterplot(x = 'Average_Card-card_All sample_test 1 _04.15.2022', y = 'Average_Card-card_loss modulus_04.15.2022', data = df, color = 'none', marker = 'o', edgecolor = 'red', label = 'G\u2032\u2032, pH 6.8 Card-Card')
d_fn = sns.scatterplot(x = 'Average_ASCc_All sample_test 1 _04.15.2022', y = 'Average_ASCc_test1_storage modulus_04.15.2022', data = df, color = 'black', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.8 ASCc')
d_fn = sns.scatterplot(x = 'Average_ASCc_All sample_test 1 _04.15.2022', y = 'Average_ASCc_test1_loss modulus_04.15.2022', data = df, color = 'none', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.8 ASCc')
## FOR BRANDON##
'''SET 2'''
#d_fn = sns.scatterplot(x = 'Average_Card-card_All sample_test 2 _04.15.2022', y = 'Average_Card-card_test2_storage modulus_04.15.2022', data = df, color = 'red', marker = 'o', edgecolor = 'red', label = 'G\u2032, pH 6.8 Card-Card')
#d_fn = sns.scatterplot(x = 'Average_Card-card_All sample_test 2 _04.15.2022', y = 'Average_Card-card_test2_loss modulus_04.15.2022', data = df, color = 'none', marker = 'o', edgecolor = 'red', label = 'G\u2032\u2032, pH 6.8 Card-Card')
#d_fn = sns.scatterplot(x = 'Average_ASCc_All sample_test 1_Shear strain _04.15.2022', y = 'Average_ASCc_test2_storage modulus_04.15.2022', data = df, color = 'black', marker = 'o', edgecolor = 'black', label = 'G\u2032, pH 6.8 ASCc')
#d_fn = sns.scatterplot(x = 'Average_ASCc_All sample_test 1_Shear strain _04.15.2022', y = 'Average_ASCc_test2_loss modulus_04.15.2022', data = df, color = 'none', marker = 'o', edgecolor = 'black', label = 'G\u2032\u2032, pH 6.8 ASCc')
########################################SJSU 05.06.2022##############################
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.82_Sample1', y = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.82_Sample1_Storagemodulus', data = df, color = 'g', marker = 'o', edgecolor = 'g', label = 'G\u2032, pH 6.82 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.82_Sample1', y = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.82_Sample1_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'g', label = 'G\u2032\u2032, pH 6.82 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.85_Sample2', y = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.85_Sample2_Storagemodulus', data = df, color = 'orange', marker = 'o', edgecolor = 'orange', label = 'G\u2032, pH 6.85 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.85_Sample2', y = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.85_Sample2_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'orange', label = 'G\u2032\u2032, pH 6.85 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.86_Sample3', y = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.86_Sample3_Storagemodulus', data = df, color = 'orange', marker = 'o', edgecolor = 'orange', label = 'G\u2032,  pH 6.86 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.86_Sample3', y = 'AriellSmith_ASCc+card_test1_05.06.2022_pH6.86_Sample3_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'orange', label = 'G\u2032\u2032,  pH 6.86 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.88_Sample4', y = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.88_Sample4_Storagemodulus', data = df, color = 'orange', marker = 'o', edgecolor = 'orange', label = 'G\u2032,  pH 6.88 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.88_Sample4', y = 'AriellSmith_ASCc+card_test2_05.06.2022_pH6.88_Sample4_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'orange', label = 'G\u2032\u2032,  pH 6.88 ASCc+Card')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASC_test1_05.06.2022_pH6.82_Sample5', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.82_Sample5_Storagemodulus', data = df, color = 'blue', marker = 'o', edgecolor = 'blue', label = 'G\u2032, pH 6.82 ASC')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASC_test1_05.06.2022_pH6.82_Sample5', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.82_Sample5_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'blue', label = 'G\u2032\u2032, pH 6.82 ASC')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASC_test2_05.06.2022_pH6.85_Sample6', y = 'AriellSmith_ASC_test2_05.06.2022_pH6.85_Sample6_Storagemodulus', data = df, color = 'blue', marker = 'o', edgecolor = 'blue', label = 'G\u2032, pH 6.85 ASC')
#d_fn= sns.scatterplot(x = 'AriellSmith_ASC_test2_05.06.2022_pH6.85_Sample6', y = 'AriellSmith_ASC_test2_05.06.2022_pH6.85_Sample6_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'blue', label = 'G\u2032\u2032, pH 6.85 ASC')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASC_test1_05.06.2022_pH6.79_Sample7', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.79_Sample7_Storagemodulus', data = df, color = 'blue', marker = 'o', edgecolor = 'blue', label = 'G\u2032, pH 6.79 ASC')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASC_test1_05.06.2022_pH6.79_Sample7', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.79_Sample7_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'blue', label = 'G\u2032\u2032, pH 6.79 ASC')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASC_test1_05.06.2022_pH6.88_Sample8', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.88_Sample8_Storagemodulus', data = df, color = 'blue', marker = 'o', edgecolor = 'blue', label = 'G\u2032, pH 6.88 ASC')
#d_fn = sns.scatterplot(x = 'AriellSmith_ASC_test1_05.06.2022_pH6.88_Sample8', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.88_Sample8_Lossmodulus', data = df, color = 'none', marker = 'o', edgecolor = 'blue', label = 'G\u2032\u2032, pH 6.88 ASC')
## FOR BRANDON##
'''SET 1'''
d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASC_test1_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.88_Sampleall_Storagemodulus_Average', data = df, color = 'g', marker = 'o', edgecolor = 'g', label = 'G\u2032, pH 6.8 ASC')
d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASC_test1_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASC_test1_05.06.2022_pH6.88_Sampleall_Lossmodulus_Average', data = df, color = 'none', marker = 'o', edgecolor = 'g', label = 'G\u2032\u2032, pH 6.8 ASC')

'''SET 2'''
#d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASC_test2_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASC_test2_05.06.2022_pH6.88_Sampleall_Storagemodulus_Average', data = df, color = 'g', marker = 'o', edgecolor = 'g', label = 'G\u2032, pH 6.8 ASC')
#d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASC_test2_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASC_test2_05.06.2022_pH6.88_Sampleall_Lossmodulus_Average', data = df, color = 'none', marker = 'o', edgecolor = 'g', label = 'G\u2032\u2032, pH 6.8 ASC')
## FOR BRANDON##
'''SET 1'''
d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASCc+Card_test1_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASC+Card_test1_05.06.2022_pH6.88_Sampleall_Storagemodulus_Average', data = df, color = 'orange', marker = 'o', edgecolor = 'orange', label = 'G\u2032, pH 6.8 ASCc-Card')
d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASCc+Card_test1_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASCc+Card_test1_05.06.2022_pH6.88_Sampleall_Lossmodulus_Average', data = df, color = 'none', marker = 'o', edgecolor = 'orange', label = 'G\u2032\u2032, pH 6.8 ASCc-Card')

'''SET 2'''
#d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASCc+Card_test2_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASC+Card_test2_05.06.2022_pH6.88_Sampleall_Storagemodulus_Average', data = df, color = 'orange', marker = 'o', edgecolor = 'orange', label = 'G\u2032, pH 6.8 ASCc-Card')
#d_fn = sns.scatterplot(x = 'Average_AriellSmith_ASCc+Card_test2_05.06.2022_pH6.88_Sampleall', y = 'AriellSmith_ASC+Card_test2_05.06.2022_pH6.88_Sampleall_Lossmodulus_Average', data = df, color = 'none', marker = 'o', edgecolor = 'orange', label = 'G\u2032\u2032, pH 6.8 ASCc-Card')

plt.legend(bbox_to_anchor = (1, 1), borderaxespad = 1)

d_fn.set_xlabel('Angular frequency, \u03C9 (rad/s)', fontsize = 16)
#d_fn.set_xlabel('Shear strain, \u03B3 (%)', fontsize = 16)
d_fn.set_ylabel('Storage Modulus, Loss Modulus \n $G\u2032, G\u2032\u2032$ (Pa)', fontsize = 16)

d_fn.tick_params(labelsize = 14)
#limits for frequency change
#plt.xlim(0.05, 1000)
#plt.ylim(.05, 1000)

plt.xlim(0.05, 300)
plt.ylim(.1, 1000)

plt.xscale('log')
plt.yscale('log')

plt.savefig("ACS_pH6.8.pdf", format="pdf")
plt.savefig("ACSc_pH6.8.png", format="png")


plt.show()

