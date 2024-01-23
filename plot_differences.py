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
import plotly.graph_objects as go


cufflinks.go_offline()
cufflinks.set_config_file(world_readable=True, theme='white', offline=True)
# plt.rcParams.update({'font.size': 16})

# Script to create plots of differences of a scenario with the reference
# Difference of each scenario with with the reference (FPV)
# Difference of REF_FPV and REF
# Differences for ENB and each country

# Lists and files
locs = ['ENB', 'EG', 'ET', 'SD', 'SS']
variables = {'Power Generation (Aggregate)':'PJ', 'Power Generation Capacity (Aggregate)':'GW'}
data_dir = 'input_data'
inputfiles = os.listdir(data_dir)
scenario_list = [file[:-5] for file in inputfiles if file.endswith('xlsx') and not file.startswith('~')]
scenario_ref = 'TEMBA_ENB_ref'
scenario_list = [sc for sc in scenario_list if sc != scenario_ref]
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
    df_sc['tot'] = df_sc.iloc[:,:-4].sum(axis=1)
    
    # Fix import and export
    df_ref['import'] = abs(df_ref.iloc[np.where(df_ref['power_trade']>0)]['power_trade'])
    df_ref['export'] = abs(df_ref.iloc[np.where(df_ref['power_trade']<0)]['power_trade'])
    df_sc['import'] = abs(df_sc.iloc[np.where(df_sc['power_trade']>0)]['power_trade'])
    df_sc['export'] = abs(df_sc.iloc[np.where(df_sc['power_trade']<0)]['power_trade'])
    
    df_diff = df_sc - df_ref
    df_diff = df_diff.iloc[:,0:-5] #remove power trade column
    df_diff = df_diff.fillna(0)
    df_diff = df_diff.reset_index()
    df_diff.iloc[:,1:] = df_diff.iloc[:,1:]/max(df_ref.iloc[:,1:-4].sum(axis=1)) * 100  
    df_diff = df_diff.fillna(0)
    
    return df_diff

def get_ylims(loc,var, scenario):
    # Define y ranges based on country and variable
    if loc == 'ENB':
        if var == 'Power Generation (Aggregate)':
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -4, 4
        else:
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -4, 4
    elif loc == 'EG':
        if var == 'Power Generation (Aggregate)':
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
        else:
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
    elif loc == 'ET':
        if var == 'Power Generation (Aggregate)':
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
        else:
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
    elif loc == 'SD':
        if var == 'Power Generation (Aggregate)':
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
        else:
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
    elif loc == 'SS':
        if var == 'Power Generation (Aggregate)':
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
        else:
            if 'EXT' in scenario:
                min_y, max_y = -25, 25
            else:
                min_y, max_y = -25, 25
    return [min_y,max_y]

def plot_differences(df, scenario, loc,var, color_dict = color_dict, barmode = 'relative'):
    dest_dir = f'results/ScenarioComparison/DifferencePlots/{var}/{scenario}'
    os.makedirs(dest_dir, exist_ok=True)
    
    # Ignore import and export differences
    cols = [col for col in df.columns if col!='import' and col!='export']
    df = df[cols]
    df = df.loc[:, (df != 0).any(axis=0)] # Drop columns with all 0 values    
    
    if (len(df.columns) == 1) | (np.shape(df)[1] < 2):
        print('There are no values for the result variable that you want to plot')
        print( loc+' - '+var+' - '+sc)
    else:
        # Create a bar trace for each column in the DataFrame
        bar_traces = []
        for column in df.columns:
            if column != 'y':
                bar_trace = go.Bar(
                    x=df['y'],
                    y=df[column],
                    name=column,
                    marker=dict(color=color_dict[column]),
                    showlegend=False
                )
                bar_traces.append(bar_trace)
        
        # Create the figure with bar traces
        fig = go.Figure(data=bar_traces)
        

        fig.update_layout(
            barmode=barmode,
            xaxis_title='Year',
            yaxis_title='Difference [% of max generation]',
            #title=p_title + " - " + scenario,
            font=dict(size=18, color='black'),
            xaxis=dict(range=[first_year, last_year]),
            # yaxis=dict(range=[-50, 50])
            yaxis=dict(range=get_ylims(loc, var, scenario)),
           # legend=dict(orientation="h", x=0, xanchor='left', y=-0.2)
        )
        fig.update_layout(title_text=None, title_x=0.5, margin=dict(t=10, r=10, b=10, l=10))

        pio.write_image(fig, os.path.join(dest_dir, '{}.png'.format(loc+' - '+var+' - '+sc)), 
                        scale=1, width=846, height=611)
        df.to_csv(os.path.join(dest_dir, loc+' - '+var+' - '+sc+".csv"))
        return None


for sc in scenario_list:
    for loc in locs:
        for var in variables.keys():
            df_diff = calculate_differences(scenario_ref, sc, loc, var)
            plot_differences(df_diff, sc, loc,var)















































