# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 15:22:25 2023

@author: Alessandro Pieruzzi
"""

import os 
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn'

folder = r'data_sites'

file_list = os.listdir(folder)
file = file_list[0]

tot_list = []

for file in file_list: 
    loc_list = []
    loc_list.append(file.removesuffix('.csv'))
    
    filename = os.path.join(folder, file)
    df = pd.read_csv(filename, skiprows = 10)
    df = df[:8760] # remove notes in last rows
    df['time'] = pd.to_datetime(df['time'], format = '%Y%m%d:%H%M')
    df = df[['time','P']]
    df['month'] = df['time'].dt.to_period('M')
    df = df.set_index('time')

    # Extract by months and get representative day 
    tab_month=np.zeros((13,2))
    
    for i in range(1,13):
        
        if i <10:
            month = '2019-0' + str(i)
        else: 
            month = '2019-' + str(i)
            
        series = df.loc[df['month']== month]['P']
        ndays = int(len(series)/24)
        month = series.to_numpy(dtype=float).reshape(ndays,24)
        
        # Hourly profiles of power (W) for a representative day for each month:
        rep_day = np.mean(month, axis = 0)
        daypart1 = rep_day[9:18]
        idx = [0,1,2,3,4,5,6,7,8,18,19,20,21,22,23]
        daypart2 = rep_day[idx]
        
        # Capacity factors per day part for each month (capacity=1000Wp)
        cfd1 = sum(daypart1)/(9*1000)
        cfd2 = sum(daypart2)/(15*1000)
        
        tab_month[i] = [cfd1,cfd2]
    
    
    # Calculate season averages
    loc_list.append(np.mean(tab_month[3:6,0])) 
    loc_list.append(np.mean(tab_month[3:6,1]))
    loc_list.append(np.mean(tab_month[6:9,0]))
    loc_list.append(np.mean(tab_month[6:9,1]))
    loc_list.append(np.mean(tab_month[9:12,0]))
    loc_list.append(np.mean(tab_month[9:12,1]))
    loc_list.append(np.mean(tab_month[[12,1,2],0]))
    loc_list.append(np.mean(tab_month[[12,1,2],1]))


    # Create list with values for each location
    tot_list.append(loc_list)
    
    
# Save to excel 
cols = ['loc_name', 's1d1', 's1d2', 's2d1', 's2d2',
        's3d1', 's3d2', 's4d1', 's4d2']

df = pd.DataFrame(data=tot_list,columns=cols)

df.to_excel('CapacityFactors.xlsx')
    
    
    
    
    
    
    
    
    