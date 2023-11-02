# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 12:07:50 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np

filename = r'Created Files/TEMBA_ENB_ref.xlsx'
filename_codes = r'Data/techcodes.csv'

df_codes = pd.read_csv(filename_codes)
codes_dict = dict(zip(df_codes['tech_code'], df_codes['tech_name']))

df_in = pd.read_excel(filename, sheet_name='InputActivityRatio')
df_out = pd.read_excel(filename, sheet_name='OutputActivityRatio')
writer = pd.ExcelWriter(r'Created Files/WaterRatios.xlsx')


tech_list = ['EGBIOFUELX', 'EGBMCHP01N', 'EGCO00X00X', 'EGCOSCP01N', 'EGCOSCP03N',
             'EGCOSCP04N', 'EGCR00X00X', 'EGCRUDPROX', 'EGHFGCP01N', 'EGLFRCP01N', 
             'EGNG00X00X', 'EGNGCCP01N', 'EGNGGCP01N', 'EGGOCVP02N', 'EGUR00X00X', 
             'EGNULWP04N', 'EGSOC1P00X', 'EGSOU1P03X', 'EGWINDP00X']


def select_lines(df):
    df = df.iloc[np.where(df['FUEL'].str.contains('EGWAT'))]
    df = df[['TECHNOLOGY',2023]]
    df = df.loc[df['TECHNOLOGY'].isin(tech_list)]
    return df


df_in = select_lines(df_in).set_index('TECHNOLOGY')
df_in = df_in.sort_values(by='TECHNOLOGY')
df_out = select_lines(df_out).set_index('TECHNOLOGY')
df_out = df_out.sort_values(by='TECHNOLOGY')
df_diff = df_in-df_out    

df_in['Name'] = [codes_dict[k[2:]] for k in df_in.index.tolist()]
df_out['Name'] = [codes_dict[k[2:]] for k in df_out.index.tolist()]
df_diff['Name'] = [codes_dict[k[2:]] for k in df_diff.index.tolist()]


df_in.to_excel(writer, sheet_name='InputActivityRatio')
df_out.to_excel(writer, sheet_name='OutputActivityRatio')
df_diff.to_excel(writer, sheet_name='Difference')

writer.close()