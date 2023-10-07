# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:57:49 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import colorcet as cc
import sys
import tempfile
import shutil

# Goal: obtain quantification of results
# - How many reservoirs are built out of the planned list (after 2023)? Total number and number per country
# - Calculate the percentages and amounts of capacity and generation per aggregate technology 
# - Save all these info in an excel


def create_pie_charts(filename, title, scenario, writer, file, code):
    
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError as fi:
        print(fi)
        return
    
    df = df.iloc[:,1:] #drop useless column
    columns = df.columns[1:]
    if title == 'Generation' and file == 'Aggregate' and code != 'SS':
        df['power_trade'] = [v if v>0 else 0 for v in df['power_trade']]
    df['tot'] = df.iloc[:,1:].sum(axis=1)
    df.loc['tot'] = df.sum()
    for col in columns:
        df[f'{col} - Percentage'] = df[f'{col}'] / df['tot']
    df = df.fillna(int(0))
    
    # Save to excel only hydro values
    if file == 'Detail hydro':
        df.to_excel(writer, sheet_name = code + '- ' + title + '_' + file[7:], index=False)
    # Calculate max total capacity and generation and save them to df
        max_value = np.max(df['tot'].iloc[:-1])
        max_year = np.argmax(df['tot'].iloc[:-1]) + df['y'].loc[0]
        if title == 'Capacity':
            df_comb_hydro.loc[code]['MaxCapacity'] = max_value
            df_comb_hydro.loc[code]['YearC'] = max_year
        elif title == 'Generation':
            df_comb_hydro.loc[code]['MaxGeneration'] = max_value
            df_comb_hydro.loc[code]['YearG'] = max_year
            df_comb_hydro.loc[code]['TotalGeneration'] = df['tot'].iloc[-1]     
    
    # Save to excel the FPV values
    if file == 'Detail fpv':
        df.to_excel(writer, sheet_name = code + '- ' + title + '_' + file[7:], index=False)
    # Calculate max total capacity and generation and save them to df
        max_value = np.max(df['tot'].iloc[:-1])
        max_year = np.argmax(df['tot'].iloc[:-1]) + df['y'].loc[0]
        if title == 'Capacity':
            df_comb_fpv.loc[code]['MaxCapacity'] = max_value
            df_comb_fpv.loc[code]['YearC'] = max_year
        elif title == 'Generation':
            df_comb_fpv.loc[code]['MaxGeneration'] = max_value
            df_comb_fpv.loc[code]['YearG'] = max_year
            df_comb_fpv.loc[code]['TotalGeneration'] = df['tot'].iloc[-1]  
    
    if file == 'Aggregate' and code != 'SS':
        max_share = np.max(df['Solar FPV - Percentage'].iloc[:-1])
        max_year = np.argmax(df['tot'].iloc[:-1]) + df['y'].loc[0]
        if title == 'Capacity':
            df_comb_fpv.loc[code]['MaxCapacityShare'] = max_share
            df_comb_fpv.loc[code]['YearCS'] = max_year
            first_non_zero = df['Solar FPV'].to_numpy().nonzero()[0][0] + df['y'].loc[0]
            df_comb_fpv.loc[code]['Onset'] = first_non_zero
        elif title == 'Generation':
            df_comb_fpv.loc[code]['MaxGenerationShare'] = max_share
            df_comb_fpv.loc[code]['YearGS'] = max_year
            df_comb_fpv.loc[code]['TotalGeneration'] = df['tot'].iloc[-1]  
            
            

    # Plot pie charts of mix for every decade (2030,2040,2050,2060,2070)
    df = df.set_index('y')
    idx = df.columns.get_loc(f'{columns[0]} - Percentage')
    df = df.iloc[:,idx:]
    df_t = df.transpose()
    
    years_to_plot = [2023,2030,2040,2050,2060,2070]
    years = [col for col in df_t.columns if col in years_to_plot] 
    df_sel = df_t.loc[:,years]
    df_sel = df_sel.loc[:, (df_sel != 0).any(axis=0)]
    
    labels = [label[:-13] for label in df_sel.index]
    fig, axes = plt.subplots(2,3, figsize=(20,15))
    if file != 'Aggregate':
        colors_dict = colors_dict_detail
    else:
        colors_dict = colors_dict_agg
    
    for ax in axes.flatten():
        ax.set_axis_off()
    for col, ax in zip(df_sel.columns,axes.flatten()):
        ax.pie(df_sel[col],
               autopct=lambda p: '{:.1f}%'.format(round(p)) if p > 0 else '', 
               colors=[colors_dict[p] for p in df_sel.index])
        ax.set(ylabel='', title=col, aspect='equal')
        ax.set_axis_on()

    plt.subplots_adjust(wspace=0.01, hspace=0.1)        
    fig.suptitle(title + ' mixes' + ' - ' + file + ' - ' + code + ' - '+ scenario)
    axes.flatten()[0].legend(bbox_to_anchor=(0, 0.7), labels=labels)
    fig.savefig(os.path.join(homedir, f'{code} - {title} - {file}.png'), bbox_inches='tight')
    plt.close()

input_file_dummy = sys.argv[1]
scenario = sys.argv[-2]
destination_folder = sys.argv[-1]

# scenario = 'TEMBA_2.0_ENB'
# destination_folder = 'results/export_{scenario}'

with tempfile.TemporaryDirectory() as temp:

    global homedir
    homedir = temp

    print("Using temporary directory {}".format(homedir))

    # Load files
    hydro_plants_filename = r'input_data/planned_hydro_plants.csv' #Doesnt have ror plants 
    tech_codes_filename = r'input_data/techcodes.csv'
    new_capacity_filename = f'results/{scenario}/NewCapacity.csv'
    
    # Calculate amount of HP plants that are built:
    hydro_plants_list = pd.read_csv(hydro_plants_filename, header=None)
    hydro_plants_list = hydro_plants_list.rename(columns={0:'t'})
    new_capacity_df = pd.read_csv(new_capacity_filename)
    built_plants = new_capacity_df[['t','y']].iloc[np.where(new_capacity_df['t'].isin(hydro_plants_list['t']))]
    nplants_tot = len(hydro_plants_list)
    nplants_tot_built = len(built_plants)
    nplants_ET = len(built_plants.iloc[np.where(built_plants['t'].str.startswith('ET'))])
    nplants_SD = len(built_plants.iloc[np.where(built_plants['t'].str.startswith('SD'))])
    nplants_SS = len(built_plants.iloc[np.where(built_plants['t'].str.startswith('SS'))])
    
    # Calculate capacity amounts and percentages for each country and year
    country_codes = ['EG', 'ET', 'SD', 'SS']
    years = np.arange(2015,2071,1)
    writer = pd.ExcelWriter(f'results/export_{scenario}/Mixes_percentages_{scenario}.xlsx')
    
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
    built_plants = built_plants.reset_index(drop=True)
    built_plants_names = built_plants_names.reset_index(drop=True)
    built_plants_names['Year'] = built_plants['y']
    built_plants_names.to_excel(writer, sheet_name = 'List of built HP plants', index=False)
     
    # Create pie charts
    colors_dict_agg = {
        "Coal - Percentage":"darkgrey",
        "Oil - Percentage" : "grey",
        "Gas - Percentage" : "darkorange",
        "Hydro - Percentage" : "lightblue",
        "Solar CSP - Percentage" : "red",
        "Solar PV - Percentage" : "yellow",
        "Solar FPV - Percentage" : "green",
        "Wind - Percentage" : "blue",
        "Biomass - Percentage" : "lightgreen",
        "Geothermal - Percentage" : "brown", 
        "power_trade - Percentage" : "pink",
        "Nuclear - Percentage" : "cyan",
	"Backstop - Percentage": "red"
        }
    
    file_prodtechs = r'input_data/power_tech.csv'
    prodtechs_df = pd.read_csv(file_prodtechs)
    prod_techs_codes_df = tech_codes_df.iloc[np.where(tech_codes_df['tech_code'].isin(prodtechs_df['power_tech']))]
    names_list = [name + ' - Percentage' for name in  prod_techs_codes_df['tech_name']]
    names_list.append('Solar FPV - Percentage')
    
    palette = sns.color_palette(cc.glasbey, n_colors=len(names_list))
    palette = palette.as_hex()
    colors_dict_detail = dict(zip(names_list, palette))
    
    tech_codes_df['tech_name'] = [name + ' - Percentage' for name in tech_codes_df['tech_name']]
    
    df_comb_hydro = pd.DataFrame(columns=['MaxCapacity', 'YearC', 'MaxGeneration', 'YearG', 'TotalGeneration'], 
                           index=['EAPP', 'EG', 'ET', 'SD', 'SS'])
    df_comb_fpv = pd.DataFrame(columns=['MaxCapacity', 'YearC', 'MaxGeneration', 
                                        'YearG', 'TotalGeneration', 
                                        'MaxCapacityShare', 'YearCS',
                                        'MaxGenerationShare', 'YearGS', 'Onset'], 
                           index=['EAPP', 'EG', 'ET', 'SD', 'SS'])
    
    files = ['Aggregate', 'Detail solar', 'Detail hydro', 'Detail fpv']
    
    for file in files:
        capacity_filename = f'results/export_{scenario}/barcharts/EAPP/EAPP-Power Generation Capacity ({file})-{scenario}.csv'
        create_pie_charts(capacity_filename, 'Capacity', scenario, writer, file, code='EAPP')
        generation_filename =   f'results/export_{scenario}/barcharts/EAPP/EAPP-Power Generation ({file})-{scenario}.csv'
        create_pie_charts(generation_filename, 'Generation', scenario, writer, file, code='EAPP')
    
    for code in country_codes:
        for file in files:
            # Capacity:
            capacity_filename = f'results/export_{scenario}/barcharts/{code}/{code}-Power Generation Capacity ({file})-{scenario}.csv'
            create_pie_charts(capacity_filename, 'Capacity', scenario, writer, file, code)
            
            # Generation:
            generation_filename = f'results/export_{scenario}/barcharts/{code}/{code}-Power Generation ({file})-{scenario}.csv'
            create_pie_charts(generation_filename, 'Generation', scenario, writer, file, code)
        
    # Calculate cumulative water consumption
    wc_filename = f'results/export_{scenario}/barcharts/EAPP/EAPP-Water Consumption-{scenario}.csv'
    wc_df = pd.read_csv(wc_filename)
    wc_df['tot'] = wc_df.iloc[:,2:].sum(axis=1)
    wc_tot = wc_df['tot'].sum()
    df_wc = pd.DataFrame(data = [wc_tot], columns=['Total Water Consumption'])
    df_wc.to_excel(writer, sheet_name='TotalWaterConsumption', index=False)
    
    df_comb_hydro.to_excel(writer, sheet_name='Max values_hydro')
    df_comb_fpv.to_excel(writer, sheet_name='Max values_fpv')
    
    writer.close()
    
    
    # Move files:    
    os.makedirs(os.path.join(destination_folder), exist_ok=True)
    folder_names = ['EAPP', 'EG', 'ET', 'SD', 'SS']
        
    resultpath = os.path.join(destination_folder)
    files = os.listdir(homedir)
    for name in folder_names:
        dest1 = os.path.join(resultpath, name)
        os.makedirs(dest1, exist_ok=True)
        for f in files:
            if (f.startswith(name)):
                filepath = os.path.join(homedir, f)
                shutil.move(filepath, dest1)











