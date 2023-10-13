# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 12:07:50 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np

filename = r'Created Files/TEMBA_ENB_ref.xlsx'

df_in = pd.read_excel(filename, sheet_name='InputActivityRatio')
df_out = pd.read_excel(filename, sheet_name='OutputActivityRatio')
writer = pd.ExcelWriter(r'Created Files/WaterRatios.xlsx')

def select_lines(df):
    df = df.iloc[np.where(df['FUEL'].str.contains('EGWAT'))]
    df = df[['TECHNOLOGY',2023]]
    return df

df_in = select_lines(df_in).set_index('TECHNOLOGY')
df_out = select_lines(df_out).set_index('TECHNOLOGY')
df_diff = df_in-df_out

df_in.to_excel(writer, sheet_name='InputActivityRatio')
df_out.to_excel(writer, sheet_name='OutputActivityRatio')
df_diff.to_excel(writer, sheet_name='Difference')

writer.close()