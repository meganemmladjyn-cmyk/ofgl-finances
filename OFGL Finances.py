import pandas as pd

df = pd.read_csv("ofgl-base-communes.csv", nrows=5)
print(df.columns.tolist())
print(df.shape)
