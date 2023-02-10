# Covid-19 Prevalance
This code estimates true new infections of COVID-19 over time in each state of the US based on a combination of wastewater data and seroprevalence data. 

## Summary
The code obtains the COVID-19 wastewater concentration data, smooths it and scales it in a way that during the early part of the pandemic the time-series matches with that obtained by processing seroprevalence data. The output is `ww_ts`, which holds the time series data of estimated new COVID-19 infections for each state over days since January 23, 2020. 
<br>

The Python code uses the following libraries:

```
csaps==1.1.0
numpy==1.23.3
pandas==1.5.0
requests==2.28.1
scipy==1.10.0
```

### The following hyperparameters can be reset by the user:

`wlag`: The expected lag between the reported cases time-series and the wastewater time-series <br>
`eq_start`: The start date for matching against seroprevalence data  <br>
`eq_end`: The end date for matching against seroprevalence data  <br>
`smooth_factor`: Smoothing window in number of days <br>

### The code loads data from several sources:
1. Biobot.io [COVID-19 Wastewater Concentration](https://raw.githubusercontent.com/biobotanalytics/covid19-wastewater-data/master/wastewater_by_county.csv)
2. [2020-2021 Nationwide Blood Donor Seroprevalence Survey Infection-Induced Seroprevalence Estimates](https://data.cdc.gov/api/views/mtc3-kq6r/rows.csv?accessType=DOWNLOAD)
3. `us_states_population_data.txt`: List of populations by state
4. `us_states_abbr_list.txt`: List of state abbreviations
5. `fips_table.txt`: FIPS information on US counties and states

### There are total 4 Python scripts in the Folder.
  `python Prevalence_ww.py` executes everything

#### Secondary files

`CDC_Sero.py`: Loads and processes seroprevalence data <br>
`latest_us_data.py`: Loads recent time-series for COVID-19 reported cases in the states of the US <br>
`smooth_epidata.py`: Preprocessing function to smooth and remove outliers from time-series <br>

All the secondary files are called in the main `prevalance_ww.py`` and necessary files are stored as Pickle objects in Output_Pickles Folder.

### List of output files
```
1. true_new_infec_ww.pkl
2. true_new_infec_final.pkl
3. un_array.pkl
```





