"""
Created on Tue Jun 13 09:14:00 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np 
import os
import scipy.interpolate
       
# Creates the final input files for OSEMOSYS merging TEMBA ENB with 
# the hydro and fpv solar technologies 

# Import existing input file

filenames = ["TEMBA_Refer_ENB.xlsx"]
# , "TEMBA_1.5_ENB.xlsx", "TEMBA_2.0_ENB.xlsx"]

filename_out = 'TEMBA_ENB'

sheet_names_to_comb = ['TECHNOLOGY', 'AvailabilityFactor', 'CapacityFactor', 
                       'CapacityOfOneTechnologyUnit', 'CapacityToActivityUnit',
                       'CapitalCost', 'EmissionActivityRatio', 'FixedCost', 
                       'InputActivityRatio','OutputActivityRatio','OperationalLife',
                       'ResidualCapacity', 'TotalAnnualMaxCapacity',
                       'TotalAnnualMaxCapacityInvestmen',
                       'TotalAnnualMinCapacityInvestmen', 
                       'TotalTechnologyAnnualActivityUp','VariableCost']


first_year = 2015
years = np.arange(first_year,2071)

scenarios = ['Carb_Low', 'Land_Low']
                   # 'RCP26_dry']
# 'RCP26_wet', 
#                    'RCP60_dry', 'RCP60_wet', 
#                    'EXT_High', 'EXT_Low']

# scenarios = ['EXT_High', 'EXT_Low',
#              ]
# # 'ref', 'Carb_High', 'Carb_Low', 

FPV_switch = 'Yes' # [Yes or No]
NoConstSwitch = 'No' # [Yes or No]
ssa_switch = 'No' # [Low or High or No]
pot_switch = 'Yes' # [Yes or No]

for s,scenario in enumerate(scenarios):

    # Import disaggregated plant file
    if FPV_switch == 'No' and scenario in ['ref','RCP26_dry', 'RCP26_wet', 'RCP60_dry', 'RCP60_wet']:
            filename_plants = f'Parameters_hybrid_plants_{scenario}_NoFPV.xlsx'
    elif FPV_switch == 'Yes' and scenario in ['ref','RCP26_dry', 'RCP26_wet', 'RCP60_dry', 'RCP60_wet']:
        filename_plants = f'Parameters_hybrid_plants_{scenario}.xlsx'
    elif FPV_switch == 'No' and scenario not in ['ref','RCP26_dry', 'RCP26_wet', 'RCP60_dry', 'RCP60_wet']: 
        filename_plants = 'Parameters_hybrid_plants_ref_NoFPV.xlsx'
    elif FPV_switch == 'Yes' and scenario not in ['ref','RCP26_dry', 'RCP26_wet', 'RCP60_dry', 'RCP60_wet']: 
        filename_plants = 'Parameters_hybrid_plants_ref.xlsx'
    
    print(filename_plants)
    folder = r'Created Files'
    
    if scenario == 'EXT_High':
        land_tax_switch = 'High'
        carbon_tax_switch = 'High'
    elif scenario == 'EXT_Low':
        land_tax_switch = 'Low'
        carbon_tax_switch = 'Low'
    elif scenario == 'Carb_High':
        land_tax_switch = 'No'
        carbon_tax_switch = 'High'
    elif scenario == 'Carb_Low':
        land_tax_switch = 'No'
        carbon_tax_switch = 'Low'
    elif scenario == 'Land_High':
        land_tax_switch = 'High'
        carbon_tax_switch = 'No'
    elif scenario == 'Land_Low':
        land_tax_switch = 'Low'
        carbon_tax_switch = 'No'
    else:
        carbon_tax_switch = 'No'
        land_tax_switch = 'No'

    
    for x, filename in enumerate(filenames):
        if FPV_switch =='No':
            name = os.path.join(folder,filename_out +'_'+ scenario + 'NoFPV'+'.xlsx')
        else:
            if ssa_switch == 'Low':
                name = os.path.join(folder,filename_out + '_'+ scenario + '_Low' + '.xlsx')
            if ssa_switch == 'High':
                name = os.path.join(folder,filename_out + '_'+ scenario + '_High' + '.xlsx')
            if NoConstSwitch == 'Yes':
                name = os.path.join(folder,filename_out + '_'+ scenario + '_Const' + '.xlsx')
            else:
                name = os.path.join(folder,filename_out + '_'+ scenario +'.xlsx')

        writer = pd.ExcelWriter(name)
        xl = pd.ExcelFile(filename)
        sheet_names = xl.sheet_names
        
        # Add two sheets for the new sets
        df_hyd = pd.read_excel(filename_plants, sheet_name='TECHS_HYD')
        df_fpv = pd.read_excel(filename_plants, sheet_name='TECHS_FPV')
        df_hyd.to_excel(writer, sheet_name = 'TECHS_HYD', index=False)
        df_fpv.to_excel(writer, sheet_name = 'TECHS_FPV', index=False)  
        
        for i in range(len(sheet_names)):
            
            df = pd.read_excel(filename, sheet_name = sheet_names[i])
            
            if 2015 in df.columns and sheet_names[i]!='YEAR':
                idx1 = df.columns.get_loc(2015)
                idx2 = df.columns.get_loc(first_year)
                idx3 = df.columns.get_loc(2070)
                df = df.iloc[:,np.r_[0:idx1,idx2:idx3+1]]
            if sheet_names[i] == 'YEAR':
                df = df.loc[first_year-2015:]
                df = df.rename(columns={2015:first_year})
            
            if sheet_names[i] in sheet_names_to_comb:
                # Add new disaggregated techs
                df_add = pd.read_excel(filename_plants, sheet_name = sheet_names[i])
                if 2015 in df_add.columns:
                    idx1 = df_add.columns.get_loc(2015)
                    idx2 = df_add.columns.get_loc(first_year)
                    idx3 = df_add.columns.get_loc(2070)
                    df_add = df_add.iloc[:,np.r_[0:idx1,idx2:idx3+1]]
                df_comb = pd.concat([df, df_add], axis=0, ignore_index=True)
                
                def insert_row(row, data):                
                    if 'HYDMS03X' in row['TECHNOLOGY']:
                        if 'ET' in row['TECHNOLOGY']:
                            return data[0]
                    elif 'HYDMS02X' in row['TECHNOLOGY']:
                        if 'ET' in row['TECHNOLOGY']:
                            return data[1]
                    if 'HYDMS01X' in row['TECHNOLOGY']:
                        if 'ET' in row['TECHNOLOGY']:
                            return data[2]
                    else: 
                        return row[1:]
                
                # Fix hydropower outside of the Nile Basin
                if sheet_names[i] == 'ResidualCapacity':
                    resc_med1 = (np.ones(46)*0.107).tolist() #2015 to 2060
                    resc_med2 = (np.ones(6)*0.064).tolist() #2060 to 2066
                    resc_med3 = (np.ones(4)*0.032).tolist() #2066 to 2070
                    resc_med = resc_med1+resc_med2+resc_med3
                    resc_small =np.zeros(56).tolist()
                    resc_large = (np.ones(56)*0.604).tolist()
                    data = [resc_large, resc_med, resc_small]
                    df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row, data), axis = 1)
                
                if sheet_names[i] == 'TotalAnnualMaxCapacity':
                    maxc_large = (np.ones(56)*3.262).tolist()
                    maxc_med = (np.ones(56)*0.291).tolist()
                    maxc_small = (np.ones(56)*0.006).tolist() 
                    data = [maxc_large, maxc_med, maxc_small]
                    df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row, data), axis = 1)
                    if NoConstSwitch == 'Yes':
                        # data = df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('FPV'))[0], 2015:].values
                        # df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('FPV'))[0], 2015:] = data*10
                        df_comb.iloc[:,1:] = 99999
                    if pot_switch == 'Yes':
                        df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('EGSOU1P03X'))[0], 2015:] = np.ones(56) * 99999
                        df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('EGSOV1F01X'))[0], 2015:] = np.ones(56) * 99999
                        df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('EGSOV2F01X'))[0], 2015:] = np.ones(56) * 99999
                        df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('EGWINDP00X'))[0], 2015:] = np.ones(56) * 99999
                                            
                if sheet_names[i] == 'TotalAnnualMaxCapacityInvestmen':
                    maxci_large1 = np.zeros(9).tolist()
                    maxci_large1[2] = 1.87 #2017
                    maxci_large1[8] = 0.688 #2023
                    maxci_large2 = (np.ones(47)*2.658).tolist() 
                    maxci_large = maxci_large1 + maxci_large2
                    maxci_med1 = np.zeros(17).tolist()
                    maxci_med2 = (np.ones(39)*0.088).tolist() 
                    maxci_med = maxci_med1 + maxci_med2
                    maxci_small1 = np.zeros(17).tolist()
                    maxci_small2 = (np.ones(39)*0.006).tolist() 
                    maxci_small = maxci_small1 + maxci_small2
                    data = [maxci_large, maxci_med, maxci_small]
                    df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row, data), axis = 1)
                    # if NoConstSwitch == 'Yes':
                    #     df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('FPV'))[0], 2015:] = np.ones(56)*99999
                
                if sheet_names[i] == 'TotalAnnualMinCapacityInvestmen':
                    minci_large = np.zeros(56).tolist()
                    minci_large[2] = 1.87 #2017
                    minci_large[8] = 0.688 #2023
                    minci_med = np.zeros(56).tolist()
                    minci_small = np.zeros(56).tolist()
                    data = [minci_large, minci_med, minci_small]
                    df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row, data), axis = 1)
                
                # Get technology list
                if sheet_names[i] == 'TECHNOLOGY':
                    tech_list = df_comb['TECHNOLOGY']
                
                # Fix emission activity ratios
                if sheet_names[i] == 'EmissionActivityRatio':
                    row_eg_hyd = df_comb.iloc[np.where(df_comb['TECHNOLOGY'] == 'EGHYDMS03X')]
                    values_eg_hyd = row_eg_hyd.iloc[:,1:].values.flatten().tolist()
                    row_sd_hyd = df_comb.iloc[np.where(df_comb['TECHNOLOGY'] == 'SDHYDMS03X')]
                    values_sd_hyd = row_sd_hyd.iloc[:,1:].values.flatten().tolist()
                    row_eg_sol = df_comb.iloc[np.where(df_comb['TECHNOLOGY'] == 'EGSOU1P03X')]
                    values_eg_sol = row_eg_sol.iloc[:,1:].values.flatten().tolist()
                    row_sd_sol = df_comb.iloc[np.where(df_comb['TECHNOLOGY'] == 'SDSOU1P03X')]
                    values_sd_sol = row_sd_sol.iloc[:,1:].values.flatten().tolist()
                    
                    def assign_row(row):
                        if 'EGHYD'in row['TECHNOLOGY']:
                            return values_eg_hyd
                        elif 'SDHYD' in row['TECHNOLOGY']:
                            return values_sd_hyd
                        if 'EGSO'in row['TECHNOLOGY']:
                            return values_eg_sol
                        elif 'SDSO' in row['TECHNOLOGY']:
                            return values_sd_sol
                        else:
                            return row[1:]
                    
                    df_comb.iloc[:,1:] = df_comb.apply(lambda row: assign_row(row), axis=1)
                    
                    # Remove the ET and SS hydro and FPV techs 
                    df_comb = df_comb[~df_comb['TECHNOLOGY'].str.contains('ETHYD')]
                    df_comb = df_comb[~df_comb['TECHNOLOGY'].str.contains('ETSOFPV')]
                    df_comb = df_comb[~df_comb['TECHNOLOGY'].str.contains('SSHYD')]
                    df_comb = df_comb[~df_comb['TECHNOLOGY'].str.contains('SSSOFPV')]
                    
                    # And land use activity ratio
                    planned_hyds = pd.read_excel(filename_plants, sheet_name='TECHS_HYD', header=None)
                    new_df = tech_list.iloc[np.where(tech_list.str.contains('SOU1P03X') |
                                                      tech_list.str.contains('WINDP00X') |
                                                      tech_list.str.contains('SOC') |
                                                      tech_list.str.contains('NULWP04N') |
                                                      tech_list.str.contains('GOCVP0') |
                                                      (tech_list.str.contains('NGCC') & ~tech_list.str.contains('X')) |
                                                      (tech_list.str.contains('COSC') & ~tech_list.str.contains('X')) |
                                                      (tech_list.str.contains('HF') & ~tech_list.str.contains('X')) |
                                                      (tech_list.str.contains('LF') & ~tech_list.str.contains('X')))].tolist()
                    new_df = new_df + planned_hyds[0].tolist()
                    new_df = pd.DataFrame(new_df, columns=['TECHNOLOGY'])
                    new_df['EMISSION'] = ['LAND'] * len(new_df)
                    new_df['MODEOFOPERATION'] = np.ones(len(new_df)).tolist()
                    new_df[2015] = np.zeros(len(new_df))
                    new_df = new_df.reset_index(drop=True)
                    years_cols = pd.concat([new_df[2015]]*55, axis=1,
                                       ignore_index=True).rename(lambda x: 2016+x, axis=1)
                    new_df = pd.concat([new_df,years_cols],axis=1)
                    
                    wind_value = (np.ones(56)*round(130/3.6,1)).tolist()
                    solar_value = (np.ones(56)*round(2000/3.6,1)).tolist()
                    csp_value = (np.ones(56)*round(1300/3.6,1)).tolist()
                    hydro_value = (np.ones(56)*round(650/3.6,1)).tolist()
                    nuclear_value = (np.ones(56)*round(7.1/3.6,1)).tolist()
                    geothermal_value = (np.ones(56)*round(45/3.6,1)).tolist()
                    gas_value = (np.ones(56)*round(410/3.6,1)).tolist()
                    coal_value = (np.ones(56)*round(1000/3.6,1)).tolist()
                    oil_value = gas_value
                    
                    def assign_emission(row):
                        if 'EG' in row['TECHNOLOGY']:
                            if 'WINDP00X' in row['TECHNOLOGY']:
                                return 'EGLANDWND'
                            if 'SOU1P03X' in row['TECHNOLOGY']:
                                return 'EGLANDSOL'
                            if 'HYD'in row['TECHNOLOGY']:
                                return 'EGLANDHYD'
                            if 'SOC'in row['TECHNOLOGY']:
                                return 'EGLANDSOC'
                            if 'NULWP04N' in row['TECHNOLOGY']:
                                return 'EGLANDNUL'
                            if 'GOCVP0'in row['TECHNOLOGY']:
                                return 'EGLANDGT'
                            if 'NGCC'in row['TECHNOLOGY']:
                                return 'EGLANDGAS'
                            if 'COSC'in row['TECHNOLOGY']:
                                return 'EGLANDCOAL'
                            if 'LF' in row['TECHNOLOGY'] or 'HF' in row['TECHNOLOGY']:
                                return 'EGLANDOIL'
                            else:
                                return row[3:]
                        else: 
                            if 'WINDP00X' in row['TECHNOLOGY']:
                                return 'LANDWND'
                            if 'SOU1P03X' in row['TECHNOLOGY']:
                                return 'LANDSOL'
                            if 'HYD'in row['TECHNOLOGY']:
                                return 'LANDHYD'
                            if 'SOC'in row['TECHNOLOGY']:
                                return 'LANDSOC'
                            if 'NULWP04N' in row['TECHNOLOGY']:
                                return 'LANDNUL'
                            if 'GOCVP0'in row['TECHNOLOGY']:
                                return 'LANDGT'
                            if 'NGCC'in row['TECHNOLOGY']:
                                return 'LANDGAS'
                            if 'COSC'in row['TECHNOLOGY']:
                                return 'LANDCOAL'
                            if 'LF' in row['TECHNOLOGY'] or 'HF' in row['TECHNOLOGY']:
                                return 'LANDOIL'
                            else:
                                return row[3:]
                    new_df.iloc[:,1] = new_df.apply(lambda row: assign_emission(row), axis=1)
                    
                    def assign_land_ratios(row):
                        if 'WINDP00X' in row['TECHNOLOGY']:
                            return pd.Series(wind_value)
                        if 'SOU1P03X' in row['TECHNOLOGY']:
                            return pd.Series(solar_value)
                        if 'HYD'in row['TECHNOLOGY']:
                            return pd.Series(hydro_value)
                        if 'SOC'in row['TECHNOLOGY']:
                            return pd.Series(csp_value)
                        if 'NULWP04N' in row['TECHNOLOGY']:
                            return pd.Series(nuclear_value)
                        if 'GOCVP0'in row['TECHNOLOGY']:
                            return pd.Series(geothermal_value)
                        if 'NGCC'in row['TECHNOLOGY']:
                            return pd.Series(gas_value)
                        if 'COSC'in row['TECHNOLOGY']:
                            return pd.Series(coal_value)
                        if 'LF' in row['TECHNOLOGY'] or 'HF' in row['TECHNOLOGY']:
                            return pd.Series(oil_value)
                        else:
                            return row[3:]
                    
                    new_df.iloc[:,3:] = new_df.apply(lambda row: assign_land_ratios(row), axis=1)
                    df_comb = pd.concat([df_comb,new_df], ignore_index=True)
                
                
                # Capital costs variation for sensitivity analysis
                if sheet_names[i] == 'CapitalCost' and ssa_switch!='No':
                    value = df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('SO'))[0],2015:]
                    if ssa_switch == 'Low':
                        value_changed = value.subtract(value[2015]*0.2, axis=0)
                    elif ssa_switch == 'High':
                        value_changed = value.add(value[2015]*0.2, axis=0)
                    df_comb.loc[np.where(df_comb['TECHNOLOGY'].str.contains('SO'))[0],2015:] = value_changed
                
                # Fix trade link costs
                if sheet_names[i] == 'VariableCost':
                    def add_row(row):
                        if 'ETELKE' in row['TECHNOLOGY']:
                            initial_value = 18
                            value = (np.ones(15)*initial_value).tolist() + (np.ones(10)*initial_value+30).tolist() \
                                + (np.ones(10)*initial_value+2*30).tolist() + (np.ones(21)*initial_value+3*30).tolist()
                            if row['MODEOFOPERATION'] == 1:
                                return [-x for x in value]
                            elif row['MODEOFOPERATION'] == 2:
                                return value
                        if 'ETELDJ'in row['TECHNOLOGY']:
                            initial_value = 18
                            value = (np.ones(15)*initial_value).tolist() + (np.ones(10)*initial_value+15).tolist() \
                                + (np.ones(10)*initial_value+2*15).tolist() + (np.ones(21)*initial_value+3*15).tolist()
                            if row['MODEOFOPERATION'] == 1:
                                return [-x for x in value]
                            elif row['MODEOFOPERATION'] == 2:
                                return (np.ones(56)*(99999)).tolist()
                        if 'LYELEG'in row['TECHNOLOGY']:
                            initial_value = 40
                            value = (np.ones(15)*initial_value).tolist() + (np.ones(10)*initial_value+15).tolist() \
                                + (np.ones(10)*initial_value+2*15).tolist() + (np.ones(21)*initial_value+3*15).tolist()
                            if row['MODEOFOPERATION'] == 1:
                                return value
                            elif row['MODEOFOPERATION'] == 2:
                                return [-x for x in value]
                        else:
                            return row[2:]
                        
                    df_comb.iloc[:,2:] = df_comb.apply(lambda row: add_row(row), axis=1)                    
                    
                # Remove generic hydro techs for all countries but Ethiopia
                if 'TECHNOLOGY' in df_comb.columns: 
                    df_comb = df_comb[~df_comb['TECHNOLOGY'].str.contains('EGHYDMS')]
                    df_comb = df_comb[~df_comb['TECHNOLOGY'].str.contains('SDHYDMS')]
                    df_comb = df_comb[~df_comb['TECHNOLOGY'].str.contains('SSHYDMS')]
                
                
                # Don't save the header for the techs sheet
                if sheet_names[i] == 'TECHNOLOGY':
                    df_comb.to_excel(writer, sheet_name = sheet_names[i], index=False, header=False)
                else:    
                    df_comb.to_excel(writer, sheet_name = sheet_names[i], index=False)
                
            
            else:   
                
                # Fix potentials
                if sheet_names[i] == 'TotalTechnologyModelPeriodActUp' and pot_switch == 'Yes':
                    df.loc[len(df),:] = ['EGSOU1P03X',31.536*63.8*len(years)]
                    df.loc[len(df),:] = ['ETSOU1P03X', 31.536*16.5*len(years)]
                    df.loc[len(df),:] = ['SDSOU1P03X',31.536*2.16*len(years)]
                    df.loc[len(df),:] = ['EGWINDP00X',31.536*58.8*len(years)]
                    df.loc[len(df),:] = ['ETWINDP00X',31.536*5.93*len(years)]
                    df.loc[len(df),:] = ['SDWINDP00X',31.536*5.78*len(years)]           
                
                # Add new emissions
                if sheet_names[i] == 'EMISSION':
                    codes = ['WND', 'SOL', 'HYD', 'SOC', 'NUL', 
                          'GT', 'GAS', 'COAL', 'OIL']
                    for pl in ['EG','']:
                        for code in codes:
                            df.loc[len(df)] = pl + 'LAND' + code
                
                if carbon_tax_switch != 'No':
                    # Add carbon tax
                    if carbon_tax_switch == 'Low':
                        value_init = 25
                        increase = value_init * 0.01
                        value_fin = value_init + 56 * value_init * 0.01
                        carbon_tax = np.arange(value_init,value_fin,increase)
                    elif carbon_tax_switch == 'High':
                        values = [80,140,200]
                        years_points = [2020,2030,2050]
                        interp_lin = scipy.interpolate.interp1d(years_points, values, fill_value='extrapolate')
                        carbon_tax = interp_lin(years)
                    
                    if sheet_names[i] == 'EmissionsPenalty':
                        df.loc[df['EMISSION'].str.contains('CO2'),2015:] = carbon_tax
                        carbon_tax_list = carbon_tax.tolist()
                        carbon_tax_list[0:0] = ['SSCO2']
                        df.loc[len(df)] = carbon_tax_list
                
                values = [80,140,200]
                years_points = [2020,2030,2050]
                interp_lin = scipy.interpolate.interp1d(years_points, values, fill_value='extrapolate')
                new_cost_values = interp_lin(years) 

                if land_tax_switch != 'No':
                    # Add land tax 
                    if sheet_names[i] == 'EmissionsPenalty':
                        codes_dict = {'OIL':'Oil',
                                      'COAL':'Oil',
                                      'GAS':'Gas', 
                                      'WND':'Wind',
                                      'SOL':'Solar',
                                      'SOC':'Solar',
                                      'HYD':'Hydro',
                                      'GT':'Geothermal',
                                      'NUL':'Nuclear'}
                        codes = ['WND', 'SOL', 'HYD', 'SOC', 'NUL', 
                              'GT', 'GAS', 'COAL', 'OIL']
                        for pl in ['EG','']:
                            if pl == 'EG':
                                df_values = pd.read_excel(r'Data/LandValues.xlsx', sheet_name='Stats_EG', index_col='Unnamed: 0')
                            else:
                                df_values = pd.read_excel(r'Data/LandValues.xlsx', sheet_name='Stats_ETSDSS', index_col='Unnamed: 0')
                            for code in codes:
                                if land_tax_switch == 'Low':
                                    land_tax = np.ones(56) * df_values.loc['First quantile', codes_dict[code]] * 0.001
                                elif land_tax_switch == 'High':
                                    land_tax = np.ones(56) * df_values.loc['Third quantile', codes_dict[code]] * 0.001    
                                df.loc[len(df)] = [pl + 'LAND' + code] + land_tax.tolist()
                    

                # Remove REN emission limits
                if sheet_names[i] == 'AnnualEmissionLimit':
                    df.loc[:, 2015:] = 99999
                
                # Remove generic hydro techs for all countries but Ethiopia
                if 'TECHNOLOGY' in df.columns:  
                    df = df[~df['TECHNOLOGY'].str.contains('EGHYD')]
                    df = df[~df['TECHNOLOGY'].str.contains('SDHYD')]
                    df = df[~df['TECHNOLOGY'].str.contains('SSHYD')]
                
                df.to_excel(writer, sheet_name = sheet_names[i], index=False)
        
        writer.close()
        print('Created file ', name)


























