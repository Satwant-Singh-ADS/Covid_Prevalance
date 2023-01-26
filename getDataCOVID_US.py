import datetime
import requests
import pandas as pd

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
  
  return tableConfirmed,tableDeaths,tableRecovered,time

