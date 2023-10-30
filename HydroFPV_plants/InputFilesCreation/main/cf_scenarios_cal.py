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

# Read data hydro
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
        path = os.path.join('boxplots_cf', country+scenario+'.png')
        plt.savefig(path)
        plt.close()
        
     # Lines        
    df_lines.transpose().plot(title=f'Average hydropower capacity factors vs season - {country}')
    path = os.path.join('boxplots_cf', country + ' hydro'+'.png')
    plt.savefig(path)
    
# Read data solar
file = 'CombinedHydroSolar_ref.csv'
df_read = pd.read_csv(os.path.join('Data',file))
df_temba = pd.read_excel(r'Created Files/TEMBA_ENB_ref.xlsx', sheet_name='CapacityFactor')
df_temba = df_temba.loc[np.where(df_temba['TECHNOLOGY'].str.contains('SO'))[0],:2015].reset_index(drop=True)
df_lines = pd.DataFrame(columns=['S1D1', 'S1D2','S2D1', 'S2D2', 'S3D1','S3D2', 'S4D1','S4D2'])
country_codes = dict({'EG':'EGYPT', 'ET':'ETHIOPIA', 'SD':'SUDAN', 'SS':'SOUTH SUDAN'})

for cc in country_codes.keys():
    # Calculate FPV means from csv file
    df = pd.DataFrame()
    for col in df_lines.columns:
        col_read = 'CF_S' + col[1:] 
        df[col] = df_read.iloc[np.where(df_read['Country'] == country_codes[cc])][col_read]
    df_lines.loc['Solar FPV (mean)'] = df.mean()
    
    # Take cf for other solar techs from temba file
    df_lines.loc['Solar utility'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOU1P03X')[0],2015].values
    df_lines.loc['Solar rooftop'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOV1F01X')[0],2015].values
    df_lines.loc['Solar CSP'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOC1P00X')[0],2015].values
    
    df_lines.transpose().plot(figsize=(10,8),title=f'Average solar capacity factors vs season - {country_codes[cc]}')
    path = os.path.join('boxplots_cf', country_codes[cc]+ ' solar'+ '.png')
    plt.savefig(path)



















    
    
    
    