#Import the required libraries
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def college_predict(gre, toefl, rating, sop, lor, cgpa, research):
    
    #Read the dataset
    df = pd.read_csv("data/Admission_Predict.csv")
    print(df.describe())
    
    #Data preprocessing
    df.rename(columns = {'Chance of Admit ':'Chance of Admit', 'LOR ':'LOR'}, inplace=True)
    df.drop(labels='Serial No.', axis=1, inplace=True)
    
    targets = df['Chance of Admit']
    features = df.drop(columns = {'Chance of Admit'})
    
    X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.2, random_state=42)
    X_exp = [[gre, toefl, rating, sop, lor, cgpa, research]]
    
    linreg = LinearRegression()
    linreg.fit(X_train, y_train)
    linreg_score = (linreg.score(X_test, y_test))*100
    
    y_pred = linreg.predict(X_exp)
    return y_pred, linreg_score