# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 11:51:56 2023

@author: Alessandro Pieruzzi
"""

import os
import sys
from distutils.dir_util import copy_tree
import tempfile
import shutil

input_file_dummy = sys.argv[1]
scenario = sys.argv[2]

codes = ['EAPP', 'EG', 'ET', 'SD', 'SS']

with tempfile.TemporaryDirectory() as temp:

    global homedir
    homedir = temp
    print("Using temporary directory {}".format(homedir))
    
    # Copy results to the temp folder 
    path = f'results/export_{scenario}'
    copy_tree(path, homedir)
    
    
    # Barcharts
    folder = r'results/ScenarioComparison/barcharts' 
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
        files = os.listdir(os.path.join(homedir,'barcharts',code))
        files_to_keep_c = [code + '-' + file + '.png' for file in files_to_keep]
        for filename in files:        
            filepath = os.path.join(homedir,'barcharts', code, filename)
            if filename not in files_to_keep_c:
                os.remove(filepath)
        
        # Rename and move remaining files:
        files = os.listdir(os.path.join(homedir,'barcharts',code))
        os.makedirs(f'results/ScenarioComparison/barcharts/{code}', exist_ok=True)
        for filename in files:        
            filepath = os.path.join(homedir,'barcharts', code, filename)
            filename_new = filename[3:-4] + '_' + scenario + '.png'
            filepath_new = os.path.join(folder, code, filename_new)
            shutil.move(filepath,filepath_new)            
            
        
    # Piecharts
    folder = r'results/ScenarioComparison/piecharts'
    files_to_keep = ['Capacity - Aggregate', 'Capacity - Detail solar',
                     'Generation - Aggregate', 'Generation - Detail hydro',
                     'Generation - Detail solar']
    for code in codes:
        # Remove useless files:
        files = os.listdir(os.path.join(homedir,'piecharts',code))
        files_to_keep_c = [code + ' - ' + file + '.png' for file in files_to_keep]
        for filename in files:        
            filepath = os.path.join(homedir,'piecharts',code,filename)
            if filename not in files_to_keep_c:
                os.remove(filepath)
        
        # Rename and move remaining files:
        files = os.listdir(os.path.join(homedir,'piecharts',code))
        os.makedirs(f'results/ScenarioComparison/piecharts/{code}', exist_ok=True)
        for filename in files:        
            filepath = os.path.join(homedir,'piecharts',code,filename)
            filename_new = filename[:-4] + '_' + scenario + '.png'
            filepath_new = os.path.join(folder, code, filename_new)
            shutil.move(filepath,filepath_new) 
    
    # Excel file
    shutil.move(f'{homedir}/Mixes_percentages_{scenario}.xlsx',f'results/ScenarioComparison/Mixes_percentages_{scenario}.xlsx')




    