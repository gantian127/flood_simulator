"""This is used to analyze the model outputs"""

import numpy as np
import os
from landlab.io import read_esri_ascii
import pandas as pd

# change working dir
os.chdir('/Users/tiga7385/Desktop/flood_simulator/results_analysis/')

# get watershed area
watershed_dem, watershed_dem_1d = read_esri_ascii(
    '/Users/tiga7385/Desktop/flood_simulator/geer_canyon.txt')
watershed_cell_number = len(np.where(watershed_dem_1d>0)[0])
watershed_area = watershed_cell_number * 30 * 30

# process outlet_discharge data
DF = pd.read_csv(r'/Users/tiga7385/Desktop/flood_simulator/output/outlet_discharge.csv')
DF['time_diff'] = DF['time'].diff()
DF.at[0, 'time_diff'] = DF['time'].iloc[0]
DF['discharge_cmm'] = DF['discharge'] * 60   # cms -> cmm
DF['discharge_vol'] = DF['discharge'] * DF['time_diff']
DF['cum_discharge_vol'] = DF.cumsum(axis=0)['discharge_vol']

# calculate percentage flow out of watershed
prec_rate = 59.2 /1000/3600 * 10 * 60  # mm/hr to m/s &  10min rain
cum_rain_vol = watershed_area * prec_rate
flow_vol = DF['cum_discharge_vol'].iloc[-1]
flow_perc = flow_vol/cum_rain_vol * 100
print(f'percentage of precipitation: {round(flow_perc,3)}%')

# export results with min as time step
DF['time_min'] = (DF['time']/60).astype(int)
DF_min = DF.drop_duplicates(subset=['time_min'])
DF_min.to_csv('discharge_analysis.csv')

