import numpy as np
import pandas as pd
import datetime
import requests

def getDataCOVID_US():
    Ndays = (datetime.datetime.now() - datetime.datetime(2020,1,22)).days - 1
    address = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
    ext = '.csv'

    filename = 'time_series_covid19_confirmed_US'
    url = address + filename + ext
    response = requests.get(url)
    with open('dummy.csv', 'w') as f:
        f.write(response.text)

    tableConfirmed = pd.read_csv('dummy.csv')

    Ndays = (datetime.datetime.now() - datetime.datetime(2020,1,22)).days - 1
    address = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
    ext = '.csv'

    # Options and names for confirmed
    filename = 'time_series_covid19_confirmed_US'
    fullName = address + filename + ext
    url = requests.get(fullName)
    open('dummy.csv', 'wb').write(url.content)
    tableConfirmed = pd.read_csv('dummy.csv')

    # Options and names for deceased
    filename = 'time_series_covid19_deaths_US'
    fullName = address + filename + ext
    url = requests.get(fullName)
    open('dummy.csv', 'wb').write(url.content)
    tableDeaths = pd.read_csv('dummy.csv')

    # Get time
    start_date = datetime.datetime(2020,1,22)
    end_date = datetime.datetime.now() - datetime.timedelta(days=1)
    time = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date - start_date).days)]

    # So far no data on recovered
    tableRecovered = []

    return tableConfirmed,tableDeaths



# [tableConfirmed,tableDeaths,tableRecovered,time] = getDataCOVID_US()
tableConfirmed, tableDeaths = getDataCOVID_US()

# countries = readcell('us_states_list.txt', 'Delimiter','')
with open('us_states_list.txt', 'r') as f:
    countries = f.read().splitlines()

# passengerFlow = load('us_states_travel_data.txt')
passengerFlow = pd.read_csv("us_states_travel_data.txt",header=None).to_numpy()
passengerFlow = passengerFlow - np.diag(np.diag(passengerFlow))

# popu = load('us_states_population_data.txt')
popu = np.loadtxt('us_states_population_data.txt')

# state_ab = readcell('us_states_abbr_list.txt', 'Delimiter','')
with open('us_states_abbr_list.txt', 'r') as f:
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
