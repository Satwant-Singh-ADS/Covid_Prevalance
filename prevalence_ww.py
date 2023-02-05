import pandas as pd
import requests
import datetime

from smooth_epidata import *

sel_url = 'https://raw.githubusercontent.com/biobotanalytics/covid19-wastewater-data/master/wastewater_by_county.csv'
ww_data = pd.read_csv(sel_url)

abvs = pd.read_csv('us_states_abbr_list.txt', header=None)[0].to_list()


fips_tab = pd.read_csv('reich_fips.txt')


def impute_us(x):
    if x=='US':
        return '0'
    else:
        return x
fips_tab['location'] = fips_tab['location'].apply(impute_us)

ww_data['fipscode'] = ww_data.fipscode.astype(str)

ww_data_fips = ww_data.fipscode.to_list()

fips_tab_codes = fips_tab['location'].to_list()

fips_idx = []
second_grp = [float(k) for k in (fips_tab_codes)]
for w in range(len(ww_data_fips)):
    if float(ww_data_fips[w]) in second_grp:
        
        fips_idx.append(second_grp.index(float(ww_data_fips[w])))
    else:
        fips_idx.append(0)
        

import numpy as np
from datetime import datetime, timedelta
xx = ww_data.sampling_week.to_list()

whichday = np.zeros(len(xx))
for ii in range(len(xx)):
    whichday[ii] = int((datetime.strptime(xx[ii], '%Y-%m-%d') - datetime(2020, 1, 23)).days)


from latest_us_data import *
get_data()
filehandler = open("data_4.pkl", 'rb') 
#     print(a)
data_4 = pickle.load(filehandler)

ww_ts = np.zeros((data_4.shape[0],data_4.shape[1]))

ww_pres = np.zeros((data_4.shape[0],data_4.shape[1]))

abvs_idx = [abvs.index(i) for i in ww_data.state if i in abvs]

popu = np.loadtxt('us_states_population_data.txt')

for ii in range(len(xx)):
    if whichday[ii] < 1 or fips_idx[ii] < 1:
        continue
#     print(ii)
    ww_pres[abvs_idx[ii], int(whichday[ii])] = 1
    ww_ts[abvs_idx[ii], int(whichday[ii])] = ww_ts[abvs_idx[ii], int(whichday[ii])] + ww_data.effective_concentration_rolling_average[ii]*fips_tab.population[fips_idx[ii]]/popu[abvs_idx[ii]]


ww_ts[ww_pres < 1] = np.nan
ww_ts[ww_ts <= 0] = np.nan

ww_ts1 = pd.DataFrame(ww_ts).interpolate( limit_direction='both', axis=1).to_numpy()
ww_tsm = pd.DataFrame(ww_ts1).rolling(14, axis=1).mean().to_numpy()

data_4_s = Smooth_epiData(data_4,smooth_factor = 14,week_correction = 0,week_smoothing = 1)
data_diff = np.insert(np.diff(data_4_s, axis=1), 0, 0, axis=1)

ww_tsw = np.insert(ww_ts[:, 5::7], 0, 0, axis=1)
weekly_dat = np.insert(np.diff(ww_tsw, axis=1), 0, 0, axis=1)


import csaps

wlag = 7
ww_tsm[ww_ts == 0] = np.nan
f = np.empty_like(ww_ts)
f[:, wlag:] = ww_ts[:, :-wlag] / data_diff[:, wlag:]
f[:, :200] = np.nan
f1 = f


for jj in range(f1.shape[0]):
    xx = np.flatnonzero(~np.isnan(f1[jj,:]))
    xx2 = np.flatnonzero(np.isfinite(f1[jj,:]))
    xx = np.array(list(set(xx2).intersection(set(xx))))
    xx.sort()
    
    
    if (len(xx) > 5) and (sum((xx>200) & (xx<600))) > 2:
        yy = f1[jj, xx]
        f[jj, 200:] = sp = csaps.CubicSmoothingSpline(xx, yy,smooth = 0.0001)(list(range(200,f.shape[1])))
    f[jj,:] = pd.DataFrame(f[jj,:]).interpolate( limit_direction='both', axis=1).to_numpy().ravel()
    f[jj,:] = pd.DataFrame(f[jj,:]).interpolate(limit_direction='both', axis=1).to_numpy().ravel()


f[f<0] = 0
f = pd.DataFrame(f).rolling(7,axis=1).mean().to_numpy()
ww_adj = pd.DataFrame(data_diff*f).rolling(14,axis=1).mean().to_numpy()

from CDC_Sero import *
CDC_SERO_Function()


filehandler = open("true_new_infec.pkl", 'rb') 
true_new_infec = pickle.load(filehandler)


filehandler = open("un_array.pkl", 'rb') 
un_array = pickle.load(filehandler)


true_new_infec[0] = (true_new_infec[0]+abs(true_new_infec[0]))/2
true_new_infec[1] = (true_new_infec[1]+abs(true_new_infec[1]))/2
true_new_infec[2] = (true_new_infec[2]+abs(true_new_infec[2]))/2


eq_range = range(200,601)
nz_idx = ww_adj[:, eq_range]>0.5

ww_year1 = np.nansum(ww_adj[:, eq_range]*nz_idx, axis=1)


sero_year1 = np.nansum(true_new_infec[0].iloc[:, eq_range]*nz_idx, axis=1)


true_new_infec_ww = [0,0,0]
b = sero_year1/ww_year1
true_new_infec_ww[0] = ww_adj*b.reshape((b.size, 1))


true_new_infec_ww[0][np.isnan(true_new_infec_ww[0])] = 0


true_new_infec_ww[0] = pd.DataFrame(np.maximum(true_new_infec_ww[0],true_new_infec[0].to_numpy())).rolling(14,axis=1,min_periods=0).mean().to_numpy()


eq_range = range(200,601)
nz_idx = ww_adj[:, eq_range]>0.5

# ww_year2 = np.nansum(ww_adj[:, eq_range]*nz_idx, axis=1)


sero_year2 = np.nansum(true_new_infec[1].iloc[:, eq_range]*nz_idx, axis=1)

b = sero_year2/ww_year1
true_new_infec_ww[1] = ww_adj*b.reshape((b.size, 1))


true_new_infec_ww[1][np.isnan(true_new_infec_ww[1])] = 0


true_new_infec_ww[1] = pd.DataFrame(np.maximum(true_new_infec_ww[1],true_new_infec[1].to_numpy())).rolling(14,axis=1,min_periods=0).mean().to_numpy()


eq_range = range(200,601)
nz_idx = ww_adj[:, eq_range]>0.5

# ww_year2 = np.nansum(ww_adj[:, eq_range]*nz_idx, axis=1)


sero_year3 = np.nansum(true_new_infec[2].iloc[:, eq_range]*nz_idx, axis=1)

b = sero_year3/ww_year1
true_new_infec_ww[2] = ww_adj*b.reshape((b.size, 1))


true_new_infec_ww[2][np.isnan(true_new_infec_ww[2])] = 0


true_new_infec_ww[2] = pd.DataFrame(np.maximum(true_new_infec_ww[2],true_new_infec[2].to_numpy())).rolling(14,axis=1,min_periods=0).mean().to_numpy()


bad_states = (np.isnan(ww_ts).sum(axis=1)<1) & (np.isnan(true_new_infec[1]).sum(axis=1)<1)


# true_new_infec_ww[0][bad_states, :] = true_new_infec[0][bad_states, :]
# true_new_infec_ww[1][bad_states, :] = true_new_infec[1][bad_states, :]
# true_new_infec_ww[2][bad_states, :] = true_new_infec[2][bad_states, :]

true_new_infec_ww[0][bad_states, :] = data_diff[bad_states, :]
true_new_infec_ww[1][bad_states, :] = data_diff[bad_states, :]
true_new_infec_ww[2][bad_states, :] = data_diff[bad_states, :]

import pickle 
with open("true_new_infec_ww.pkl", "wb") as f:
    pickle.dump(true_new_infec_ww, f)
with open("true_new_infec_final.pkl", "wb") as f:
    pickle.dump(true_new_infec, f)


print("Process completed")