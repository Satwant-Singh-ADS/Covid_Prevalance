import numpy as np
from scipy.signal import savgol_filter
from scipy.signal import find_peaks

import pandas as pd

import warnings
warnings.filterwarnings('ignore')

def hampel_filter_forloop(input_series, window_size=15, n_sigmas=4):
    
    n = len(input_series)
    new_series = input_series.copy()
    k = 1.4826 # scale factor for Gaussian distribution
    
    indices = []
    
    # possibly use np.nanmedian 
    for i in range((window_size),(n - window_size)):
        x0 = np.median(input_series[(i - window_size):(i + window_size)])
        S0 = k * np.median(np.abs(input_series[(i - window_size):(i + window_size)] - x0))
        if (np.abs(input_series[i] - x0) > n_sigmas * S0):
            new_series[i] = x0
            indices.append(i)
    
    return new_series, indices


def Smooth_epiData(data_4,smooth_factor = 14,week_correction = 1,week_smoothing = 1):
    
    if smooth_factor<=0:
        return data_4

    data_4 = pd.DataFrame(data_4).interpolate(method='linear',limit=2,limit_direction='both')

    deldata = np.diff(data_4, axis=1)

    deldata = pd.DataFrame(deldata).T

    data_4_s = data_4

    maxt = data_4.shape[1]

    date_map = np.ceil((np.arange(1, maxt) - np.mod(maxt-1, 7))/7).reshape(1,-1)

    cleandel = deldata




    if week_correction==1:
        for cid in range(len(data_4)): 
            week_dat = pd.DataFrame(data_4).loc[cid][list(range((maxt-1)%7,maxt,7))].diff()[1:]

            from scipy import signal



            clean_week_tmp,TF = hampel_filter_forloop(week_dat.to_numpy())

            week_dat_tmp = week_dat.to_list()

            for idx_out in TF:
                week_dat_tmp[idx_out] = np.nan

            clean_week = pd.DataFrame(week_dat_tmp).interpolate(method='linear')

            week_dat_1 = week_dat.to_list()
            week_dat_1.append(0)
            peak_idx = np.array([i for i in range(1, len(week_dat_1)-1) if week_dat_1[i] > week_dat_1[i-1] and week_dat_1[i] > week_dat_1[i+1]])


            tf_vals = []
            for i in TF:
                if i in peak_idx:
            #         print(i)
                    tf_vals.append(i)

        #     cid = 0

            for jj in tf_vals:
        #         print(jj)
                get_idx = [w for w in range(len(date_map[0])) if date_map[0][w]==jj]
        #         print(get_idx)
                for w in get_idx:
        #             print(cleandel.iloc[w][cid])
                    cleandel.iloc[w][cid] = clean_week.iloc[jj][0]/7
        #             print(cleandel.iloc[w][cid])

        deldata = cleandel

#     week_smoothing = 1

    # if week_smoothing == 1:

    if week_smoothing == 1:
        temp = np.cumsum(deldata.T, axis=1)

        temp['new'] = 0 ### add a constant colum with value 0 

        temp = temp[[list(temp.columns)[-1]]+list(temp.columns)[0:-1]]

        temp_array = np.array(temp)

        diff = np.diff(temp_array[:,(maxt-1)%7::7].T,axis=0)

        week_dat = pd.DataFrame(diff)

        xx = np.full((deldata.shape), np.nan)

        xx[int((maxt-1-7*week_dat.shape[0])+7)-1:maxt-1:7,:] = np.cumsum(week_dat, axis=0)

        xx = pd.DataFrame(xx).interpolate(method='linear',limit_direction='both')

        deldata.iloc[1:,:] = np.diff(xx, axis=0)

    deldata[deldata<0] = 0

    for state_idx in range(deldata.shape[1]):

        deldata[state_idx] = deldata[state_idx].rolling(smooth_factor,min_periods=0).mean()


    data_4_s = np.concatenate((data_4.iloc[:,:1].to_numpy(),np.cumsum(deldata,axis=0).T),axis=1)

    return data_4_s




def CDC_SERO_Function():
    import pandas as pd

    import requests
    import pandas as pd
    from datetime import datetime, timedelta
    import numpy as np

# Load sero data from CDC
    url = 'https://data.cdc.gov/api/views/mtc3-kq6r/rows.csv?accessType=DOWNLOAD'
    response = requests.get(url)
    open('dummy.csv', 'wb').write(response.content)
    sero_data = pd.read_csv('dummy.csv')

    import pickle

    filehandler = open("../Output_Pickles/data_4.pkl", 'rb') 
    #     print(a)
    data_4 = pickle.load(filehandler)


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


    abvs = pd.read_csv('../Static_Files/us_states_abbr_list.txt', header=None)

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

    popu_tmp = pd.read_csv("../Static_Files/us_states_population_data.txt",header=None)

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
#                         try:
                        un_lts[cidx, (ii)] = x1*popu[cidx]/data_4[cidx, ii]
                        un_ts[cidx, (ii)] = x2*popu[cidx]/data_4[cidx, ii]
                        un_uts[cidx, (ii)] = x3*popu[cidx]/data_4[cidx, ii]
#                         except:
#                             continue





    import numpy as np

    thisday = data_4.shape[1]

    un_ts[un_ts<1] = np.nan
    un_ts_s = pd.DataFrame(un_ts).interpolate(axis=1,limit_direction='both').fillna(1).to_numpy()


    un_lts[un_lts<1] = np.nan
    un_lts_s = pd.DataFrame(un_lts).interpolate(axis=1,limit_direction='both').fillna(1).to_numpy()

    un_uts[un_uts<1] = np.nan
    un_uts_s = pd.DataFrame(un_uts).interpolate(axis=1,limit_direction='both').fillna(1).to_numpy()


    dd_s = Smooth_epiData(data_4)
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
        np.sum(np.multiply(un_lts_s,ddata.to_numpy()),axis=1)/dd_s[:,-1],
        np.sum(np.multiply(un_ts_s,ddata.to_numpy()),axis=1)/dd_s[:,-1],
        np.sum(np.multiply(un_uts_s,ddata.to_numpy()),axis=1)/dd_s[:,-1]
    ]

    un_array[0][np.isnan(un_array[0])] = 1

    un_array[1][np.isnan(un_array[1])] = 1

    un_array[2][np.isnan(un_array[2])] = 1


    import pickle 
    with open("../Output_Pickles/true_new_infec.pkl", "wb") as f:
        pickle.dump(true_new_infec, f)
    with open("../Output_Pickles/un_array.pkl", "wb") as f:
        pickle.dump(un_array, f)
#     print(un_array)
    

#     filehandler = open("un_array.pkl", 'wb') 
#     #     print(a)
#     pickle.dump(un_array, filehandler)







