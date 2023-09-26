# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:33 2023

@author: Alessandro Pieruzzi
"""

import os
import pandas as pd
import openpyxl

folder = 'results/ScenarioComparison'

inputfiles = os.listdir('input_data')
scenario_list = [file[:-5] for file in inputfiles if file.endswith('xlsx') and not file.startswith('~')]

sheet_names = ['Metrics of built HP plants',
               'List of built HP plants',
               'TotalWaterConsumption',
               'Max values_hydro',
               'Max values_fpv']

filepath = 'results/ScenarioComparison/ValuesHydro.xlsx'
wb = openpyxl.Workbook()
wb.save(filepath)

filepath = 'results/ScenarioComparison/ValuesFPV.xlsx'
wb = openpyxl.Workbook()
wb.save(filepath)

writer_hyd = pd.ExcelWriter('results/ScenarioComparison/ValuesHydro.xlsx', mode='a', if_sheet_exists='overlay')
writer_fpv = pd.ExcelWriter('results/ScenarioComparison/ValuesFPV.xlsx', mode='a', if_sheet_exists='overlay')

for i, scenario in enumerate(scenario_list):
    filename = os.path.join(folder, f'Mixes_percentages_{scenario}.xlsx')
    
    # Create file with hydro info 
        # list of built plants, total number of built plants, total water consumption,
        #  max capacity, max generation, total generation
    
    df_metrics = pd.read_excel(filename, sheet_name=sheet_names[0], header=None)
    df_metrics = df_metrics.rename(columns={0:scenario, 1:''})
    df_metrics.to_excel(writer_hyd, sheet_name='HydroNumber', index=False, startrow=i*len(df_metrics)+1)
    # Create file with fpv info
        # max generation share, total max capacity, FPVOnset, total generation
    
    
    