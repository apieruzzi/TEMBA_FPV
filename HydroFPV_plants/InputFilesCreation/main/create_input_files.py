# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 09:14:00 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np 
import os
       


# Import existing input file

filenames = ["TEMBA_Refer_ENB.xlsx", "TEMBA_1.5_ENB.xlsx", "TEMBA_2.0_ENB.xlsx"]
hydrological_regime = 'RCP85_dry'


sheet_names_to_comb = ['TECHNOLOGY', 'AvailabilityFactor', 'CapacityFactor', 
                       'CapacityOfOneTechnologyUnit', 'CapacityToActivityUnit',
                       'CapitalCost', 'EmissionActivityRatio', 'FixedCost', 
                       'InputActivityRatio','OutputActivityRatio','OperationalLife',
                       'ResidualCapacity', 'TotalAnnualMaxCapacity',
                       'TotalAnnualMaxCapacityInvestmen',
                       'TotalAnnualMinCapacityInvestmen', 'VariableCost']


first_year = 2015
years = np.arange(first_year,2071)

# Import disaggregated plant file
filename_plants = 'Parameters_hybrid_plants_RCP85_dry.xlsx'
folder = r'Created Files'



for x, filename in enumerate(filenames):
    writer = pd.ExcelWriter(os.path.join(folder,filenames[x][0:-5]+'_'+hydrological_regime+'.xlsx'))
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
            
            # Fix hydropower outside of the Nile Basin
            if sheet_names[i] == 'ResidualCapacity':
                resc_med1 = (np.ones(46)*0.107).tolist() #2015 to 2060
                resc_med2 = (np.ones(6)*0.064).tolist() #2060 to 2066
                resc_med3 = (np.ones(4)*0.032).tolist() #2066 to 2070
                resc_med = resc_med1+resc_med2+resc_med3
                resc_small =np.zeros(56).tolist()
                resc_large = (np.ones(56)*0.604).tolist()
                data = [resc_large, resc_med, resc_small]
    
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
                    
                df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row, data), axis = 1)
            
            if sheet_names[i] == 'TotalAnnualMaxCapacity':
                maxc_large = (np.ones(56)*3.262).tolist()
                maxc_med = (np.ones(56)*0.291).tolist()
                maxc_small = (np.ones(56)*0.006).tolist() 
                data = [maxc_large, maxc_med, maxc_small]
                df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row, data), axis = 1)
                
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
            
            if sheet_names[i] == 'TotalAnnualMinCapacityInvestmen':
                minci_large = np.zeros(56).tolist()
                minci_large[2] = 1.87 #2017
                minci_large[8] = 0.688 #2023
                minci_med = np.zeros(56).tolist()
                minci_small = np.zeros(56).tolist()
                data = [minci_large, minci_med, minci_small]
                df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row, data), axis = 1)
            
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
            
            # Fix trade link costs
            if sheet_names[i] == 'VariableCost':
                def add_row(row):
                    if 'ETELKE' in row['TECHNOLOGY']:
                        initial_value = 180
                        value = (np.ones(15)*initial_value).tolist() + (np.ones(10)*initial_value+30).tolist() \
                            + (np.ones(10)*initial_value+2*30).tolist() + (np.ones(21)*initial_value+3*30).tolist()
                        if row['MODEOFOPERATION'] == 1:
                            return [-x for x in value]
                        elif row['MODEOFOPERATION'] == 2:
                            return value
                    if 'ETELDJ'in row['TECHNOLOGY']:
                        initial_value = 100
                        value = (np.ones(15)*initial_value).tolist() + (np.ones(10)*initial_value+15).tolist() \
                            + (np.ones(10)*initial_value+2*15).tolist() + (np.ones(21)*initial_value+3*15).tolist()
                        if row['MODEOFOPERATION'] == 1:
                            return [-x for x in value]
                        elif row['MODEOFOPERATION'] == 2:
                            return (np.ones(56)*(99999)).tolist()
                    if 'LYELEG'in row['TECHNOLOGY']:
                        initial_value = 85
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
            # Remove generic hydro techs for all countries but Ethiopia
            if 'TECHNOLOGY' in df.columns:  
                df = df[~df['TECHNOLOGY'].str.contains('EGHYD')]
                df = df[~df['TECHNOLOGY'].str.contains('SDHYD')]
                df = df[~df['TECHNOLOGY'].str.contains('SSHYD')]
            df.to_excel(writer, sheet_name = sheet_names[i], index=False)
    
    writer.close()


























