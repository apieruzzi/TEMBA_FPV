# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 12:00:24 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np

# Goal: for each timeslice we need to calculate the total production for each tech 

filename_good = r'RateOfActivity_good.csv'
filename_wrong = r'RateOfActivity_wrong.csv'

df_good = pd.read_csv(filename_good)
df_wrong = pd.read_csv(filename_wrong)

df_good = df_good.drop(columns=['r'])
df_wrong = df_wrong.drop(columns=['r'])

# Keep only 2021 and 2022
df_good = df_good.iloc[np.where((df_good['y']==2021) | (df_good['y']==2022))[0]]
df_wrong = df_wrong.iloc[np.where((df_wrong['y']==2021) | (df_wrong['y']==2022))[0]]

# Keep only Egypt
df_good = df_good[df_good['t'].str.contains('EG')]
df_wrong = df_wrong[df_wrong['t'].str.contains('EG')]

# Remove country prefix
def pref_remover(row):
    return str(row['t'][2:])

df_good['t'] = df_good.apply(lambda row: pref_remover(row), axis=1)
df_wrong['t'] = df_wrong.apply(lambda row: pref_remover(row), axis=1)

# Techs need to be filtered by power techs only 
power_tech = pd.read_csv(r'power_tech.csv')
power_tech = power_tech['power_tech'].tolist()
power_tech.append('ELJOBP00')
power_tech.append('ELSABP00')
power_tech.append('ELSDBP00')
power_tech.append('ELEGBP00')

df_good = df_good[df_good['t'].isin(power_tech)]
df_wrong = df_wrong[df_wrong['t'].isin(power_tech)]

# Group dfs by timeslice and year 
# Desired outcome: one df per timeslice per year per run = 32 dfs

df_good = df_good.sort_values(by=['y', 'l'])
df_wrong = df_wrong.sort_values(by=['y', 'l'])

   
timeslices = ['S1D1', 'S1D2', 'S2D1', 'S2D2',
              'S3D1','S3D2','S4D1','S4D2']
years = [2021, 2022]
ts = 0
yr = 0
list_df_merg = []
demands= [629.2577637,
            467.8544811,
            696.4657375,
            518.3329731,
            665.8378829,
            504.5268406,
            568.3883684,
            429.3584213,
            643.8118038,
            478.6754407,
            712.574224,
            530.3214447,
            681.2379809,
            516.1959915,
            581.5345662,
            439.2890094]


for i in range(0,16,1):
    df1 = df_good.iloc[np.where((df_good['l']==timeslices[ts]) & (df_good['y'] == years[yr]))[0]]
    df1 = df1.drop(columns=['l','m','y'])
    df1 = df1.set_index('t')
    df1 = df1.rename(columns={'RateOfActivity':'good'})

    df1_wrong = df_wrong.iloc[np.where((df_wrong['l']==timeslices[ts]) & (df_wrong['y'] == years[yr]))[0]]
    df1_wrong = df1_wrong.drop(columns=['l','m','y'])
    df1_wrong = df1_wrong.set_index('t')
    df1_wrong  = df1_wrong.rename(columns={'RateOfActivity':'wrong'})

    df1merg = pd.concat([df1,df1_wrong],axis=1)
    df1merg = df1merg.fillna(0)
    df1merg['diff'] = df1merg['wrong'] - df1merg['good']
    df1merg.loc['total'] = df1merg.sum(numeric_only=True)
    
    df2 = pd.DataFrame({'good' : [demands[i]],
                       'wrong' : [demands[i]]},
                       index=['demand'])
    df1merg = pd.concat([df1merg,df2])
    
    df1merg.loc['diff'] = df1merg.loc['demand'] - df1merg.loc['total']
    df1merg.loc['diffNoBackstop'] = df1merg.loc['diff'] + df1_wrong.loc['BACKSTOP'][0]
    
    list_df_merg.append(df1merg)
    
    if ts >= 7:
        yr = 1
        ts = 0
    else:
        ts = ts + 1


writer = pd.ExcelWriter('RateOfAct.xlsx')

sheet_names = ['2021S1D1', '2021S1D2','2021S2D1', '2021S2D2',
               '2021S3D1', '2021S3D2','2021S4D1', '2021S4D2',
               '2022S1D1', '2022S1D2','2022S2D1', '2022S2D2',
               '2022S3D1', '2022S3D2','2022S4D1', '2022S4D2',]

for i,dfr in enumerate(list_df_merg):
    dfr.to_excel(writer, sheet_name = sheet_names[i])

writer.close()


















