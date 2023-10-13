# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:33 2023

@author: Alessandro Pieruzzi
"""

import os
import pandas as pd
import openpyxl
import sys

# folder = 'results/ScenarioComparison'
folder = 'results/ScenarioComparison'
dest_folder = 'AggregatedExcels'

inputfiles = os.listdir('input_data')
scenario_list = [file[:-5] for file in inputfiles if file.endswith('xlsx') and not file.startswith('~')]

sheet_names = ['Metrics of built HP plants',
               'List of built HP plants',
               'TotalWaterConsumption',
               'Max values_hydro',
               'Max values_fpv']

dest_path = os.path.join(folder, dest_folder)
os.makedirs(dest_path, exist_ok=True)

filepath_hyd = os.path.join(dest_path,'ValuesHydro.xlsx')
wb = openpyxl.Workbook()
wb.save(filepath_hyd)

filepath_fpv = os.path.join(dest_path,'ValuesFPV.xlsx')
wb = openpyxl.Workbook()
wb.save(filepath_fpv)

writer_hyd = pd.ExcelWriter(filepath_hyd, mode='a', if_sheet_exists='overlay')
writer_fpv = pd.ExcelWriter(filepath_fpv, mode='a', if_sheet_exists='overlay')
skip = 0
j=1

for i, scenario in enumerate(scenario_list):
    filename = os.path.join(folder, f'Mixes_percentages_{scenario}.xlsx')
    
    # Create file with hydro info 
        # list of built plants, total number of built plants, total water consumption,
        #  max capacity, max generation, total generation
    
    df_metrics = pd.read_excel(filename, sheet_name=sheet_names[0], header=None)
    df_metrics = df_metrics.rename(columns={0:scenario, 1:''})
    df_metrics.to_excel(writer_hyd, sheet_name='HydroNumber', index=False, startrow=i*(len(df_metrics)+1)+i)
    
    df_list_hp = pd.read_excel(filename, sheet_name=sheet_names[1])
    df_list_hp = df_list_hp.rename(columns={'tech_code':scenario, 'tech_name':''})
    df_list_hp.to_excel(writer_hyd, sheet_name='HydroList', index=False, startrow=skip)
    skip = skip + (len(df_list_hp)+1)+j
    j+=1

    df_water = pd.read_excel(filename, sheet_name=sheet_names[2])
    df_water = df_water.rename(columns={'Total Water Consumption':scenario})
    df_water.to_excel(writer_hyd, sheet_name='TotalWaterConsumption', index=False, startrow=i*(len(df_water)+1)+i)
    
    df_totgen = pd.read_excel(filename, sheet_name=sheet_names[3], index_col='Unnamed: 0')
    df_totgen = df_totgen['TotalGeneration']
    df_totgen.name = scenario
    df_totgen.to_excel(writer_hyd, sheet_name='TotalGeneration', startrow=i*(len(df_totgen)+1)+i)
    
    df_maxgen = pd.read_excel(filename, sheet_name=sheet_names[3], index_col='Unnamed: 0')
    df_maxgen = df_maxgen[['MaxGeneration', 'YearG']]
    df_maxgen = df_maxgen.rename(columns={'MaxGeneration':scenario, 'YearG':''})
    df_maxgen.to_excel(writer_hyd, sheet_name='MaxGeneration', startrow=i*(len(df_maxgen)+1)+i)
    
    df_maxcap = pd.read_excel(filename, sheet_name=sheet_names[3], index_col='Unnamed: 0')
    df_maxcap = df_maxcap[['MaxCapacity', 'YearC']]
    df_maxcap = df_maxcap.rename(columns={'MaxCapacity':scenario, 'YearC':''})
    df_maxcap.to_excel(writer_hyd, sheet_name='MaxCapacity', startrow=i*(len(df_maxcap)+1)+i)
    
    
    # Create file with fpv info
        # max generation share, total max capacity, FPVOnset, total generation
        
    df_maxgen_share = pd.read_excel(filename, sheet_name=sheet_names[4], index_col='Unnamed: 0')
    df_maxgen_share = df_maxgen_share[['MaxGenerationShare', 'YearGS']]
    df_maxgen_share = df_maxgen_share.rename(columns={'MaxGenerationShare':scenario, 'YearGS':''})
    df_maxgen_share.to_excel(writer_fpv, sheet_name='MaxGenerationShare', startrow=i*(len(df_maxgen_share)+1)+i)
    
    df_maxcap_share = pd.read_excel(filename, sheet_name=sheet_names[4], index_col='Unnamed: 0')
    df_maxcap_share = df_maxcap_share[['MaxCapacityShare', 'YearCS']]
    df_maxcap_share = df_maxcap_share.rename(columns={'MaxCapacityShare':scenario, 'YearCS':''})
    df_maxcap_share.to_excel(writer_fpv, sheet_name='MaxCapacityShare', startrow=i*(len(df_maxcap_share)+1)+i)
    
    df_totgen = pd.read_excel(filename, sheet_name=sheet_names[4], index_col='Unnamed: 0')
    df_totgen = df_totgen['TotalGeneration']
    df_totgen.name = scenario
    df_totgen.to_excel(writer_fpv, sheet_name='TotalGeneration', startrow=i*(len(df_totgen)+1)+i)
    
    df_maxcap = pd.read_excel(filename, sheet_name=sheet_names[4], index_col='Unnamed: 0')
    df_maxcap = df_maxcap[['MaxCapacity', 'YearC']]
    df_maxcap = df_maxcap.rename(columns={'MaxCapacity':scenario, 'YearC':''})
    df_maxcap.to_excel(writer_fpv, sheet_name='MaxCapacity', startrow=i*(len(df_maxcap)+1)+i)
    
    df_maxgen = pd.read_excel(filename, sheet_name=sheet_names[4], index_col='Unnamed: 0')
    df_maxgen = df_maxgen[['MaxGeneration', 'YearG']]
    df_maxgen = df_maxgen.rename(columns={'MaxGeneration':scenario, 'YearG':''})
    df_maxgen.to_excel(writer_fpv, sheet_name='MaxGeneration', startrow=i*(len(df_maxgen)+1)+i)
    
    df_onset = pd.read_excel(filename, sheet_name=sheet_names[4], index_col='Unnamed: 0')
    df_onset = df_onset['Onset']
    df_onset.name = scenario
    df_onset.to_excel(writer_fpv, sheet_name='Onset', startrow=i*(len(df_onset)+1)+i)

    # Add emission calculations
    filename_emi = f'results/export_{scenario}/barcharts/EAPP/EAPP-Annual Emissions-{scenario}.csv'
    df = pd.read_csv(filename_emi)
    df.loc['tot'] = df.sum()
    value = df.loc['tot'][-1]
    df = pd.DataFrame({scenario:[value]}, index=['TotalEmissions'])
    df.to_excel(writer_hyd, sheet_name='Emissions', startrow=i*(len(df)+1)+i)
    
    # Add total costs
    df_cost = pd.read_excel(filename, sheet_name=sheet_names[-1])
    df_cost.to_excel(writer_hyd, sheet_name='TotalCosts', index=False, startrow=i*(len(df_cost)+1)+i)
    
writer_hyd.close()
writer_fpv.close()

















