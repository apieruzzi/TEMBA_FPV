# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 11:06:40 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np

scenario = 'TEMBA_Refer_refNoFPV'
filename = f'results/export_{scenario}/barcharts/EAPP/EAPP-Annual Emissions-{scenario}.csv'

df = pd.read_csv(filename)
df.loc['tot'] = df.sum()
print("Total emissions: ", df.loc['tot'][-1], "MTCO2e")