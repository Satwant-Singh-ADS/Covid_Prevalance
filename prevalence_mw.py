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
