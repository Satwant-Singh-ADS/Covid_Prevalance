# Covid-19 Prevalance
This code processes wastewater data to estimate the SARS-CoV-2 concentration over time for each state in the United States.
The resulting data can be used to create heatmaps that can be used to visualize changes in the SARS-CoV-2 concentration over time.
These heatmaps can provide valuable insights into the spread of the virus, allowing public health officials to make informed decisions about how to respond to the pandemic.
<br>

This code is written in Python and uses the following libraries:

<br>
csaps==1.1.0<br>
numpy==1.23.3<br>
pandas==1.5.0<br>
requests==2.28.1<br>
scipy==1.10.0<br>

### Hyperparameters for the code are defined and include:

wlag
eq_start
eq_end
smooth_factor

### The code loads data from several sources:

us_states_population_data.txt
us_states_abbr_list.txt
reich_fips.txt
wastewater_by_county.csv

The code manipulates the loaded data and defines two matrices (ww_ts and ww_pres) of size (# of states x days).

### There are total 4 Python scripts in the Folder.

Prevalence_ww.py is the main file which user needs to run-
  python Prevalence_ww.py executes everything

#### Secondary files

1. CDC_Sero.py
2. getDataCOVID_US.py
3. latest_us_data.py
4. smooth_epidata.py

All the secondary files are called in the main Prevalance_ww file and necessary files are stored as Pickle objects in Output_Pickles Folder.

### List of output files
1. true_new_infec_ww.pkl
2. true_new_infec_final.pkl
3. un_array.pkl


The code also imports data from a file named latest_us_data.py and loads it into a pickle file named data_4.pkl.

Any missing data or data from dates before 2020-01-23 and for unavailable states is ignored in the code.
The code is meant to extract COVID-19 wastewater data, clean and process it, and prepare it for analysis.
The code takes data from various sources, including a CSV file from a GitHub repository, and a data_4 object from a pickle file. 
It then calculates the time series of wastewater data for each state and the corresponding day since January 23, 2020. 
The resulting data is stored in two matrices, ww_ts and ww_pres, where ww_ts holds the time series data, and ww_pres holds information about whether data is available for a state and a corresponding day. 
The data is finally set to NaN values in ww_ts if the corresponding value in ww_pres is less than 1. 
The processed data can then be used for further analysis, such as forecasting and modeling.



