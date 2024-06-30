import csv
import pandas as pd

# Step 3: Merge the two CSV files
naver_df = pd.read_csv('naver_to_kakao_restaurants.csv')
kakao_df = pd.read_csv('kakao_api_detail_response.csv')

# Merge on the 'id' and 'name' columns to ensure the correct data is combined
merged_df = pd.merge(naver_df, kakao_df, on=['id', 'name'], how='left')

# Save the merged data to a new CSV file
merged_df.to_csv('combined_restaurants.csv', index=False)

print("Data merge and CSV file creation complete.")