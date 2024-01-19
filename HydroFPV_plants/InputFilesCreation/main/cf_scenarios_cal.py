# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 11:52:10 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 14})


# Import files 
file_list = os.listdir('Data')
file_list = [file for file in file_list if file.startswith('Combined')]
scenario_list = [file[19:-4] for file in file_list]

countries = ['EGYPT', 'ETHIOPIA', 'SUDAN', 'SOUTH SUDAN']
seasons = [1,2,3,4]

# Read data hydro
df_lines_hydro = pd.DataFrame(columns=['S1','S2', 'S3', 'S4'])
for country in countries:
    df_lines = pd.DataFrame(index=scenario_list,columns=['S1','S2', 'S3', 'S4'])
    for file in file_list:
        scenario = file[19:-4]
        df_read = pd.read_csv(os.path.join('Data',file))
        df = pd.DataFrame()
        for season in seasons:
            col = 'CF_H' + str(season) + 'D1' 
            col_out = 'S' + str(season)
            df[[col_out, 'Capacity (MW)']] = df_read.iloc[np.where(df_read['Country'] == country)][[col, 'Capacity (MW)']]
            df_lines.loc[scenario][col_out] = np.average(df[col_out],weights=df['Capacity (MW)'])
        # Boxplots
        # plt.figure()
        # plt.boxplot(df)
        # plt.xlabel('Season')
        # plt.ylabel('Capacity factor')
        # plt.title(f'Capacity factor variations - {country} - {scenario}')
        # path = os.path.join('boxplots_cf', country+scenario+'.png')
        # plt.savefig(path)
        # plt.close()
        
     # Lines  
    df_lines_hydro.loc[country] = df_lines.loc['ref']      
    df_lines.transpose().plot(title=f'Average hydropower capacity factors vs season - {country}')
    path = os.path.join('boxplots_cf', country + ' hydro'+'.png')
    plt.savefig(path)
    
# Read data solar
file = 'CombinedHydroSolar_ref.csv'
df_read = pd.read_csv(os.path.join('Data',file))
df_temba = pd.read_excel(r'Created Files/TEMBA_ENB_ref.xlsx', sheet_name='CapacityFactor')
df_temba = df_temba.loc[np.where(df_temba['TECHNOLOGY'].str.contains('SO'))[0],:2015].reset_index(drop=True)
df_lines = pd.DataFrame(columns=['S1D1', 'S1D2','S2D1', 'S2D2', 'S3D1','S3D2', 'S4D1','S4D2'])
country_codes = dict({'EG':'EGYPT', 'ET':'ETHIOPIA', 'SD':'SUDAN', 'SS':'SOUTH SUDAN'})

for cc in country_codes.keys():
    # Calculate FPV means from csv file
    df = pd.DataFrame()
    for col in df_lines.columns:
        col_read = 'CF_S' + col[1:] 
        df[col] = df_read.iloc[np.where(df_read['Country'] == country_codes[cc])][col_read]
    df_lines.loc['Solar FPV (mean)'] = df.mean()
    
    # Take cf for other solar techs from temba file
    df_lines.loc['Solar utility'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOU1P03X')[0],2015].values
    df_lines.loc['Solar rooftop'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOV1F01X')[0],2015].values
    df_lines.loc['Solar CSP'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOC1P00X')[0],2015].values
    
    df_lines.transpose().plot(title=f'Average solar capacity factors vs season - {country_codes[cc]}')
    path = os.path.join('boxplots_cf', country_codes[cc]+ ' solar'+ '.png')
    plt.savefig(path)



# =============================================================================
# Plot CFs of each plant for FPVs in the ref
# =============================================================================


# Read data solar
file = 'CombinedHydroSolar_ref.csv'
df_read = pd.read_csv(os.path.join('Data',file))
df_temba = pd.read_excel(r'Created Files/TEMBA_ENB_ref.xlsx', sheet_name='CapacityFactor')
df_temba = df_temba.loc[np.where(df_temba['TECHNOLOGY'].str.contains('SO'))[0],:2015].reset_index(drop=True)
df_lines = pd.DataFrame(columns=['S1D1', 'S1D2','S2D1', 'S2D2', 'S3D1','S3D2', 'S4D1','S4D2'])
country_codes = dict({'EG':'EGYPT', 'ET':'ETHIOPIA', 'SD':'SUDAN', 'SS':'SOUTH SUDAN'})

for cc in country_codes.keys():
    # Calculate FPV means from csv file
    df = pd.DataFrame()
    for col in df_lines.columns:
        col_read = 'CF_S' + col[1:] 
        locs = df_read.iloc[np.where((df_read['Country'] == country_codes[cc]) & 
                                     (df_read['Type'] == 'Reservoir'))]['Unit Name'].tolist()
        df[['loc',col]] = df_read.iloc[np.where(df_read['Country'] == country_codes[cc])][['Unit Name',col_read]]
    
    df = df.set_index('loc')
    df = df.loc[locs]


    # Take cf for other solar techs from temba file
    # df.loc['Solar utility'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOU1P03X')[0],2015].values
    # df.loc['Solar rooftop'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOV1F01X')[0],2015].values
    # df.loc['Solar CSP'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOC1P00X')[0],2015].values
    
    ax = df.transpose().plot(figsize=(10,8), fontsize=16)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=14)

    # Increase title font size
    ax.set_title(f'Average solar capacity factors vs season - {country_codes[cc]}', fontsize=16)

    path = os.path.join('boxplots_cf', country_codes[cc]+ ' solar FPV'+ '.png')
    plt.savefig(path)



# Plot CFs of all techs, both together and day and night separately
file = 'CombinedHydroSolar_ref.csv'
df_read = pd.read_csv(os.path.join('Data',file))
df_temba = pd.read_excel(r'Created Files/TEMBA_ENB_ref.xlsx', sheet_name='CapacityFactor')
df_lines = pd.DataFrame(columns=['S1D1', 'S1D2','S2D1', 'S2D2', 'S3D1','S3D2', 'S4D1','S4D2'])
country_codes = dict({'EG':'EGYPT', 'ET':'ETHIOPIA', 'SD':'SUDAN', 'SS':'SOUTH SUDAN'})
df_lines_hydro.loc[:,'S1D1'] = df_lines_hydro['S1']
df_lines_hydro.loc[:,'S1D2'] = df_lines_hydro['S1']
df_lines_hydro.loc[:,'S2D1'] = df_lines_hydro['S2']
df_lines_hydro.loc[:,'S2D2'] = df_lines_hydro['S2']
df_lines_hydro.loc[:,'S3D1'] = df_lines_hydro['S3']
df_lines_hydro.loc[:,'S3D2'] = df_lines_hydro['S3']
df_lines_hydro.loc[:,'S4D1'] = df_lines_hydro['S4']
df_lines_hydro.loc[:,'S4D2'] = df_lines_hydro['S4']
df_lines_hydro = df_lines_hydro[df_lines.columns]


colors_dict_agg = {
    "Coal":"black",
    "Oil" : "darkgrey",
    "Gas" : "darkorange",
    "Hydro" : "aqua",
    "Solar CSP" : "red",
    "Solar PV" : "gold",
    "Solar FPV" : "green",
    "Wind" : "royalblue",
    "Biomass" : "lightgreen",
    "Geothermal" : "brown", 
    "Nuclear" : "blueviolet",
    "Solar CSP_high" : "red",
    "Solar PV_high" : "yellow",
    "Solar CSP_low" : "red",
    "Solar PV_low" : "orange",
    }


for cc in country_codes.keys():
    # Calculate FPV means from csv file
    df = pd.DataFrame()
    for col in df_lines.columns:
        col_read = 'CF_S' + col[1:] 
        df[col] = df_read.iloc[np.where(df_read['Country'] == country_codes[cc])][col_read]
    df_lines.loc['Solar FPV'] = df.mean()
    
    # Take cf for other solar techs from temba file
    df_lines.loc['Solar PV'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOU1P03X')[0],2015].values
    df_lines.loc['Solar CSP'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'SOC1P00X')[0],2015].values
    df_lines.loc['Biomass'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'BMCHC01N')[0],2015].values
    df_lines.loc['Coal'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'COSCP02N')[0],2015].values
    df_lines.loc['Gas'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'NGCCP01N')[0],2015].values
    df_lines.loc['Geothermal'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'GOCVP02N')[0],2015].values
    df_lines.loc['Hydro'] = df_lines_hydro.loc[country_codes[cc]]
    df_lines.loc['Oil'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'LFRCP01N')[0],2015].values
    df_lines.loc['Wind'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'WINDP00X')[0],2015].values
    df_lines.loc['Nuclear'] = df_temba.loc[np.where(df_temba['TECHNOLOGY']==cc+'NULWP04N')[0],2015].values
    
    
    # df_lines.transpose().plot(title=f'Average capacity factors vs season - {country_codes[cc]}')

    
    lines = []
    plt.figure(figsize=(10,8))

    for idx, row in df_lines.iterrows():
        if row.name in ['Geothermal','Coal']:
            style = 'dashed'
        else:
            style = 'solid'
            
        line, = plt.plot(row,color=colors_dict_agg[idx], linestyle=style)
        lines.append(line)

    # plt.legend(lines, df_lines.index, loc='upper left', bbox_to_anchor=(1, 1))
    plt.legend(lines, df_lines.index, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=6)
    plt.title(f'Capacity factors vs timeslices - {country_codes[cc]}')
    plt.xlabel('Timeslice')
    plt.ylabel('Capacity factor [-]')
    plt.tight_layout()
    path = os.path.join('boxplots_cf', country_codes[cc]+ ' total'+ '.png')
    plt.savefig(path)
    















    
    
    
    