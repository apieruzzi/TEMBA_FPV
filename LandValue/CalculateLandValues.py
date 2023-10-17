# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 12:00:13 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns


# Read files
file1 = 'Sampled_values_JRC.csv'
file2 = 'Sampled_values_WRI.csv'
jrc_df = pd.read_csv(file1)
wri_df = pd.read_csv(file2)

# Uniform column names
cols_wri = ['latitude', 'longitude', 'country', 'name', 
            'primary_fu','capacity_m', 'SAMPLE_1']
cols_jrc = jrc_df.columns[[8,7,3,1,5,2,6]]
cols_merged = ['Lat', 'Long', 'Country', 'Plant name', 
               'Fuel', 'Capacity (MW)', 'Yield (K$/ha)']
jrc_df = jrc_df[cols_jrc]
wri_df = wri_df[cols_wri]
jrc_df = jrc_df.rename(columns=dict(map(lambda i,j : (i,j) , cols_jrc,cols_merged)))
wri_df = wri_df.rename(columns=dict(map(lambda i,j : (i,j) , cols_wri,cols_merged)))

# Uniform fuel and country names
jrc_df.loc[jrc_df['Fuel']=='NG','Fuel'] = 'Gas'
jrc_df.loc[jrc_df['Fuel']=='Water','Fuel'] = 'Hydro'
jrc_df.loc[jrc_df['Fuel']=='Sun','Fuel'] = 'Solar'
jrc_df.loc[jrc_df['Fuel']=='Geo','Fuel'] = 'Geothermal'
jrc_df.loc[jrc_df['Fuel']=='Uranium','Fuel'] = 'Nuclear'
jrc_df.loc[jrc_df['Fuel']=='waste heat','Fuel'] = 'Biomass & Waste'
jrc_df.loc[jrc_df['Fuel']=='Biomass','Fuel'] = 'Biomass & Waste'
wri_df.loc[wri_df['Fuel']=='Biomass','Fuel'] = 'Biomass & Waste'

jrc_df.loc[jrc_df['Country']=='EGYPT','Country'] = 'EG'
jrc_df.loc[jrc_df['Country']=='ETHIOPIA','Country'] = 'ET'
jrc_df.loc[jrc_df['Country']=='SUDAN','Country'] = 'SD'
jrc_df.loc[jrc_df['Country']=='SOUTH SUDAN','Country'] = 'SS'
wri_df.loc[wri_df['Country']=='EGY','Country'] = 'EG'
wri_df.loc[wri_df['Country']=='ETH','Country'] = 'ET'
wri_df.loc[wri_df['Country']=='SDN','Country'] = 'SD'


# Transform in geopandas dfs
jrc_gdf = gpd.GeoDataFrame(
    jrc_df, geometry=gpd.points_from_xy(jrc_df.Long, jrc_df.Lat), crs="EPSG:4326")
wri_gdf = gpd.GeoDataFrame(
    wri_df, geometry=gpd.points_from_xy(wri_df.Long, wri_df.Lat), crs="EPSG:4326")

# Merge and drop duplicates
merged_gdf = pd.concat([jrc_gdf,wri_gdf])
merged_gdf = merged_gdf.drop_duplicates(subset='geometry')
merged_gdf = merged_gdf.dropna()


# Calculate statistics of fuels and put them in a df
fuels = merged_gdf.Fuel.unique().tolist()
fuels = [i for i in fuels if i is not np.nan]
stats_df = pd.DataFrame(index=['mean', 'min', 'max', 'median',
                               'First quantile', 'Third quantile'], 
                        columns=fuels)


def calc_dfs(country, merged_gdf):
    if country == 'ENB':
        df_country = merged_gdf
    else:
        df_country = merged_gdf.loc[merged_gdf['Country'] == country]
    
    df_fuel = pd.DataFrame()
    for fuel in fuels:
        df = df_country.loc[df_country['Fuel'] == fuel ,'Yield (K$/ha)'].rename(fuel).reset_index(drop=True)
        df_fuel = pd.concat([df_fuel, df], axis=1, ignore_index=True)
        df_fuel = df_fuel.rename(columns=dict(map(lambda i,j : (i,j) , df_fuel.columns,fuels)))
        # mean
        stats_df.loc['mean',fuel] = df.mean()
        # min
        stats_df.loc['min',fuel] = df.min()
        # max
        stats_df.loc['max',fuel] = df.max()
        # median
        stats_df.loc['median',fuel] = df.median()
        # quantiles
        stats_df.loc['First quantile',fuel] = df.quantile(0.25)
        stats_df.loc['Third quantile',fuel] = df.quantile(0.75)
    
    # box plot
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
    

    plt.figure(figsize=(10,8))
    plt.ylabel('Value [K$/ha]')
    plt.title(f'Agricultural land yield at power plants locations: {country}')
    sns.boxplot(df_fuel, palette=color_dict)
    plt.savefig(f'Boxplots_{country}.png')
    
    return df_fuel, stats_df



writer = pd.ExcelWriter('LandValues.xlsx')


for country in ['ENB', 'EG', 'ET', 'SD', 'SS']:
    dfs = calc_dfs(country,merged_gdf)
    df_fuel = dfs[0]
    df_stats = dfs[1]
    
    df_fuel.to_excel(writer, sheet_name=f'Fuels_{country}')
    df_stats.to_excel(writer, sheet_name=f'Stats_{country}')

writer.close()
















