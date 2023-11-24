# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 14:00:14 2023

@author: Alessandro Pieruzzi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


input_file = r'CombinedHydroSolar.csv'

df = pd.read_csv(input_file)
df = df.iloc[:37]

cols = ['UnitName', 'tech_code', 'Volume',
        'Area', 'Capacity(MW)']

df = df[cols]

# Mark which loc is missing what
def assign_var(row):
    if np.isnan(row['Volume']) & np.isnan(row['Area']):
        return 'Capacity'
    elif ~np.isnan(row['Volume']) & np.isnan(row['Area']):
        return 'Volume'
    else:
        return 'Literature'
    
df['Area estimated from'] = df.apply(lambda row: assign_var(row), axis = 1)

# Fill the gaps using volume - area curve
known = df.iloc[np.where(~(df['Volume'].isna() | df['Area'].isna()))[0]]
known = known.drop([2,4,11]) # Remove other outliers

model = LinearRegression()
model.fit(known['Volume'].values.reshape(-1, 1), known['Area'].values)
unknown = df.iloc[np.where((~df['Volume'].isna() & df['Area'].isna()))[0]]
unknown.loc[:,'Area'] = model.predict(unknown['Volume'].values.reshape(-1, 1))

plt.figure()
plt.scatter(known['Volume'],known['Area'], label='Data points')
plt.scatter(unknown['Volume'],unknown['Area'], label='Predicted points')
plt.plot(known['Volume'], model.predict(known['Volume'].values.reshape(-1, 1)), color='red', label='Regression line')
plt.xlabel('Volume [mcm]')
plt.ylabel('Area [km2]')
plt.legend()

df.loc[unknown.index] = unknown # Fill the gaps in the whole df


# Fill the remaining gaps using the capacity - area curve
known_cap = df.iloc[np.where(~ df['Area'].isna())[0]]
unknown_cap = df.iloc[np.where(df['Area'].isna())[0]]

known_cap = known_cap.drop([2,4,11,7]) # Remove other outliers

model = LinearRegression()
model.fit(known_cap['Capacity(MW)'].values.reshape(-1, 1), known_cap['Area'].values)
unknown_cap = df.iloc[np.where((~df['Capacity(MW)'].isna() & df['Area'].isna()))[0]]
unknown_cap.loc[:,'Area'] = model.predict(unknown_cap['Capacity(MW)'].values.reshape(-1, 1))

plt.figure()
plt.scatter(known_cap['Capacity(MW)'],known_cap['Area'], label='Data points')
plt.scatter(unknown_cap['Capacity(MW)'],unknown_cap['Area'], label='Predicted points')
plt.plot(known_cap['Capacity(MW)'], model.predict(known_cap['Capacity(MW)'].values.reshape(-1, 1)), color='red', label='Regression line')
plt.xlabel('Capacity(MW)')
plt.ylabel('Area [km2]')
plt.legend()

df.loc[unknown_cap.index] = unknown_cap

df.to_excel('FullAreasDataset.xlsx')

# X = known_cap['Capacity(MW)'].values.reshape(-1, 1)
# y = known_cap['Area'].values.reshape(-1, 1)

# poly_features = PolynomialFeatures(degree=4)
# X_poly = poly_features.fit_transform(X)

# # Create and fit the polynomial regression model
# poly_model = LinearRegression()
# poly_model.fit(X_poly, y)

# # Visualize the results
# plt.figure()
# plt.scatter(X, y, color='blue', label='Data points')

# # Plot the polynomial regression curve
# x_range = unknown_cap['Capacity(MW)'].values.reshape(-1, 1)
# x_range_poly = poly_features.transform(x_range)
# plt.plot(x_range, poly_model.predict(x_range_poly), color='red', label='Polynomial regression curve (degree=2)')

# plt.xlabel('X-axis label')
# plt.ylabel('Y-axis label')
# plt.title('Polynomial Regression Example')
# plt.legend()
# plt.show()









