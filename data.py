class my_class(object):
    pass

import pandas as pd    #  pip install pandas
import os
from pathlib import Path
data_dir = os.getcwd()
df1 = pd.read_csv('table1.csv')
df2 = pd.read_csv('table2.csv')
df3 = pd.read_csv('table3.csv')
df4 = pd.read_csv('table4.csv')
df5 = pd.read_csv('table5.csv')
df6 = pd.read_csv('table6.csv')
df7 = pd.read_csv('table7.csv')
df8 = pd.read_csv('table8.csv')
df9 = pd.read_csv('table9.csv')
df10 = pd.read_csv('table10.csv')

df_merged = df1.merge(df2, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df3, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df3, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df4, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df5, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df6, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df7, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df8, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df9, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
df_merged = df_merged.merge(df10, on='HeatNo', how='outer')
df_merged = df_merged.dropna()
data = df_merged.to_csv('data.csv')