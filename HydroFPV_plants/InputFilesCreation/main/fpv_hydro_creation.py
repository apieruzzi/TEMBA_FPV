# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 11:56:35 2023

@author: Alessandro Pieruzzi
"""

# Creates excel file with all FPV and hydro location and respective parameters 
# in separate sheets

import pandas as pd
import os
import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt

folder = r'Data'
df_list = []

# Create tech codes
loc_codes = ['HA', 'A1', 'A2', 'RN', 'UM', 'KA', 'BA', 'CY', 'LT', 'MR', 
             'RO', 'SE', 'JA', 'DA', 'SH', 'KJ', 'DG', 'MG', 'SB', 'ES', 
             'NH', 'NA', 'T1', 'T2']
country_codes = ['EG', 'ET', 'SD']


# Read file
filename = r'Data/CombinedHydroSolar.csv'
df = pd.read_csv(filename)
df = df.fillna(0)

# Add codes column
loc_codes_df = pd.DataFrame(loc_codes, columns = ['loc_codes'])
df = pd.concat([df,loc_codes_df], axis = 1)


# Create technology codes
def create_codes(row, tech):
    
    if tech == 'hydro':
        prefix = 'HYD'
    elif tech == 'solar':
        prefix = 'SOFPV'
    else:
        print('Invalid tech')
    
    if int(row['Capacity (MW)']) < 100:
        if prefix == 'HYD':
            suffix = 'S02'
        else:
            suffix = '3'
            
    elif int(row['Capacity (MW)']) > 100:
        if prefix == 'HYD':
            suffix = 'S03'
        else:
            suffix = '3'
    
    if row['Country'] == 'EGYPT':
        return str(country_codes[0] + prefix
                   + row['loc_codes'] + suffix)
    
    elif row['Country'] == 'ETHIOPIA':
        return str(country_codes[1] + prefix
                   + row['loc_codes'] + suffix)
    
    elif row['Country'] == 'SUDAN':
        return str(country_codes[2] + prefix
                   + row['loc_codes'] + suffix)
    
for tech in ['hydro', 'solar']:  
    col_name = tech + '_codes'
    df[col_name] = df.apply(lambda row: create_codes(row,tech), axis = 1)


# Split solar and hydro dfs
cols_hydro = ['Country', 'Unit Name', 'Latitude ', 'Longitude', 'Status',
       'Reservoir area (km2)', 'Capacity (MW)', 'CF_H1D1', 'CF_H1D2',
       'CF_H2D1', 'CF_H2D2', 'CF_H3D1', 'CF_H3D2', 'CF_H4D1', 'CF_H4D2',
        'First Year', 'loc_codes', 'hydro_codes']
cols_solar = ['Country', 'Unit Name', 'Latitude ', 'Longitude', 'Status',
       'Reservoir area (km2)', 'Capacity (MW)', 'CF_S1D1', 'CF_S1D2',
       'CF_S2D1', 'CF_S2D2', 'CF_S3D1', 'CF_S3D2','CF_S4D1', 'CF_S4D2',
       'First Year', 'loc_codes', 'solar_codes']
df_hydro = df[cols_hydro]
df_hydro = df_hydro[(df_hydro['hydro_codes'] != 'ETHYDLTS02')] #No hydropower on lake tana
df_hydro = df_hydro.reset_index(drop=True)
df_solar = df[cols_solar][:19] #harcoded index for plants without reservoir (no fpv)

df_techs_hydro = df_hydro['hydro_codes']
df_techs_solar = df_solar['solar_codes']
df_techs = pd.concat([df_techs_hydro, df_techs_solar], ignore_index = True) #it is a series, problems with saving column name 
df_techs = pd.DataFrame(df_techs).rename(columns={0:'TECHNOLOGY'})
df_list.append(df_techs)

timeslices_full = np.arange(2015,2071,1)
col_names = timeslices_full.tolist()
col_names.insert(0,'TECHNOLOGY')

# ------------------------------------------------------------------------------

# AvailabilityFactor
def select_values(row, values):
    if ('HYD' in row.iloc[0]):
        return values[0].tolist()
    elif ('SOFPV' in row.iloc[0]):
        return values[1].tolist()

def create_df(df_sample, values, col_names):
    df = pd.DataFrame(df_sample, columns = ['TECHNOLOGY'])
    df = df.reindex(columns = col_names)
    values = df[col_names].apply(lambda row: select_values(row,values), axis = 1)
    
    for i in range(len(values)):
        df.iloc[i,1:] = values[i]
        
    return df
    
values_hyd = np.ones(56) * 0.95
values_sol = np.ones(56)
values = [values_hyd, values_sol]

df_avfc = create_df(df_techs, values, col_names)
df_list.append(df_avfc)


# -----------------------------------------------------------------------------
# Capacity factors 
# Expand dataframe and add timeslices column
df_new = pd.DataFrame(np.repeat(df_techs.values, 8, axis = 0), columns = ['TECHNOLOGY']) 
timeslices = ['S1D1', 'S1D2', 
              'S2D1', 'S2D2', 
              'S3D1', 'S3D2', 
              'S4D1', 'S4D2']
timeslices_exp = pd.DataFrame(timeslices*len(df_techs), columns = ['TIMESLICE'])
df_tot = pd.concat([df_new,timeslices_exp], axis = 1)


# Create df with tech codes and CF only

df_cf_hydro = df_hydro[[ 'hydro_codes', 'CF_H1D1', 'CF_H1D2','CF_H2D1', 'CF_H2D2',
                  'CF_H3D1', 'CF_H3D2', 'CF_H4D1', 'CF_H4D2']]

df_cf_hydro = df_cf_hydro.rename(columns={'CF_H1D1':'S1D1', 
                                          'CF_H1D2':'S1D2',
                                          'CF_H2D1':'S2D1', 
                                          'CF_H2D2':'S2D2',
                                          'CF_H3D1':'S3D1',
                                          'CF_H3D2':'S3D2',
                                          'CF_H4D1':'S4D1',
                                          'CF_H4D2':'S4D2', 
                                          'hydro_codes':'codes'})

df_cf_solar = df_solar[['solar_codes','CF_S1D1', 'CF_S1D2', 'CF_S2D1', 'CF_S2D2',
                  'CF_S3D1', 'CF_S3D2','CF_S4D1', 'CF_S4D2']]
df_cf_solar = df_cf_solar.rename(columns={'solar_codes':'codes',
                                          'CF_S1D1':'S1D1', 
                                          'CF_S1D2':'S1D2',
                                          'CF_S2D1':'S2D1', 
                                          'CF_S2D2':'S2D2',
                                          'CF_S3D1':'S3D1',
                                          'CF_S3D2':'S3D2',
                                          'CF_S4D1':'S4D1',
                                          'CF_S4D2':'S4D2'})

df_tot2 = pd.concat([df_cf_hydro, df_cf_solar], ignore_index=True)

# Flatten df 
cf_array = df_tot2.to_numpy()[:,1:].flatten().astype(float)
cf_list = cf_array.tolist()
cf_df = pd.DataFrame(cf_list, columns=[2015])
cf_df = pd.concat([cf_df[2015]]*56, axis=1,
                      ignore_index=True).rename(lambda x: 2015+x, axis=1)

# Put the df together
df_cf = pd.concat([df_tot,cf_df], axis=1) 
df_list.append(df_cf)


# -----------------------------------------------------------------------------
# CapacityToActivityUnit
values_hyd = np.ones(1) * 31.536 
values_sol = np.ones(1) * 31.536  
values = [values_hyd, values_sol]

df_ctau = create_df(df_techs, values, ['TECHNOLOGY','VALUE'])
df_list.append(df_ctau)


# -----------------------------------------------------------------------------
# Costs 

# Parameters
op_cap_pv = 0.013 # opex are 1.3% of capex for ground mounted panels 
fpv_gpv = 1.08 # FPV capex are 8% more than GPV capex
op_cap_fpv = 0.025 # opex are 2.5% of capex for FPV 

timeslices_old = np.arange(2015,2045,5)
timeslices_new = np.arange(2015,2041,1)


# Read data
capex_irena = pd.read_csv('Data/capital_cost_curves_IRENA.csv').to_numpy().astype(float).T.flatten()
capex_temba = pd.read_csv('Data/capital_cost_curves_TEMBA.csv').to_numpy().astype(float).T.flatten()


# Interpolate IRENA
# interp_lin = scipy.interpolate.interp1d(timeslices_old, capex_irena)
# capex_irena_lin = interp_lin(timeslices_new)

interp = scipy.interpolate.interp1d(timeslices_old, capex_irena, kind = 'cubic')
capex_irena = interp(timeslices_new)

# interp_slin = scipy.interpolate.interp1d(timeslices_old, capex_irena, kind = 'slinear')
# capex_irena_slin = interp_cub(timeslices_new)

# plt.figure()
# plt.plot(timeslices_new,capex_irena_lin)
# plt.plot(timeslices_new,capex_irena)
# plt.plot(timeslices_new,capex_irena_slin)

# Calculate opex IRENA
opex_irena = capex_irena * op_cap_pv 

# Extend series to 2040 using TEMBA
# Extract function from temba series from 2040 onwards 

def lin_funct(a,b,x):
    return a + b * x

a = capex_irena[-1]
b = (capex_temba[-1] - capex_temba[25]) / (30)
capex_irena_end = lin_funct(a,b,np.arange(0,30,1))

# Merge the series 
capex_irena_tot = np.hstack((capex_irena, capex_irena_end))

opex_irena_end = np.ones(29)*opex_irena[-1]
opex_irena_tot = np.hstack((opex_irena, opex_irena_end))


# Calculate costs for FPV
capex_fpv = capex_irena_tot * fpv_gpv
opex_fpv = capex_fpv * op_cap_fpv


# Add cost for hydro 
capex_hydro_large = 3074.61 * np.ones(56) #same for medium size
capex_hydro_small = 4831.53 * np.ones(56)

opex_hydro_large = 55 * np.ones(56)
opex_hydro_small = 65 * np.ones(56)

# Create capital and fixed costs dataframes 

capexes = [capex_hydro_large, capex_hydro_small, capex_fpv]
opexes = [opex_hydro_large, opex_hydro_small, opex_fpv]

df_capex = pd.DataFrame(df_techs, columns = ['TECHNOLOGY'])
df_opex = pd.DataFrame(df_techs, columns = ['TECHNOLOGY'])

df_capex = df_capex.reindex(columns = col_names)
df_opex = df_opex.reindex(columns = col_names)

def create_costs(row, costs):
    if ('HYD' in row.iloc[0]) & (('S03' in row.iloc[0]) | ('S02' in row.iloc[0])):
        return costs[0].tolist()
    elif ('HYD' in row.iloc[0]) & ('S01' in row.iloc[0]):
        return costs[1].tolist()
    elif ('SOFPV' in row.iloc[0]):
        return costs[2].tolist()


values_capex = df_capex[col_names].apply(lambda row: create_costs(row, capexes), axis = 1)
values_opex = df_opex[col_names].apply(lambda row: create_costs(row, opexes), axis = 1)

for i in range(len(values_capex)):
    df_capex.iloc[i,1:] = values_capex[i]
    df_opex.iloc[i,1:] = values_opex[i]

df_list.append(df_capex)


# ----------------------------------------------------------------------------
# EmissionActivityRatio
values_hyd = np.append(1,np.zeros(56)).tolist()
values_hyd.insert(0,'EGREN')
values_sol = np.append(1,np.zeros(56)).tolist() 
values_sol.insert(0,'EGREN')
values = [values_hyd, values_sol]

cols = col_names.copy()
cols.insert(1,'EMISSION')
cols.insert(2,'MODEOFOPERATION')

df_emar = pd.DataFrame(df_techs, columns = ['TECHNOLOGY'])
df_emar = df_emar.reindex(columns = cols)


def create_emissions(row, values):
    if ('HYD' in row.iloc[0]):
        return values[0]
    elif ('SOFPV' in row.iloc[0]):
        return values[1]


values_df = df_emar[cols].apply(lambda row: create_emissions(row, values), axis = 1)
for i in range(len(values_df)):
    df_emar.iloc[i,1:] = values_df[i]

df_list.append(df_emar)


# ----------------------------------------------------------------------------
# FixedCosts
df_list.append(df_opex)


# -----------------------------------------------------------------------------
# InputActivityRatio

def assign_fuels(row):
    if ('EG' in row['TECHNOLOGY']):
        return 'EGWAT1'
    elif ('ET' in row['TECHNOLOGY']):
        return 'ETWAT1'
    elif ('SD' in row['TECHNOLOGY']):
        return 'SDWAT1'
    elif ('SS' in row['TECHNOLOGY']):
        return 'SSWAT1'   
    
    
def assign_values_inar(row, values_hydro, values_sol):
    if 'HYD' in row['TECHNOLOGY']:
        if ('EG' in row['TECHNOLOGY']):
            return values_hydro[0]
        elif ('ET' in row['TECHNOLOGY']):
            return values_hydro[1]
        elif ('SD' in row['TECHNOLOGY']):
            return values_hydro[2]
        elif ('SS' in row['TECHNOLOGY']):
            return values_hydro[3]
    elif ('SOFPV' in row['TECHNOLOGY']):
        if ('SOL' in row['FUEL']):
            return values_sol[0]
        elif ('WAT' in row['FUEL']):
            return values_sol[1]


value_hydro_EG = np.append(1, np.ones(56) * 125.0371).tolist()
value_hydro_ET = np.append(1, np.ones(56) * 23.67248).tolist()
value_hydro_SD = np.append(1, np.ones(56) * 93.90445).tolist()
value_hydro_SS = np.append(1, np.ones(56) * 30.96987).tolist()
values_hydro = [value_hydro_EG, value_hydro_ET, value_hydro_SD, value_hydro_SS]

value_sol_ele = np.append(1, np.ones(56)).tolist()
value_sol_wat = np.append(1, np.zeros(56)).tolist()
values_sol = [value_sol_ele, value_sol_wat]

# Create empty df with all necessary rows and columns
# Only the solar techs use both wat and sola fuel, hydro techs only use wat fuel
df_inar = pd.DataFrame(df_techs, columns = ['TECHNOLOGY'])
df_inar_exp = pd.DataFrame(np.repeat(df_inar.loc[len(df_techs_hydro):].values, 2, axis = 0), columns = ['TECHNOLOGY'])
df_inar = pd.concat([df_inar.loc[0:len(df_techs_hydro)-1], df_inar_exp], axis = 0, ignore_index=True) #hardcoded index
cols = col_names.copy()
cols.insert(1,'FUEL')
cols.insert(2,'MODEOFOPERATION')
df_inar = df_inar.reindex(columns = cols)

# Fill the fuel column
fuels_df = df_inar[cols].apply(lambda row: assign_fuels(row), axis = 1)
for i in range(len(fuels_df)):
    df_inar.iloc[i,1] = fuels_df[i]
    
fuel_codes = df_inar.iloc[len(df_techs_hydro)::2,1].values #hardcoded index
solar_codes = []
for i in range(len(fuel_codes)):
    country_code = fuel_codes[i][0:2]
    solar_codes.append(country_code + 'SOLA')
df_inar.iloc[len(df_techs_hydro)::2,1] = solar_codes

# Fill the other columns
values_df = df_inar[cols].apply(lambda row: assign_values_inar(row, values_hydro, values_sol), axis = 1)
for i in range(len(values_df)):
    df_inar.iloc[i,2:] = values_df[i]

df_list.append(df_inar)


# -----------------------------------------------------------------------------
# OutputActivityRatio

def assign_values_otar(row, values):
    if 'EL01' in row['FUEL']:
        return values[0]
    elif 'WAT' in row['FUEL']:
        return values[1]
    
    
value_ele = np.append(1, np.ones(56)).tolist()
value_wat = np.append(1, np.zeros(56)).tolist()
values = [value_ele, value_wat]

# Create empty df with all necessary rows and columns
# Both solar and hydro techs use both fuels 
df_otar = pd.DataFrame(df_techs, columns = ['TECHNOLOGY'])
df_otar = pd.DataFrame(np.repeat(df_otar.values, 2, axis = 0), columns = ['TECHNOLOGY'])
cols = col_names.copy()
cols.insert(1,'FUEL')
cols.insert(2,'MODEOFOPERATION')
df_otar = df_otar.reindex(columns = cols)

# Fill the fuel column
fuels_df = df_otar[cols].apply(lambda row: assign_fuels(row), axis = 1)
for i in range(len(fuels_df)):
    df_otar.iloc[i,1] = fuels_df[i]
    
fuel_codes = df_otar.iloc[::2,1].values 
solar_codes = []
for i in range(len(fuel_codes)):
    country_code = fuel_codes[i][0:2]
    solar_codes.append(country_code + 'EL01')
df_otar.iloc[::2,1] = solar_codes

# Fill the other columns
values_df = df_otar[cols].apply(lambda row: assign_values_otar(row, values), axis = 1)
for i in range(len(values_df)):
    df_otar.iloc[i,2:] = values_df[i]

df_list.append(df_otar)


# -----------------------------------------------------------------------------
# OperationalLife
values_hyd = np.ones(1) * 80
values_sol = np.ones(1) * 25 
values = [values_hyd, values_sol]

df_opl = create_df(df_techs, values, ['TECHNOLOGY','VALUE'])
df_list.append(df_opl)


# -----------------------------------------------------------------------------
# ResidualCapacity
# Hydro:
# Existing plants have as residual capacity their full capacity for the whole period (assumption)
# Planned plants have as residual capacity 0
# FPV: 0 for all

df_resc = pd.DataFrame(df_hydro[['hydro_codes','Capacity (MW)', 'Status']])
df_resc = df_resc.rename(columns = {'hydro_codes' : 'TECHNOLOGY'})
cols = col_names.copy()
cols.insert(1,'Capacity (MW)')
cols.insert(2, 'Status' )
df_resc = df_resc.reindex(columns = cols)

def get_capacities(row):
    if row['Status'] == 'Existing':
        value = (np.ones(56) * row['Capacity (MW)'] / 1000).tolist()
        return value
    elif row['Status'] == 'Candidate':
        return np.zeros(56)

values = df_resc[cols].apply(lambda row: get_capacities(row), axis = 1)

for i in range(len(values)):
    df_resc.iloc[i,3:] = values[i]

df_resc = df_resc[col_names]

# Add solar techs
df_resc_solar = pd.DataFrame(df_techs_solar)
df_resc_solar = df_resc_solar.rename(columns = {'solar_codes' : 'TECHNOLOGY'})
df_values = pd.DataFrame(np.zeros((len(df_resc_solar),56)), 
                         columns = timeslices_full.tolist())
df_resc_solar = pd.concat([df_resc_solar, df_values], axis = 1)

# Concat two techs
df_resc = pd.concat([df_resc, df_resc_solar], axis=0, ignore_index=True)

df_list.append(df_resc)


# -----------------------------------------------------------------------------
# TotalAnnualMaxCapacity
# Total capacity allowed for a specific tech in a specific year

# Hydro: max capacity of the HP plant every year 
df_tamc = pd.DataFrame(df_hydro[['hydro_codes','Capacity (MW)']])
df_tamc = df_tamc.rename(columns = {'hydro_codes' : 'TECHNOLOGY'})
df_capmax = pd.concat([df_tamc['Capacity (MW)']/1000]*56, axis=1,
                      ignore_index=True).rename(lambda x: 2015+x, axis=1)
df_tamc_hydro = pd.concat([df_tamc['TECHNOLOGY'], df_capmax], axis=1)

# FPV: depends on the area available and year of construction of a dam (0 for ref scenario)
# Trial 1. using values from Sanchez: 8810 MWp for whole EAPP if 1% coverage (existing plants only).
# Assumed total capacity between the 4 countries to be 8000 including planned 
# Spreading over the plants based on their capacity (as proxy for area)

df_tamc = pd.DataFrame(df_solar[['solar_codes','Capacity (MW)']])
df_tamc = df_tamc.rename(columns = {'solar_codes' : 'TECHNOLOGY'})
df_capmax = pd.DataFrame(np.zeros((len(df_tamc),56)), columns = col_names[1:])

tot_capmax = 8
perc = df_tamc["Capacity (MW)"] / df_tamc["Capacity (MW)"].sum()
perc[8] = perc[0] # lake tana
cap = perc * tot_capmax
df_capmax_fpv = pd.concat([cap]*49, axis = 1, ignore_index=True).rename(lambda x: 2022+x, axis=1)
df_capmax.loc[:,2022:] = df_capmax_fpv #only allow after 2022
df_tamc_solar = pd.concat([df_tamc['TECHNOLOGY'], df_capmax], axis = 1)

df_tamc_tot = pd.concat([df_tamc_hydro, df_tamc_solar], axis=0, ignore_index=True)
df_list.append(df_tamc_tot)


# -----------------------------------------------------------------------------
# TotalAnnualMaxCapacityInvestment
# Total capacity installable for a specific tech in a specific year  

# Hydro: max capacity of the HP plant every year, after year of construction
df_tmci_hydro = pd.concat([df_tamc_hydro, df_hydro['First Year']], axis = 1)

for i in range(np.shape(df_tmci_hydro)[0]):
    for j in range(1,np.shape(df_tmci_hydro)[1]-1):
        if df_tmci_hydro.columns[j] < df_tmci_hydro['First Year'][i]:
            df_tmci_hydro.iloc[i,j] = 0

df_tmci_hydro = df_tmci_hydro.iloc[:,:-1]    

# FPV: same as max capacity: after the lake is present, osemosys can allocate 
# how much of the total available capacity as it wants every year (0 for ref scenario)
df_tmci_solar = df_tamc_solar #for ref scenario 

df_solar.loc[8,'First Year'] = 2022
df_tmci_solar = pd.concat([df_tamc_solar, df_solar['First Year']], axis = 1)


for i in range(np.shape(df_tmci_solar)[0]):
    for j in range(1,np.shape(df_tmci_solar)[1]-1):
        if df_tmci_solar.columns[j] < df_tmci_solar['First Year'][i] + 2: # considering 2 years of construction time 
            df_tmci_solar.iloc[i,j] = 0
            
df_tmci_solar = df_tmci_solar.iloc[:,:-1]  



df_tmci_tot = pd.concat([df_tmci_hydro, df_tmci_solar], axis=0, ignore_index=True)
df_list.append(df_tmci_tot)

# -----------------------------------------------------------------------------
# VariableCost
values_hyd = np.insert(np.ones(56) * 0.00001, 0, 1)
values_sol = np.insert(np.ones(56) * 0.00001, 0, 1)
values = [values_hyd, values_sol]

cols = col_names.copy()
cols.insert(1, 'MODEOFOPERATION')
df_vc = create_df(df_techs, values, cols)
df_list.append(df_vc)

# -----------------------------------------------------------------------------


# Save all dataframes to excel in different sheets
sheet_names = ['TECHNOLOGY', 'AvailabilityFactor', 'CapacityFactor', 
               'CapacityToActivityUnit','CapitalCost', 'EmissionActivityRatio', 
               'FixedCost', 'InputActivityRatio','OutputActivityRatio', 
               'OperationalLife', 'ResidualCapacity', 'TotalAnnualMaxCapacity',
               'TotalAnnualMaxCapacityInvestmen','VariableCost']

# 'TotalAnnualMaxCapacity',
# 'TotalAnnualMaxCapacityInvestment',

writer = pd.ExcelWriter('Parameters_hybrid_plants.xlsx')

for i,dfr in enumerate(df_list):
    dfr.to_excel(writer, sheet_name = sheet_names[i], index=False)

writer.close()
    
    













