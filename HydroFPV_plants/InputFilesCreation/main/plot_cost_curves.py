# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:04:58 2023

@author: Alessandro Pieruzzi
"""

# Script to plot cost curves of technologies aggregated by type

import pandas as pd
import os
import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt


# Read current values from created input files
filepath = r'Created Files/TEMBA_ENB_ref.xlsx'
df_capex = pd.read_excel(filepath, sheet_name='CapitalCost')
df_opex = pd.read_excel(filepath, sheet_name='FixedCost')
# Read dict for techs names and aggregations
data_dir = 'Data'
url1 = os.path.join(data_dir, 'agg_col.csv')
url2 = os.path.join(data_dir, 'agg_pow_col.csv')
url4 = os.path.join(data_dir, 'power_tech.csv')
url5 = os.path.join(data_dir, 'techcodes.csv')
agg1 = pd.read_csv(url1, sep=',', encoding="ISO-8859-1")
agg2 = pd.read_csv(url2, sep=',', encoding="ISO-8859-1")
agg_col = agg1.to_dict('list')
agg_pow_col = agg2.to_dict('list')
power_tech = pd.read_csv(url4, sep=',', encoding="ISO-8859-1")
codes = pd.read_csv(url5)
codes_dict = dict(zip(codes['tech_code'],codes['tech_name']))
# Values from IRENA 2021
capex_irena = pd.read_csv('Data/capital_cost_curves_irena.csv', index_col='TECH')
# Interpolate to the years
years = np.arange(2015,2071,1)
capex_irena_interp = pd.DataFrame(np.zeros(shape=(len(capex_irena),56)), 
                           index=capex_irena.index, 
                           columns=df_capex.columns[1:])

for idx,row in capex_irena.iterrows():
    interp_lin = scipy.interpolate.interp1d(np.arange(2015,2045,5), row.values, fill_value='extrapolate')
    capex_irena_interp.loc[idx] = interp_lin(years)


# Extract the techs from temba
capex_temba = pd.DataFrame(np.zeros(shape=(len(capex_irena),56)), 
                           index=capex_irena.index, 
                           columns=df_capex.columns[1:])

capex_temba.loc['BIO'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGBMCHP01N', 2015:].values
capex_temba.loc['SOL'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGSOU1P03X', 2015:].values
capex_temba.loc['WIND'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGWINDP00X', 2015:].values
capex_temba.loc['CSP'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGSOC1P00X', 2015:].values
capex_temba.loc['COAL'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGCOSCP01N', 2015:].values
capex_temba.loc['NUCLEAR'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGNULWP04N', 2015:].values
capex_temba.loc['LFOLCC'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGLFRCP01N', 2015:].values
capex_temba.loc['LFOE'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGLFRCP01N', 2015:].values
capex_temba.loc['GASCC'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGNGCCP01N', 2015:].values
capex_temba.loc['GASOC'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGNGGCP01N', 2015:].values
capex_temba.loc['GASTE'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGNGGCP01N', 2015:].values
capex_temba.loc['GEO'] = df_capex.loc[df_capex['TECHNOLOGY']=='ETGOCVP02N', 2015:].values
capex_temba.loc['HFOE'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGHFGCP01N', 2015:].values
capex_temba.loc['HFOT'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGHFGCP01N', 2015:].values
capex_temba.loc['HYDROsm'] = df_capex.loc[df_capex['TECHNOLOGY']=='ETHYDSRS02', 2015:].values
capex_temba.loc['HYDROror'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGHYDESS02', 2015:].values
capex_temba.loc['HYDRO'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGHYDHAS03', 2015:].values

# Plot
for idx,row in capex_temba.iterrows():
    plt.figure(figsize=(10,8))
    plt.plot(years,capex_irena_interp.loc[idx],label='irena')
    plt.plot(years,capex_temba.loc[idx],label='temba')
    plt.title(idx)
    plt.ylabel('Capital cost (M$)')
    plt.ylim(0,8000)
    plt.xlabel('Year')
    plt.legend()


# # Plot solar TEMBA
# capex_solar_temba = df_capex.iloc[np.where(df_capex['TECHNOLOGY'].str.contains('EGSO'))]
# plt.figure(figsize=(10,8))
# for idx,row in capex_solar_temba.iterrows():
#     plt.plot(years,capex_solar_temba.loc[idx][1:].values,label=codes_dict[capex_solar_temba.loc[idx]['TECHNOLOGY'][2:]])
# plt.title('Solar')
# plt.ylabel('Capital cost (M$)')
# plt.ylim(0,8000)
# plt.xlabel('Year')
# plt.legend()

