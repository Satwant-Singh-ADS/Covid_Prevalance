import numpy as np
import pandas as pd
import datetime
import requests

from getDataCOVID_US import *

def get_latest_data():
# [tableConfirmed,tableDeaths,tableRecovered,time] = getDataCOVID_US()
    tableConfirmed, tableDeaths = getDataCOVID_US()

    # countries = readcell('us_states_list.txt', 'Delimiter','')
    with open('../Static_Files/us_states_list.txt', 'r') as f:
        countries = f.read().splitlines()

    # passengerFlow = load('us_states_travel_data.txt')
    passengerFlow = pd.read_csv("../Static_Files/us_states_travel_data.txt",header=None).to_numpy()
    passengerFlow = passengerFlow - np.diag(np.diag(passengerFlow))

    # popu = load('us_states_population_data.txt')
    popu = np.loadtxt('../Static_Files/us_states_population_data.txt')

    # state_ab = readcell('us_states_abbr_list.txt', 'Delimiter','')
    with open('../Static_Files/us_states_abbr_list.txt', 'r') as f:
        state_ab = f.read().splitlines()

    # Extract confirmed cases from JHU data
    vals = tableConfirmed.iloc[:, 12:].to_numpy() # Day-wise values
    if np.all(np.isnan(vals[:, -1])):
        vals = vals[:, :-1]
    data_4 = np.zeros((len(countries), vals.shape[1]))
    lats = np.zeros(len(countries))
    longs = np.zeros(len(countries))
    for cidx, country in enumerate(countries):
        idx = tableConfirmed["Province_State"].str.contains(countries[cidx], case=False)
        if idx.sum() == 0:
            print(f'{countries[cidx]} not found')
        data_4[cidx, :] = vals[idx, :].sum(axis=0)
        lats[cidx] = tableConfirmed.loc[idx, 'Lat'].mean()
        longs[cidx] = tableConfirmed.loc[idx, 'Long_'].mean()

    # Extract deaths from JHU data
    vals = tableDeaths.iloc[:, 14:].to_numpy() # Day-wise values
    if np.all(np.isnan(vals[:, -1])):
        vals = vals[:, :-1]
    deaths = np.zeros((len(countries), vals.shape[1]))
    for cidx, country in enumerate(countries):
        idx = tableDeaths["Province_State"].str.contains(countries[cidx], case=False)
        if idx.sum() == 0:
            print(f'{countries[cidx]} not found')
        deaths[cidx, :] = vals[idx, :].sum(axis=0)
    data_4_JHU = data_4
    deaths_JHU = deaths
    return data_4_JHU


import pickle  

def get_data():
    a = get_latest_data()
    filehandler = open("../Output_Pickles/data_4.pkl", 'wb') 
#     print(a)
    pickle.dump(a, filehandler)

#### Add below lines to whereever you want to call this Python file
# from latest_us_data import *
# #get_data()
# filehandler = open("data_4.pkl", 'rb') 
# #     print(a)
# data_4 = pickle.load(filehandler)
