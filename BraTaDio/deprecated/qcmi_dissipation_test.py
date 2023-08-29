import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.float_format = f'{{:.{12}f}}'.format

qcmi_df = pd.read_csv("../raw_data/QSM-I-BSA_1mgpml.csv")

qcmi_offset_df = pd.read_excel("../offset_data/QCMI-BSA-offset.xlsx", index_col=None)

# get dis vals
# convert qcmi from FWHM to actual value
# FWHM_n / rf_n
fwhm = qcmi_offset_df.filter(like='D_').loc[0].values # get fwhm values
freqs = qcmi_offset_df.filter(like='F_').loc[0].values # get fwhm values
qcmi_offset_dis = (fwhm / freqs)
print(fwhm, freqs, qcmi_offset_dis)

print('***OFFSETS\nQCMI:', '\n', qcmi_offset_dis)

qcmi_delta_cols = [
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
qcmi_delta_fig, qcmi_delta_ax = plt.subplots()
qcmi_delta_fig.suptitle("QCMI DELTA + OFFSETS Dissipation")
qcmi_val_fig, qcmi_val_ax = plt.subplots()
qcmi_val_fig.suptitle("QCMI FULL VALUES Dissipation")
num_overtones = len(qcmi_val_cols)

print("***BEFORE ADDING OFFSETS\n", qcmi_df[qcmi_delta_cols[1]])

# adding offset vals
for i, col in enumerate(qcmi_delta_cols):
    if not col.__contains__('Time'):
        qcmi_df[col] += qcmi_offset_dis[i-1]
        
print("***OFFSETS ADDED\n", qcmi_df[qcmi_delta_cols[1]], "\n***FULL VALUES\n",qcmi_df[qcmi_val_cols[1]])


for i in range(num_overtones-1):
    qcmi_delta_ax.plot(qcmi_df[qcmi_delta_cols[0]].values, qcmi_df[qcmi_delta_cols[i+1]],'o', markersize=2, label=qcmi_delta_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)
    qcmi_val_ax.plot(qcmi_df[qcmi_val_cols[0]].values, qcmi_df[qcmi_val_cols[i+1]].values,'.', markersize=2, label=qcmi_val_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)
    
    dis_ax.plot(qcmi_df[qcmi_delta_cols[0]].values, qcmi_df[qcmi_delta_cols[i+1]].values,'.', markersize=2, label=qcmi_delta_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)
    dis_ax.plot(qcmi_df[qcmi_val_cols[0]].values, qcmi_df[qcmi_val_cols[i+1]],'o', markersize=2, label=qcmi_val_cols[i+1], markerfacecolor='none', markeredgewidth=0.32)

#plt.show()

qcmi_delta_fig.savefig("QCMi-DELTA-W-OFFSETS.png")
qcmi_val_fig.savefig("QCMI-FULL-VALUES.png")
dis_fig.savefig("combined.png")