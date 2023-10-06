# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 11:56:35 2023

@author: Alessandro Pieruzzi
"""

# Creates excel file with all FPV and hydro location and respective parameters 
# in separate sheets

import pandas as pd
import numpy as np
import scipy.interpolate

folder = r'Data'
FPV_switch = 'Yes'

country_codes = ['EG', 'ET', 'SD', 'SS']
scenarios = ['ref','RCP26_dry', 'RCP26_wet', 
            'RCP60_dry', 'RCP60_wet', 
            'RCP85_dry', 'RCP85_wet',]
 

for s,scenario in enumerate(scenarios):
    df_list = []
    # Read file
    filename = f'Data/CombinedHydroSolar_{scenario}.csv'
    if FPV_switch == 'No':
        filename_out = f'Parameters_hybrid_plants_{scenario}_NoFPV.xlsx'
    else:
        filename_out = f'Parameters_hybrid_plants_{scenario}.xlsx'
    df = pd.read_csv(filename)
    df = df.fillna(0)
    
    # # Add codes column
    # loc_codes_df = pd.DataFrame(loc_codes, columns = ['loc_codes'])
    # df = pd.concat([df,loc_codes_df], axis = 1)
    
    
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
        
        elif row['Country'] == 'SOUTH SUDAN':
            return str(country_codes[3] + prefix
                       + row['loc_codes'] + suffix)
        else:
            print('Missing country')
        
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
    df_solar = df[cols_solar][:37] #harcoded index for plants without reservoir (no fpv)
    
    df_techs_hydro = df_hydro['hydro_codes']
    df_techs_solar = df_solar['solar_codes']
    df_techs = pd.concat([df_techs_hydro, df_techs_solar], ignore_index = True) #it is a series, problems with saving column name 
    df_techs = pd.DataFrame(df_techs).rename(columns={0:'TECHNOLOGY'})
    df_list.append(df_techs)
    
    timeslices_full = np.arange(2015,2071,1)
    col_names = timeslices_full.tolist()
    col_names.insert(0,'TECHNOLOGY')
    
    
    # ------------------------------------------------------------------------------
    
    # HYD and FPV Techs sets
    df_sel = df.iloc[np.where((df['Type'] == 'Reservoir') &
                              (df['First Year'] > 2023))[0]]
    df_sorted = df_sel.sort_values(by=['Country', 'Unit Name'])
    
    df_fpv = df_sorted['solar_codes']
    df_hyd = df_sorted['hydro_codes']
    
    df_list.append(df_hyd)
    df_list.append(df_fpv)
    
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
    # CapacityOfOneTechnologyUnit
    
    df_cotu = pd.DataFrame(df_hydro[['hydro_codes','Capacity (MW)', 'First Year']])
    df_cotu = df_cotu.rename(columns = {'hydro_codes' : 'TECHNOLOGY'})
    df_cotu = df_cotu.iloc[np.where(df_hydro['First Year']>2015)]
    df_cotu_tot = pd.concat([df_cotu['Capacity (MW)']/1000]*56, axis=1,
                          ignore_index=True).rename(lambda x: 2015+x, axis=1)
    df_cotu = pd.concat([df_cotu['TECHNOLOGY'], df_cotu_tot], axis=1)
    df_list.append(df_cotu)
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
    
    
    # Read data
    capex_temba = pd.read_csv('Data/capital_cost_curves_TEMBA.csv', index_col='TECH')
    capex_irena = pd.read_csv('Data/capital_cost_curves_irena.csv', index_col='TECH')
    solar_capex_irena = capex_irena.loc['SOL'].to_numpy().astype(float).T.flatten()
    solar_capex_temba = capex_temba.loc['SOL'].to_numpy().astype(float).T.flatten()
    years_points = np.arange(2015,2045,5)
    years = np.arange(2015,2071,1)

    def create_new_capex(temba,irena):
        # Interpolate irena up to 2045
        interp_lin = scipy.interpolate.interp1d(years_points, irena)
        new_cost_values = interp_lin(years[0:26]) 
        # Extrapolate using temba linear behaviour
        m = (temba[-1]-temba[26])/(years[-1]-years[26])
        new_cost_values = np.concatenate([new_cost_values,new_cost_values[-1]+m*np.arange(1,31,1)])
        return new_cost_values
    
    capex_solar = create_new_capex(solar_capex_temba,solar_capex_irena)
    
    # Calculate costs for FPV
    capex_fpv = capex_solar * fpv_gpv
    opex_fpv = capex_fpv * op_cap_fpv
    
    # Calculate costs for hydro
    opex_hydro_large = 55 * np.ones(56)
    opex_hydro_small = 65 * np.ones(56)
    
    # Create capital and fixed costs dataframes 
    opexes = [opex_hydro_large, opex_hydro_small, opex_fpv]
    df_opex = pd.DataFrame(df_techs, columns = ['TECHNOLOGY'])
    df_opex = df_opex.reindex(columns = col_names)
    
    def create_costs(row, costs):
        if ('HYD' in row.iloc[0]) & (('S03' in row.iloc[0]) | ('S02' in row.iloc[0])):
            return costs[0].tolist()
        elif ('HYD' in row.iloc[0]) & ('S01' in row.iloc[0]):
            return costs[1].tolist()
        elif ('SOFPV' in row.iloc[0]):
            return costs[2].tolist()
    
    values_opex = df_opex[col_names].apply(lambda row: create_costs(row, opexes), axis = 1)
    
    for i in range(len(values_opex)):
        df_opex.iloc[i,1:] = values_opex[i]
    
    # Capex for hydro (following Carlino et al)
    capacity_values = [0.1, 1, 10, 500, 11000]
    cost_values = [3744.4, 3256, 2836, 2446, 2054.5]
    new_cap_values = df_hydro['Capacity (MW)'].tolist()
    new_cap_values = sorted(new_cap_values)
    
    interp_lin = scipy.interpolate.interp1d(capacity_values, cost_values)
    new_cost_values = interp_lin(new_cap_values)
    
    df_capcost = pd.DataFrame(np.column_stack([new_cap_values, new_cost_values]), 
                              columns = ['Capacity', 'Cost'])
    
    df_hydro_sorted = df_hydro.sort_values('Capacity (MW)')
    df_hydro_sorted['CapCost'] = new_cost_values.tolist()
    
    df_capex_hydro = pd.DataFrame(df_hydro_sorted[['hydro_codes','CapCost']])
    df_capex_hydro = df_capex_hydro.rename(columns = {'hydro_codes' : 'TECHNOLOGY'})
    df_capcost = pd.concat([df_capex_hydro['CapCost']]*56, axis = 1, ignore_index=True).rename(lambda x: 2015+x, axis=1)
    df_capex_hydro = pd.concat([df_capex_hydro['TECHNOLOGY'], df_capcost], axis=1)
    
    
    df_capex_fpv = pd.DataFrame(df_solar[['solar_codes']])
    df_capex_fpv = df_capex_fpv.rename(columns = {'solar_codes' : 'TECHNOLOGY'})
    df_capcost_fpv = pd.DataFrame([capex_fpv], columns = col_names[1:])
    df_capcost_fpv = pd.concat([df_capcost_fpv]*len(df_techs_solar), ignore_index=True)
    
    df_capex_fpv = pd.concat([df_capex_fpv['TECHNOLOGY'], df_capcost_fpv], axis = 1)
    
    df_capex = pd.concat([df_capex_hydro, df_capex_fpv], axis=0, ignore_index=True)
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
    # Existing plants have as residual capacity their full capacity for 80 years
    # Planned plants have as residual capacity 0
    # FPV: 0 for all
    
    df_resc = pd.DataFrame(df_hydro[['hydro_codes','Capacity (MW)', 'Status', 'First Year']])
    df_resc = df_resc.rename(columns = {'hydro_codes' : 'TECHNOLOGY'})
    cols = col_names.copy()
    cols.insert(1,'Capacity (MW)')
    cols.insert(2, 'Status' )
    cols.insert(3,'First Year')
    df_resc = df_resc.reindex(columns = cols)
    
    def get_capacities(row):
        if row['First Year'] <= 2015:
            last_year = row['First Year'] + 80
            idx = min(last_year - 2015, 56)
            value = (np.ones(idx) * row['Capacity (MW)'] / 1000).tolist()
            value = value + np.zeros(56-idx).tolist()
            return value
        elif row['First Year'] > 2015:
            return np.zeros(56)
        else:
            print('Something is wrong')
    
    values = df_resc[cols].apply(lambda row: get_capacities(row), axis = 1)
    
    for i in range(len(values)):
        df_resc.iloc[i,4:] = values[i]
    
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
    
    tot_capmax = 8 #GW
    # perc = df_tamc["Capacity (MW)"] / df_tamc["Capacity (MW)"].sum()
    # cap = perc * tot_capmax
    cap = df_tamc["Capacity (MW)"]/1000
    
    df_capmax_fpv = pd.concat([cap]*49, axis = 1, ignore_index=True).rename(lambda x: 2023+x, axis=1)
    df_capmax.loc[:,2023:] = df_capmax_fpv #only allow FPV after 2023
    df_tamc_solar = pd.concat([df_tamc['TECHNOLOGY'], df_capmax], axis = 1)
    
    df_tamc_tot = pd.concat([df_tamc_hydro, df_tamc_solar], axis=0, ignore_index=True)
    df_list.append(df_tamc_tot)
    
    
    # -----------------------------------------------------------------------------
    # TotalAnnualMaxCapacityInvestment
    # Total capacity installable for a specific tech in a specific year  
    
    # Hydro: max capacity of the HP plant every year, after year of construction
    # Assumption: force the model to install the plant from the year it is supposed to be ready
    df_tmci_hydro = pd.concat([df_tamc_hydro, df_hydro['First Year']], axis = 1)
    
    for i in range(np.shape(df_tmci_hydro)[0]):
        for j in range(1,np.shape(df_tmci_hydro)[1]-1):
            if df_tmci_hydro.columns[j] < df_tmci_hydro['First Year'][i]:
                df_tmci_hydro.iloc[i,j] = 0
            if df_tmci_hydro['First Year'][i] < 2015:
                df_tmci_hydro.iloc[i,j] = 0
    
    df_tmci_hydro = df_tmci_hydro.iloc[:,:-1]    
    
    # FPV: same as max capacity: after the lake is present, osemosys can allocate 
    # how much of the total available capacity as it wants every year (0 for ref scenario)
    
    max_cap_inv = cap
    for i in range(len(max_cap_inv)):
        max_cap_inv[i]=min(max_cap_inv[i],0.3)
        
    
    df_tmci_solar = df_tamc_solar 
    
    df_solar.loc[8,'First Year'] = 2022
    df_tmci_solar = pd.concat([df_tamc_solar, df_solar['First Year']], axis = 1)
    
    for i in range(len(df_tmci_solar)):
        df_tmci_solar.loc[i,2022:2040] = np.minimum(df_tmci_solar.loc[i,2015:2040], 
                                                    np.ones(len(df_tmci_solar.loc[i,2015:2040]))*0.3)
        df_tmci_solar.loc[i,2041:2050] = np.minimum(df_tmci_solar.loc[i,2041:2050], 
                                                    np.ones(len(df_tmci_solar.loc[i,2041:2050]))*0.6)
        df_tmci_solar.loc[i,2051:2070] = np.minimum(df_tmci_solar.loc[i,2051:2070], 
                                                    np.ones(len(df_tmci_solar.loc[i,2051:2070])))
        
    
    for i in range(np.shape(df_tmci_solar)[0]):
        for j in range(1,np.shape(df_tmci_solar)[1]-1):
            if df_tmci_solar.columns[j] < df_tmci_solar['First Year'][i] + 2: # considering 2 years of construction time 
                df_tmci_solar.iloc[i,j] = 0
                
    df_tmci_solar = df_tmci_solar.iloc[:,:-1]  
    
    
    
    df_tmci_tot = pd.concat([df_tmci_hydro, df_tmci_solar], axis=0, ignore_index=True)
    df_list.append(df_tmci_tot)
    
    
    # -----------------------------------------------------------------------------
    # TotalAnnualMinCapacityInvestment
    df_mincap = pd.DataFrame(df_hydro[['hydro_codes','First Year', 'Capacity (MW)']])
    df_mincap = df_mincap.iloc[np.where((df_mincap['hydro_codes'] == 'ETHYDRNS03') |
                          (df_mincap['hydro_codes'] == 'EGHYDNBS02') |
                          (df_mincap['hydro_codes'] == 'SDHYDUAS03'))[0]].reset_index(drop=True)
    df_mincap['value'] = np.zeros(len(df_mincap)).tolist()
    
    df_value = pd.concat([df_mincap['value']]*56, axis = 1, ignore_index=True).rename(lambda x: 2015+x, axis=1)
    df_mincap = pd.concat([df_mincap,df_value], axis =1)
    
    df_mincap.iloc[0,df_mincap['First Year'][0]-2015+4] = df_mincap['Capacity (MW)'][0]/1000
    df_mincap.iloc[1,df_mincap['First Year'][1]-2015+4] = df_mincap['Capacity (MW)'][1]/1000
    df_mincap.iloc[2,df_mincap['First Year'][2]-2015+4] = df_mincap['Capacity (MW)'][2]/1000
    
    df_mincap = df_mincap.drop(columns = ['First Year', 'Capacity (MW)', 'value'])
    df_mincap = df_mincap.rename(columns = {'hydro_codes' : 'TECHNOLOGY'})
    df_list.append(df_mincap)
    
    # -----------------------------------------------------------------------------
    # TotalTechnologyAnnualActivityUp
    
    series = np.zeros(56)
    series[8:12] = np.arange(13.3734,66.867,13.3734)
    series[12:] = 53.4936
    list_values = series.tolist()
    list_values.insert(0,'ETHYDRNS03')
    
    df = pd.DataFrame([list_values], columns=col_names)
    df_list.append(df)
    
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
    sheet_names = ['TECHNOLOGY', 'TECHS_HYD', 'TECHS_FPV', 'AvailabilityFactor', 'CapacityFactor', 'CapacityOfOneTechnologyUnit',
                   'CapacityToActivityUnit','CapitalCost', 'EmissionActivityRatio', 
                   'FixedCost', 'InputActivityRatio','OutputActivityRatio', 
                   'OperationalLife', 'ResidualCapacity', 'TotalAnnualMaxCapacity',
                   'TotalAnnualMaxCapacityInvestmen','TotalAnnualMinCapacityInvestmen', 
                   'TotalTechnologyAnnualActivityUp', 'VariableCost']
    
    # 'TotalAnnualMaxCapacity',
    # 'TotalAnnualMaxCapacityInvestment',
    
    writer = pd.ExcelWriter(filename_out)
    
    for i,dfr in enumerate(df_list):
        if FPV_switch == 'No':
            if isinstance(dfr,pd.Series):
                dfr = dfr.iloc[np.where(~dfr.iloc[:].str.contains('FPV'))[0]]
            else:
                dfr = dfr.iloc[np.where(~dfr.iloc[:,0].str.contains('FPV'))[0]]
        if sheet_names[i] in ['TECHS_HYD', 'TECHS_FPV']:
            dfr.to_excel(writer, sheet_name = sheet_names[i], index=False, header=False)
        else:
            dfr.to_excel(writer, sheet_name = sheet_names[i], index=False)
    
    writer.close()
    
    













