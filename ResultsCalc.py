# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:57:49 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Goal: obtain quantification of results
# - How many reservoirs are built out of the planned list (after 2023)? Total number and number per country
# - Calculate the percentages and amounts of capacity and generation per aggregate technology 
# - Save all these info in an excel


def create_pie_charts(filename, title, scenario, writer, file, code):
    df = pd.read_csv(filename)
    df = df.iloc[:,1:] #drop useless column
    columns = df.columns[1:]
    if title == 'Generation' and file == 'Aggregate' and code != 'SS':
        df['power_trade'] = [v if v>0 else 0 for v in df['power_trade']]
    df['tot'] = df.iloc[:,1:].sum(axis=1)
    df.loc['tot'] = df.sum()
    for col in columns:
        df[f'{col} - Percentage'] = df[f'{col}'] / df['tot']
    df.to_excel(writer, sheet_name = code + '- ' + title, index=False)

    # Plot pie charts of mix for every decade (2030,2040,2050,2060,2070)
    df = df.set_index('y')
    idx = df.columns.get_loc(f'{columns[0]} - Percentage')
    df = df.iloc[:,idx:]
    df_t = df.transpose()
    
    years_to_plot = [2023,2030,2040,2050,2060,2070]
    years = [col for col in df_t.columns if col in years_to_plot] 
    df_sel = df_t.loc[:,years]
    labels = [label[:-13] for label in df_sel.index]
    
    fig, axes = plt.subplots(2,3, figsize=(20,15))
    if file != 'Aggregate':
        for ax, col in zip(axes.flatten(), df_sel.columns):
            ax.pie(df_sel[col], autopct='%.0f')
            ax.set(ylabel='', title=col, aspect='equal')
    else:
        for ax, col in zip(axes.flatten(), df_sel.columns):
            ax.pie(df_sel[col], autopct='%.0f', colors=[colors_dict[p] for p in df_sel.index])
            ax.set(ylabel='', title=col, aspect='equal')
    
    plt.subplots_adjust(wspace=0.01,
                        hspace=0.1)        
    fig.suptitle(title + ' mixes' + ' - ' + file + ' - ' + code + ' - '+ scenario)
    axes.flatten()[0].legend(bbox_to_anchor=(0, 0.7), labels=labels)
    fig.savefig(f'results/piecharts/{code}/{title} - {file} - {code}.png', bbox_inches='tight')
    plt.close()


scenario = "TEMBA_Refer_ENB"
os.makedirs(r'results/piecharts', exist_ok=True)
folder_names = ['EAPP', 'EG', 'ET', 'SD', 'SS']
for name in folder_names:
    os.makedirs(f'results/piecharts/{name}', exist_ok=True)
    


# Load files
hydro_plants_filename = r'input_data/planned_hydro_plants.csv' #Doesnt have ror plants 
tech_codes_filename = r'input_data/techcodes.csv'
new_capacity_filename = f'results/{scenario}/NewCapacity.csv'

# Calculate amount of HP plants that are built:
hydro_plants_list = pd.read_csv(hydro_plants_filename, header=None)
hydro_plants_list = hydro_plants_list.rename(columns={0:'t'})
new_capacity_df = pd.read_csv(new_capacity_filename)
built_plants = hydro_plants_list.iloc[np.where(hydro_plants_list['t'].isin(new_capacity_df['t']))]
nplants_tot = len(hydro_plants_list)
nplants_tot_built = len(built_plants)
nplants_ET = len(built_plants.iloc[np.where(built_plants['t'].str.startswith('ET'))])
nplants_SD = len(built_plants.iloc[np.where(built_plants['t'].str.startswith('SD'))])
nplants_SS = len(built_plants.iloc[np.where(built_plants['t'].str.startswith('SS'))])

# Calculate capacity amounts and percentages for each country and year
country_codes = ['EG', 'ET', 'SD', 'SS']
years = np.arange(2015,2071,1)
writer = pd.ExcelWriter(r'results/Mixes_percentages.xlsx')

# Save hydro plants values and lists                                                                                       
data = [['Total planned plants',nplants_tot], ['Total built plants', nplants_tot_built],
        ['Total built plants ET', nplants_ET], ['Total built plants SD', nplants_SD],
        ['Total built plants SS', nplants_SS]]
df_plants = pd.DataFrame(data)
df_plants.to_excel(writer, sheet_name = 'Metrics of built HP plants', index=False, header = None)

tech_codes_df = pd.read_csv(tech_codes_filename)
hydro_plants_mod = [plant[2:] for plant in hydro_plants_list['t']]
hydro_plants_names = tech_codes_df.iloc[np.where(tech_codes_df['tech_code'].isin(hydro_plants_mod))[0],:2]
built_plants_mod = [plant[2:] for plant in built_plants['t']]
built_plants_names = tech_codes_df.iloc[np.where(tech_codes_df['tech_code'].isin(built_plants_mod))[0],:2]
built_plants_names.to_excel(writer, sheet_name = 'List of built HP plants', index=False)

# Create pie charts
colors_dict = {
    "Coal - Percentage":"darkgrey",
    "Oil - Percentage" : "grey",
    "Gas - Percentage" : "darkorange",
    "Hydro - Percentage" : "lightblue",
    "Solar CSP - Percentage" : "yellow",
    "Solar PV - Percentage" : "gold",
    "Solar FPV - Percentage" : "lightgreen",
    "Wind - Percentage" : "blue",
    "Biomass - Percentage" : "brown",
    "Geothermal - Percentage" : "beige", 
    "power_trade - Percentage" : "pink",
    }

tech_codes_df['tech_name'] = [name + ' - Percentage' for name in tech_codes_df['tech_name']]

files = ['Aggregate', 'Detail fossil', 'Detail solar', 'Detail hydro']

for file in files:
    capacity_filename = f'results/export_{scenario}/powerpool/EAPP/EAPP-Power Generation Capacity ({file})-{scenario}.csv'
    create_pie_charts(capacity_filename, 'Capacity', scenario, writer, file, code='EAPP')
    generation_filename =   f'results/export_{scenario}/powerpool/EAPP/EAPP-Power Generation ({file})-{scenario}.csv'
    create_pie_charts(generation_filename, 'Generation', scenario, writer, file, code='EAPP')

for code in country_codes:
    for file in files:
        # Capacity:
        capacity_filename = f'results/export_{scenario}/country/{code}/{code}-Power Generation Capacity ({file})-{scenario}.csv'
        create_pie_charts(capacity_filename, 'Capacity', scenario, writer, file, code)
        
        # Generation:
        generation_filename = f'results/export_{scenario}/country/{code}/{code}-Power Generation ({file})-{scenario}.csv'
        create_pie_charts(generation_filename, 'Generation', scenario, writer, file, code)
    
    
writer.close()












