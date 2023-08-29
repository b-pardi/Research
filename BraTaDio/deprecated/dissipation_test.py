import pandas as pd
import matplotlib.pyplot as plt

qcmi_df = pd.read_csv("../raw_data/QSM-I-BSA_1mgpml.csv")
qsense_df = pd.read_excel("../raw_data/Qsense-BSA-exp.xlsx")
print(qcmi_df, '\n', qsense_df)

qsense_offset_df = pd.read_excel("../offset_data/QSense_BSA-offset.xlsx", index_col=None)
qcmi_offset_df = pd.read_excel("../offset_data/QCMI-BSA-offset.xlsx", index_col=None)

# get dis vals
qsense_offset_dis = qsense_offset_df.filter(like='D_').values[0]

# convert qcmi from FWHM to actual value
# FWHM_n / rf_n
fwhm = qcmi_offset_df.filter(like='D_').loc[0].values # get fwhm values
freqs = qcmi_offset_df.filter(like='F_').loc[0].values # get fwhm values
qcmi_offset_dis = (fwhm / freqs)
print(fwhm, freqs, qcmi_offset_dis)

print('***OFFSETS\nQCMI:', '\n', qcmi_offset_dis, '\nQSENSE:', '\n', qsense_offset_dis)


qsense_cols = [
    'Time',
    #'fundamental_dis',
    '3rd_dis',
    '5th_dis',
    '7th_dis',
    '9th_dis',
    '11th_dis',
    '13th_dis'
]

qcmi_cols = [
    'Channel A QCM Time [sec]',
    #'Channel A Fundamental Dissipation Variation [ ]',
    'Channel A 3. Dissipation Variation [ ]',
    'Channel A 5. Dissipation Variation [ ]',
    'Channel A 7. Dissipation Variation [ ]',
    'Channel A 9. Dissipation Variation [ ]',
    'Channel A 11. Dissipation Variation [ ]',
    'Channel A 13. Dissipation Variation [ ]'
]

qcmi_val_cols = [
    'Channel A QCM Time [sec]',
    #'Channel A Fundamental Dissipation [ ]',
    'Channel A 3. Dissipation  [ ]',
    'Channel A 5. Dissipation  [ ]',
    'Channel A 7. Dissipation  [ ]',
    'Channel A 9. Dissipation  [ ]',
    'Channel A 11. Dissipation  [ ]',
    'Channel A 13. Dissipation  [ ]',

]

dis_fig, dis_ax = plt.subplots()
dis_fig.suptitle("Combined Dissipation")
qcmi_fig, qcmi_ax = plt.subplots()
qcmi_fig.suptitle("QCMI Dissipation")
qsense_fig, qsense_ax = plt.subplots()
qsense_fig.suptitle("Qsense Dissipation")
qcmi_val_fig, qcmi_val_ax = plt.subplots()
num_overtones = len(qcmi_cols)

# adding offset vals
for i, col in enumerate(qsense_cols):
    if not col.__contains__('Time'):
        print(qsense_offset_dis[i-1])
        qsense_df[col] += qsense_offset_dis[i-1]

for i, col in enumerate(qcmi_cols):
    if not col.__contains__('Time'):
        qcmi_df[col] += qcmi_offset_dis[i-1]
        
print("***OFFSETS ADDED\n", qcmi_df, '\n', qsense_df)


for i in range(num_overtones-1):
    qcmi_ax.plot(qcmi_df[qcmi_cols[0]].values, qcmi_df[qcmi_cols[i+1]],'o', markersize=2, label=qcmi_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)
    qsense_ax.plot(qsense_df[qsense_cols[0]].values, qsense_df[qsense_cols[i+1]].values * 1e-6,'.', markersize=2, label=qcmi_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)
    
    dis_ax.plot(qsense_df[qsense_cols[0]].values, qsense_df[qsense_cols[i+1]].values * 1e-6,'.', markersize=2, label=qcmi_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)
    dis_ax.plot(qcmi_df[qcmi_cols[0]].values, qcmi_df[qcmi_cols[i+1]],'o', markersize=2, label=qcmi_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)

#plt.show()

qcmi_fig.savefig("QCMi.png")
qsense_fig.savefig("Qsense.png")
dis_fig.savefig("combined.png")