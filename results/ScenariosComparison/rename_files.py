# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 11:51:56 2023

@author: Alessandro Pieruzzi
"""

import os


# Barcharts
folder_dest = r'barcharts_dest'
folder = r'barcharts'
scenario = 'RCP85'
codes = ['EAPP', 'EG', 'ET', 'SD', 'SS']

files_to_keep = ['Annual Emissions', 'New power generation capacity (Aggregate)',
                 'New power generation capacity (Detail solar)',
                 'New power generation capacity (Detail fpv)',
                 'New power generation capacity (Detail hydro)',
                 'Power Generation (Aggregate)','Power Generation (Detail hydro)',
                 'Power Generation (Detail solar)','Power Generation (Detail trades)', 
                 'Power Generation (Detail fpv)', 
                 'Power Generation Capacity (Aggregate)', 
                 'Power Generation Capacity (Detail hydro)',
                 'Power Generation Capacity (Detail solar)', 
                 'Power Generation Capacity (Detail fpv)', 
                 'Water consumption aggregated', 
                 'Water Consumption']

for code in codes:
    
    # Remove useless files:
    files = os.listdir(os.path.join(folder,code))
    files_to_keep_c = [code + '-' + file + '.png' for file in files_to_keep]
    for filename in files:        
        filepath = os.path.join(folder, code, filename)
        if filename not in files_to_keep_c:
            os.remove(filepath)
    
    # Rename remaining files:
    files = os.listdir(os.path.join(folder,code))
    for filename in files:        
        filepath = os.path.join(folder, code, filename)
        filename_new = filename[3:-4] + '_' + scenario + '.png'
        filepath_new = os.path.join(folder_dest, code, filename_new)
        os.rename(filepath,filepath_new)
        
        
        
    
# Piecharts
folder_dest = r'piecharts_dest'
folder = r'piecharts'
codes = ['EAPP', 'EG', 'ET', 'SD', 'SS']

files_to_keep = ['Capacity - Aggregate', 'Capacity - Detail solar',
                 'Generation - Aggregate', 'Generation - Detail hydro',
                 'Generation - Detail solar']


for code in codes:
    
    # Remove useless files:
    files = os.listdir(os.path.join(folder,code))
    files_to_keep_c = [file + ' - ' + code + '.png' for file in files_to_keep]
    for filename in files:        
        filepath = os.path.join(folder, code, filename)
        if filename not in files_to_keep_c:
            os.remove(filepath)
    
    # Rename remaining files:
    files = os.listdir(os.path.join(folder,code))
    for filename in files:        
        filepath = os.path.join(folder, code, filename)
        filename_new = filename[:-4] + '_' + scenario + '.png'
        filepath_new = os.path.join(folder_dest, code, filename_new)
        os.rename(filepath,filepath_new) 
        















    