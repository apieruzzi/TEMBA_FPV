# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 16:17:25 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np


file = r'results\export_TEMBA_Refer_ref\barcharts\EAPP\EAPP-Annual Emissions-TEMBA_Refer_ref.csv'

df = pd.read_csv(file)
df.loc['tot'] = df.sum()
print('Total Emissions: ', round(df.iloc[-1,2],3), 'MtCO2')


sum{r in REGION, t in TECHNOLOGY, y in YEAR} (((((sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0} NewCapacity[r,t,yy]) + ResidualCapacity[r,t,y]) * FixedCost[r,t,y] 
                                                + sum{m in MODEperTECHNOLOGY[t], l in TIMESLICE} RateOfActivity[r,l,t,m,y]*YearSplit[l,y]*VariableCost[r,t,m,y]) /((1+DiscountRate[r])^(y-min{yy in YEAR} min(yy)+0.5))
                                               +CapitalCost[r,t,y] * NewCapacity[r,t,y]/((1+DiscountRate[r])^(y-min{yy in YEAR} min(yy)))
                                               +DiscountedTechnologyEmissionsPenalty[r,t,y]
                                               -DiscountedSalvageValue[r,t,y]) 
                                              + sum{s in STORAGE} (CapitalCostStorage[r,s,y] * NewStorageCapacity[r,s,y]/((1+DiscountRate[r])^(y-min{yy in YEAR} min(yy)))-DiscountedSalvageValueStorage[r,s,y])
                                              )