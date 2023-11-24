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
import plotly.io as pio
import cufflinks
import plotly.graph_objects as go


cufflinks.go_offline()
cufflinks.set_config_file(world_readable=True, theme='white', offline=True)

# =============================================================================
# Input stuff for plots
# =============================================================================

url1 = os.path.join('input_files', 'agg_col.csv')
url2 = os.path.join('input_files', 'agg_pow_col.csv')
url4 = os.path.join('input_files', 'power_tech.csv')
url5 = os.path.join('input_files', 'techcodes.csv')

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
first_year = 2022
last_year = 2066

color_dict_solar = {key.replace(' ', ''): value for key, value in color_dict_solar.items()}
color_dict_solar = {key.replace('FPV', ''): value for key, value in color_dict_solar.items()}

# =============================================================================
# Functions
# =============================================================================
def plot_df(df, scenario, loc, color_dict = color_dict_solar, barmode = 'stack'):
    dest_dir = f'results/{scenario}'
    os.makedirs(dest_dir, exist_ok=True)
    
    df = df.loc[:, (df != 0).any(axis=0)] # Drop columns with all 0 values
    df = df.iloc[:-2,:] # Drop tot rows

    # Create a bar trace for each column in the DataFrame
    bar_traces = []
    for column in df.columns:
        if column != 'y':
            bar_trace = go.Bar(
                x=df.index,
                y=df[column],
                name=column,
                marker=dict(color=color_dict[column]),
                showlegend=True
            )
            bar_traces.append(bar_trace)
    
    # Create the figure with bar traces
    fig = go.Figure(data=bar_traces)
    

    fig.update_layout(
        barmode=barmode,
        xaxis_title='Year',
        yaxis_title='Water saved [mcm]',
        #title=p_title + " - " + scenario,
        font=dict(size=18, color='black'),
        xaxis=dict(range=[first_year, last_year]),
        # yaxis=dict(range=[-50, 50])
        yaxis=dict(range=get_ylims(loc)),
        legend=dict(orientation="h", x=0, xanchor='left', y=-0.2)
    )
    fig.update_layout(title_text=None, title_x=0.5, margin=dict(t=10, r=10, b=10, l=10))

    pio.write_image(fig, os.path.join(dest_dir, '{}.png'.format(loc+' - '+scenario)), 
                    scale=1, width=846, height=611)
    return None



def get_ylims(loc):
    # Define y ranges based on country and variable
    if loc == 'ENB':
        min_y, max_y = 0, 400
    elif loc == 'EG':
        min_y, max_y = 0, 260
    elif loc == 'ET':
        min_y, max_y = 0, 260
    elif loc == 'SD':
        min_y, max_y = 0, 260
    return [min_y,max_y]




# =============================================================================
# Main
# =============================================================================
files = os.listdir('result_files')
files_hydro = [file for file in files if 'hydro' in file and 'Capacity' in file]
files_fpv = [file for file in files if 'fpv' in file]
files_gen = [file for file in files if 'Generation' in file and 'Capacity' not in file]
file_areas = 'FullAreasDataset.xlsx'

# Water losses for each country (mcm/km2)
data = {'EG':[5757.43/5248.37],
         'ET':[923.27/1966.50],
         'SD':[2718.96/796.06]}
df_wl = pd.DataFrame(data)

# Evaporation reduction rates 
coverage_perc = [0,0.1, 0.3, 0.5, 0.7, 1]
evap_red_perc = [0,0.18, 0.49, 0.73, 0.89, 1]
interp = scipy.interpolate.interp1d(coverage_perc, evap_red_perc, fill_value='extrapolate', kind='cubic')
plt.figure()
plt.scatter(coverage_perc,evap_red_perc, label='points')
plt.plot(np.arange(0,1.1,0.1),interp(np.arange(0,1.1,0.1)), color='orange', label='cubic interpolation')
plt.xlabel('FPV area coverage [%]')
plt.ylabel('Evaporation reduction [%]')
plt.legend()
# data = {0.1:[0.18],
#         0.3:[0.49],
#         0.5:[0.73],
#         0.7:[0.89],
#         1:[1]   
#         }
# df_rates = pd.DataFrame(data)
scenlist = [file[57:-4] for file in files_hydro]
df_tot = pd.DataFrame(index=scenlist, columns=['Tot reduction [%]','Tot reduction [mcm]'])

years = np.arange(2022,2066,1)

for i in range(len(files_hydro)):
# =============================================================================
#     Assign area of each reservoir
# =============================================================================
    filepath = os.path.join('result_files',files_hydro[i])
    df_hydro = pd.read_csv(filepath)
    df_areas = pd.read_excel(file_areas)
    df_areas_ele = df_areas.copy() #df for ele analysis
    
    df_hydro[df_hydro != 0] = 1
    df_hydro['y'] = np.arange(2015,2071,1)
    df_hydro.set_index('y', inplace=True)
    df_hydro = df_hydro.loc[years]
    
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
                 'Renaissance','Baro', 'Birbir','ChemogaYeda', 'Geba', 'Genji', 
                 'LowerDedessa','UpperDabus','Karadobi','BekoAbo','UpperMandaya',
                 'AleltuEast','AleltuWest','LowerDabus','Tams','Tekeze2']
    plants_sd = ['Sennar', 'KashmElGirba',
           'Roseires', 'JebelAulia', 'Merowe','UpperAtbara',
           'Kajbar', 'Shereik', 'Dagash', 'Dal', 'Mograt', 'Sabaloka']
    
    # Filter the plants that are actually in the scenario
    plants_eg = [plant for plant in plants_eg if plant in df_area_loc.columns]
    plants_et = [plant for plant in plants_et if plant in df_area_loc.columns]
    plants_sd = [plant for plant in plants_sd if plant in df_area_loc.columns]
    
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
    df_fpv = df_fpv.loc[years]
    cols_fpv = df_fpv.columns[2:]
    df_fpv = df_fpv.loc[:,cols_fpv]
    df_fpv = df_fpv/0.1
    # df_fpv.drop('Sor2',axis=1,inplace=True)
    
    # Calculate the cover percentage
    df_area_perc = df_fpv/df_area_loc
    df_area_perc.fillna(0,inplace=True)
    df_area_perc.replace([np.inf, -np.inf], 0, inplace=True)
    
    # Assign the evaporation reduction percentage
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
    
    df_reductions.loc['tot%'] = df_reductions.loc['tot'] / df_wl_loc.loc['tot'] * 100
    df_reductions.loc[:,'tot%'] = df_reductions.loc[:,'tot'] / df_wl_loc.loc[:,'tot'] * 100
    
    # Transform to percentages 
    df_reductions_perc = df_reductions_perc*100
    df_area_perc = df_area_perc*100
    
    # Transform to mm
    df_reductions_mm = df_reductions / df_area_loc * 1000
    df_reductions_mm.loc['tot'] = df_reductions_mm.sum()
    df_reductions_mm.loc[:,'tot'] = df_reductions_mm.sum(axis=1)

# =============================================================================
# Calculate increase in HP generation
# =============================================================================
    filepath = os.path.join('result_files',files_gen[i])
    df_gen = pd.read_csv(filepath) 
    df_gen.rename(columns=lambda x: x.replace(' ', ''), inplace=True)
    df_gen.set_index('y', inplace=True)
    df_gen = df_gen.loc[years]
    df_gen = df_gen[df_reductions.columns[:-2]]

    p = 1000
    n = 0.85
    g = 9.81
    
    df_area_loc = df_area_loc[df_reductions.columns[:-2]]
    df_ele = (df_reductions.iloc[:-2,:-2]**2*10**6/df_area_loc * p * g * n) /3600*3.6*10**(-9)
    df_ele.loc['tot'] = df_ele.sum()
    df_ele.loc[:,'tot'] = df_ele.sum(axis=1)
    
    df_ele_perc = df_ele / df_gen * 100
    df_ele_perc.loc['tot'] = df_ele.loc['tot'] / df_gen.sum() *100
    df_ele_perc.loc[:,'tot'] = df_ele.loc[:,'tot'] / df_gen.sum(axis=1) *100
# =============================================================================
#     Save to excel
# =============================================================================
    output_filepath = f'EvapReductions_{files_hydro[i][57:-4]}.xlsx'
    wb = openpyxl.Workbook()
    wb.save(output_filepath)
    writer = pd.ExcelWriter(output_filepath, mode='a', if_sheet_exists='overlay')
    
    df_wl_loc.to_excel(writer, sheet_name='Reservoir evaporation', index=True, startcol=0)
    df_area_perc.to_excel(writer, sheet_name='FPVArea %', index=True, startcol=0)
    df_reductions_perc.to_excel(writer, sheet_name='Reductions % of tot evap', index=True, startcol=0)
    df_reductions.to_excel(writer, sheet_name='Reductions mcm', index=True, startcol=0)
    df_reductions_mm.to_excel(writer, sheet_name='Reductions mm', index=True, startcol=0)
    df_ele.to_excel(writer, sheet_name='Extra HP generation PJ', index=True, startcol=0)
    df_ele.max().to_excel(writer, sheet_name='Max extra HP generation PJ', index=True, startcol=0)
    df_ele_perc.to_excel(writer, sheet_name='Extra HP generation %', index=True, startcol=0)
    df_ele_perc.max().to_excel(writer, sheet_name='Max extra HP generation %', index=True, startcol=0)
    
    
# =============================================================================
# Save all the totals 
# =============================================================================
    df_tot.loc[scenlist[i]]['Tot reduction [%]'] = df_reductions.loc['tot']['tot%']
    df_tot.loc[scenlist[i]]['Tot reduction [mcm]'] = df_reductions.loc['tot']['tot']
    df_tot.sort_values(by=('Tot reduction [%]'), ascending=False, inplace=True)
    
# =============================================================================
#     Plot the barchart
# =============================================================================
    scenario = files_hydro[i][57:-4]
    for loc in ['ENB','EG', 'ET', 'SD']:
        if loc == 'ENB':
            df_reductions_country = df_reductions.iloc[:,:-2] #remove tot cols
        elif loc == 'EG':
            df_reductions_country = df_reductions[plants_eg]
        elif loc == 'ET':
            df_reductions_country = df_reductions[plants_et]
        elif loc == 'SD':
            df_reductions_country = df_reductions[plants_sd]
            
        plot_df(df_reductions_country,scenario, loc)





writer.close()


df_tot.to_excel('TotalValues.xlsx')

