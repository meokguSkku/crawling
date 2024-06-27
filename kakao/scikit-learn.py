import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 첫 번째 CSV 파일 읽기
df1 = pd.read_csv('kakao_url_response.csv', encoding='utf-8')

# 상위 디렉토리에 있는 두 번째 CSV 파일 읽기
parent_dir_csv = os.path.join('..', 'restaurants.csv')
df2 = pd.read_csv(parent_dir_csv, encoding='utf-8')

# 데이터 전처리
def preprocess_data(df):
  df['name_prefix'] = df['name'].str[:3]
  df['address_suffix'] = df['address'].str[-9:]
  df['phone_suffix'] = df['phone_number'].str[-7:]
  df['combined'] = df['name_prefix'] + ' ' + df['address_suffix'] + ' ' + df['phone_suffix']
  return df

df1 = preprocess_data(df1)
df2 = preprocess_data(df2)

# TF-IDF 벡터화
vectorizer = TfidfVectorizer()
tfidf_matrix1 = vectorizer.fit_transform(df1['combined'])
tfidf_matrix2 = vectorizer.transform(df2['combined'])

# 코사인 유사도 계산
cosine_sim = cosine_similarity(tfidf_matrix1, tfidf_matrix2)

# 유사도 매트릭스에서 가장 유사한 인덱스 찾기
matched_indices = np.argmax(cosine_sim, axis=1)
matched_scores = np.max(cosine_sim, axis=1)

# 매칭 결과 데이터프레임에 추가
df1['matched_index'] = matched_indices
df1['match_score'] = matched_scores
df1['matched_name'] = df2.iloc[matched_indices]['name'].values
df1['matched_address'] = df2.iloc[matched_indices]['address'].values
df1['matched_phone_number'] = df2.iloc[matched_indices]['phone_number'].values

# 결과를 새로운 CSV 파일로 저장
merged_df = df1
merged_df.to_csv('merged_output.csv', index=False, encoding='utf-8')

print("Data matching and CSV file creation complete.")
