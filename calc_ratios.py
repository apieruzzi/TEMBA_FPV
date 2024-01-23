# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 11:14:02 2023

@author: Alessandro Pieruzzi
"""


import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
plt.rcParams.update({'font.size': 16})

 # Script that calculates the potential usage of FPVs and the locations with largest usage and largest capacity

# Scenarios
listf = os.listdir('input_data')
listf = [file for file in listf if file.endswith('.xlsx') and not file.startswith('~')]
listf = [file for file in listf if 'ref.' not in file]
listf = listf[-2:] + listf
listf = listf[:-2]
countries = ['ENB', 'EG', 'ET', 'SD']

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
    input_df_hydro = input_df.iloc[np.where(input_df['TECHNOLOGY'].str.contains('HYD'))][cols]
    result_df_hydro = result_df.iloc[np.where(result_df['t'].str.contains('HYD'))][['t','y','TotalCapacityAnnual']]  
    
# =============================================================================
#     FPVs
# ============================================================================    
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
    techs_fpv = df_capact['TECHNOLOGY'].tolist()
    techs_fpv = [tech[-6:-4] for tech in techs_fpv]
    df_capmax.loc[:,'TECH'] = techs_fpv
    df_capact.loc[:,'TECH'] = techs_fpv
    df_capmax.set_index('TECH', inplace=True)
    df_capact.set_index('TECH', inplace=True)
    df_capmax.sort_index(inplace=True)
    
# =============================================================================
#     HYDRO    
# =============================================================================
    df_hydro_capact = pd.DataFrame(columns=input_df_hydro.columns)
    
    for i in range(len(input_df_hydro)):
        new_result_df_hydro = result_df_hydro.iloc[np.where(result_df_hydro['t'] == input_df_hydro['TECHNOLOGY'].iloc[i])]
        new_result_df_hydro = new_result_df_hydro[['y','TotalCapacityAnnual']].set_index('y')
        new_result_df_hydro = new_result_df_hydro.rename(columns={'TotalCapacityAnnual':input_df_hydro['TECHNOLOGY'].iloc[i]})
        new_result_df_hydro = new_result_df_hydro.transpose()
        new_result_df_hydro['TECHNOLOGY'] = input_df_hydro['TECHNOLOGY'].iloc[i]
        new_result_df_hydro = new_result_df_hydro.reset_index(drop=True)
        df_hydro_capact = pd.concat([df_hydro_capact, new_result_df_hydro], axis=0)

    df_hydro_capact.fillna(0,inplace=True)
    df_hydro_capact = df_hydro_capact.iloc[:,0:49].reset_index(drop=True)
    df_hydro_capact = df_hydro_capact.loc[~(df_hydro_capact.iloc[:,1:]==0).all(axis=1)]
   
    techs_hyd = df_hydro_capact['TECHNOLOGY'].tolist()
    techs_hyd = [tech[-5:-3] for tech in techs_hyd]
    df_hydro_capact.loc[:,'TECH'] = techs_hyd
    df_hydro_capact.set_index('TECH', inplace=True)
    df_hydro_capact.sort_index(inplace=True)
    
# =============================================================================
#     Combine the two
# =============================================================================
    # Keep only the hydropower plants that are actually built and have reservoirs 
    plants = list(set(df_hydro_capact.index).intersection(df_capmax.index))
    df_hydro_capact = df_hydro_capact.loc[plants]
    df_capmax = df_capmax.loc[plants]
    df_capact = df_capact.loc[plants]
    
    df_ratio = df_capact.iloc[:,1:]/(df_capmax.iloc[:,1:]) 
    df_ratio = df_ratio.fillna(0)
    df_ratio.replace([np.inf, -np.inf], 1, inplace=True)
    df_ratio['TECHNOLOGY'] = df_capact.TECHNOLOGY
    
    # Split by country
    if country=='ENB':
        df_country = df_ratio.set_index('TECHNOLOGY')
        df_capmax_country = df_capmax.set_index('TECHNOLOGY')
    else:
        df_country = df_ratio.iloc[np.where(df_ratio['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
        df_capmax_country = df_capmax.iloc[np.where(df_capmax['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
        df_capact = df_capact.iloc[np.where(df_capact['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
        
    df_country.loc['mean'] = df_country.mean()
    df_capmax_country.loc['tot'] = df_capmax_country.sum()
    
    return [df_country, df_capact, df_capmax_country]


# # Plot ratio lines
# for country in countries:
#     plt.figure(figsize=(10,8))
#     for file in listf:
#         df_country = calc_df(file,country)[0]
#         df_capmax = calc_df(file,country)[2]
#         linewidth=1
#         if 'EXT' in file[:-5]:
#             linestyle = 'dashed'
#         elif 'RCP' in file[:-5]:
#             linestyle = 'dotted'
#             if '60' in file[:-5]:
#                 linewidth=5
#         else:
#             linestyle='solid'
#         df_country.loc['mean',:2065].transpose().plot(label=file[10:-5],
#                                                       linestyle=linestyle, linewidth=linewidth)
#         # plt.legend()
#         plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),ncol=4)
#         plt.xlabel('Year')
#         plt.ylabel('Used capacity potential')
#         plt.title(f'Max potential: {round(df_capmax.iloc[-1,-1],2)} GW')
#         path = os.path.join('results/ScenarioComparison',country + ' .png')
#         plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=0))
#         plt.tight_layout()
#         plt.savefig(path)
#         # plt.close()

df_potentials = pd.DataFrame(index=listf)
writer = pd.ExcelWriter(os.path.join('results/ScenarioComparison/potentials.xlsx'))

# Plot ratio lines
for country in countries:
    plt.figure(figsize=(10,8))
    for file in listf:
        df_country = calc_df(file,country)[0]
        df_capmax = calc_df(file,country)[2]
        linewidth=1
        if 'TAX' in file[:-5]:
            linestyle = 'dashed'
        elif 'RCP' in file[:-5]:
            linestyle = 'dotted'
            if '60' in file[:-5]:
                linewidth=5
        else:
            linestyle='solid'
        df_country.loc['mean',:2065].transpose().plot(label=file[10:-5],
                                                      linestyle=linestyle, linewidth=linewidth)
        # # plt.legend()
        # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),ncol=4)
        # plt.xlabel('Year')
        # plt.ylabel('Used capacity potential')
        # plt.title(f'Max potential: {round(df_capmax.iloc[-1,-1],2)} GW')
        # path = os.path.join('results/ScenarioComparison',country + ' .png')
        # plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=0))
        # plt.tight_layout()
        # plt.savefig(path)
        # # plt.close()
        
        df_potentials.loc[file[10:-5],'Value'] = round(df_capmax.iloc[-1,-1],2)
    df_potentials.to_excel(writer,sheet_name=country)

writer.close()     


# Plot capacity lines
for country in countries:
    plt.figure(figsize=(10,8))
    for file in listf:
        df_capact = calc_df(file,country)[1]
        df_capmax = calc_df(file,country)[2]
        if country=='ENB':
            df_capact_country = df_capact.set_index('TECHNOLOGY')
        else:
            df_capact_country = df_capact.iloc[np.where(df_capact.index.str.contains(country))]
        df_capact_country.loc['tot'] = df_capact_country.sum()
        linewidth=1
        if 'TAX' in file[:-5]:
            linestyle = 'dashed'
        elif 'RCP' in file[:-5]:
            linestyle = 'dotted'
            if '60' in file[:-5]:
                linewidth=5
        else:
            linestyle='solid'
        df_capact_country.loc['tot',:2065].transpose().plot(label=file[10:-5],
                                                      linestyle=linestyle, linewidth=linewidth)
        plt.legend()
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),ncol=4)
        plt.xlabel('Year')
        plt.ylabel('Built capacity [GW]')
        # plt.title(f'Max potential: {round(df_capmax.iloc[-1,-1],2)} GW')
        path = os.path.join('results/ScenarioComparison',country + ' .png')
        plt.tight_layout()
        plt.savefig(path)
        # plt.close()

        
# for country in countries:
#     plt.figure(figsize=(10,8))
#     for file in listf:    
#         # Find location with highest total capacity 
#         df_capact = calc_df(file,country)[1]
#         if country=='ENB':
#             df_capact_country = df_capact.set_index('TECHNOLOGY')
#         else:
#             df_capact_country = df_capact.iloc[np.where(df_capact['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
#         df_capact_country['tot'] = df_capact_country.sum(axis=1)
#         max_cap_plant = df_capact_country.iloc[np.argmax(df_capact_country['tot'])]
#         linewidth=1
#         if 'EXT' in file[:-5]:
#             linestyle = 'dashed'
#         elif 'RCP' in file[:-5]:
#             linestyle = 'dotted'
#             if '60' in file[:-5]:
#                 linewidth=5
#         else:
#             linestyle='solid'
#         plt.plot(max_cap_plant[:-6], label=file[10:-5], linestyle=linestyle, linewidth=linewidth)
#         plt.xlabel('year')
#         plt.ylabel('Capacity [GW]')
#         plant_name = names_dict[max_cap_plant.name[7:-4]]
#         plt.title('FPV capacity expansion for ' + plant_name)
#         plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),ncol=4)
#         path = os.path.join('results/ScenarioComparison',max_cap_plant.name[:-3] + ' .png')
#         plt.tight_layout()
#         plt.savefig(path)
#         # plt.close()
        

# for country in countries:
#     plt.figure(figsize=(10,8))
#     for file in listf:
#         # Find location with highest total potential         
#         df_ratio_country = calc_df(file,country)[0]
#         df_capact = calc_df(file,country)[1]
#         if country=='ENB':
#             df_capact_country = df_capact.set_index('TECHNOLOGY')
#         else:
#             df_capact_country = df_capact.iloc[np.where(df_capact['TECHNOLOGY'].str.contains(country))].set_index('TECHNOLOGY')
#         df_capact_country['tot'] = df_capact_country.sum(axis=1)
#         df_ratio_country['tot'] = df_ratio_country.sum(axis=1)
#         max_ratio_plant = df_ratio_country.iloc[np.argmax(df_ratio_country['tot'])]
#         linewidth=1
#         if 'EXT' in file[:-5]:
#             linestyle = 'dashed'
#         elif 'RCP' in file[:-5]:
#             linestyle = 'dotted'
#             if '60' in file[:-5]:
#                 linewidth=5
#         else:
#             linestyle='solid'
#         plt.plot(max_ratio_plant[:-6], label=file[10:-5], linestyle=linestyle, linewidth=linewidth)
#         plt.xlabel('year')
#         plt.ylabel('Used capacity potential [%]')
#         plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),ncol=4)
#         plant_name = names_dict[max_ratio_plant.name[7:-1]]
#         cap_act = df_capact_country[2065].iloc[np.where(df_capact_country.index.str.contains(max_ratio_plant.name))]
#         plt.title('Used FPV capacity potential for ' + plant_name + f' ({round(cap_act[0],2)} GW)')
#         path = os.path.join('results/ScenarioComparison',max_ratio_plant.name + ' .png')
#         plt.tight_layout()
#         plt.savefig(path)
#         # plt.close()
        
        
        
        
# # Plot single locations

# for file in listf:
#     for country in  ['EG', 'ET', 'SD']:
#         df_country = calc_df(file,country)[1]
#         df_capmax = calc_df(file,country)[2]
#         linewidth=1
#         if 'EXT' in file[:-5]:
#             linestyle = 'dashed'
#         elif 'RCP' in file[:-5]:
#             linestyle = 'dotted'
#             if '60' in file[:-5]:
#                 linewidth=5
#         else:
#             linestyle='solid'
            
#         df_country.loc[:,:2065].transpose().plot(figsize=(10,8),label=file[10:-5],
#                                                       linestyle=linestyle, linewidth=linewidth)
#         plt.legend()
#         # plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
#         plt.xlabel('Year')
#         plt.ylabel('Capacity [GW]')
#         plt.title(f'{file[:-5]}')
#         path = os.path.join('results/ScenarioComparison/locations',country + file[:-5] + ' .png')
#         plt.tight_layout()
#         plt.savefig(path)
#         # plt.close()
    
        
        
        
        
        
        
        
        
        
        
        
        
        






