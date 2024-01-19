# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:41:53 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import os 
import matplotlib.pyplot as plt


filename = r'input_data/TEMBA_ENB_ref.xlsx'

acc_dem_df = pd.read_excel(filename, sheet_name='AccumulatedAnnualDemand')
spc_dem_df = pd.read_excel(filename, sheet_name='SpecifiedAnnualDemand')
spc_dem_prof_df = pd.read_excel(filename, sheet_name='SpecifiedDemandProfile')

years = np.arange(2015,2071,1)
countries = ['Egypt', 'Ethiopia', 'Sudan', 'South Sudan']
cc = ['EG', 'ET', 'SD', 'SS']

plt.figure(figsize=(10,8))
for i,country in enumerate(countries):
    os.makedirs(f'results/demand_profiles/{cc[i]}', exist_ok=True)
    acc_dem_df_country = acc_dem_df[acc_dem_df['FUEL'].str.contains(cc[i])]    
    # plt.figure(figsize=(15,10))
    # for row in range(len(acc_dem_df_country)):
    #     plt.plot(years, acc_dem_df_country.iloc[row,1:], label=acc_dem_df_country.iloc[row,0])
    #     plt.title('Accumulated annual demand external fuels - ' + country)
    #     plt.xlabel('year')
    #     plt.ylabel('PJ')
    #     plt.legend()
    # plt.savefig(f'results/demand_profiles/{cc[i]}/ext_fuels.png')
    
    spc_dem_df_country = spc_dem_df[spc_dem_df['FUEL'].str.contains(cc[i])]    
    plt.plot(years, spc_dem_df_country.iloc[:,1:].values.flatten(), label=country)
    plt.title('Total annual electricity demand')
    plt.xlabel('year')
    plt.ylabel('PJ')
    plt.legend()
    plt.savefig(f'results/demand_profiles/{cc[i]}/ele_annual.png')

plt.figure(figsize=(10,8))
for i,country in enumerate(countries):
    spc_dem_prof_df_country = spc_dem_prof_df[spc_dem_prof_df['FUEL'].str.contains(cc[i])]
    x = spc_dem_prof_df_country['TIMESLICE']
    y = spc_dem_prof_df_country[2015]
    plt.plot(x,y, label=country)
    plt.title('Total electricity demand per timeslice')
    plt.xlabel('timeslice')
    plt.ylabel('PJ')
    plt.legend()
    plt.savefig(f'results/demand_profiles/{cc[i]}/ele_timeslices.png')









