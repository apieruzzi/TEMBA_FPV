# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 10:25:07 2023

@author: Alessandro Pieruzzi
"""


# Script to plot cost curves of technologies aggregated by type

import pandas as pd
import os
import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt


# Read current values from created input files
# filepath = r'Created Files/TEMBA_Refer_ENB.xlsx'
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

techs = ['Solar PV', 'Solar CSP', 'Solar FPV', 'Rooftop', 'With Storage']

colors_dict_agg = {
    "Coal":"black",
    "Oil" : "darkgrey",
    "Gas" : "darkorange",
    "Hydro" : "aqua",
    "Solar CSP" : "red",
    "Solar PV" : "orange",
    "Solar FPV" : "green",
    "Solar FPV_high" : "green",
    "Solar FPV_low" : "green",
    "Wind" : "royalblue",
    "Biomass" : "lightgreen",
    "Geothermal" : "brown", 
    "Nuclear" : "blueviolet",
    "Solar CSP_high" : "red",
    "Solar PV_high" : "orange",
    "Solar CSP_low" : "red",
    "Solar PV_low" : "orange",
    'Rooftop':'pink',
    'Rooftop_high':'pink',
    'Rooftop_low':'pink',
    'With Storage':'purple',
    'With Storage_high':'purple',
    'With Storage_low':'purple'
    }


# =============================================================================
# CAPEX
# =============================================================================
# Extract the techs from temba
capex_temba = pd.DataFrame(np.zeros(shape=(len(techs),56)), 
                           index=techs, 
                           columns=np.arange(2015,2071,1))

capex_temba.loc['Rooftop'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGSOV1F01X', 2015:].values
capex_temba.loc['Solar PV'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGSOU1P03X', 2015:].values
capex_temba.loc['With Storage'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGSOV2F01X', 2015:].values
capex_temba.loc['Solar CSP'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGSOC1P00X', 2015:].values


capex_temba.loc['Solar FPV'] = df_capex.loc[df_capex['TECHNOLOGY']=='EGSOFPVHA3', 2015:].values[0]

capex_temba = capex_temba.loc[~(capex_temba==0).all(axis=1)]



capex_temba.loc['Solar PV_low'] = capex_temba.loc['Solar PV'] - capex_temba.loc['Solar PV',2015]*0.2
capex_temba.loc['Solar PV_high'] = capex_temba.loc['Solar PV'] + capex_temba.loc['Solar PV',2015]*0.2
capex_temba.loc['Solar CSP_low'] = capex_temba.loc['Solar CSP'] - capex_temba.loc['Solar CSP',2015]*0.2
capex_temba.loc['Solar CSP_high'] = capex_temba.loc['Solar CSP'] + capex_temba.loc['Solar CSP',2015]*0.2
capex_temba.loc['Rooftop_low'] = capex_temba.loc['Rooftop'] - capex_temba.loc['Rooftop',2015]*0.2
capex_temba.loc['Rooftop_high'] = capex_temba.loc['Rooftop'] + capex_temba.loc['Rooftop',2015]*0.2
capex_temba.loc['With Storage_low'] = capex_temba.loc['With Storage'] - capex_temba.loc['With Storage',2015]*0.2
capex_temba.loc['With Storage_high'] = capex_temba.loc['With Storage'] + capex_temba.loc['With Storage',2015]*0.2
capex_temba.loc['Solar FPV_high'] = capex_temba.loc['Solar PV_high']*1.08
capex_temba.loc['Solar FPV_low'] = capex_temba.loc['Solar PV_low']*1.08

df_capex_high = capex_temba.iloc[np.where(capex_temba.index.str.contains('high'))[0]]
df_capex_low = capex_temba.iloc[np.where(capex_temba.index.str.contains('low'))[0]]

# Plot - normal
# lines = []
# plt.figure(figsize=(10,8)),

# for idx, row in capex_temba.iterrows():
#     line, = plt.plot(row,color=colors_dict_agg[idx])
#     lines.append(line)

# plt.legend(lines, capex_temba.index, loc='upper left', bbox_to_anchor=(1, 1))
# plt.title('Capital cost evolution of each technology')
# plt.xlabel('Year')
# plt.ylabel('Capital cost [M$/GW]')
# plt.tight_layout()
# plt.savefig('Capex.png')

# High
lines = []
plt.figure(figsize=(10,8)),

for idx, row in df_capex_high.iterrows():
    line, = plt.plot(row,color=colors_dict_agg[idx])
    lines.append(line)

plt.legend(lines, df_capex_high.index, loc='upper left', bbox_to_anchor=(1, 1))
plt.title('Capital cost evolution of each technology')
plt.xlabel('Year')
plt.ylabel('Capital cost [M$/GW]')
plt.tight_layout()
plt.savefig('Capex_high.png')

# Low
lines = []
plt.figure(figsize=(10,8)),

for idx, row in df_capex_low.iterrows():
    line, = plt.plot(row,color=colors_dict_agg[idx])
    lines.append(line)

plt.legend(lines, df_capex_low.index, loc='upper left', bbox_to_anchor=(1, 1))
plt.title('Capital cost evolution of each technology')
plt.xlabel('Year')
plt.ylabel('Capital cost [M$/GW]')
plt.tight_layout()
plt.savefig('Capex_low.png')



# =============================================================================
# OPEX
# =============================================================================
opex_temba = pd.DataFrame(np.zeros(shape=(len(techs),56)), 
                           index=techs, 
                           columns=np.arange(2015,2071,1))

opex_temba.loc['Biomass'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGBMCHP01N', 2015:].values
opex_temba.loc['Solar PV'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGSOU1P03X', 2015:].values
opex_temba.loc['Wind'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGWINDP00X', 2015:].values
opex_temba.loc['Solar CSP'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGSOC1P00X', 2015:].values
opex_temba.loc['Coal'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGCOSCP01N', 2015:].values
opex_temba.loc['Nuclear'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGNULWP04N', 2015:].values
opex_temba.loc['Oil'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGLFRCP01N', 2015:].values
opex_temba.loc['Gas'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGNGCCP01N', 2015:].values
opex_temba.loc['Geothermal'] = df_opex.loc[df_opex['TECHNOLOGY']=='ETGOCVP02N', 2015:].values
opex_temba.loc['Hydro'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGHYDHAS03', 2015:].values
opex_temba.loc['Solar FPV'] = df_opex.loc[df_opex['TECHNOLOGY']=='EGSOFPVHA3', 2015:].values[0]
opex_temba = opex_temba.loc[~(opex_temba==0).all(axis=1)]

opex_temba.loc['Solar PV_low'] = opex_temba.loc['Solar PV'] - opex_temba.loc['Solar PV',2015]*0.2
opex_temba.loc['Solar PV_high'] = opex_temba.loc['Solar PV'] + opex_temba.loc['Solar PV',2015]*0.2
opex_temba.loc['Solar CSP_low'] = opex_temba.loc['Solar CSP'] - opex_temba.loc['Solar CSP',2015]*0.2
opex_temba.loc['Solar CSP_high'] = opex_temba.loc['Solar CSP'] + opex_temba.loc['Solar CSP',2015]*0.2

# Plot
lines = []
plt.figure(figsize=(10,8)),

for idx, row in opex_temba.iterrows():
    line, = plt.plot(row,color=colors_dict_agg[idx])
    lines.append(line)

plt.legend(lines, opex_temba.index, loc='upper left', bbox_to_anchor=(1, 1))
plt.title('Operational cost evolution of each technology')
plt.xlabel('Year')
plt.ylabel('Capital cost [M$/GW]')
plt.tight_layout()
plt.savefig('Opex.png')
