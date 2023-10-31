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
# plt.rcParams.update({'font.size': 16})

# Script to create plots of differences of a scenario with the reference
# Variables to plot:
    # - Power generation
    # - Water consumption
# Difference of each scenario with with the reference (FPV)
# Difference of REF_FPV and REF
# Differences for ENB and each country

# Lists and files
locs = ['ENB', 'EG', 'ET', 'SD', 'SS']
variables = {'Power Generation (Aggregate)':'PJ', 'Water Consumption':'MCM'}
data_dir = 'input_data'
inputfiles = os.listdir(data_dir)
scenario_list = [file[:-5] for file in inputfiles if file.endswith('xlsx') and not file.startswith('~') and 'NoFPV' in file]
scenario_ref_list = [file[:-5] for file in inputfiles if file.endswith('xlsx') and not file.startswith('~') and 'NoFPV' not in file]
scenario_dict = dict(zip(scenario_ref_list, scenario_list))
first_year = 2022
last_year = 2066
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
color_dict['import'] = 'pink'
color_dict['export'] = 'lime'
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
    filename_ref = f'{loc} - {variable}-{scenario_ref}.csv'
    filepath_ref = os.path.join(folder_ref, filename_ref)
    
    folder = f'results/export_{scenario}/barcharts/{loc}'
    filename = f'{loc} - {variable}-{scenario}.csv'
    filepath = os.path.join(folder, filename)
    
    df_ref_data = pd.read_csv(filepath_ref).iloc[:,1:]
    df_sc_data = pd.read_csv(filepath).iloc[:,1:]
    
    cols = agg2.columns.insert(0,'y')
    cols = cols.insert(-1,'import')
    cols = cols.insert(-1, 'export')
    df_ref = pd.DataFrame(np.zeros(shape=(len(years),len(cols))), columns=cols)
    df_sc = pd.DataFrame(np.zeros(shape=(len(years),len(cols))), columns=cols)
    df_ref['y'] = years
    df_sc['y'] = years    
    df_ref = df_ref.set_index('y').add(
        df_ref_data.set_index('y'), fill_value=0)
    df_sc = df_sc.set_index('y').add(
        df_sc_data.set_index('y'), fill_value=0)
    
    # Fix import and export
    df_ref['import'] = abs(df_ref.iloc[np.where(df_ref['power_trade']>0)]['power_trade'])
    df_ref['export'] = abs(df_ref.iloc[np.where(df_ref['power_trade']<0)]['power_trade'])
    df_sc['import'] = abs(df_sc.iloc[np.where(df_sc['power_trade']>0)]['power_trade'])
    df_sc['export'] = abs(df_sc.iloc[np.where(df_sc['power_trade']<0)]['power_trade'])
    
    df_diff = df_sc - df_ref
    df_diff = df_diff.iloc[:,0:-1] #remove power trade column
    df_diff = df_diff.fillna(0)
    df_diff = df_diff.reset_index()
    return df_diff

def get_ylims(loc,var, scenario):
    # Define y ranges based on country and variable
    if loc == 'ENB':
        if var == 'Power Generation (Aggregate)':
            min_y, max_y = -150, 150
        else:
            min_y, max_y = -5000, 5000
    elif loc == 'EG':
        if var == 'Power Generation (Aggregate)':
            if 'EXT' in scenario:
                min_y, max_y = -800, 800
            else:
                min_y, max_y = -30, 30
        else:
            if 'EXT' in scenario:
                min_y, max_y = -90, 90
            else:
                min_y, max_y = -200, 1800
    elif loc == 'ET':
        if var == 'Power Generation (Aggregate)':
            min_y, max_y = -100, 100
        else:
            min_y, max_y = -500, 2000
    elif loc == 'SD':
        if var == 'Power Generation (Aggregate)':
            if 'EXT' in scenario:
                min_y, max_y = -150, 150
            else:
                min_y, max_y = -40, 40
        else:
            min_y, max_y = -3000, 3000
    elif loc == 'SS':
        if var == 'Power Generation (Aggregate)':
            min_y, max_y = -1, 1
        else:
            min_y, max_y = -600, 300
    return [min_y,max_y]

def plot_differences(df, scenario, loc,var, color_dict = color_dict, barmode = 'relative'):
    dest_dir = f'results/ScenarioComparison/DifferencePlots/{loc}'
    os.makedirs(dest_dir, exist_ok=True)
    
    df = df.loc[:, (df != 0).any(axis=0)] # Drop columns with all 0 values    
    
    if (len(df.columns) == 1) | (np.shape(df)[1] < 2):
        print('There are no values for the result variable that you want to plot')
        print( loc+' - '+var+' - '+sc)
    else:
        fig = df.iplot(x='y',
                    kind='bar',
                    barmode=barmode,
                    width=1,
                    xTitle='Year',
                    yTitle=variables[var],
                    color=[color_dict[x] for x in df.columns if x != 'y'],
                    title= loc + ' - ' + var + ' - difference with reference scenario' +  ' - ' + sc,
                    showlegend=True,
                    asFigure=True)
        fig.update_layout(font_size=16)
        fig.update_xaxes(range=[first_year, last_year])
        fig.update_yaxes(range=get_ylims(loc, var, scenario))
        fig.update_traces(width=0.7)
        pio.write_image(fig, os.path.join(dest_dir, '{}.png'.format(loc+' - '+var+' - '+sc)), 
                        scale=1, width=1500, height=1000)
        df.to_csv(os.path.join(dest_dir, loc+' - '+var+' - '+sc+".csv"))
        return None


# Debugging
loc='SD'
sc = scenario_list[0]
var = 'Power Generation (Aggregate)'

for sc in scenario_dict.keys():
    for loc in locs:
        for var in variables.keys():
            df_diff = calculate_differences(scenario_dict[sc], sc, loc, var)
            plot_differences(df_diff, sc, loc,var)















































