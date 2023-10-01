# -*- coding: utf-8 -*-
"""
Created on Tue May 16 11:18:57 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np 
import os


# folder = r'E:\TUDELFT\THESIS\OSeMOSYS\TEMBA 2.1_ENB\input_data'
# filenames =  ["TEMBA_Refer.xlsx", "TEMBA_1.5.xlsx", "TEMBA_2.0.xlsx"]


prefixes = ["EG","ET","SD","SS", "ISNGEGBP00","LYELEGBP00"]
carbon_removal_tech = pd.DataFrame(['DZLYC', 'MATNC', 'RSACO'],columns = ['CIFGA'])

#  Data to add extra fuels for trade links that become external: 
nyears = 56
values_el = np.ones((3,nyears))*0.95
values_gas = np.ones((1, nyears))*0.99
data = [['ETELDJBP00','ETDUEL', 1 ], ['ETELKEBP00','ETDUEL', 1 ],
        ['ETNGDJBP00', 'ETDUNG',1], ['LYELEGBP00', 'EGDUEL', 2]]

folder = r'Data'
filenames = ["TEMBA_Refer.xlsx","TEMBA_1.5.xlsx", "TEMBA_2.0.xlsx"]


for x, filename in enumerate(filenames):
    filepath = os.path.join(folder, filenames [x])
    
    xl = pd.ExcelFile(filepath)
    sheet_names = xl.sheet_names
    DF_list = [pd.read_excel(filepath, sheet_name=sheet) for sheet in sheet_names]
    
    sheet_names_to_keep = ['STORAGE', 
                       'MODE_OF_OPERATION',
                       'REGION',
                       'TIMESLICE',
                       'YEAR',
                       'AnnualExogenousEmission',
                       'DiscountRate', 
                       'DepreciationMethod',
                       'ModelPeriodEmissionLimit',
                       'ModelPeriodExogenousEmission',
                       'OperationalLifeStorage',
                       'REMinProductionTarget', 
                       'RETagFuel',
                       'RETagTechnology',
                       'ReserveMargin',
                       'ReserveMarginTagFuel',
                       'ReserveMarginTagTechnology',
                       'TradeRoute',
                       'YearSplit']
    
    sheet_names_to_modify = [name for name in sheet_names if name not in sheet_names_to_keep]
    index = [sheet_names.index(i) for i in sheet_names_to_modify]
    

    writer = pd.ExcelWriter(filenames[x][0:-5]+'_ENB.xlsx')
    
    for i,df_orig in enumerate(DF_list):
        
        df = df_orig.copy()
        
        #Keep only selected countries and technology
        if i in index:
            df = df[df.iloc[:,0].str.startswith(tuple(prefixes))==True]
        
        #Fix fuels - tech combinations
        if sheet_names[i] == "InputActivityRatio" or sheet_names[i] == "OutputActivityRatio":
            df = df[(df.iloc[:,0].str.startswith(tuple(prefixes))==True) & 
                     (df.iloc[:,1].str.startswith(tuple(prefixes))==True)]
        
        #Add carbon removal techs
        if sheet_names[i] == "EMISSION" and filenames[x] != "TEMBA_Refer.xlsx":
            df = pd.concat([df,carbon_removal_tech], ignore_index = True)
        
        # Add dummy fuels 
        if sheet_names[i] == "OutputActivityRatio":
            df_1 = pd.DataFrame (data = data, columns = df.columns[:3])
            df_2 = pd.DataFrame (data = values_el, columns = df.columns[3:], index = [0,1,3])
            df_3 = pd.DataFrame (data = values_gas, columns = df.columns[3:], index = [2])
            df_values = pd.concat([df_2,df_3])
            df_fuels = pd.concat([df_1,df_values],axis=1)
            df = pd.concat([df,df_fuels], ignore_index=True)
        
        
        # Fix EGELSA date and biomass residual capacity
        if sheet_names[i] == 'TotalAnnualMaxCapacityInvestmen' \
        or sheet_names[i] == 'TotalAnnualMinCapacityInvestmen':
            df.loc[df['TECHNOLOGY']=='EGELSABP00',2015:] = 0
            df.loc[df['TECHNOLOGY']=='EGELSABP00',2024] = 1.5
            df.loc[df['TECHNOLOGY']=='EGELSABP00',2025] = 3
    
        if sheet_names[i] == 'ResidualCapacity' \
        or sheet_names[i] == 'TotalAnnualMaxCapacityInvestmen' \
        or sheet_names[i] == 'TotalAnnualMinCapacityInvestmen':
            df.loc[df['TECHNOLOGY'].str.contains('EGBM'),2015:2023] = 0
        
        # Fix technology header
        if sheet_names[i] == 'TECHNOLOGY':
            df = df.rename(columns = {list(df)[0]: 'TECHNOLOGY'})
        if sheet_names[i] in ['FUEL', 'EMISSION']:
            df.to_excel(writer, sheet_name = sheet_names[i], index=False, header=False)
        else:
            df.to_excel(writer, sheet_name = sheet_names[i], index=False)
        
        
    
    writer.close()






