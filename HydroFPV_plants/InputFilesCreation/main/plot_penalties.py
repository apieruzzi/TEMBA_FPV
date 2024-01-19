# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 11:02:59 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate

plt.rcParams.update({'font.size': 14})
plt.rcParams['legend.handlelength'] = 1
plt.rcParams['legend.handleheight'] = 1


# =============================================================================
# Land tax
# =============================================================================
# Emission activity ratios (Land use intensities [ha/PJ])
wind_value = round(130/3.6,1) 
solar_value = round(2000/3.6,1) 
csp_value = round(1300/3.6,1) 
hydro_value = round(650/3.6,1) 
nuclear_value = round(7.1/3.6,1) 
geothermal_value = round(45/3.6,1) 
gas_value = round(410/3.6,1) 
coal_value = round(1000/3.6,1) 
oil_value = gas_value # Assume that land use for oil is similar to gas

for country in ['EG', 'ETSDSS']:
    # Emission penalties (Land values [M$/ha])
    df_values = pd.read_excel(r'Data/LandValues.xlsx', sheet_name=f'Stats_{country}', index_col='Unnamed: 0')
    df_values = df_values.loc[['mean', 'First quantile','Third quantile']]
    df_values['Solar CSP'] = df_values['Solar'] # Assume land value for csp is similar to solar
    df_values['Coal'] = df_values['Oil'] # Assume land value for coal is similar to oil
    cols = df_values.columns.drop('Biomass & Waste')
    
    df_values = df_values[cols]
    df_values = df_values * 0.001 #convert to M$
    df_landuse = pd.DataFrame([[oil_value, gas_value, wind_value, solar_value,
                                hydro_value, geothermal_value, nuclear_value,
                                coal_value, csp_value]],
                              index=['Land use'], columns=cols)
    df_comb = pd.concat([df_values, df_landuse])
    
    
    color_dict = {
        "Coal":"#0d0700",
        "Oil" : "#595755",
        "Gas" : "#f07d0a",
        "Hydro" : "#179aff",
        "Solar" : "#f5de0f",
        "Wind" : "#0237f5",
        "Biomass & Waste" : "#5de841",
        "Geothermal" : "#7d0c06", 
        "Nuclear" : "#5ce6f2",
        }
    
    colors = ["#595755","#f07d0a",'#0237f5', '#f5de0f', '#179aff', '#7d0c06', "#5ce6f2", '#e31e42', "#0d0700"]
    # plt.figure(figsize=(10,8))
    # for i,tech in enumerate(df_comb.columns):
    #     plt.scatter(df_comb.iloc[3,i],df_comb.iloc[0,i],marker='o', 
    #                 color=colors[i], label=tech)
    #     plt.errorbar(df_comb.iloc[3,i],df_comb.iloc[0,i], yerr=(df_comb.iloc[2,i]-df_comb.iloc[1,i])/2, color=colors[i])
    # plt.xlabel('Land use [ha/PJ]')
    # plt.ylabel('Land value [M$/ha]')
    # plt.title('Land use vs land value per technology type')
    # plt.legend()
    # plt.grid(True)
    # plt.savefig(r'penalties_plots/LandUsevsLandValue.png')
    
    # Absolute penalties [M$/PJ]
    df_land = df_comb.copy().iloc[1:,:]
    df_land.loc['First quantile'] = df_land.loc['First quantile'] * df_land.loc['Land use']
    df_land.loc['Third quantile'] = df_land.loc['Third quantile'] * df_land.loc['Land use']
    
    # =============================================================================
    # Carbon tax                  
    # =============================================================================
    years = np.arange(2015,2071,1)
    # Emission activity ratios
    df_emi = pd.read_excel(r'Created Files/TEMBA_ENB_ref.xlsx', sheet_name='EmissionActivityRatio')
    df_emi = df_emi.iloc[np.where(df_emi['EMISSION'].str.contains('CO2'))]
    
    mean_ratio_oil = abs(df_emi[2015].iloc[
        np.where(df_emi['TECHNOLOGY'].str.contains('HF') | 
                 df_emi['TECHNOLOGY'].str.contains('LF') |
                 df_emi['TECHNOLOGY'].str.contains('CR'))]).mean()
    mean_ratio_coal = abs(df_emi[2015].iloc[
        np.where(df_emi['TECHNOLOGY'].str.contains('CO'))]).mean()
    mean_ratio_gas = abs(df_emi[2015].iloc[
        np.where(df_emi['TECHNOLOGY'].str.contains('NG'))]).mean()
                 
    # Slow tax 
    value_init = 25
    increase = value_init * 0.01
    value_fin = value_init + 56 * value_init * 0.01
    carbon_tax_slow = np.arange(value_init,value_fin,increase)
    
    # Aggressive tax
    values = [80,140,200]
    years_points = [2020,2030,2050]
    interp_lin = scipy.interpolate.interp1d(years_points, values, fill_value='extrapolate')
    carbon_tax_agg = interp_lin(years)
    
    
    # plt.figure(figsize=(10,8))
    # plt.plot(years, carbon_tax_slow, label='Slow tax')
    # plt.plot(years, carbon_tax_agg, label='Aggressive tax')
    # plt.xlabel('Year')
    # plt.ylabel('Carbon price [$/tCO2]')
    # plt.title('Carbon tax evolution')
    # plt.legend()
    # plt.savefig(r'penalties_plots/CarbonTaxes.png')
    
    # Absolute penalties [M$/PJ]
    penalty_oil_slow = mean_ratio_oil * carbon_tax_slow
    penalty_oil_agg = mean_ratio_oil * carbon_tax_agg
    penalty_gas_slow = mean_ratio_gas * carbon_tax_slow
    penalty_gas_agg = mean_ratio_gas * carbon_tax_agg
    penalty_coal_slow = mean_ratio_coal * carbon_tax_slow
    penalty_coal_agg = mean_ratio_coal * carbon_tax_agg
    
    # =============================================================================
    # Comparing the taxes in terms of absolute penalties
    # =============================================================================
    
    # Slow case
    plt.figure(figsize=(10,8))
    plt.plot(years, penalty_oil_slow, label='Carbon tax oil', linestyle='dashed', color='#595755')
    plt.plot(years, penalty_gas_slow, label='Carbon tax gas', linestyle='dashed', color='#f07d0a')
    plt.plot(years, penalty_coal_slow, label='Carbon tax coal', linestyle='dashed', color='#0d0700')
    for i,tech in enumerate(df_land.columns):
        plt.plot(years,df_land.iloc[0,i]*np.ones(56),label='Land tax '+tech, color=colors[i])
    plt.xlabel('Year')
    plt.ylabel('Tax price [M$/PJ]')
    # plt.title('Externality taxes evolution (Slow case)')
    plt.ylim((-0.5,5))
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=4)  # Adjust ncol based on the number of legend entries
    plt.savefig(f'penalties_plots/PenaltiesSlow_{country}.png', bbox_inches='tight')
    
    # Aggressive case
    plt.figure(figsize=(10,8))
    plt.plot(years, penalty_oil_agg, label='Carbon tax oil', linestyle='dashed', color='#595755')
    plt.plot(years, penalty_gas_agg, label='Carbon tax gas', linestyle='dashed', color='#f07d0a')
    plt.plot(years, penalty_coal_agg, label='Carbon tax coal', linestyle='dashed', color='#0d0700')
    for i,tech in enumerate(df_land.columns):
        plt.plot(years,df_land.iloc[1,i]*np.ones(56),label='Land tax '+tech, color=colors[i])
    plt.xlabel('Year')
    plt.ylabel('Tax price [M$/PJ]')
    # plt.title('Externality taxes evolution (Aggressive case)')
    plt.ylim((-0.5,25))
    # plt.legend()
    plt.savefig(f'penalties_plots/PenaltiesAgg_{country}.png', bbox_inches='tight')
