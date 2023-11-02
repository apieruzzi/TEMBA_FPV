# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:30:31 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import scipy.interpolate 

ratios = np.array([331, 889, 1307, 1572, 1743]) * 10**(-3) #m
perc = [0.1, 0.3, 0.5, 0.7, 1]

new_perc = [0.003, 0.1, 0.3, 0.34, 0.5, 0.7, 1]

interp= scipy.interpolate.interp1d(perc, ratios, fill_value='extrapolate', kind='cubic')
new_ratios = interp(new_perc)

df_ratios = pd.DataFrame(zip(new_perc,new_ratios.tolist()), columns = [['percentages','ratios' ]])

A1 = 6500 * 10**6 #m2
A2 = 8.24 * 10**6 #m2
p = 1000 #kg/m3
g = 9.81 #m/s2
eta = 0.85

dE1 = []
dE2 = []

for idx,row in df_ratios.iterrows():
    dH = row['ratios']
    dE1.append((dH**2 * eta * p * g * A1)*10**(-3)/3600*3.6*10**(-9))
    dE2.append((dH**2 * eta * p * g * A2)*10**(-3)/3600*3.6*10**(-9))

df_ele = pd.DataFrame(zip(dE1,dE2), columns=[['High Aswan Dam', 'Aswan 1']])    
df_final = pd.concat([df_ratios, df_ele], axis=1)
