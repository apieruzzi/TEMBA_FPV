# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 13:56:30 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import openpyxl

locs = ['EAPP', 'EG', 'ET', 'SD', 'SS']

idx=0

# File paths
file_fpv = r'results/ScenarioComparison/AggregatedExcels/ValuesFPV.xlsx'
file_hyd = r'results/ScenarioComparison/AggregatedExcels/ValuesHydro.xlsx'
output_filepath = f'results/ScenarioComparison/AggregatedExcels/ValuesRanked_{locs[idx]}.xlsx'

#  Scenario and variable lists
sheet_names_in = ['TotalGeneration', 'MaxGenerationShare', 'Onset',
               'HydroNumber', 'TotalGeneration', 
               'TotalCosts', 'Emissions']
sheet_names_out = ['TotalGeneration', 'MaxGenerationShare', 'Onset',
               'HydroNumber', 'TotalGenerationHyd', 
               'TotalCosts', 'Emissions']

scenario_list = ["TEMBA_ENB_EXT_High", "TEMBA_ENB_EXT_Low", "TEMBA_ENB_RCP26_dry",
                 "TEMBA_ENB_RCP26_wet", "TEMBA_ENB_RCP60_dry", "TEMBA_ENB_RCP60_wet", 
                 "TEMBA_ENB_ref", "TEMBA_ENB_EXT_HighNoFPV", "TEMBA_ENB_EXT_LowNoFPV", 
                 "TEMBA_ENB_RCP26_dryNoFPV", "TEMBA_ENB_RCP26_wetNoFPV", "TEMBA_ENB_RCP60_dryNoFPV", 
                 "TEMBA_ENB_RCP60_wetNoFPV", "TEMBA_ENB_refNoFPV"]

nrows = [6,6,6,6,6,2,2]
col_names = ['Total generation FPV','Max generation share FPV',
             'FPV onset year','Hydropower expansion','Hydropower total generation',
             'Total costs','Total emissions']
files = [file_fpv]*3+[file_hyd]*4

if idx==1:
    sheet_names_in.remove('HydroNumber')
    sheet_names_out.remove('HydroNumber')
    col_names.remove('Hydropower expansion')
    nrows=nrows[1:]
    files = files[0:-1]
    
if idx>=1:
    sheet_names_in.remove('TotalCosts') 
    sheet_names_in.remove('Emissions')
    sheet_names_out.remove('TotalCosts') 
    sheet_names_out.remove('Emissions')
    col_names.remove('Total costs') 
    col_names.remove('Total emissions')
    nrows=nrows[0:-2]
    files = files[0:-2]

#  Create new excel file
wb = openpyxl.Workbook()
wb.save(output_filepath)
writer = pd.ExcelWriter(output_filepath, mode='a', if_sheet_exists='overlay')


def create_table(file,sheet_name_in,sheet_name_out,nrows,col_name):
    values_list = []
      
    for i,scenario in enumerate(scenario_list[0:7]):
        df = pd.read_excel(file,sheet_name=sheet_name_in,
                           skiprows=i*nrows+i, nrows=nrows)
        if sheet_name_in == 'HydroNumber':
            values_list.append([df.columns[0][10:],df.iloc[1+idx,1]])
        else:
            values_list.append([df.columns[1][10:],df.iloc[idx,1]])
    
    tot_df = pd.DataFrame(values_list, columns=['Scenario',col_name])
    tot_df = tot_df.sort_values(by=[col_name], ascending=False, ignore_index=True)
    tot_df.to_excel(writer, sheet_name=sheet_name_out, index=False, startcol=0)
    
    if file == file_hyd:
        values_list=[]
        for i,scenario in enumerate(scenario_list[7:]):
            i=i+7
            df = pd.read_excel(file,sheet_name=sheet_name_in,
                               skiprows=i*nrows+i, nrows=nrows)
            if sheet_name_in == 'HydroNumber':
                values_list.append([df.columns[0][10:],df.iloc[1+idx,1]])
            else:
                values_list.append([df.columns[1][10:],df.iloc[idx,1]])
                
        tot_df = pd.DataFrame(values_list, columns=['Scenario',col_name])
        tot_df = tot_df.sort_values(by=[col_name], ascending=False, ignore_index=True)
        tot_df.to_excel(writer, sheet_name=sheet_name_out, index=False, startcol=3)


    tot_df = tot_df.set_index('Scenario')
    return tot_df

def create_scatter(df1,df2):
    df1.loc[:] = df1.loc[:]*0.001
    df2.loc[:] = df2.loc[:]*0.001
    df_comb = pd.concat([df1,df2])
    
    plt.figure(figsize=(10,6))
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    for i,scenario in enumerate(df_comb.index):
        plt.scatter(df_comb.iloc[i,0],df_comb.iloc[i,1],marker='o', 
                    color=colors[i], label=scenario)
    plt.xlabel('Total Emissions ($10^3$ MTCO2)')
    plt.ylabel('Total Costs ($10^3$ M$)')
    plt.title('Costs vs Emissions')
    plt.legend()
    plt.grid(True)
    plt.show()
        
df_list=[]
for i in range(len(sheet_names_in)):
    df_list.append(create_table(files[i],sheet_names_in[i],sheet_names_out[i],nrows[i],col_names[i]))

writer.close()