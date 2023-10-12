# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 11:52:10 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Import files 
file_list = os.listdir('Data')
file_list = [file for file in file_list if file.startswith('Combined')]


countries = ['EGYPT', 'ETHIOPIA', 'SUDAN', 'SOUTH SUDAN']
seasons = [1,2,3,4]

# Read data
for country in countries:
    df_lines = pd.DataFrame(columns=['S1','S2', 'S3', 'S4'])
    for file in file_list:
        scenario = file[19:-4]
        df_read = pd.read_csv(os.path.join('Data',file))
        df = pd.DataFrame()
        for season in seasons:
            col = 'CF_H' + str(season) + 'D1' 
            col_out = 'S' + str(season)
            df[col_out] = df_read.iloc[np.where(df_read['Country'] == country)][col]
        
        df_lines.loc[scenario] = df.mean()
        # Boxplots
        plt.figure()
        plt.boxplot(df)
        plt.xlabel('Season')
        plt.ylabel('Capacity factor')
        plt.title(f'Capacity factor variations - {country} - {scenario}')
        path = os.path.join('boxplots', country+scenario+'.png')
        plt.savefig(path)
        plt.close()
        
     # Lines        
    df_lines.transpose().plot(title=f'Average capacity factors vs season - {country}')
    path = os.path.join('boxplots', country + '.png')
    plt.savefig(path)
    
    
    
    
    
    