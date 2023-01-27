
import requests
import pandas as pd
from datetime import datetime, timedelta

# Load sero data from CDC
url = 'https://data.cdc.gov/api/views/mtc3-kq6r/rows.csv?accessType=DOWNLOAD'
response = requests.get(url)
open('dummy.csv', 'wb').write(response.content)
sero_data = pd.read_csv('dummy.csv')

abvs = pd.read_csv('us_states_abbr_list.txt', header=None)

state_map = dict(zip(abvs[0], range(len(abvs))))
try:
    xx = sero_data['Median \nDonation Date']
except:
    xx = sero_data['MedianDonationDate']
whichday = [0]*len(xx)

for ii in range(len(xx)):
    whichday[ii] = (datetime.strptime(xx[ii], '%m/%d/%Y') - datetime(2020, 1, 23)).days

un_ts = [float('nan')]*len(data_4)
un_lts = [float('nan')]*len(data_4)
un_uts = [float('nan')]*len(data_4)
un_idx = np.empty(np.shape(data_4), dtype=object)


#Note down where parts of different states occur in the table
for ii in range(len(whichday)):
    if sero_data['RegionAbbreviation'][ii][:2].upper() not in state_map:
        continue
    cidx = state_map[sero_data['RegionAbbreviation'][ii][:2].upper()]
    un_idx[cidx, whichday[ii]] = [un_idx[cidx, whichday[ii]], ii]

un_ts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan
un_lts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan
un_uts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan

for cidx in range(data_4.shape[0]):
    for ii in range(data_4.shape[1]):
        if not un_idx[cidx, ii]:
            continue
        valid_idx = un_idx[cidx, ii]
        x1 = sero_data["Lower CI %[Total Prevalence]"][valid_idx]*sero_data["n [Total Prevalence]"][valid_idx]/sero_data["n [Total Prevalence]"][valid_idx]
        x2 = sero_data["Rate %[Total Prevalence]"][valid_idx]*sero_data["n [Total Prevalence]"][valid_idx]/sero_data["n [Total Prevalence]"][valid_idx]
        x3 = sero_data["Upper CI  %[Total Prevalence]"][valid_idx]*sero_data["n [Total Prevalence]"][valid_idx]/sero_data["n [Total Prevalence]"][valid_idx]
        un_lts[cidx, (ii)] = 0.01*x1*popu[cidx]/data_4[cidx, ii]
        un_ts[cidx, (ii)] = 0.01*x2*popu[cidx]/data_4[cidx, ii]
        un_uts[cidx, (ii)] = 0.01*x3*popu[cidx]/data_4[cidx, ii]
        
                
        

import numpy as np

thisday = data_4.shape[1]

un_ts[un_ts<1] = np.nan
un_ts_s = np.nan_to_num(un_ts[:, :thisday], nan=np.nan, posinf=None, neginf=None)
un_ts_s = pd.DataFrame(un_ts_s).interpolate(method='linear', limit_direction='forward', limit=2).to_numpy()
un_ts_s = pd.DataFrame(un_ts_s).interpolate(method='nearest', limit_direction='forward', limit=2).to_numpy()
un_ts_s = pd.DataFrame(un_ts_s).fillna(method='ffill').to_numpy()



un_lts[un_lts<1] = np.nan
un_lts_s = np.nan_to_num(un_lts[:, :thisday], nan=np.nan, posinf=None, neginf=None)
un_lts_s = pd.DataFrame(un_lts_s).interpolate(method='linear', limit_direction='forward', limit=2).to_numpy()
un_lts_s = pd.DataFrame(un_lts_s).interpolate(method='nearest', limit_direction='forward', limit=2).to_numpy()
un_lts_s = pd.DataFrame(un_lts_s).fillna(method='ffill').to_numpy()

un_uts[un_uts<1] = np.nan
un_uts_s = np.nan_to_num(un_uts[:, :thisday], nan=np.nan, posinf=None, neginf=None)
un_uts_s = pd.DataFrame(un_uts_s).interpolate(method='linear', limit_direction='forward', limit=2).to_numpy()
un_uts_s = pd.DataFrame(un_uts_s).interpolate(method='nearest', limit_direction='forward', limit=2).to_numpy()
un_uts_s = pd.DataFrame(un_uts_s).fillna(method='ffill').to_numpy()



from scipy.signal import savgol_filter
from numpy import diff, nan

dd_s = smooth_epidata(data_4, 14)
ddata = [0*popu, diff(dd_s, axis=1).T]

true_new_infec = [
    pd.Series(un_lts_s[:, :thisday]).rolling(window=28).mean()*ddata,
    pd.Series(un_ts_s[:, :thisday]).rolling(window=28).mean()*ddata,
    pd.Series(un_uts_s[:, :thisday]).rolling(window=28).mean()*ddata
]
import numpy as np

un_array = [
    np.nansum(un_lts_s * ddata, axis=1) / dd_s[:, -1],
    np.nansum(un_ts_s * ddata, axis=1) / dd_s[:, -1],
    np.nansum(un_uts_s * ddata, axis=1) / dd_s[:, -1]
]
un_array[np.isnan(un_array)] = 1

