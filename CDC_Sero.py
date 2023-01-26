
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
un_idx = [float('nan')]*len(data_4)

#Note down where parts of different states occur in the table
for ii in range(len(whichday)):
    if sero_data['RegionAbbreviation'][ii][:2] not in state_map:
        continue
    cidx = state_map[sero_data['RegionAbbreviation'][ii][:2]]
    un_idx[cidx, whichday[ii]] = [un_idx[cidx, whichday[ii]], ii]

un_ts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan
un_lts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan
un_uts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan

for cidx in range(data_4.shape[0]):
    for ii in range(data_4.shape[1]):
        if not un_idx[cidx, ii]:
            continue
        valid_idx = un_idx[cidx, ii]
        x1 = sero_data["LowerCI__TotalPrevalence_"][valid_idx]*sero_data["n_TotalPrevalence_"][valid_idx]/sum(sero_data["n_TotalPrevalence_"][valid_idx])
        x2 = sero_data["Rate__TotalPrevalence_"][valid_idx]*sero_data["n_TotalPrevalence_"][valid_idx]/sum(sero_data["n_TotalPrevalence_"][valid_idx])
        x3 = sero_data["UpperCI__TotalPrevalence_"][valid_idx]*sero_data["n_TotalPrevalence_"][valid_idx]/sum(sero_data["n_TotalPrevalence_"][valid_idx])
        un_lts[cidx, (ii)] = 0.01*sum(x1)*popu[cidx]/data_4[cidx, ii]
        un_ts[cidx, (ii)] = 0.01*sum(x2)*popu[cidx]/data_4[cidx, ii]
        un_uts[cidx, (ii)] = 0.01*sum(x3)*popu[cidx]/data_4[cidx, ii]
        

