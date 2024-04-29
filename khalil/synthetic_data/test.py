import pandas as pd


df = pd.read_csv('train.csv')
dict_df = df.to_dict()
print(type(dict_df['question']))
# print(dict_df.keys())
