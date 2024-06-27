import pandas as pd
import os

df1 = pd.read_csv('kakao_url_response.csv', encoding='utf-8')

df2 = pd.read_csv('kakao_restaurant_urls.csv',encoding='utf-8')

df1['id'] = df1['id'].astype(str)
df2['id'] = df2['id'].astype(str)

df1['name'] = df1['name'].astype(str)
df2['name'] = df2['name'].astype(str)


merged_df = pd.merge(df1,df2,on='name',how='left')

merged_df.to_csv('merged_output.csv',index=False, encoding='utf-8')
