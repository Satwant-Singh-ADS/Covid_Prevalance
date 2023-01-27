import numpy as np
from scipy.signal import savgol_filter
from csaps import csaps


def smooth_epidata(data_4, smooth_factor=1, week_correction=1, week_smoothing=1):
    if week_smoothing is None:
        week_smoothing = 1
    if week_correction is None:
        week_correction = 1
    data_4 = np.interp(np.nan, (np.nan, np.nan), data_4)
    deldata = np.diff(data_4, axis=1)
    data_4_s = data_4
    maxt = data_4.shape[1]
    date_map = np.ceil((np.arange(1, maxt) - np.mod(maxt-1, 7))/7)
    if isinstance(smooth_factor, (int, float)):
        cleandel = deldata
        if week_correction == 1:
            for cid in range(data_4.shape[0]):
                week_dat = np.diff(data_4[cid, int(np.mod(maxt-1, 7))::7])
                clean_week = savgol_filter(week_dat, 15, 3)
                peak_idx = np.array([i for i in range(1, len(week_dat)) if week_dat[i] > week_dat[i-1] and week_dat[i] > week_dat[i+1]])
                tf_vals = np.intersect1d(np.where(week_dat != clean_week)[0], peak_idx)
                for jj in range(tf_vals.shape[0]):
                    cleandel[date_map == tf_vals[jj], cid] = clean_week[tf_vals[jj]]/7
            deldata = cleandel
        if week_smoothing == 1:
            temp = np.cumsum(deldata, axis=1)
            week_dat = np.diff(temp[:, int(np.mod(maxt-1, 7))::7], axis=1)
            xx = np.full((deldata.shape), np.nan)
            xx[int((maxt-1)-7*week_dat.shape[1]+7)::7,:] = np.cumsum(week_dat, axis=1)
            xx = np.interp(np.nan, (np.nan, np.nan), xx)
            deldata[1:,:] = np.diff(xx, axis=1)
        deldata[deldata < 0] = 0
        data_4_s = np.concatenate((data_4[:,:1], np.cumsum(np.convolve(deldata, np.ones(smooth_factor)/smooth_factor, mode='same'), axis=1)), axis=1)
    else:
        cleandel = deldata
        for cid in range(data_4.shape[0]):
            xx = cleandel[:, cid]
            t = csaps(np.arange(len(xx)), xx, 0.00001, np.arange(len(xx)))
            t[t<0] = 0
            t = movmean(t, 7)
            data_4_s[cid, :] = [data_4[cid, 0] cumsum(t, 2)]
