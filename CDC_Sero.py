import pandas as pd
data_4 = pd.read_csv("matlab_python_poc/Covid_Prevalance/data_4.csv",header=None)

import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
# Load sero data from CDC
url = 'https://data.cdc.gov/api/views/mtc3-kq6r/rows.csv?accessType=DOWNLOAD'
response = requests.get(url)
open('dummy.csv', 'wb').write(response.content)
sero_data = pd.read_csv('dummy.csv')


sero_data['Region Abbreviation_tmp'] = sero_data['Region Abbreviation'].str[:2]

sero_data['x1_tmp'] = sero_data["Lower CI %[Total Prevalence]"]*sero_data["n [Total Prevalence]"]

sero_data['x2_tmp'] = sero_data["Rate %[Total Prevalence]"]*sero_data["n [Total Prevalence]"]

sero_data['x3_tmp'] = sero_data["Upper CI  %[Total Prevalence]"]*sero_data["n [Total Prevalence]"]

tmp = sero_data.groupby(['Region Abbreviation_tmp','Median \nDonation Date']).agg({"n [Total Prevalence]":"sum",
                                                   }).reset_index()

sero_subset = sero_data[['Region Abbreviation_tmp','Median \nDonation Date','x1_tmp','x2_tmp','x3_tmp']]

# sero_subset['key'] = sero_subset['Region Abbreviation_tmp']+"_"+sero_subset['Median \nDonation Date']

new_df = pd.merge(sero_subset, tmp,  how='left', left_on=['Region Abbreviation_tmp','Median \nDonation Date'],\
                  right_on = ['Region Abbreviation_tmp','Median \nDonation Date'])

new_df['x1'] = (new_df['x1_tmp']/new_df['n [Total Prevalence]'])*0.01
new_df['x2'] = (new_df['x2_tmp']/new_df['n [Total Prevalence]'])*0.01
new_df['x3'] = (new_df['x3_tmp']/new_df['n [Total Prevalence]'])*0.01


sero_data_processed = new_df.groupby(['Region Abbreviation_tmp','Median \nDonation Date']).agg({"x1":"sum",\
                                                                                                "x2":"sum",\
                                                                                                "x3":"sum",\
                                                   }).reset_index()


abvs = pd.read_csv('us_states_abbr_list.txt', header=None)

state_map = dict(zip(abvs[0], range(len(abvs))))
try:
    xx = sero_data_processed['Median \nDonation Date']
except:
    xx = sero_data_processed['MedianDonationDate']
whichday = [0]*len(xx)

for ii in range(len(xx)):
    whichday[ii] = (datetime.strptime(xx[ii], '%m/%d/%Y') - datetime(2020, 1, 23)).days



un_ts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan
un_lts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan
un_uts = np.empty((data_4.shape[0],data_4.shape[1]))*np.nan

sero_data_processed['idx'] = sero_data_processed['Median \nDonation Date'].apply(lambda x :\
                                    (datetime.strptime(x, '%m/%d/%Y') - datetime(2020, 1, 23)).days
                                                                                )


sero_data_processed['cidx'] = sero_data_processed['Region Abbreviation_tmp'].apply(lambda x : \
                                                   state_map.get(x,None))

popu_tmp = pd.read_csv("matlab_python_poc/Covid_Prevalance/us_states_population_data.txt",header=None)

popu = popu_tmp[0].to_list()

for cidx in range(data_4.shape[0]):
    for ii in range(data_4.shape[1]):
#         print(cidx)
        if len(sero_data_processed[sero_data_processed['cidx'] == cidx])>0:
            if len(sero_data_processed[sero_data_processed['idx'] == ii])>0:
                data_subset = sero_data_processed[(sero_data_processed['cidx']==cidx) & (sero_data_processed['idx']==ii)]
                if len(data_subset)>0:
                    x1 = data_subset['x1'].values[0]
                    x2 = data_subset['x2'].values[0]
                    x3 = data_subset['x3'].values[0]                
    #                     print(x1*popu[cidx])
    #                 x2 = 
#                     try:
#                         data_4[cidx, ii]
#                         print("aaa",cidx,ii)
                        
#                     except:
#                         print(cidx,ii)
#                         break
                    try:
                        un_lts[cidx, (ii)] = x1*popu[cidx]/data_4.iloc[cidx, ii]
                        un_ts[cidx, (ii)] = x2*popu[cidx]/data_4.iloc[cidx, ii]
                        un_uts[cidx, (ii)] = x3*popu[cidx]/data_4.iloc[cidx, ii]
                    except:
                        continue
                
        
        


import numpy as np

thisday = data_4.shape[1]

un_ts[un_ts<1] = np.nan
un_ts_s = pd.DataFrame(un_ts).interpolate(axis=1,limit_direction='both').fillna(1).to_numpy()


un_lts[un_lts<1] = np.nan
un_lts_s = pd.DataFrame(un_lts).interpolate(axis=1,limit_direction='both').fillna(1).to_numpy()

un_uts[un_uts<1] = np.nan
un_uts_s = pd.DataFrame(un_uts).interpolate(axis=1,limit_direction='both').fillna(1).to_numpy()


dd_s = data_4
ddata = np.diff(dd_s)


temp = pd.DataFrame(ddata)
temp['new'] = 0 ### add a constant colum with value 0 

ddata = temp[[list(temp.columns)[-1]]+list(temp.columns)[0:-1]]



true_new_infec = [
    pd.DataFrame(np.multiply(un_lts_s,ddata.to_numpy())).rolling(window=28,axis=1,min_periods=0).mean(),
    pd.DataFrame(np.multiply(un_ts_s,ddata.to_numpy())).rolling(window=28,axis=1,min_periods=0).mean(),
    pd.DataFrame(np.multiply(un_uts_s,ddata.to_numpy())).rolling(window=28,axis=1,min_periods=0).mean()
]



un_array = [
    np.sum(np.multiply(un_lts_s,ddata.to_numpy()),axis=1)/dd_s.iloc[:,-1].to_numpy(),
    np.sum(np.multiply(un_ts_s,ddata.to_numpy()),axis=1)/dd_s.iloc[:,-1].to_numpy(),
    np.sum(np.multiply(un_uts_s,ddata.to_numpy()),axis=1)/dd_s.iloc[:,-1].to_numpy()
]

un_array[0][np.isnan(un_array[0])] = 1

un_array[1][np.isnan(un_array[1])] = 1

un_array[2][np.isnan(un_array[2])] = 1





