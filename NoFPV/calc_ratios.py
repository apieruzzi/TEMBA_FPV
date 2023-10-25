# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 15:45:54 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Scenarios
listf = os.listdir('input_data')
listf = [file for file in listf if file.endswith('.xlsx') and not file.startswith('~')]
countries = ['EG', 'ET', 'SD']

# Get location codes and names
df_names = pd.read_csv(r'input_data/CombinedHydroSolar_ref.csv')
names = df_names['Unit Name']
codes = df_names['loc_codes']
names_dict = dict(zip(codes,names))

def calc_df(file,country):
    input_file = f'input_data/{file}'
    result_filename = 'TotalCapacityAnnual.csv'
    result_file = os.path.join(f'results/{file[:-5]}',result_filename)
    
    input_df = pd.read_excel(input_file, sheet_name='TotalAnnualMaxCapacity')
    result_df = pd.read_csv(result_file)
    cols = [col for col in input_df.columns[9:]]
    cols[0:0] = ['TECHNOLOGY']
    input_df = input_df.iloc[np.where(input_df['TECHNOLOGY'].str.contains('FPV'))][cols]
    result_df = result_df.iloc[np.where(result_df['t'].str.contains('FPV'))][['t','y','TotalCapacityAnnual']]
    new_input_df = input_df.copy()
    
    for i in range(len(input_df)):
        new_result_df = result_df.iloc[np.where(result_df['t'] == input_df['TECHNOLOGY'].iloc[i])]
        new_result_df = new_result_df[['y','TotalCapacityAnnual']].set_index('y')
        new_result_df = new_result_df.rename(columns={'TotalCapacityAnnual':input_df['TECHNOLOGY'].iloc[i]+'mod'})
        new_result_df = new_result_df.transpose()
        new_result_df['TECHNOLOGY'] = input_df['TECHNOLOGY'].iloc[i]+'mod'
        new_result_df = new_result_df.reset_index(drop=True)
        new_input_df = new_input_df.reset_index(drop=True)
        new_input_df = pd.concat([new_input_df, new_result_df], axis=0)
        
    new_input_df = new_input_df.fillna(0)
    df_capmax = new_input_df.iloc[0:len(input_df)].reset_index(drop=True)
    df_capact = new_input_df.iloc[len(input_df):].reset_index(drop=True)
    
    df_ratio = df_capact.iloc[:,1:]/df_capmax.iloc[:,1:]
    df_ratio = df_ratio.fillna(0)
    df_ratio['TECHNOLOGY'] = df_capmax['TECHNOLOGY']
    
    # Split by country
    df_country = df_ratio.iloc[np.where(df_ratio['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
    df_country.loc['mean'] = df_country.mean()
    
    return [df_country, df_capact]


for country in countries:
    plt.figure(figsize=(10,8))
    for file in listf:
        df_country = calc_df(file,country)[0]
        df_country.loc['mean'].transpose().plot(label=file[:-5])
        plt.legend()
        plt.xlabel('year')
        plt.ylabel('Used capacity potential [%]')
        plt.title('Used FPV capacity potential ' + country)
        path = os.path.join('results/ScenarioComparison',country + ' .png')
        plt.savefig(path)
        
for country in countries:
    plt.figure(figsize=(10,8))
    for file in listf:    
        # Find location with highest total capacity 
        df_capact = calc_df(file,country)[1]
        df_capact_country = df_capact.iloc[np.where(df_capact['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
        df_capact_country['tot'] = df_capact_country.sum(axis=1)
        max_cap_plant = df_capact_country.iloc[np.argmax(df_capact_country['tot'])]
        plt.plot(max_cap_plant[:-1], label=file[:-5])
        plt.xlabel('year')
        plt.ylabel('Capacity [GW]')
        plant_name = names_dict[max_cap_plant.name[7:-4]]
        plt.title('FPV capacity expansion for ' + plant_name)
        plt.legend()
        path = os.path.join('results/ScenarioComparison',max_cap_plant.name[:-3] + ' .png')
        plt.savefig(path)
        

for country in countries:
    plt.figure(figsize=(10,8))
    for file in listf:
        # Find location with highest total potential         
        df_ratio_country = calc_df(file,country)[0]
        df_capact = calc_df(file,country)[1]
        df_capact_country = df_capact.iloc[np.where(df_capact['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
        df_capact_country['tot'] = df_capact_country.sum(axis=1)
        df_ratio_country['tot'] = df_ratio_country.sum(axis=1)
        max_ratio_plant = df_ratio_country.iloc[np.argmax(df_ratio_country['tot'])]
        plt.plot(max_ratio_plant[:-1], label=file[:-5])
        plt.xlabel('year')
        plt.ylabel('Used capacity potential [%]')
        plt.legend()
        plant_name = names_dict[max_ratio_plant.name[7:-1]]
        cap_act = df_capact_country[2070].iloc[np.where(df_capact_country.index.str.contains(max_ratio_plant.name))]
        plt.title('Used FPV capacity potential for ' + plant_name + f' ({round(cap_act[0],2)} GW)')
        path = os.path.join('results/ScenarioComparison',max_ratio_plant.name + ' .png')
        plt.savefig(path)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        






