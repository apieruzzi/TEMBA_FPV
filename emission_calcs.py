# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 15:59:27 2023

@author: Alessandro Pieruzzi
"""

# =============================================================================
# Script to calculate carbon emissions and land use timeseries
# =============================================================================

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import openpyxl
pd.options.mode.chained_assignment = None  # default='warn'
plt.rcParams.update({'font.size': 16})

# Scenarios
listf = os.listdir('input_data')
listf = [file for file in listf if file.endswith('.xlsx') and not file.startswith('~')]
listf = [file for file in listf if 'ref.' not in file]
listf = listf[-2:] + listf
listf = listf[:-2]
countries = ['ENB', 'EG', 'ET', 'SD', 'SS']
scenarios = [file[10:-5] for file in listf]
# Years
years = np.arange(2022,2066,1)

listf=listf[-2:]
scenarios=scenarios[-2:]

# df_save_co2 = pd.DataFrame(index=scenarios)
# df_save_land = pd.DataFrame(index=scenarios)

output_filepath = 'results/TotEmi.xlsx'
wb = openpyxl.Workbook()
wb.save(output_filepath)
writer = pd.ExcelWriter(output_filepath, mode='a', if_sheet_exists='overlay')

# Import emission file
for country in countries:
    plt.figure(figsize=(10,8))
    for i,file in enumerate(listf):
        # Import data
        result_file = os.path.join('results', file[:-5],'AnnualEmissions.csv')
        df = pd.read_csv(result_file)
    
        # Transform table
        df = df.pivot_table(index='y', columns='e',
                            values='AnnualEmissions',
                            aggfunc='sum').fillna(0)
        df = df.loc[years]
        
        # Select emissions
        df_co2 = df[[col for col in df.columns if 'CO2' in col]]
        df_land = df[[col for col in df.columns if 'LAND' in col]]
        
        # Calculate totals 
        df_co2.loc[:,'ENB'] = df_co2.sum(axis=1)
        df_land.loc[:,'ENB'] = df_land.sum(axis=1)
        
        # Select country
        df_co2 = df_co2[[col for col in df_co2.columns if country in col]]

        
        # Plot
        plt.plot(df_co2.index,df_co2.iloc[:],label=scenarios[i])
        plt.xlabel('year')
        plt.ylabel('CO2 emissions (MT)')
        plt.legend()
        # plt.title(country)
        
        # plt.plot(df_land.index,df_land.iloc[:,-1],label=scenarios[i])
        # plt.xlabel('year')
        # plt.ylabel('Land use (ha)')
        # plt.legend()
        
        # Calculate tot and save to excel
    #     df_save_co2.loc[scenarios[i],'TotEmissions'] = df_co2.sum().iloc[0]
    #     df_save_land.loc[scenarios[i],'TotLandUse'] = df_land.iloc[:,-1].sum()
        
    # df_save_co2.to_excel(writer,
    #                       sheet_name=f'{country}-CO2')
    # df_save_land.to_excel(writer,
    #                       sheet_name=f'{country}-land')
    
writer.close()    
        
        
        
        
        
        
        
        
        
        
        

