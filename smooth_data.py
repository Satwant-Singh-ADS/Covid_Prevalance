import numpy as np
from scipy.signal import savgol_filter

def smooth_epidata(data_4, smooth_factor=1, week_correction=1, week_smoothing=1):
    #SMOOTH_EPIDATA removes outliers and smoothes

    data_4 = np.interp(np.arange(len(data_4)), np.flatnonzero(~np.isnan(data_4)), data_4[~np.isnan(data_4)])
    deldata = np.diff(data_4, axis=1)

    data_4_s = data_4

    maxt = data_4.shape[1]
    date_map = (np.arange(maxt-1) - (maxt-1) % 7) // 7

    if isinstance(smooth_factor, (int,float)):
        cleandel = deldata

        if week_correction == 1:
            for cid in range(data_4.shape[0]):
                week_dat = np.diff(data_4[cid, (maxt-1) % 7::7])
                clean_week = savgol_filter(week_dat, 15, 4)
                peak_idx = np.flatnonzero(np.r_[False, clean_week[1:] > clean_week[:-1]] & np.r_[clean_week[:-1] > clean_week[1:], False])

                tf_vals = np.intersect1d(np.flatnonzero(TF), peak_idx)

                for jj in range(len(tf_vals)):
                    cleandel[date_map==tf_vals[jj], cid] = clean_week[tf_vals[jj]]/7

            deldata = cleandel

        if week_smoothing == 1:
            temp = np.cumsum(deldata, axis=1)
            week_dat = np.diff(temp[:, (maxt-1) % 7::7], axis=1)
            xx = np.empty(deldata.shape)
            xx[:, ((maxt-1)-7*week_dat.shape[1]+7):7:maxt-1] = np.cumsum(week_dat, axis=1)
            xx = np.interp(np.arange(len(xx)), np.flatnonzero(~np.isnan(xx)), xx[~np.isnan(xx)])
            deldata[1:] = np.diff(xx, axis=1)

        deldata[deldata < 0] = 0
        data_4_s = np.cumsum(np.convolve(deldata, np.ones(smooth_factor)/smooth_factor, mode='valid'), axis=1)
    else:
        cleandel = deldata
        for cid in range(data_4.shape[0]):
            xx = cleandel[:, cid]
            t = savgol_filter(xx, 7, 3)
            t[t<0] = 0
            data_4_s[cid, :] = np.cumsum(t)
