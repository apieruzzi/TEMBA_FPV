# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 15:33:00 2023

@author: Alessandro Pieruzzi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
plt.rcParams.update({'font.size': 16})

#Import all filenames

PG_mod_EG_filename = r'results\export_TEMBA_ENB_ref\barcharts\EG\EG - Power Generation (Aggregate)-TEMBA_ENB_ref.csv'
PG_mod_ET_filename = r'results\export_TEMBA_ENB_ref\barcharts\ET\ET - Power Generation (Aggregate)-TEMBA_ENB_ref.csv'
PG_mod_SD_filename = r'results\export_TEMBA_ENB_ref\barcharts\SD\SD - Power Generation (Aggregate)-TEMBA_ENB_ref.csv'
PG_mod_SS_filename = r'results\export_TEMBA_ENB_ref\barcharts\SS\SS - Power Generation (Aggregate)-TEMBA_ENB_ref.csv'

PG_act_EG_filename = r'Literature\Data IEA\Electricity generation by source - Egypt (1).csv'
PG_act_ET_filename = r'Literature\Data IEA\Electricity generation by source - Ethiopia (1).csv'
PG_act_SD_filename = r'Literature\Data IEA\Electricity generation by source - Sudan (1).csv'
PG_act_SS_filename = r'Literature\Data IEA\Electricity generation by source - South Sudan (1).csv'

#Read data
PG_mod_EG = pd.read_csv(PG_mod_EG_filename)
PG_mod_ET = pd.read_csv(PG_mod_ET_filename)
PG_mod_SD = pd.read_csv(PG_mod_SD_filename)
PG_mod_SS = pd.read_csv(PG_mod_SS_filename)
PG_mod_EG.drop('Unnamed: 0', axis=1,inplace=True)
PG_mod_ET.drop('Unnamed: 0', axis=1,inplace=True)
PG_mod_SD.drop('Unnamed: 0', axis=1,inplace=True)
PG_mod_SS.drop('Unnamed: 0', axis=1,inplace=True)
PG_mod_EG.set_index('y',inplace=True)
PG_mod_ET.set_index('y',inplace=True)
PG_mod_SD.set_index('y',inplace=True)
PG_mod_SS.set_index('y',inplace=True)

PG_act_EG = pd.read_csv(PG_act_EG_filename)
PG_act_ET = pd.read_csv(PG_act_ET_filename)
PG_act_SD = pd.read_csv(PG_act_SD_filename)
PG_act_SS = pd.read_csv(PG_act_SS_filename)
PG_act_EG.set_index('y',inplace=True)
PG_act_ET.set_index('y',inplace=True)
PG_act_SD.set_index('y',inplace=True)
PG_act_SS.set_index('y',inplace=True)


cols_mod = list(set(PG_mod_SS.columns).union(PG_mod_SD.columns,PG_mod_ET.columns,PG_mod_EG.columns))
cols_act = list(set(PG_act_SS.columns).union(PG_act_SD.columns,PG_act_ET.columns,PG_act_EG.columns))

PG_mod_EG.loc[:,[col for col in cols_mod if col not in PG_mod_EG.columns]]=0
PG_mod_ET.loc[:,[col for col in cols_mod if col not in PG_mod_ET.columns]]=0
PG_mod_SD.loc[:,[col for col in cols_mod if col not in PG_mod_SD.columns]]=0
PG_mod_SS.loc[:,[col for col in cols_mod if col not in PG_mod_SS.columns]]=0

PG_mod_EG = PG_mod_EG[cols_mod]
PG_mod_ET = PG_mod_ET[cols_mod]
PG_mod_SD = PG_mod_SD[cols_mod]
PG_mod_SS = PG_mod_SS[cols_mod]
PG_mod_ENB = PG_mod_EG + PG_mod_ET +PG_mod_SD +PG_mod_SS


PG_act_EG.loc[:,[col for col in cols_act if col not in PG_act_EG.columns]]=0
PG_act_ET.loc[:,[col for col in cols_act if col not in PG_act_ET.columns]]=0
PG_act_SD.loc[:,[col for col in cols_act if col not in PG_act_SD.columns]]=0
PG_act_SS.loc[:,[col for col in cols_act if col not in PG_act_SS.columns]]=0

PG_act_EG = PG_act_EG[cols_act]
PG_act_ET = PG_act_ET[cols_act]
PG_act_SD = PG_act_SD[cols_act]
PG_act_SS = PG_act_SS[cols_act]
PG_act_ENB = PG_act_EG + PG_act_ET +PG_act_SD +PG_act_SS

#Extract relevant year and create combined df

df_list_mod = [PG_mod_EG, PG_mod_ET, PG_mod_SD, PG_mod_SS, PG_mod_ENB]
df_list_act = [PG_act_EG, PG_act_ET, PG_act_SD, PG_act_SS, PG_act_ENB]
sheet_names = ["EG", "ET", "SD", "SS", 'ENB']

writer = pd.ExcelWriter(r'results\results_check.xlsx')

for i in range(len(df_list_mod)):
    # Select df
    df_mod = df_list_mod[i]
    df_act = df_list_act[i]
    
    # Select year and transpose
    if sheet_names[i] == 'SS':
       df_mod = df_mod.loc[2019].transpose()   
    else:
        df_mod = df_mod.loc[2020].transpose()    
        
    df_act = df_act.loc[2020].transpose() 
    
    # Fix dtypes
    df_act = df_act.drop('Units')
    df_act = df_act.astype('Float64')
    
    # Convert units to GWh
    df_mod = df_mod*277.78
    
    # Combine df and keep only relevant rows
    df_mod.rename('Modelled', inplace=True)
    df_act.rename('Actual data', inplace=True)
    df_comb = pd.concat([df_mod, df_act], axis = 1)
    df_comb.iloc[np.where(df_comb.iloc[:,1].isnull() == True)[0],1] = 0
    df_comb = df_comb.drop(df_comb.index[((df_comb.iloc[:,0] == 0) & (df_comb.iloc[:,1] == 0))])
    
    # Calculate difference 
    diff_col = pd.DataFrame(data = [df_comb.iloc[:,0] - df_comb.iloc[:,1]]).transpose()
    df = pd.concat([df_comb, diff_col], axis = 1)
    df = df.rename(columns={df.columns[2]:"Difference (GW)"})
    df['Difference (PJ)'] = df['Difference (GW)'] * 0.0036
    
    #Save to file
    df.to_excel(writer, sheet_name = sheet_names[i])
    
    df = df[['Modelled', 'Actual data']]
    if 'power_trade' in df.index:
        df = df.drop(['power_trade'])
        
    
    # Plot

    colors_dict= {
        "Coal":"grey",
        "Oil" : "darkgrey",
        "Gas" : "darkorange",
        "Hydro" : "lightblue",
        "Solar CSP" : "red",
        "Solar PV" : "yellow",
        "Solar FPV" : "green",
        "Wind" : "blue",
        "Biomass" : "lightgreen",
        "Geothermal" : "brown", 
        "power_trade" : "pink",
        "Nuclear" : "cyan"
        }
    
    # labels = [label[:-13] for label in df_sel.index]
    fig, axes = plt.subplots(1,2, figsize=(20,15))
    labels = [label for label in df.index]
    
    for ax in axes.flatten():
        ax.set_axis_off()
    for col, ax in zip(df.columns,axes.flatten()):
        ax.pie(df[col],
               autopct=lambda p: '{:.0f}%'.format(p) if p >= 0.5 else '',
               colors=[colors_dict[p] for p in df.index])
        ax.set(ylabel='', title=col, aspect='equal')
        ax.set_axis_on()
        
    fig.suptitle(f'Generation mixes comparison for {sheet_names[i]} (2020)', y=0.8)
    plt.subplots_adjust(wspace=0.01, hspace=0.1)
    axes.flatten()[0].legend(bbox_to_anchor=(0, 0.9), labels=labels)
    fig.savefig(f'results/{sheet_names[i]} - Generation mixes comparison (2020).png', bbox_inches='tight')
    


writer.close()

    
    

    
















