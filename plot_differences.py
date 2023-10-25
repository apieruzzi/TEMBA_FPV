# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 15:09:39 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import os
import plotly.io as pio
import cufflinks

cufflinks.go_offline()
cufflinks.set_config_file(world_readable=True, theme='white', offline=True)

# Script to create plots of differences of a scenario with the reference
# Variables to plot:
    # - Power generation
    # - Water consumption
# Difference of each scenario with with the reference (FPV)
# Difference of REF_FPV and REF
# Differences for EAPP and each country

# Lists and files
locs = ['EAPP', 'EG', 'ET', 'SD', 'SS']
variables = {'Power Generation (Aggregate)':'PJ', 'Water Consumption':'MCM'}
data_dir = 'input_data'
inputfiles = os.listdir(data_dir)
scenario_list = [file[:-5] for file in inputfiles if file.endswith('xlsx') and not file.startswith('~')]
scenario_ref = 'TEMBA_ENB_ref'
scenario_list = [sc for sc in scenario_list if sc != scenario_ref]
first_year = 2022
last_year = 2070
years = pd.Series(range(first_year, last_year+1))

# Codes and colours
url1 = os.path.join(data_dir, 'agg_col.csv')
url2 = os.path.join(data_dir, 'agg_pow_col.csv')
url4 = os.path.join(data_dir, 'power_tech.csv')
url5 = os.path.join(data_dir, 'techcodes.csv')

colorcode = pd.read_csv(url5, sep=',', encoding="ISO-8859-1")
colorcode1 = colorcode.drop('colour', axis=1)
colorcode2 = colorcode.drop('tech_code', axis=1)
det_col = dict(
    [(a, b) for a, b in zip(colorcode1.tech_code, colorcode1.tech_name)])
color_dict = dict(
    [(a, b) for a, b in zip(colorcode2.tech_name, colorcode2.colour)])
colorcode_hydro = colorcode[colorcode['tech_code'].str.contains('HYD')].iloc[1:].drop('tech_code', axis=1)
new_colors_hydro = ['yellow','chartreuse', 'cornflowerblue', #Egypt
                    'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                    'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                    'red', 'black', 'lime', 'darkred', 'midnightblue', 
                    'olive', 'orange', 'purple', 'teal', 'lime', 'dimgrey', #Ethiopia
                    'yellow', 'red', #SouthSudan
                    'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                    'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                    'midnightblue', 'black', #Sudan
                    'red', 'orange', 'green', #Egypt ROR
                    'pink', 'violet', 'lightyellow', #Ethiopia ROR
                    'yellow','chartreuse', 'cornflowerblue', 'orange', 'green' #SS ROR
                    ]
colorcode_hydro.iloc[3:,1] = new_colors_hydro
color_dict_hydro = dict(
    [(a, b) for a, b in zip(colorcode_hydro.tech_name, colorcode_hydro.colour)])
colorcode_solar = colorcode[colorcode['tech_code'].str.contains('SO')].drop('tech_code', axis=1)
new_colors_solar = ['yellow','chartreuse', 'cornflowerblue', #Egypt
                    'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                    'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                    'red', 'black', 'lime', 'darkred', 'midnightblue', 
                    'olive', 'orange', 'purple', 'teal', 'lime', 'darkslategrey', #Ethiopia
                    'yellow', 'red', #SouthSudan
                    'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                    'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                    'midnightblue', 'black' #Sudan
                    ]
colorcode_solar.iloc[9:,1] = new_colors_solar
color_dict_solar = dict(
    [(a, b) for a, b in zip(colorcode_solar.tech_name, colorcode_solar.colour)])

# Color dicts for power pool graphs
colorcode_hydro_pp = colorcode_hydro
colorcode_hydro_pp.iloc[12,1]='black'
colorcode_solar_pp = colorcode_solar
colorcode_solar_pp.iloc[19,1]='black'
color_dict_hydro_pp = dict(
    [(a, b) for a, b in zip(colorcode_hydro_pp.tech_name, colorcode_hydro_pp.colour)])
color_dict_solar_pp = dict(
    [(a, b) for a, b in zip(colorcode_solar_pp.tech_name, colorcode_solar_pp.colour)])

agg1 = pd.read_csv(url1, sep=',', encoding="ISO-8859-1")
agg2 = pd.read_csv(url2, sep=',', encoding="ISO-8859-1")
agg_col = agg1.to_dict('list')
agg_pow_col = agg2.to_dict('list')
power_tech = pd.read_csv(url4, sep=',', encoding="ISO-8859-1")
t_include = list(power_tech['power_tech'])
t_include_hydro = [i for i in t_include if i.startswith('HYD')]
t_include_solar = [i for i in t_include if i.startswith('SO')]
t_include_fpv = [i for i in t_include if i.startswith('SOFPV')]



def calculate_differences(scenario_ref, scenario, loc, variable):
    folder_ref = f'results/export_{scenario_ref}/barcharts/{loc}'
    filename_ref = f'{loc}-{variable}-{scenario_ref}.csv'
    filepath_ref = os.path.join(folder_ref, filename_ref)
    
    folder = f'results/export_{scenario}/barcharts/{loc}'
    filename = f'{loc}-{variable}-{scenario}.csv'
    filepath = os.path.join(folder, filename)
    
    df_ref = pd.read_csv(filepath_ref)
    df_sc = pd.read_csv(filepath)
    
    df_diff = df_sc - df_ref
    df_diff = df_diff.fillna(0)
    df_diff['y'] = years
    return df_diff


def plot_differences(df, scenario, loc, y_title, p_title, color_dict = color_dict, barmode = 'relative'):
    dest_dir = f'results/ScenarioComparison/DifferencePlots/{loc}'
    os.makedirs(dest_dir, exist_ok=True)
    
    df = df.loc[:, (df != 0).any(axis=0)] # Drop columns with all 0 values
    
    if (len(df.columns) == 1) | (np.shape(df)[1] < 2):
        print('There are no values for the result variable that you want to plot')
        print(p_title)
    else:
        fig = df.iplot(x='y',
                    kind='bar',
                    barmode=barmode,
                    width=1,
                    xTitle='Year',
                    yTitle=y_title,
                    color=[color_dict[x] for x in df.columns if x != 'y'],
                    title=p_title,
                    showlegend=True,
                    asFigure=True)
        fig.update_xaxes(range=[first_year, last_year])
        fig.update_traces(width=0.7)
        pio.write_image(fig, os.path.join(dest_dir, '{}.png'.format(p_title)), 
                        scale=1, width=1500, height=1000)
        df.to_csv(os.path.join(dest_dir, p_title+".csv"))
        return None



# Debugging
# loc='EG'
# sc = scenario_list[0]
# var = 'Power Generation (Aggregate)'

for sc in scenario_list:
    for loc in locs:
        for var in variables.keys():
            df_diff = calculate_differences(scenario_ref, sc, loc, var)
            plot_differences(df_diff, sc, loc,variables[var], loc+' - '+var+' - '+sc)















































