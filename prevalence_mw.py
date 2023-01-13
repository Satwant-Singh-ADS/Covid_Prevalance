import pandas as pd
import requests
import datetime

sel_url = 'https://raw.githubusercontent.com/biobotanalytics/covid19-wastewater-data/master/wastewater_by_county.csv'
ww_data = pd.read_csv(sel_url)

abvs = pd.read_csv('us_states_abbr_list.txt', header=None)[0].to_list()
fips_tab = pd.read_csv('reich_fips.txt', names = ["location", "population"])

fips_tab.location = fips_tab.location.replace({'US':'0'})
fips_idx = fips_tab.location.isin(ww_data.fipscode).nonzero()[0]
xx = ww_data.sampling_week

whichday = np.zeros(len(xx))
for ii in range(len(xx)):
    whichday[ii] = (xx[ii] - datetime.datetime(2020, 1, 23)).days

ww_ts = np.zeros((len(data_4)))
ww_pres = np.zeros((len(data_4)))

abvs_idx = [abvs.index(i) for i in ww_data.state if i in abvs]

for ii in range(len(xx)):
    if whichday[ii] < 1 or fips_idx[ii] < 1:
        continue
    ww_pres[abvs_idx[ii], whichday[ii]] = 1
    ww_ts[abvs_idx[ii], whichday[ii]] = ww_ts[abvs_idx[ii], whichday[ii]] + ww_data.effective_concentration_rolling_average[ii]*fips_tab.population[fips_idx[ii]]/popu[abvs_idx[ii]]

ww_ts[ww_pres < 1] = np.nan
ww_ts[ww_ts <= 0] = np.nan

ww_ts1 = pd.DataFrame(ww_ts).interpolate(method='linear', limit_direction='forward', axis=1).to_numpy()
ww_tsm = pd.DataFrame(ww_ts1).rolling(14, axis=1).mean().to_numpy()
data_4_s = smooth_epidata(data_4, 14, 0, 1)
data_diff = np.insert(np.diff(data_4_s, axis=1), 0, 0, axis=1)

ww_tsw = np.insert(ww_ts[:, 5::7], 0, 0, axis=1)
weekly_dat = np.insert(np.diff(ww_tsw, axis=1), 0, 0, axis=1)


wlag = 7
ww_tsm[ww_ts == 0] = np.nan
f = np.empty_like(ww_ts)
f[:, wlag:] = ww_ts[:, :-wlag] / data_diff[:, wlag:]
f[:, :200] = np.nan
f1 = f

from scipy.interpolate import CubicSpline

for jj in range(f1.shape[0]):
    xx = np.flatnonzero(~np.isnan(f1[jj,:]))
    yy = f1[jj, xx]
    if len(xx) > 5 and sum(xx > 200 and xx < 600) > 2:
        f[jj, 200:] = CubicSpline(xx, yy, extrapolate=True)(range(200,f.shape[1]))
    f[jj,:] = pd.DataFrame(f[jj,:]).interpolate(method='linear', limit_direction='forward', axis=1).to_numpy().ravel()
    f[jj,:] = pd.DataFrame(f[jj,:]).interpolate(method='nearest', limit_direction='forward', axis=1).to_numpy().ravel()


f[f<0] = 0
f = pd.DataFrame(f).rolling(7,axis=1).mean().to_numpy()
ww_adj = pd.DataFrame(data_diff*f).rolling(14,axis=1).mean().to_numpy()

CDC_sero(). ### this function needs to be imported above
true_new_infec[0] = (true_new_infec[0]+abs(true_new_infec[0]))/2
true_new_infec[1] = (true_new_infec[1]+abs(true_new_infec[1]))/2
true_new_infec[2] = (true_new_infec[2]+abs(true_new_infec[2]))/2


eq_range = range(200,601)
nz_idx = ww_adj[:, eq_range]>0.5

ww_year1 = np.sum(ww_adj[:, eq_range]*nz_idx, axis=1)

sero_year1 = np.sum(true_new_infec[1][:, eq_range]*nz_idx, axis=1)
true_new_infec_ww[0] = (sero_year1/ww_year1)*ww_adj
true_new_infec_ww[0] = pd.DataFrame(np.maximum(true_new_infec_ww[0], np.maximum(true_new_infec[0], un_array[:,0]*data_diff))).rolling(14,axis=1).mean().to_numpy()

sero_year2 = np.sum(true_new_infec[1][:, eq_range]*nz_idx, axis=1)
true_new_infec_ww[1] = (sero_year2/ww_year1)*ww_adj
true_new_infec_ww[1] = pd.DataFrame(np.maximum(true_new_infec_ww[1], np.maximum(true_new_infec[1], un_array[:,1]*data_diff))).rolling(14,axis=1).mean().to_numpy()

sero_year3 = np.sum(true_new_infec[2][:, eq_range]*nz_idx, axis=1)
true_new_infec_ww[2] = (sero_year3/ww_year1)*ww_adj
true_new_infec_ww[2] = pd.DataFrame(np.maximum(true_new_infec_ww[2], np.maximum(true_new_infec[2], un_array[:,2]*data_diff))).rolling(14,axis=1).mean().to_numpy()

# bad_states = (np.isnan(ww_ts).sum(axis=1) < 1) & (np.isnan(true_new_infec[1]).sum(axis=1) > 1)
# true_new_infec_ww[0][bad_states, :] = true_new_infec[0][bad_states, :]
# true_new_infec_ww[1][bad_states, :] = true_new_infec[1][bad_states, :]
# true_new_infec_ww[2][bad_states, :] = true_new_infec[2][bad_states, :]

# bad_states = (np.isnan(ww_ts).sum(axis=1) < 1) & (np.isnan(true_new_infec[1]).sum(axis=1) < 1)
# true_new_infec_ww[0][bad_states, :] = data_diff[bad_states, :]
# true_new_infec_ww[1][bad_states, :] = data_diff[bad_states, :]
# true_new_infec_ww[2][bad_states, :] = data_diff[bad_states, :]

bad_states = (np.isnan(ww_ts).sum(axis=1)<1) & (np.isnan(true_new_infec[2]).sum(axis=1)>1)
true_new_infec_ww[1][bad_states, :] = true_new_infec[1][bad_states, :]
true_new_infec_ww[2][bad_states, :] = true_new_infec[2][bad_states, :]
true_new_infec_ww[3][bad_states, :] = true_new_infec[3][bad_states, :]

bad_states = (np.isnan(ww_ts).sum(axis=1)<1) & (np.isnan(true_new_infec[2]).sum(axis=1)<1)
true_new_infec_ww[1][bad_states, :] = data_diff[bad_states, :]
true_new_infec_ww[2][bad_states, :] = data_diff[bad_states, :]
true_new_infec_ww[3][bad_states, :] = data_diff[bad_states, :]





