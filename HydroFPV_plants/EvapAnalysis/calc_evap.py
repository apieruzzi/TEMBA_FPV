# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 15:11:39 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.interpolate 
import openpyxl


files = os.listdir('result_files')
files_hydro = [file for file in files if 'hydro' in file]
files_fpv = [file for file in files if 'fpv' in file]
file_areas = 'FullAreasDataset.xlsx'

# Water losses for each country (mcm/km2)
data = {'EG':[5757.43/5248.37],
         'ET':[923.27/1966.50],
         'SD':[2718.96/796.06]}
df_wl = pd.DataFrame(data)

# Evaporation reduction rates 
coverage_perc = [0,0.1, 0.3, 0.5, 0.7, 1]
evap_red_perc = [0,0.18, 0.49, 0.73, 0.89, 1]
# data = {0.1:[0.18],
#         0.3:[0.49],
#         0.5:[0.73],
#         0.7:[0.89],
#         1:[1]   
#         }
# df_rates = pd.DataFrame(data)

for i in range(len(files_hydro)):
# =============================================================================
#     Assign area of each reservoir
# =============================================================================
    filepath = os.path.join('result_files',files_hydro[i])
    df_hydro = pd.read_csv(filepath)
    df_areas = pd.read_excel(file_areas)
    
    df_hydro[df_hydro != 0] = 1
    df_hydro['y'] = np.arange(2015,2071,1)
    df_hydro.set_index('y', inplace=True)
    
    # Select common columns
    df_hydro.rename(columns=lambda x: x.replace(' ', ''), inplace=True)
    cols = [col for col in df_areas.UnitName if col in df_hydro.columns]
    df_hydro = df_hydro[cols]  
    df_areas = df_areas[['UnitName','Area']].set_index('UnitName').transpose()
    df_areas = df_areas[cols]
    # Calculate area at each location each year
    prod = df_hydro.values * df_areas.values
    df_area_loc = df_hydro.copy()
    df_area_loc.loc[:,cols] = prod
    

# =============================================================================
#     Calculate evaporation from each reservoir
# =============================================================================
    plants_eg = ['Aswan1', 'Aswan2', 'HighAswanDam']
    plants_et = ['Finchaa', 'LakeTana-Beles', 'Tekeze1', 'Amarti-Neshe',
                 'Renaissance','Baro', 'Tekeze2']
    plants_sd = ['Sennar', 'KashmElGirba',
           'Roseires', 'JebelAulia', 'Merowe',
           'Kajbar', 'Shereik', 'Dagash', 'Dal', 'Mograt', 'Sabaloka']
    
    # Calculate the water losses per year  
    df_wl_loc = df_area_loc.copy()
    df_wl_loc.loc[:,plants_eg] = df_wl_loc.loc[:,plants_eg].values * df_wl['EG'].values
    df_wl_loc.loc[:,plants_et] = df_wl_loc.loc[:,plants_et].values * df_wl['ET'].values
    df_wl_loc.loc[:,plants_sd] = df_wl_loc.loc[:,plants_sd].values * df_wl['SD'].values
    
# =============================================================================
#     Calculate FPVs evaporation reductions
# =============================================================================
    # Calculate the area covered by FPVs
    filepath = os.path.join('result_files',files_fpv[i])
    df_fpv = pd.read_csv(filepath)
    df_fpv.rename(columns=lambda x: x.replace(' ', ''), inplace=True)
    df_fpv.rename(columns=lambda x: x.replace('FPV', ''), inplace=True)
    df_fpv.set_index('y', inplace=True)
    cols = df_fpv.columns[2:]
    df_fpv = df_fpv.loc[:,cols]
    df_fpv = df_fpv/0.1
    df_fpv.drop('Sor2',axis=1,inplace=True)
    
    # Calculate the cover percentage
    df_area_perc = df_fpv/df_area_loc
    df_area_perc.fillna(0,inplace=True)
    df_area_perc.replace([np.inf, -np.inf], 0, inplace=True)
    
    # Assign the evaporation reduction percentage
    interp = scipy.interpolate.interp1d(coverage_perc, evap_red_perc, fill_value='extrapolate', kind='cubic')
    df_reductions_perc = df_area_perc.copy()
    df_reductions_perc.loc[:] = interp(df_area_perc.values)

    
    # Calculate the volume of water saved
    df_wl_loc = df_wl_loc[df_reductions_perc.columns]
    df_reductions = df_reductions_perc.copy()
    df_reductions.loc[:] = df_reductions_perc.values * df_wl_loc.values
    df_reductions.loc['tot'] = df_reductions.sum()
    df_reductions.loc[:,'tot'] = df_reductions.sum(axis=1)
    
    # Calculate the total percentage of water saved
    df_wl_loc.loc['tot'] = df_wl_loc.sum()
    df_wl_loc.loc[:,'tot'] = df_wl_loc.sum(axis=1)
    
    df_reductions.loc['tot%'] = df_reductions.loc['tot'] / df_wl_loc.loc['tot']
    df_reductions.loc[:,'tot%'] = df_reductions.loc[:,'tot'] / df_wl_loc.loc[:,'tot']
    
    
# =============================================================================
#     Save to excel
# =============================================================================
    output_filepath = f'EvapReductions_{files_hydro[i][57:-4]}.xlsx'
    wb = openpyxl.Workbook()
    wb.save(output_filepath)
    writer = pd.ExcelWriter(output_filepath, mode='a', if_sheet_exists='overlay')
    
    df_area_perc.to_excel(writer, sheet_name='FPVArea %', index=True, startcol=0)
    df_reductions_perc.to_excel(writer, sheet_name='Reductions %', index=True, startcol=0)
    df_reductions.to_excel(writer, sheet_name='Reductions mcm', index=True, startcol=0)
    
writer.close()
