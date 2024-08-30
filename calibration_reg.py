"""
Script for calibration of the pixel intensity to the ice thickness measured with energy filter.
Input: CSV file with pixel intensity and measured ice columns
Output: linear function equation, MAE, MSE and RMSE metrics.
"""
import pandas as pd
import numpy as np
import sys
import random
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

path_file = sys.argv[1]

df = pd.read_csv(path_file)

y = df['ib_val'].values.reshape(-1,1)
X = df['filter_val'].values.reshape(-1,1)
seed = random.randint(0,100)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = seed)


regressor = LinearRegression()

regressor.fit(X_train, y_train)

slope = float(regressor.coef_)
intercept = float(regressor.intercept_)

y_pred = regressor.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test,y_pred)
rmse = np.sqrt(mse)

print('Approximated function: y = '+str(round(slope,4)) + 'x + '+str(round(intercept,4)))
print('Mean Absolute Error: '+str(round(mae,4)))
print('Mean Squared Error: '+str(round(mse,4)))
print('Root Mean Squared Error: '+str(round(rmse,4)))


