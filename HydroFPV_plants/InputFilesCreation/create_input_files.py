# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 09:14:00 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np 
import os
       


# Import existing input file
filename = r'TEMBA_Refer.xlsx'

sheet_names = ['TECHNOLOGY', 'AvailabilityFactor', 'CapacityFactor', 'CapacityToActivityUnit',
               'CapitalCost', 'EmissionActivityRatio', 'FixedCost', 'InputActivityRatio',
               'OutputActivityRatio', 'OperationalLife', 'ResidualCapacity', 'VariableCost']

# 'TotalAnnualMaxCapacity',
# 'TotalAnnualMaxCapacityInvestment

# Import disaggregated plant file
filename_plants = r'Parameters_hybrid_plants.xlsx'


# Add disaggregated power plants 
writer = pd.ExcelWriter('Combined_techs_input_file.xlsx')



for i in range(len(sheet_names)):
    
    # Add new disaggregated techs
    df = pd.read_excel(filename, sheet_name = sheet_names[i])
    df_add = pd.read_excel(filename_plants, sheet_name = sheet_names[i])
    df_comb = pd.concat([df, df_add], axis=0, ignore_index=True)
    
    # Fix hydropower outside of the Nile Basin
    if sheet_names[i] == 'ResidualCapacity':
        # Residual capacities of HP plants in the Nile for each country per size
        resc_eg_med_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('EGHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_eg_large_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('EGHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_et_med_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('ETHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_et_large_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('ETHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_sd_med_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SDHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_sd_large_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SDHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_ss_med_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SSHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_ss_large_nile = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SSHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         &~ (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
    
        # Total residual capacities of HP plants for each country per size (from TEMBA)
        resc_eg_med_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('EGHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_eg_large_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('EGHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_et_med_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('ETHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_et_large_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('ETHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_sd_med_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SDHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_sd_large_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SDHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_ss_med_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SSHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S02'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        resc_ss_large_temba = sum(df_comb[(df_comb['TECHNOLOGY'].str.contains('SSHY'))
                                         & (df_comb['TECHNOLOGY'].str.contains('S03'))
                                         & (df_comb['TECHNOLOGY'].str.contains('DM'))][2015])
        
     
        # Actual residual capacities of HP plants in other rivers for each country per size
        resc_eg_med = max(resc_eg_med_temba - resc_eg_med_nile, 0)
        resc_eg_large = max(resc_eg_med_temba - resc_eg_med_nile, 0)
        resc_et_med = max(resc_et_med_temba - resc_et_med_nile, 0)
        resc_et_large = max(resc_et_med_temba - resc_et_med_nile, 0)
        resc_sd_med = max(resc_sd_med_temba - resc_sd_med_nile, 0)
        resc_sd_large = max(resc_sd_med_temba - resc_sd_med_nile, 0)
        resc_ss_med = max(resc_ss_med_temba - resc_ss_med_nile, 0)
        resc_ss_large = max(resc_ss_med_temba - resc_ss_med_nile, 0)
    
        # Insert the calculated value in the df 
        resc_eg_med_list = (np.ones(56) * resc_eg_med).tolist()
        resc_eg_large_list = (np.ones(56) * resc_eg_large).tolist()
        resc_et_med_list = (np.ones(56) * resc_et_med).tolist()
        resc_et_large_list = (np.ones(56) * resc_et_large).tolist()
        resc_sd_med_list = (np.ones(56) * resc_sd_med).tolist()
        resc_sd_large_list = (np.ones(56) * resc_sd_large).tolist()
        resc_ss_med_list = (np.ones(56) * resc_ss_med).tolist()
        resc_ss_large_list = (np.ones(56) * resc_ss_large).tolist()
        
        def insert_row(row):
            if 'HYDMS03X' in row['TECHNOLOGY']:
                if 'EG' in row['TECHNOLOGY']:
                    return resc_eg_large_list
                elif 'ET' in row['TECHNOLOGY']:
                    return resc_et_large_list
                elif 'SD' in row['TECHNOLOGY']:
                    return resc_sd_large_list
                elif 'SS' in row['TECHNOLOGY']:
                    return resc_ss_large_list
            
            elif 'HYDMS02X' in row['TECHNOLOGY']:
                if 'EG' in row['TECHNOLOGY']:
                    return resc_eg_med_list
                elif 'ET' in row['TECHNOLOGY']:
                    return resc_et_med_list
                elif 'SD' in row['TECHNOLOGY']:
                    return resc_sd_med_list
                elif 'SS' in row['TECHNOLOGY']:
                    return resc_ss_med_list
                
            else: 
                return row[1:]
            
        df_comb.iloc[:,1:] = df_comb.apply(lambda row: insert_row(row), axis = 1)
        
    
    
    df_comb.to_excel(writer, sheet_name = sheet_names[i], index=False)

writer.close()


























