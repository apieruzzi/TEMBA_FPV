# -*- coding: utf-8 -*-
"""
Created on Mon May 22 09:44:41 2023

@author: Alessandro Pieruzzi
"""
"""

Arguments
---------
picklefile : str
    The filepath to the results file for which to produce plots
    and data csv files
scenario : str
    A short and descriptive scenario name (appears in plot titles)

"""
import shutil
import os
import sys
import pandas as pd
import numpy as np
import pickle
import plotly.io as pio
import tempfile
import cufflinks

cufflinks.go_offline()
cufflinks.set_config_file(world_readable=True, theme='white', offline=True)


picklefile = sys.argv[1]
scenario = sys.argv[2]
destination_folder = sys.argv[3]

first_year = 2022
last_year = 2070


with tempfile.TemporaryDirectory() as temp:

    global homedir
    homedir = temp

    print("Using temporary directory {}".format(homedir))

    # The pickle file is loaded onto the all_params dictionary
    with open(picklefile, 'rb') as pkl_file:
        all_params = pickle.load(pkl_file)

    # Fundamental dictionaries that govern naming and colour coding
    data_dir = 'input_data'

    url1 = os.path.join(data_dir, 'agg_col.csv')
    url2 = os.path.join(data_dir, 'agg_pow_col.csv')
    url3 = os.path.join(data_dir, 'countrycode.csv')
    url4 = os.path.join(data_dir, 'power_tech.csv')
    url5 = os.path.join(data_dir, 'techcodes.csv')

    colorcode = pd.read_csv(url5, sep=',', encoding="ISO-8859-1")
    colorcode1 = colorcode.drop('colour', axis=1)
    colorcode2 = colorcode.drop('tech_code', axis=1)
    det_col = dict(
        [(a, b) for a, b in zip(colorcode1.tech_code, colorcode1.tech_name)])
    color_dict = dict(
        [(a, b) for a, b in zip(colorcode2.tech_name, colorcode2.colour)])
    colorcode_hydro = colorcode[colorcode['tech_code'].str.contains('HYD')].iloc[1:].drop('tech_code', axis=1)
    new_colors_hydro = ['yellow','chartreuse', 'cornflowerblue', #Egypt
                        'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                        'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                        'red', 'black', 'lime', 'darkred', 'midnightblue', 
                        'olive', 'orange', 'purple', 'teal', 'lime', 'dimgrey', #Ethiopia
                        'yellow', 'red', #SouthSudan
                        'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                        'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                        'midnightblue', 'black', #Sudan
                        'red', 'orange', 'green', #Egypt ROR
                        'pink', 'violet', 'lightyellow', #Ethiopia ROR
                        'yellow','chartreuse', 'cornflowerblue', 'orange', 'green' #SS ROR
                        ]
    colorcode_hydro.iloc[3:,1] = new_colors_hydro
    color_dict_hydro = dict(
        [(a, b) for a, b in zip(colorcode_hydro.tech_name, colorcode_hydro.colour)])
    colorcode_solar = colorcode[colorcode['tech_code'].str.contains('SO')].drop('tech_code', axis=1)
    new_colors_solar = ['yellow','chartreuse', 'cornflowerblue', #Egypt
                        'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                        'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                        'red', 'black', 'lime', 'darkred', 'midnightblue', 
                        'olive', 'orange', 'purple', 'teal', 'lime', 'darkslategrey', #Ethiopia
                        'yellow', 'red', #SouthSudan
                        'brown', 'blue', 'chocolate', 'coral', 'crimson', 
                        'forestgreen','yellow', 'indigo', 'greenyellow', 'lightblue', 
                        'midnightblue', 'black' #Sudan
                        ]
    colorcode_solar.iloc[9:,1] = new_colors_solar
    color_dict_solar = dict(
        [(a, b) for a, b in zip(colorcode_solar.tech_name, colorcode_solar.colour)])
    
    # Color dicts for power pool graphs
    colorcode_hydro_pp = colorcode_hydro
    colorcode_hydro_pp.iloc[12,1]='black'
    colorcode_solar_pp = colorcode_solar
    colorcode_solar_pp.iloc[19,1]='black'
    color_dict_hydro_pp = dict(
        [(a, b) for a, b in zip(colorcode_hydro_pp.tech_name, colorcode_hydro_pp.colour)])
    color_dict_solar_pp = dict(
        [(a, b) for a, b in zip(colorcode_solar_pp.tech_name, colorcode_solar_pp.colour)])
    
    agg1 = pd.read_csv(url1, sep=',', encoding="ISO-8859-1")
    agg2 = pd.read_csv(url2, sep=',', encoding="ISO-8859-1")
    agg_col = agg1.to_dict('list')
    agg_pow_col = agg2.to_dict('list')
    power_tech = pd.read_csv(url4, sep=',', encoding="ISO-8859-1")
    t_include = list(power_tech['power_tech'])
    t_include_hydro = [i for i in t_include if i.startswith('HYD')]
    t_include_solar = [i for i in t_include if i.startswith('SO')]
    t_include_fpv = [i for i in t_include if i.startswith('SOFPV')]
    # t_include_fossil = [i for i in t_include if (i.startswith('CO')|
    #                                              i.startswith('HF')|
    #                                              i.startswith('LF')|
    #                                              i.startswith('NG')|
    #                                              i.startswith('CR'))]
    # colorcode_fossil = colorcode[colorcode['tech_code'].isin(t_include_fossil)].drop('tech_code', axis=1)
    # color_dict_fossil = dict(
    #     [(a, b) for a, b in zip(colorcode_fossil.tech_name, colorcode_fossil.colour)])
    
    # Country code list
    country_code = pd.read_csv(url3, sep=',', encoding="ISO-8859-1")
    
    years = pd.Series(range(2015, 2071))

    def df_filter(df, lb, ub, t_exclude):
        """base function used for many different variables (mainly cost)
        """
        df['t'] = df['t'].str[lb:ub]
        df['value'] = df['value'].astype('float64')
        df = df[~df['t'].isin(t_exclude)].pivot_table(
            index='y',
            columns='t',
            values='value',
            aggfunc='sum').reset_index().fillna(0)
        df = df.reindex(sorted(df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        df = df.iloc[np.where(df['y']>first_year)] 
        df['y'] = years
        # df=df[df['y']>2022]
        return df

    def df_plot(df, y_title, p_title, color_dict = color_dict, barmode = 'stack'):
        """Plotting function for all graphs except Gas (as it needs relative charts)
        """
        # Drop columns with all 0 values
        df = df.loc[:, (df != 0).any(axis=0)]
        
        if (len(df.columns) == 1) | (np.shape(df)[1] < 2):
            print('There are no values for the result variable that you want to plot')
            print(p_title)
        else:
            fig = df.iplot(x='y',
                        kind='bar',
                        barmode=barmode,
                        width=1,
                        xTitle='Year',
                        yTitle=y_title,
                        color=[color_dict[x] for x in df.columns if x != 'y'],
                        title=p_title+"-"+scenario,
                        showlegend=True,
                        asFigure=True)
            fig.update_xaxes(range=[first_year, last_year])
            fig.update_traces(width=0.7)
            pio.write_image(fig, os.path.join(homedir, '{}.png'.format(p_title)), 
                            scale=1, width=1500, height=1000)
            df.to_csv(os.path.join(homedir, p_title+"-"+scenario+".csv"))
            return None

    def df_filter_emission_tech(df, lb, ub):
        """Emissions
        """
        df['t'] = df['t'].str[lb:ub]
        df['e'] = df['e'].str[2:5]
        df['value'] = df['value'].astype('float64')
        df = df.pivot_table(index='y', columns='t',
                            values='value',
                            aggfunc='sum').reset_index().fillna(0)
        df = df.reindex(sorted(df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        df = df.iloc[np.where(df['y']>first_year)] 
        df['y'] = years
        # df=df[df['y']>2022]
        return df

    def df_filter_emission_tot(df):
        """Annual Emissions
        """
        df['e'] = df['e'].str[2:5]
        df['value'] = df['value'].astype('float64')
        df = df.pivot_table(index='y', columns='e',
                            values='value',
                            aggfunc='sum').reset_index().fillna(0)
        df = df.reindex(sorted(df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        df = df.iloc[np.where(df['y']>first_year)] 
        df['y'] = years
        # df=df[df['y']>2022]
        return df
    
    def detailed_power_chart(cc,col_name, t_include=t_include, color_dict=color_dict, barmode='stack', add_title = None, plotting=True):
        df = all_params[col_name]
        df = df[df['t'].str[:2] == cc].copy() # select country 
        df['t'] = df['t'].str[2:10] # remove country code
        df['value'] = df['value'].astype('float64') # convert values to float
        df['y'] = df['y'].astype('float64') # convert years to float
        # Create pivot table with relevant technologies (the ones inside power_tech.csv and pickle file): 
        df = df[df['t'].isin(t_include)].pivot_table(
            index='y',
            columns='t',
            values='value',
            aggfunc='sum').reset_index().fillna(0)
        # Rename the columns and reindex:
        df = df.reindex(sorted(df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        df = df.iloc[np.where(df['y']>first_year)] 
        
        if t_include == t_include_solar:
            tech_names = [det_col[t] for t in t_include_fpv]
            cols = [col for col in df.columns if col in tech_names]
            df['Solar FPV'] = df[cols].sum(axis=1)
            df = df[[col for col in df.columns if col not in cols]]
        
        if plotting == True:
            if col_name == 'TotalCapacityAnnual':
                plot_name = 'Power Generation Capacity'
                unit = 'Gigawatts (GW)'
            elif col_name == 'NewCapacity':
                plot_name = 'New power generation capacity' 
                unit = 'Gigawatts (GW)'
            elif col_name == 'ProductionByTechnologyAnnual':
                plot_name = 'Power Generation'
                unit = 'Petajoules (PJ)'
            
            if add_title is None:
                title = cc+"-"+ plot_name + ' (Detail)'
            else:
                title = cc+"-"+ plot_name + ' (Detail ' + add_title + ')'
            df_plot(df, unit, title, color_dict=color_dict, barmode=barmode)
        return df

    def power_chart(Country):
        cc = country_code[country_code['Country Name'] == Country]['Country code'].tolist()[0]
       
        # Power capacity (Detailed):
        cap_df = detailed_power_chart(cc,'TotalCapacityAnnual', plotting=False)
        cap_df_hydro = detailed_power_chart(cc,'TotalCapacityAnnual',
                                            t_include_hydro, 
                                            color_dict_hydro, 
                                            add_title='hydro')
        cap_df_solar = detailed_power_chart(cc,'TotalCapacityAnnual', 
                                            t_include_solar, 
                                            color_dict_solar, 
                                            add_title='solar')
        cap_df_fpv = detailed_power_chart(cc,'TotalCapacityAnnual', 
                                            t_include_fpv, 
                                            color_dict_solar, 
                                            add_title='fpv')
        # cap_df_fossil = detailed_power_chart(cc,'TotalCapacityAnnual', 
        #                                     t_include_fossil, 
        #                                     color_dict_fossil, 
        #                                     add_title='fossil')

        # Power capacity (Aggregated)
        cap_agg_df = pd.DataFrame(columns=agg_pow_col) #create empty dataframe
        cap_agg_df.insert(0, 'y', cap_df['y']) #add years as rows
        cap_agg_df = cap_agg_df.fillna(0.00) #fill NaN values
        #Fill the df summing the values from the detailed capacity dataframe:
        for each in agg_pow_col:
            for tech_exists in agg_pow_col[each]:
                if tech_exists in cap_df.columns:
                    try:
                        cap_agg_df[each] = cap_agg_df[each] + cap_df[tech_exists]
                    except TypeError as ex:
                        print(cap_agg_df[each].dtypes, cap_df[tech_exists].dtypes)
                        raise TypeError(ex)
                    cap_agg_df[each] = cap_agg_df[each].round(3)
        #
        df_plot(cap_agg_df, 'Gigawatts (GW)', cc+"-" +
                'Power Generation Capacity (Aggregate)')
        
        
        # *********************************************************************
        # New power capacity (Detailed):
        cap_new_df = detailed_power_chart(cc,'NewCapacity', plotting=False)
        cap_new_df_hydro = detailed_power_chart(cc,'NewCapacity',
                                            t_include_hydro, 
                                            color_dict_hydro, 
                                            add_title='hydro')
        cap_new_df_solar = detailed_power_chart(cc,'NewCapacity', 
                                            t_include_solar, 
                                            color_dict_solar, 
                                            add_title='solar')
        cap_new_df_fpv = detailed_power_chart(cc,'NewCapacity', 
                                            t_include_fpv, 
                                            color_dict_solar, 
                                            add_title='fpv')
        # cap_new_df_fossil = detailed_power_chart(cc,'NewCapacity', 
        #                                     t_include_fossil, 
        #                                     color_dict_fossil, 
        #                                     add_title='fossil')
        # New power capacity (Aggregated)
        cap_new_agg_df = pd.DataFrame(columns=agg_pow_col)
        cap_new_agg_df.insert(0, 'y', cap_new_df['y'])
        cap_new_agg_df = cap_new_agg_df.fillna(0.00)
        #
        for each in agg_pow_col:
            for tech_exists in agg_pow_col[each]:
                if tech_exists in cap_new_df.columns:
                    cap_new_agg_df[each] = cap_new_agg_df[each] + \
                        cap_new_df[tech_exists]
                    cap_new_agg_df[each] = cap_new_agg_df[each].round(3)
                    ##
        df_plot(cap_new_agg_df, 'Gigawatts (GW)', cc+"-" +
                'New power generation capacity (Aggregate)')


        # ********************************************************************
        # Power generation (Detailed)
        gen_df = all_params['ProductionByTechnologyAnnual'].copy() # Get power production from the file
        gen_df_export = gen_df[((gen_df['f'].str[2:6] == 'EL01') & (gen_df['f'].str[0:2] != cc))
                               | ((gen_df['f'].str[2:6] == 'DUEL') & (gen_df['f'].str[0:2] == cc))].copy() # Get all the techs that produce ele01 and are not in the country
        gen_df_export = gen_df_export[gen_df_export['t'].str[6:10] == 'BP00'].copy() # Get trade links 
        gen_df_export = gen_df_export[(gen_df_export['t'].str[0:2] == cc) | (
            gen_df_export['t'].str[4:6] == cc)] # Get trade links that contain the selected country
        gen_df_export['value'] = gen_df_export['value'].astype(float)*-1 # Put negative the production values
       
        gen_df['y'] = gen_df['y'].astype('float64')
        gen_df = gen_df[(gen_df['f'].str[:2] == cc)].copy()
        gen_df = gen_df[(gen_df['f'].str[2:6] == 'EL01') |
                        (gen_df['f'].str[2:6] == 'EL03')].copy()
        gen_df = gen_df[(gen_df['t'].str[2:10] != 'EL00T00X') &
                        (gen_df['t'].str[2:10] != 'EL00TDTX')].copy() # remove transmission and distribution 
        gen_df = pd.concat([gen_df, gen_df_export])
        gen_df['value'] = gen_df['value'].astype('float64')
        gen_df = gen_df.pivot_table(index='y',
                                    columns='t',
                                    values='value',
                                    aggfunc='sum').reset_index().fillna(0)
        for each in gen_df.columns:
            if len(each) != 1:
                if (each[2:4] == 'EL') & (each[6:10] == 'BP00'):
                    pass
                else:
                    gen_df.rename(columns={each: each[2:10]}, inplace=True)
            else:
                pass
        gen_df = gen_df.reindex(sorted(gen_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        gen_df = gen_df.iloc[np.where(gen_df['y']>first_year)]
        
        # Power generation (trades only):
        cols = [col for col in gen_df.columns if 'trade' in col]
        cols.insert(0,'y')
        gen_df_trades = gen_df[cols]
        df_plot(gen_df_trades,'Petajoules (PJ)',cc+"-"+'Power Generation (Detail trades)', barmode='relative')
        
        
        # Power generation (detailed)
        gen_df_hydro = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
                                            t_include_hydro, 
                                            color_dict_hydro, 
                                            add_title='hydro')
        gen_df_solar = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
                                            t_include_solar, 
                                            color_dict_solar, 
                                            add_title='solar')
        gen_df_fpv = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
                                            t_include_fpv, 
                                            color_dict_solar, 
                                            add_title='fpv')
        # gen_df_fossil = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
        #                                     t_include_fossil, 
        #                                     color_dict_fossil, 
        #                                     add_title='fossil')

        # Power generation (Aggregated)
        gen_agg_df = pd.DataFrame(columns=agg_pow_col)
        gen_agg_df.insert(0, 'y', gen_df['y'])
        gen_agg_df = gen_agg_df.fillna(0.00)
        for each in agg_pow_col:
            for tech_exists in agg_pow_col[each]:
                if tech_exists in gen_df.columns:
                    gen_agg_df[each] = gen_agg_df[each] + gen_df[tech_exists]
                    gen_agg_df[each] = gen_agg_df[each].round(2)

        df_plot(gen_agg_df,'Petajoules (PJ)',cc+"-"+'Power Generation (Aggregate)', barmode='relative')
        
        return None

    def water_chart(Country):
        cc = country_code[country_code['Country Name'] == Country]['Country code'].tolist()[
            0]

        # water withdrawal detailed
        wat_w_df = all_params['UseByTechnologyAnnual']
        wat_w_df = wat_w_df[wat_w_df['f'].str[:6] == cc+'WAT1'].copy()

        wat_w_df['t'] = wat_w_df['t'].str[2:10]
        wat_w_df['value'] = wat_w_df['value'].astype('float64')
        wat_w_df = wat_w_df.pivot_table(index='y',
                                        columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
        wat_w_df_original = wat_w_df.reindex(sorted(wat_w_df.columns), axis=1).set_index(
            'y').reset_index() 
        wat_w_df = wat_w_df.reindex(sorted(wat_w_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        wat_w_df = wat_w_df.iloc[np.where(wat_w_df['y']>first_year)]
        #wat_w_df['y'] = years
        # wat_w_df=wat_w_df[wat_w_df['y']>2022]
        #df_plot(wat_w_df,'Million cubic metres (Mm^3)',cc+"-"+'Water Withdrawal')

        # Water Withdrawal (Aggregated)
        watw_agg_df = pd.DataFrame(columns=agg_col)
        watw_agg_df.insert(0, 'y', wat_w_df['y'])
        watw_agg_df = watw_agg_df.fillna(0.00)
        for each in agg_col:
            for tech_exists in agg_col[each]:
                if tech_exists in wat_w_df.columns:
                    watw_agg_df[each] = watw_agg_df[each] + wat_w_df[tech_exists]
                    watw_agg_df[each] = watw_agg_df[each].round(2)

        df_plot(watw_agg_df, 'Million cubic metres (Mm^3)',
                cc+"-"+'Water Withdrawal')

        # water output detailed
        wat_o_df = all_params['ProductionByTechnologyAnnual']
        wat_o_df = wat_o_df[wat_o_df['f'].str[:6] == cc+'WAT2'].copy()
        wat_o_df['t'] = wat_o_df['t'].str[2:10].copy()
        wat_o_df['value'] = wat_o_df['value'].astype('float64')
        wat_o_df = wat_o_df.pivot_table(index='y',
                                        columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
        wat_o_df_original = wat_o_df.reindex(sorted(wat_o_df.columns), axis=1).set_index(
            'y').reset_index()
        wat_o_df = wat_o_df.reindex(sorted(wat_o_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        wat_o_df = wat_o_df.iloc[np.where(wat_o_df['y']>first_year)]
        #wat_o_df['y'] = years
        # wat_o_df=wat_o_df[wat_o_df['y']>2022]
        #df_plot(wat_o_df,'Million cubic metres (Mm^3)',cc+"-"+'Water output')

        # Water consumption missing row additions
        for wd in wat_w_df.columns:
            for wc in wat_o_df.columns:
                if wd in wat_o_df.columns:
                    pass
                else:
                    wat_o_df[wd] = 0
        
        for wd in wat_w_df_original.columns:
            for wc in wat_o_df_original.columns:
                if wd in wat_o_df_original.columns:
                    pass
                else:
                    wat_o_df_original[wd] = 0
        

        # Water consumption (Detailed)
        wat_c_df = wat_w_df.set_index('y')-wat_o_df.set_index('y')
        wat_c_df = wat_c_df.fillna(0.00)
        wat_c_df.reset_index(inplace=True)
        # Names with original column names (tech codes)
        wat_c_df_original = wat_w_df_original.set_index('y')-wat_o_df_original.set_index('y')
        wat_c_df_original = wat_c_df_original.fillna(0.00)
        wat_c_df_original.reset_index(inplace=True)
        wat_c_df_original['y'] = years
        wat_c_df_original = wat_c_df_original.set_index('y')
        
        # Detail hydro
        wat_c_df_hydro = wat_c_df_original[[col for col in wat_c_df_original.columns if col in t_include_hydro]]
        wat_c_df_hydro.reset_index(inplace=True)
        wat_c_df_hydro = wat_c_df_hydro.rename(columns=det_col)
        df_plot(wat_c_df_hydro,'Million cubic metres (Mm^3)',cc+"-"+'Water consumption (Detail Hydro)', color_dict=color_dict_hydro)
        
        # Water consumption (Aggregate)
        watc_agg_df = pd.DataFrame(columns=agg_col)
        watc_agg_df.insert(0, 'y', wat_c_df['y'])
        watc_agg_df = watc_agg_df.fillna(0.00)
        for each in agg_col:
            for tech_exists in agg_col[each]:
                if tech_exists in wat_c_df.columns:
                    watc_agg_df[each] = watc_agg_df[each] + wat_c_df[tech_exists]
                    watc_agg_df[each] = watc_agg_df[each].round(2)
        df_plot(watc_agg_df, 'Million cubic metres (Mm^3)',
                cc+'-'+'Water Consumption')
        
        # Water consumption (Aggregate no hydro)
        agg_col_nohyd = agg_col.copy()
        agg_col_nohyd.pop('Hydro', None)
        watc_agg_df_nohyd = pd.DataFrame(columns=agg_col_nohyd)
        watc_agg_df_nohyd.insert(0, 'y', wat_c_df['y'])
        watc_agg_df_nohyd = watc_agg_df_nohyd.fillna(0.00)
        for each in agg_col_nohyd:
            for tech_exists in agg_col_nohyd[each]:
                if tech_exists in wat_c_df.columns:
                    watc_agg_df_nohyd[each] = watc_agg_df_nohyd[each] + wat_c_df[tech_exists]
                    watc_agg_df_nohyd[each] = watc_agg_df_nohyd[each].round(2)
        df_plot(watc_agg_df_nohyd, 'Million cubic metres (Mm^3)',
                cc+'-'+'Water consumption aggregated no hydro')
        
        # Detail rest
        wat_c_df_other = wat_c_df_original[[col for col in wat_c_df_original.columns if col not in t_include_hydro]]
        wat_c_df_other.reset_index(inplace=True)
        wat_c_df_other = wat_c_df_other.rename(columns=det_col)
        df_plot(wat_c_df_other,'Million cubic metres (Mm^3)',cc+"-"+'Water consumption (Detail other)', color_dict=color_dict)

    def emissions_chart(Country):
        cc = country_code[country_code['Country Name'] == Country]['Country code'].tolist()[
            0]
    #     #CO2-Emission detailed
    #     co2_df = all_params['AnnualTechnologyEmission']
    #     co2_df=co2_df[co2_df['e'].str[:5]==cc+'CO2'].copy()

    #     co2_df['value'] = co2_df['value'].astype('float64')
    #     co2_df = co2_df.pivot_table(index='y',columns='t',
    #                             values='value',
    #                             aggfunc='sum').reset_index().fillna(0)
    #     for each in co2_df.columns:
    #         if len(each)!=1:
    #             if (each[2:4]=='NG') & (each[6:10]=='BP00'):
    #                 pass
    #             else:
    #                 co2_df.rename(columns={each:each[2:10]},inplace=True)
    #         else:
    #             pass
    #     co2_df = co2_df.reindex(sorted(co2_df.columns), axis=1).set_index('y').reset_index().rename(columns=det_col)
    #     #co2_df['y'] = years
        #co2_df=co2_df[co2_df['y']>2022]
    #     df_plot(co2_df,'Million Tonnes (Mt)',cc+'-'+'Emissions (CO2)-by technology')
    #     co2_df.iplot(x='y',
    #                   kind='bar',
    #                   barmode='relative',
    #                   xTitle='Year',
    #                   yTitle="Million Tonnes (Mt)",
    #                   color=[color_dict[x] for x in co2_df.columns if x != 'y'],
    #                   title=cc+'-'+'Emissions (CO2)-by technology',showlegend=True)
        # Total emissions by type- This graph shows the total emissions in the country by emissiontype
        emis_df = all_params['AnnualEmissions']
        emis_df = emis_df[emis_df['e'].str[:5] == cc+'CO2'].copy()
        emis_df = df_filter_emission_tot(emis_df)
        df_plot(emis_df, 'Million Tonnes of CO2  (Mt)', cc+'-'+'Annual Emissions')

    def gas_chart(Country):
        cc = country_code[country_code['Country Name'] == Country]['Country code'].tolist()[
            0]
        # GAS Production (Detailed)
        gas_df = all_params['ProductionByTechnologyAnnual']
        gas_df_export1 = gas_df[(gas_df['t'].str[0:4] == cc+'NG')
                                & (gas_df['t'].str[6:10] == 'BP00')].copy()
        gas_df_export1['value'] = gas_df_export1['value'].astype(float)*-1
        gas_df_import1 = gas_df[(gas_df['t'].str[2:10] == 'NG'+cc+'BP00')].copy()
        gas_df = gas_df[(gas_df['t'].str[:2] == cc) & (
            gas_df['t'].str[2:4] == 'NG') & (gas_df['t'].str[6:7] != 'P')].copy()
        gas_df = gas_df[(gas_df['t'].str[6:10] == 'ELGX') | (
            gas_df['t'].str[6:10] == 'ILGX') | (gas_df['t'].str[6:10] == 'X00X')].copy()
        #gas_df = df_filter_gas(gas_df,2,10,gas_df_export1,gas_df_import1)
        gas_df['t'] = gas_df['t'].str[2:10]
        gas_df['value'] = gas_df['value'].astype('float64')
        gas_df['t'] = gas_df['t'].astype(str)
        gas_df = pd.concat([gas_df, gas_df_export1, gas_df_import1])
        gas_df = gas_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
        gas_df = gas_df.reindex(sorted(gas_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        gas_df = gas_df.iloc[np.where(gas_df['y']>first_year)]
        gas_df = gas_df.loc[:, (gas_df != 0).any(axis=0)]

        for each in gas_df.columns:
            if each == 'Natural gas exports (Liquification terminal)':
                gas_df[each] = gas_df[each].astype(float)*-1
            else:
                pass
        if len(gas_df.columns) == 1:
            print('There are no values for the result variable that you want to plot')
        else:
            fig = gas_df.iplot(x='y',
                            kind='bar',
                            barmode='relative',
                            xTitle='Year',
                            yTitle="Petajoules (PJ)",
                            color=[color_dict[x]
                                    for x in gas_df.columns if x != 'y'],
                            title=cc+"-"+"Gas extraction, imports and exports"+"-"+scenario,
                            showlegend=True,
                            asFigure=True)
            fig.update_xaxes(range=[first_year, last_year])
            title = (cc+"-"+"Gas extraction, imports and exports")
            pio.write_image(fig, os.path.join(homedir, 
                '{}.png'.format(title+"-"+scenario)),  width=1300, height=800)
            gas_df.to_csv(os.path.join(
                homedir, cc+"-"+"Gas extraction, imports and exports"+"-"+scenario+".csv"))
            return None

    def crude_chart(Country):
        cc = country_code[country_code['Country Name'] == Country]['Country code'].tolist()[
            0]
        # Crude oil refined in the country
        cru_r_df = all_params['ProductionByTechnologyAnnual']
        cru_r_df = cru_r_df[cru_r_df['f'].str[:6] == cc+'CRU2'].copy()
        cru_r_df['t'] = cru_r_df['t'].str[2:10]
        cru_r_df['value'] = cru_r_df['value'].astype('float64')
        cru_r_df = cru_r_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
        cru_r_df = cru_r_df.reindex(sorted(cru_r_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        cru_r_df = cru_r_df.iloc[np.where(cru_r_df['y']>first_year)]
        #cru_r_df['y'] = years
        # cru_r_df=cru_r_df[cru_r_df['y']>2022]
        df_plot(cru_r_df, 'Petajoules (PJ)', cc + '-' +
                'Crude oil refined in the country')
        # Crude oil production/imports/exports (Detailed)
        cru_df = all_params['ProductionByTechnologyAnnual']
        cru_df = cru_df[(cru_df['f'].str[:6] == cc + 'CRU1')].copy()
        cru_df['t'] = cru_df['t'].str[2:10]
        cru_df['value'] = cru_df['value'].astype('float64')
        cru_df['t'] = cru_df['t'].astype(str)
        cru_df = cru_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
        cru_df = cru_df.reindex(sorted(cru_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        cru_df = cru_df.iloc[np.where(cru_df['y']>first_year)]
        cru_df = cru_df.loc[:, (cru_df != 0).any(axis=0)]

        if len(cru_df.columns) == 1:
            print('There are no values for the result variable that you want to plot')
        else:
            fig = cru_df.iplot(x='y',
                            kind='bar',
                            barmode='relative',
                            xTitle='Year',
                            yTitle="Petajoules (PJ)",
                            color=[color_dict[x]
                                    for x in cru_df.columns if x != 'y'],
                            title=cc+"-"+"Crude oil extraction, imports and exports"+"-"+scenario,
                            showlegend=True,
                            asFigure=True)
            fig.update_xaxes(range=[first_year, last_year])
            title = (cc+"-"+"Crude oil extraction, imports and exports")
            pio.write_image(fig, os.path.join(homedir, 
                '{}.png'.format(title+"-"+scenario)),  width=1300, height=800)
            cru_df.to_csv(os.path.join(
                homedir, cc+"-"+"Crude oil extraction, imports and exports"+"-"+scenario+".csv"))
        return None

    def coal_biomass_chart(Country):
        cc = country_code[country_code['Country Name'] == Country]['Country code'].tolist()[
            0]
        # Coal overview
        coal_df = all_params['ProductionByTechnologyAnnual']
        coal_df = coal_df[coal_df['f'].str[:6] == cc+'COAL'].copy()
        coal_df['t'] = coal_df['t'].str[2:10]
        coal_df['value'] = coal_df['value'].astype('float64')
        coal_df = coal_df.pivot_table(index='y', columns='t',
                                    values='value',
                                    aggfunc='sum').reset_index().fillna(0)
        coal_df = coal_df.reindex(sorted(coal_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        coal_df = coal_df.iloc[np.where(coal_df['y']>first_year)]
        #coal_df['y'] = years
        # coal_df=coal_df[coal_df['y']>2022]
        df_plot(coal_df, 'Petajoules (PJ)', cc+'-'+'Coal production by technology')
        # Biomass overview
        biom_df = all_params['ProductionByTechnologyAnnual']
        biom_df = biom_df[biom_df['f'].str[:6] == cc+'BIOM'].copy()
        biom_df['t'] = biom_df['t'].str[2:10]
        biom_df['value'] = biom_df['value'].astype('float64')
        biom_df = biom_df.pivot_table(index='y', columns='t',
                                    values='value',
                                    aggfunc='sum').reset_index().fillna(0)
        biom_df = biom_df.reindex(sorted(biom_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        biom_df = biom_df.iloc[np.where(biom_df['y']>first_year)]
        #biom_df['y'] = years
        # biom_df=biom_df[biom_df['y']>2022]
        df_plot(biom_df, 'Petajoules (PJ)', cc+'-' +
                'Biomass production by technology')

    def hfo_lfo_chart(Country):
        cc = country_code[country_code['Country Name'] == Country]['Country code'].tolist()[
            0]
        # Heavy Fuel Oil overview
        hfo_df = all_params['ProductionByTechnologyAnnual']
        hfo_df = hfo_df[hfo_df['f'].str[:6] == cc+'HFOI'].copy()
        hfo_df['t'] = hfo_df['t'].str[2:10]
        hfo_df['value'] = hfo_df['value'].astype('float64')
        hfo_df = hfo_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
        hfo_df = hfo_df.reindex(sorted(hfo_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        hfo_df = hfo_df.iloc[np.where(hfo_df['y']>first_year)]
        #hfo_df['y'] = years
        # hfo_df=hfo_df[hfo_df['y']>2022]
        df_plot(hfo_df, 'Petajoules (PJ)', cc+'-'+'HFO production by technology')
        # Light Fuel Oil overview
        lfo_df = all_params['ProductionByTechnologyAnnual']
        lfo_df = lfo_df[lfo_df['f'].str[:6] == cc+'LFOI'].copy()
        lfo_df['t'] = lfo_df['t'].str[2:10]
        lfo_df['value'] = lfo_df['value'].astype('float64')
        lfo_df = lfo_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
        lfo_df = lfo_df.reindex(sorted(lfo_df.columns), axis=1).set_index(
            'y').reset_index().rename(columns=det_col)
        lfo_df = lfo_df.iloc[np.where(lfo_df['y']>first_year)]
        #lfo_df['y'] = years
        # lfo_df=lfo_df[lfo_df['y']>2022]
        df_plot(lfo_df, 'Petajoules (PJ)', cc+'-'+'LFO production by technology')


    for ref_y in [2020, 2030, 2040, 2050, 2060, 2070]:

        ccs = country_code['Country code'].values
        total_df = []
        for cc in ccs:
            gen_df = all_params['ProductionByTechnologyAnnual'].copy()
            gen_df_export = gen_df[(gen_df['f'].str[2:6] == 'EL01') & (
                gen_df['f'].str[0:2] != cc)].copy()
            gen_df_export = gen_df_export[gen_df_export['t'].str[6:10] == 'BP00'].copy(
            )
            gen_df_export = gen_df_export[(gen_df_export['t'].str[0:2] == cc) | (
                gen_df_export['t'].str[4:6] == cc)]
            gen_df_export['value'] = gen_df_export['value'].astype(float)*-1
            gen_df = gen_df[(gen_df['f'].str[:2] == cc)].copy()
            gen_df = gen_df[(gen_df['f'].str[2:6] == 'EL01') |
                            (gen_df['f'].str[2:6] == 'EL03')].copy()
            gen_df = gen_df[(gen_df['t'].str[2:10] != 'EL00T00X') & (
                gen_df['t'].str[2:10] != 'EL00TDTX')].copy()
            gen_df = pd.concat([gen_df, gen_df_export])
            gen_df['value'] = gen_df['value'].astype('float64')
            gen_df = gen_df.pivot_table(index='y',
                                        columns='t',
                                                values='value',
                                        aggfunc='sum').reset_index().fillna(0)
            for each in gen_df.columns:
                if len(each) != 1:
                    if (each[2:4] == 'EL') & (each[6:10] == 'BP00'):
                        pass
                    else:
                        gen_df.rename(columns={each: each[2:10]}, inplace=True)
                else:
                    pass
            gen_df = gen_df.reindex(sorted(gen_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            gen_df = gen_df.iloc[np.where(gen_df['y']>first_year)]
            #gen_df['y'] = years
            # gen_df=gen_df[gen_df['y']>2022]
            #df_plot(gen_df,'Petajoules (PJ)',cc+"-"+'Power Generation (Detail)')
            #####
            # Power generation (Aggregated)
            gen_agg_df = pd.DataFrame(columns=agg_pow_col)
            gen_agg_df.insert(0, 'y', gen_df['y'])
            gen_agg_df = gen_agg_df.fillna(0.00)
            for each in agg_pow_col:
                for tech_exists in agg_pow_col[each]:
                    if tech_exists in gen_df.columns:
                        gen_agg_df[each] = gen_agg_df[each] + gen_df[tech_exists]
                        gen_agg_df[each] = gen_agg_df[each].round(2)
        #     gen_agg_df.iplot(x='y',
        #                      kind='bar',
        #                      barmode='relative',
        #                      xTitle='Year',
        #                      yTitle="Petajoules (PJ)",
        #                      color=[color_dict[x] for x in gen_agg_df.columns if x != 'y'],
        #                      title=cc+"-"+"Power Generation (Aggregate)+"-"+scenario")
            gen_agg_df['Total'] = gen_agg_df['Coal']+gen_agg_df['Oil']+gen_agg_df['Gas']+gen_agg_df['Hydro']+gen_agg_df['Nuclear']+gen_agg_df['Solar CSP'] + \
                gen_agg_df['Solar PV']+gen_agg_df['Wind']+gen_agg_df['Biomass'] + \
                gen_agg_df['Geothermal']+gen_agg_df['Backstop'] + \
                gen_agg_df['power_trade']
            gen_agg_df['CCC'] = cc
            gen_agg_df = gen_agg_df[gen_agg_df['y'] == ref_y].copy()
            total_df.append(gen_agg_df)
            #df_plot(gen_agg_df,'Petajoules (PJ)',cc+"-"+'Power Generation (Aggregate)')
        total_df = pd.concat(total_df, ignore_index=True)
        total_df = total_df.drop('y', axis=1)
        total_df = total_df.drop('Total', axis=1)
        total_df = total_df.drop('gas_trade', axis=1,)
        # The csv file will be created in the home folder.
        ref_y = str(ref_y)
        total_df.to_csv(os.path.join(homedir, ref_y +
                                    "-generation" + "-" + scenario + ".csv"), index=None)

    # Dictionary for the powerpool classifications and countries
    pp_def = {'EAPP': ['ET', 'SD','EG', 'SS']}
    
    
#%%
    # # In the follwoing block, the capacity and generation graphs for all the powerpools and 
    # TEMBA will be plotted and CSV files generated
    # first for loop to loop over the powerpools
    for tk in pp_def.keys():
        cols_hydro = list(colorcode_hydro['tech_name'])
        cols_hydro.insert(0,'y')
        cols_solar = list(colorcode_solar['tech_name'])
        cols_solar.insert(0,'y')
        cols_fpv = [det_col[t] for t in t_include_fpv]
        cols_fpv.insert(0,'y')
        # cols_fossil = list(colorcode_fossil['tech_name'])
        # cols_fossil.insert(0,'y')
        
        total_gen_df = pd.DataFrame(np.zeros(shape=(56, 15)), columns=['y', 'Coal', 'Oil', 'Gas', 'Hydro', 'Nuclear', 'Solar CSP', 'Solar PV', 'Solar FPV',
                                                                    'Wind', 'Biomass', 'Geothermal', 'Backstop', 'power_trade', 'gas_trade'], dtype='float64')
        total_gen_df_hydro = pd.DataFrame(np.zeros(shape=(56, len(cols_hydro))), columns=cols_hydro, dtype='float64')
        total_gen_df_solar = pd.DataFrame(np.zeros(shape=(56, len(cols_solar))), columns=cols_solar, dtype='float64')
        total_gen_df_fpv = pd.DataFrame(np.zeros(shape=(56, len(cols_fpv))), columns=cols_fpv, dtype='float64')
        # total_gen_df_fossil = pd.DataFrame(np.zeros(shape=(56, len(cols_fossil))), columns=cols_fossil, dtype='float64')
        total_gen_df['y'] = years
        total_gen_df_hydro['y'] = years
        total_gen_df_solar['y'] = years
        total_gen_df_fpv['y'] = years
        # total_gen_df_fossil['y'] = years
        
        total_cap_df = pd.DataFrame(np.zeros(shape=(56, 15)), columns=['y', 'Coal', 'Oil', 'Gas', 'Hydro', 'Nuclear', 'Solar CSP', 'Solar PV','Solar FPV',
                                                                    'Wind', 'Biomass', 'Geothermal', 'Backstop', 'power_trade', 'gas_trade'], dtype='float64')
        total_cap_df_hydro = pd.DataFrame(np.zeros(shape=(56, len(cols_hydro))), columns=cols_hydro, dtype='float64')
        total_cap_df_solar = pd.DataFrame(np.zeros(shape=(56, len(cols_solar))), columns=cols_solar, dtype='float64')
        total_cap_df_fpv = pd.DataFrame(np.zeros(shape=(56, len(cols_fpv))), columns=cols_fpv, dtype='float64')
        # total_cap_df_fossil = pd.DataFrame(np.zeros(shape=(56, len(cols_fossil))), columns=cols_fossil, dtype='float64')
        total_cap_df['y'] = years
        total_cap_df_hydro['y'] = years
        total_cap_df_solar['y'] = years
        total_cap_df_fpv['y'] = years
        # total_cap_df_fossil['y'] = years
        
        # for loop for each country inside a powerpool
        for cc in pp_def[tk]:
            # Power capacity
            # Extract detailed capacity
            cap_df = detailed_power_chart(cc,'TotalCapacityAnnual', plotting=False)
            cap_df_hydro = detailed_power_chart(cc,'TotalCapacityAnnual',
                                                t_include_hydro, color_dict_hydro, 
                                                add_title='hydro', plotting=False)
            cap_df_solar = detailed_power_chart(cc,'TotalCapacityAnnual',
                                                t_include_solar, color_dict_solar, 
                                                add_title='solar', plotting=False)
            cap_df_fpv = detailed_power_chart(cc,'TotalCapacityAnnual',
                                                t_include_fpv, color_dict_solar, 
                                                add_title='fpv', plotting=False)
            # cap_df_fossil = detailed_power_chart(cc,'TotalCapacityAnnual',
            #                                     t_include_fossil, color_dict_fossil, 
            #                                     add_title='fossil', plotting=False)
            # Aggregate it per technology type
            cap_agg_df = pd.DataFrame(columns=agg_pow_col)
            cap_agg_df.insert(0, 'y', cap_df['y'])
            cap_agg_df = cap_agg_df.fillna(0.00)
            cap_agg_df['y'] = cap_agg_df['y'].astype('float64')
            
            for each in agg_pow_col:
                for tech_exists in agg_pow_col[each]:
                    if tech_exists in cap_df.columns:
                        cap_agg_df[each] = cap_agg_df[each] + cap_df[tech_exists]
                        cap_agg_df[each] = cap_agg_df[each].round(3)
            
            # Add the aggregated capacity of the country to the total power pool df
            total_cap_df = cap_agg_df.set_index('y').add(
                total_cap_df.set_index('y'), fill_value=0).reset_index()
            total_cap_df_hydro = cap_df_hydro.set_index('y').add(
                total_cap_df_hydro.set_index('y'), fill_value=0).reset_index()
            total_cap_df_solar = cap_df_solar.set_index('y').add(
                total_cap_df_solar.set_index('y'), fill_value=0).reset_index()
            total_cap_df_fpv = cap_df_fpv.set_index('y').add(
                total_cap_df_fpv.set_index('y'), fill_value=0).reset_index()
            # total_cap_df_fossil = cap_df_fossil.set_index('y').add(
            #     total_cap_df_fossil.set_index('y'), fill_value=0).reset_index()


            # Power generation
            # Extract detailed generation 
            gen_df = all_params['ProductionByTechnologyAnnual'].copy()
            gen_df_export = gen_df[(gen_df['f'].str[2:6] == 'EL01') & (
                gen_df['f'].str[0:2] != cc)].copy()
            gen_df_export = gen_df_export[gen_df_export['t'].str[6:10] == 'BP00'].copy(
            )
            gen_df_export = gen_df_export[(gen_df_export['t'].str[0:2] == cc) | (
                gen_df_export['t'].str[4:6] == cc)]
            gen_df_export['value'] = gen_df_export['value'].astype(float)*-1
            gen_df = gen_df[(gen_df['f'].str[:2] == cc)].copy()
            gen_df = gen_df[(gen_df['f'].str[2:6] == 'EL01') |
                            (gen_df['f'].str[2:6] == 'EL03')].copy()
            gen_df = gen_df[(gen_df['t'].str[2:10] != 'EL00T00X') & (
                gen_df['t'].str[2:10] != 'EL00TDTX')].copy()
            gen_df = pd.concat([gen_df, gen_df_export])
            gen_df['value'] = gen_df['value'].astype('float64')
            gen_df = gen_df.pivot_table(index='y',
                                        columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
            for each in gen_df.columns:
                if len(each) != 1:
                    if (each[2:4] == 'EL') & (each[6:10] == 'BP00'):
                        pass
                    else:
                        gen_df.rename(columns={each: each[2:10]}, inplace=True)
                else:
                    pass
            gen_df = gen_df.reindex(sorted(gen_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            gen_df = gen_df.iloc[np.where(gen_df['y']>first_year)]
            
            
            gen_df_hydro = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
                                                t_include_hydro, 
                                                color_dict_hydro, 
                                                add_title='hydro', 
                                                plotting=False)
            gen_df_solar = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
                                                t_include_solar, 
                                                color_dict_solar, 
                                                add_title='solar', 
                                                plotting=False)
            gen_df_fpv = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
                                                t_include_fpv, 
                                                color_dict_solar, 
                                                add_title='fpv', 
                                                plotting=False)
            # gen_df_fossil = detailed_power_chart(cc,'ProductionByTechnologyAnnual',
            #                                     t_include_fossil, 
            #                                     color_dict_fossil, 
            #                                     add_title='fossil', 
            #                                     plotting=False)
            
            # Aggregate it by technology type
            gen_agg_df = pd.DataFrame(columns=agg_pow_col)
            gen_agg_df.insert(0, 'y', gen_df['y'])
            gen_agg_df = gen_agg_df.fillna(0.00)
            for each in agg_pow_col:
                for tech_exists in agg_pow_col[each]:
                    if tech_exists in gen_df.columns:
                        gen_agg_df[each] = gen_agg_df[each] + gen_df[tech_exists]
                        gen_agg_df[each] = gen_agg_df[each].round(2)
            
            # Add it to the  aggregated generation of the country to the power pool df
            total_gen_df = gen_agg_df.set_index('y').add(
                total_gen_df.set_index('y'), fill_value=0).reset_index()
            total_gen_df_hydro = gen_df_hydro.set_index('y').add(
                total_gen_df_hydro.set_index('y'), fill_value=0).reset_index()
            total_gen_df_solar = gen_df_solar.set_index('y').add(
                total_gen_df_solar.set_index('y'), fill_value=0).reset_index()
            total_gen_df_fpv = gen_df_fpv.set_index('y').add(
                total_gen_df_fpv.set_index('y'), fill_value=0).reset_index()
            # total_gen_df_fossil = gen_df_fossil.set_index('y').add(
            #     total_gen_df_fossil.set_index('y'), fill_value=0).reset_index()
            
        # Drop columns with only zeros
        total_cap_df = total_cap_df.loc[:, (total_cap_df != 0).any(axis=0)]
        total_cap_df_hydro = total_cap_df_hydro.loc[:, (total_cap_df_hydro != 0).any(axis=0)]
        total_cap_df_solar = total_cap_df_solar.loc[:, (total_cap_df_solar != 0).any(axis=0)]
        total_cap_df_fpv = total_cap_df_fpv.loc[:, (total_cap_df_fpv != 0).any(axis=0)]
        # total_cap_df_fossil = total_cap_df_fossil.loc[:, (total_cap_df_fossil != 0).any(axis=0)]
        total_gen_df = total_gen_df.loc[:, (total_gen_df != 0).any(axis=0)]
        total_gen_df_hydro = total_gen_df_hydro.loc[:, (total_gen_df_hydro != 0).any(axis=0)]
        total_gen_df_solar = total_gen_df_solar.loc[:, (total_gen_df_solar != 0).any(axis=0)]
        total_gen_df_fpv = total_gen_df_fpv.loc[:, (total_gen_df_fpv != 0).any(axis=0)]
        # total_gen_df_fossil = total_gen_df_fossil.loc[:, (total_gen_df_fossil != 0).any(axis=0)]

        # Plot
        df_plot(total_cap_df, 'Gigawatts (GW)', tk + "-" +
                'Power Generation Capacity (Aggregate)') 
        df_plot(total_cap_df_hydro, 'Gigawatts (GW)', tk + "-" +
                'Power Generation Capacity (Detail hydro)', color_dict=color_dict_hydro_pp) 
        df_plot(total_cap_df_solar, 'Gigawatts (GW)', tk + "-" +
                'Power Generation Capacity (Detail solar)', color_dict=color_dict_solar_pp) 
        df_plot(total_cap_df_fpv, 'Gigawatts (GW)', tk + "-" +
                'Power Generation Capacity (Detail fpv)', color_dict=color_dict_solar_pp) 
        # df_plot(total_cap_df_fossil, 'Gigawatts (GW)', tk + "-" +
        #         'Power Generation Capacity (Detail fossil)', color_dict=color_dict_fossil) 
        df_plot(total_gen_df_hydro, "Petajoules (PJ)", tk + "-" +
                'Power Generation (Detail hydro)', color_dict=color_dict_hydro_pp) 
        df_plot(total_gen_df_solar, "Petajoules (PJ)", tk + "-" +
                'Power Generation (Detail solar)', color_dict=color_dict_solar_pp) 
        df_plot(total_gen_df_fpv, "Petajoules (PJ)", tk + "-" +
                'Power Generation (Detail fpv)', color_dict=color_dict_solar_pp) 
        # df_plot(total_gen_df_fossil, "Petajoules (PJ)", tk + "-" +
        #         'Power Generation (Detail fossil)', color_dict=color_dict_fossil) 
        
        
        fig = total_gen_df.iplot(x='y',
                                kind='bar',
                                barmode='relative',
                                xTitle='Year',
                                yTitle="Petajoules (PJ)",
                                color=[color_dict[x]
                                        for x in total_gen_df.columns if x != 'y'],
                                title=tk+"-" +
                                "Power Generation (Aggregate)"+"-"+scenario,
                                showlegend=True,
                                asFigure=True)
        fig.update_xaxes(range=[first_year, last_year])
        title = (tk+"-"+"Power Generation (Aggregate)")
        pio.write_image(fig, os.path.join(homedir, '{}.png'.format(title)),
                        scale=1, width=1500, height=1000)
        # fig.show()
        # total_cap_df['y']=years
        # total_cap_df=total_cap_df.drop('gas_trade',axis=1)

        total_gen_df.to_csv(os.path.join(
            homedir, tk + "-Power Generation (Aggregate)"+"-"+scenario+".csv"))
        total_cap_df.to_csv(os.path.join(
            homedir, tk + "-Power Generation Capacity (Aggregate)"+"-"+scenario+".csv"))

#%%
    # # In the follwoing block, the water consumption and withdrawal graphs for all the powerpools and TEMBA will be plotted and CSV files generated for each
    for tk in pp_def.keys():
        # The following lines are used for creating dummy
        # (empty) dataframes to print aggregated (powerpool/TEMBA) results as csv files
        total_watc_df = pd.DataFrame(np.zeros(shape=(56, 19)), columns=['y', 'Coal', 'Oil', 'Gas', 'Hydro', 'Nuclear', 'Solar CSP', 'Solar PV',
                                                                        'Wind', 'Geothermal', 'Biomass', 'Coal Production', 'Crude Oil production', 'Crude oil Refinery',
                                                                        'Natural gas extraction', 'Uranium extraction', 'Transmission & Distribution', 'Backstop',
                                                                        'Biofuel and Biomass production'], dtype='float64')
        total_watc_df['y'] = years
        total_watw_df = pd.DataFrame(np.zeros(shape=(56, 19)), columns=['y', 'Coal', 'Oil', 'Gas', 'Hydro', 'Nuclear', 'Solar CSP', 'Solar PV',
                                                                        'Wind', 'Geothermal', 'Biomass', 'Coal Production', 'Crude Oil production', 'Crude oil Refinery',
                                                                        'Natural gas extraction', 'Uranium extraction', 'Transmission & Distribution', 'Backstop',
                                                                        'Biofuel and Biomass production'], dtype='float64')
        total_watw_df['y'] = years
        total_watc_nohyd_df = pd.DataFrame(np.zeros(shape=(56, 19)), columns=['y', 'Coal', 'Oil', 'Gas', 'Hydro', 'Nuclear', 'Solar CSP', 'Solar PV',
                                                                        'Wind', 'Geothermal', 'Biomass', 'Coal Production', 'Crude Oil production', 'Crude oil Refinery',
                                                                        'Natural gas extraction', 'Uranium extraction', 'Transmission & Distribution', 'Backstop',
                                                                        'Biofuel and Biomass production'], dtype='float64')
        total_watc_nohyd_df['y'] = years
        
        total_watc_hydro = pd.DataFrame(np.zeros(shape=(56, len(cols_hydro))), columns=cols_hydro, dtype='float64')
        total_watc_hydro['y'] = years
        ######
        for cc in pp_def[tk]:
            # Water Withdrawal (Detailed)
            wat_w_df = all_params['UseByTechnologyAnnual']
            wat_w_df = wat_w_df[wat_w_df['f'].str[:6] == cc+'WAT1'].copy()

            wat_w_df['t'] = wat_w_df['t'].str[2:10]
            wat_w_df['value'] = wat_w_df['value'].astype('float64')
            wat_w_df = wat_w_df.pivot_table(index='y',
                                            columns='t',
                                            values='value',
                                            aggfunc='sum').reset_index().fillna(0)
            wat_w_df = wat_w_df.reindex(sorted(wat_w_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            wat_w_df = wat_w_df.iloc[np.where(wat_w_df['y']>first_year)]
            #wat_w_df['y'] = years
            # wat_w_df=wat_w_df[wat_w_df['y']>2022]
            #df_plot(wat_w_df,'Million cubic metres (Mm^3)',cc+"-"+'Water Withdrawal')
           
            # Water Withdrawal (Aggregated)
            watw_agg_df = pd.DataFrame(columns=agg_col)
            watw_agg_df.insert(0, 'y', wat_w_df['y'])
            watw_agg_df = watw_agg_df.fillna(0.00)
            for each in agg_col:
                for tech_exists in agg_col[each]:
                    if tech_exists in wat_w_df.columns:
                        watw_agg_df[each] = watw_agg_df[each] + \
                            wat_w_df[tech_exists]
                        watw_agg_df[each] = watw_agg_df[each].round(2)
            total_watw_df = total_watw_df.set_index('y').add(
                watw_agg_df.set_index('y'), fill_value=0).reset_index()
            
            # water output detailed
            wat_o_df = all_params['ProductionByTechnologyAnnual']
            wat_o_df = wat_o_df[wat_o_df['f'].str[:6] == cc+'WAT2'].copy()
            wat_o_df['t'] = wat_o_df['t'].str[2:10].copy()
            wat_o_df['value'] = wat_o_df['value'].astype('float64')
            wat_o_df = wat_o_df.pivot_table(index='y',
                                            columns='t',
                                            values='value',
                                            aggfunc='sum').reset_index().fillna(0)
            wat_o_df = wat_o_df.reindex(sorted(wat_o_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            wat_o_df = wat_o_df.iloc[np.where(wat_o_df['y']>first_year)]
            #wat_o_df['y'] = years
            # wat_o_df=wat_o_df[wat_o_df['y']>2022]
            #df_plot(wat_o_df,'Million cubic metres (Mm^3)',cc+"-"+'Water output')
            ###
            # Water consumption missing row additions
            for wd in wat_w_df.columns:
                for wc in wat_o_df.columns:
                    if wd in wat_o_df.columns:
                        pass
                    else:
                        wat_o_df[wd] = 0
            
            # Water consumption (Detailed)
            wat_c_df = wat_w_df.set_index('y')-wat_o_df.set_index('y')
            wat_c_df = wat_c_df.fillna(0.00)
            wat_c_df.reset_index(inplace=True)
            total_watc_hydro = total_watc_hydro.set_index('y').add(
                wat_c_df.set_index('y'), fill_value=0).reset_index()
            total_watc_hydro = total_watc_hydro[cols_hydro]

            
            # Water consumption (Aggregate)
            watc_agg_df = pd.DataFrame(columns=agg_col)
            watc_agg_df.insert(0, 'y', wat_c_df['y'])
            watc_agg_df = watc_agg_df.fillna(0.00)
            for each in agg_col:
                for tech_exists in agg_col[each]:
                    if tech_exists in wat_c_df.columns:
                        watc_agg_df[each] = watc_agg_df[each] + \
                            wat_c_df[tech_exists]
                        watc_agg_df[each] = watc_agg_df[each].round(2)
            total_watc_df = total_watc_df.set_index('y').add(
                watc_agg_df.set_index('y'), fill_value=0).reset_index()

            # Water consumption (Aggregate no hydro)
            col_nohyd = total_watc_df.columns
            col_nohyd = col_nohyd.drop('Hydro')
            total_watc_nohyd_df = total_watc_df[col_nohyd]
            
        total_watw_df['y'] = years
        total_watc_df['y'] = years
        total_watc_nohyd_df['y'] = years
        total_watc_hydro['y'] = years
        total_watc_df['y'] = total_watc_df['y'].astype('float64')
        total_watc_nohyd_df['y'] = total_watc_nohyd_df['y'].astype('float64')
        total_watc_hydro['y'] = total_watc_hydro['y'].astype('float64')
        total_watw_df['y'] = total_watw_df['y'].astype('float64')
        total_watw_df = total_watw_df[total_watw_df['y'] <= last_year]
        total_watc_df = total_watc_df[total_watc_df['y'] <= last_year]
        total_watc_nohyd_df = total_watc_nohyd_df[total_watc_nohyd_df['y'] <= last_year]
        total_watc_hydro = total_watc_hydro[total_watc_hydro['y'] <= last_year]
        
        df_plot(total_watw_df, 'Million cubic metres (Mm^3)',
                tk+"-"+'Water Withdrawal')
        df_plot(total_watc_df, 'Million cubic metres (Mm^3)',
                tk+"-"+'Water Consumption')
        df_plot(total_watc_nohyd_df, 'Million cubic metres (Mm^3)',
                tk+"-"+'Water Consumption (No Hydro)')
        df_plot(total_watc_hydro, 'Million cubic metres (Mm^3)',
                tk+"-"+'Water Consumption (Detail Hydro)', color_dict=color_dict_hydro)


    # %%
    # This is for taking the pickle file and producing the csvs
    # x=[]
    # pkl_file = open("./TEMBA_Ref_12_08_modex.pickle", 'rb')
    # x = pickle.load(pkl_file)
    # df=pd.DataFrame()
    # for each in x:
    #     df=x[each]
    #     df.to_csv(each +".csv")


    # %%
    # Consolidated Emissions
    for tk in pp_def.keys():
        total_emis_df = pd.DataFrame(np.zeros(shape=(56, 2)), columns=[
                                    'y', 'CO2'], dtype='float64')
        total_emis_df['y'] = total_emis_df['y'].astype('float64')
        total_emis_df['y'] = years
        for cc in pp_def[tk]:
            emis_df = all_params['AnnualEmissions']
            emis_df = emis_df[emis_df['e'].str[:5] == cc+'CO2'].copy()
            emis_df = df_filter_emission_tot(emis_df)
            total_emis_df = total_emis_df.set_index('y').add(
                emis_df.set_index('y'), fill_value=0).reset_index()
        total_emis_df['y'] = years
        total_emis_df = total_emis_df[total_emis_df['y'] <= last_year]
        df_plot(total_emis_df, 'Million Tonnes of CO2 (Mt)',
                tk+"-"+'Annual Emissions')
        #total_emis_df.to_csv(os.path.join(homedir,tk +"-"+ scenario +"-"+'Annual Emissions.csv'))


    # %%
    # Consolidated HFO and LFO use
    for tk in pp_def.keys():
        total_lfo_df = pd.DataFrame(np.zeros(shape=(56, 4)), columns=[
                                    'y', 'Crude oil refinery 1', 'Crude oil refinery 2', 'Light Fuel Oil imports'], dtype='float64')
        total_lfo_df['y'] = total_lfo_df['y'].astype('float64')
        total_lfo_df['y'] = years
        total_hfo_df = pd.DataFrame(np.zeros(shape=(56, 4)), columns=[
                                    'y', 'Crude oil refinery 1', 'Crude oil refinery 2', 'Heavy Fuel Oil imports'], dtype='float64')
        total_hfo_df['y'] = total_hfo_df['y'].astype('float64')
        total_hfo_df['y'] = years
        for cc in pp_def[tk]:
            # Heavy Fuel Oil overview
            hfo_df = all_params['ProductionByTechnologyAnnual']
            hfo_df = hfo_df[hfo_df['f'].str[:6] == cc+'HFOI'].copy()
            hfo_df['t'] = hfo_df['t'].str[2:10]
            hfo_df['value'] = hfo_df['value'].astype('float64')
            hfo_df = hfo_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
            hfo_df = hfo_df.reindex(sorted(hfo_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            total_hfo_df = total_hfo_df.set_index('y').add(
                hfo_df.set_index('y'), fill_value=0).reset_index()
            total_hfo_df = total_hfo_df.iloc[np.where(total_hfo_df['y']>first_year)]
            #hfo_df['y'] = years
            # hfo_df=hfo_df[hfo_df['y']>2022]
            # Light Fuel Oil overview
            lfo_df = all_params['ProductionByTechnologyAnnual']
            lfo_df = lfo_df[lfo_df['f'].str[:6] == cc+'LFOI'].copy()
            lfo_df['t'] = lfo_df['t'].str[2:10]
            lfo_df['value'] = lfo_df['value'].astype('float64')
            lfo_df = lfo_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
            lfo_df = lfo_df.reindex(sorted(lfo_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            #df_plot(lfo_df,'Petajoules (PJ)',cc+"-"+'LFO production by technology')
            total_lfo_df = total_lfo_df.set_index('y').add(
                lfo_df.set_index('y'), fill_value=0).reset_index()
            total_lfo_df = total_lfo_df.iloc[np.where(total_lfo_df['y']>first_year)]
            #lfo_df['y'] = years
            # lfo_df=lfo_df[lfo_df['y']>2022]
        total_hfo_df['y'] = years
        total_lfo_df['y'] = years
        total_hfo_df = total_hfo_df[total_hfo_df['y'] <= last_year]
        total_lfo_df = total_lfo_df[total_lfo_df['y'] <= last_year]
        df_plot(total_hfo_df, 'Petajoules (PJ)', tk +
                "-"+'HFO production by technology')
        df_plot(total_lfo_df, 'Petajoules (PJ)', tk +
                "-"+'LFO production by technology')
        #total_hfo_df.to_csv(os.path.join(homedir,tk +"-"+ scenario +"-"+'HFO production by technology.csv'))
        #total_lfo_df.to_csv(os.path.join(homedir,tk +"-"+ scenario +"-"+'LFO production by technology.csv'))


    # %%
    # Cosnsolidated coal and bioamss usage
    for tk in pp_def.keys():
        total_coal_df = pd.DataFrame(np.zeros(shape=(56, 3)), columns=[
                                    'y', 'Coal imports (inland transport, maritime freight)', 'Coal extraction (mining)'], dtype='float64')
        total_coal_df['y'] = total_coal_df['y'].astype('float64')
        total_coal_df['y'] = years
        total_biom_df = pd.DataFrame(np.zeros(shape=(56, 2)), columns=[
                                    'y', 'Biomass extraction/production/refining'], dtype='float64')
        total_biom_df['y'] = total_biom_df['y'].astype('float64')
        total_biom_df['y'] = years
        for cc in pp_def[tk]:
            # Coal overview
            coal_df = all_params['ProductionByTechnologyAnnual']
            coal_df = coal_df[coal_df['f'].str[:6] == cc+'COAL'].copy()
            coal_df['t'] = coal_df['t'].str[2:10]
            coal_df['value'] = coal_df['value'].astype('float64')
            coal_df = coal_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
            coal_df = coal_df.reindex(sorted(coal_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            if len(coal_df.columns) == 1:
                coal_df = pd.DataFrame(np.zeros(shape=(56, 3)), columns=[
                                    'y', 'Coal imports (inland transport, maritime freight)', 'Coal extraction (mining)'], dtype='float64')
                coal_df['y'] = years
            total_coal_df = total_coal_df.set_index('y').add(
                coal_df.set_index('y'), fill_value=0).reset_index()
            total_coal_df = total_coal_df.iloc[np.where(total_coal_df['y']>first_year)]
            
            # total_coal_df=coal_df+total_coal_df
            #coal_df['y'] = years
            # coal_df=coal_df[coal_df['y']>2022]

            # Biomass overview
            biom_df = all_params['ProductionByTechnologyAnnual']
            biom_df = biom_df[biom_df['f'].str[:6] == cc+'BIOM'].copy()
            biom_df['t'] = biom_df['t'].str[2:10]
            biom_df['value'] = biom_df['value'].astype('float64')
            biom_df = biom_df.pivot_table(index='y', columns='t',
                                        values='value',
                                        aggfunc='sum').reset_index().fillna(0)
            biom_df = biom_df.reindex(sorted(biom_df.columns), axis=1).set_index(
                'y').reset_index().rename(columns=det_col)
            total_biom_df = total_biom_df.set_index('y').add(
                biom_df.set_index('y'), fill_value=0).reset_index()
            total_biom_df = total_biom_df.iloc[np.where(total_biom_df['y']>first_year)]
            #biom_df['y'] = years
            # biom_df=biom_df[biom_df['y']>2022]
        total_coal_df['y'] = years
        total_biom_df['y'] = years
        total_coal_df = total_coal_df[total_coal_df['y'] <= last_year]
        total_biom_df = total_biom_df[total_biom_df['y'] <= last_year]
        df_plot(total_biom_df, 'Petajoules (PJ)', tk +
                '-' + 'Biomass production by technology')
        df_plot(total_coal_df, 'Petajoules (PJ)', tk +
                '-' + 'Coal production by technology')


    for each in country_code['Country Name']:
        power_chart(each)
        water_chart(each)
        emissions_chart(each)
        gas_chart(each)
        crude_chart(each)
        coal_biomass_chart(each)
        hfo_lfo_chart(each)

    # this block will create individual country folders and paste (all country specific csv and png files)
    # files from the home directory to the path mentioned below

    resultpath = os.path.join(destination_folder)
    files = os.listdir(homedir)
    for country in country_code['Country code']:
        dest1 = os.path.join(resultpath, country)
        os.makedirs(dest1, exist_ok=True)
        for f in files:
            if (f.startswith(country)):
                filepath = os.path.join(homedir, f)
                shutil.move(filepath, dest1)

    # this block will create individual Power pool folders and paste (all country specific csv and png files)
    # files from the home directory to the path mentioned below
    power_p = ['EAPP']
    resultpath = os.path.join(destination_folder)
    files = os.listdir(homedir)
    for en in power_p:
        dest2 = os.path.join(resultpath, en)
        os.makedirs(dest2, exist_ok=True)
        for f in files:
            if (f.startswith(en)):
                filepath = os.path.join(homedir, f)
                shutil.move(filepath, dest2)


