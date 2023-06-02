# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 15:33:00 2023

@author: Alessandro Pieruzzi
"""

import numpy as np
import pandas as pd



#Import all filenames

PG_mod_EG_filename = r'results\export_TEMBA_Refer\country\EG\EG-Power Generation (Aggregate)-TEMBA_Refer.csv'
PG_mod_ET_filename = r'results\export_TEMBA_Refer\country\ET\ET-Power Generation (Aggregate)-TEMBA_Refer.csv'
PG_mod_SD_filename = r'results\export_TEMBA_Refer\country\SD\SD-Power Generation (Aggregate)-TEMBA_Refer.csv'
PG_mod_SS_filename = r'results\export_TEMBA_Refer\country\SS\SS-Power Generation (Aggregate)-TEMBA_Refer.csv'

PG_act_EG_filename = r'Literature\Data IEA\Electricity generation by source - Egypt (1).csv'
PG_act_ET_filename = r'Literature\Data IEA\Electricity generation by source - Ethiopia (1).csv'
PG_act_SD_filename = r'Literature\Data IEA\Electricity generation by source - Sudan (1).csv'
PG_act_SS_filename = r'Literature\Data IEA\Electricity generation by source - South Sudan (1).csv'

#Read data
PG_mod_EG = pd.read_csv(PG_mod_EG_filename)
PG_mod_ET = pd.read_csv(PG_mod_ET_filename)
PG_mod_SD = pd.read_csv(PG_mod_SD_filename)
PG_mod_SS = pd.read_csv(PG_mod_SS_filename)

PG_act_EG = pd.read_csv(PG_act_EG_filename)
PG_act_ET = pd.read_csv(PG_act_ET_filename)
PG_act_SD = pd.read_csv(PG_act_SD_filename)
PG_act_SS = pd.read_csv(PG_act_SS_filename)

#Extract relevant year and create combined df

df_list_mod = [PG_mod_EG, PG_mod_ET, PG_mod_SD, PG_mod_SS]
df_list_act = [PG_act_EG, PG_act_ET, PG_act_SD, PG_act_SS]
sheet_names = ["EG", "ET", "SD", "SS"]

writer = pd.ExcelWriter(r'results\export_TEMBA_Refer\results_check.xlsx')

for i in range(len(df_list_mod)):
    # Select df
    df_mod = df_list_mod[i]
    df_act = df_list_act[i]
    
    # Select year and transpose
    df_mod = df_mod[df_mod['y']==2020].transpose()    
    df_act = df_act[df_act['y']==2020].transpose() 
    
    # Fix dtypes
    df_act = df_act.drop('Units')
    df_act = df_act.astype('Float64')
    
    # Convert units to GWh
    df_mod = df_mod.iloc[2:,:]*277.78
    
    # Combine df and keep only relevant rows
    df_comb = pd.concat([df_mod, df_act], axis = 1)
    df_comb = df_comb.drop('y')
    df_comb.iloc[np.where(df_comb.iloc[:,1].isnull() == True)[0],1] = 0
    df_comb = df_comb.drop(df_comb.index[((df_comb.iloc[:,0] == 0) & (df_comb.iloc[:,1] == 0))])
    
    # Calculate difference 
    diff_col = pd.DataFrame(data = [df_comb.iloc[:,0] - df_comb.iloc[:,1]]).transpose()
    df = pd.concat([df_comb, diff_col], axis = 1)
    df = df.rename(columns={df.columns[0]:"Modelled", df.columns[1]:"Actual data", df.columns[2]:"Difference"})
    
    #Save to file
    df.to_excel(writer, sheet_name = sheet_names[i])

writer.close()

    
    

    
















