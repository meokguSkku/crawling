import pandas as pd
import json

# Load the CSV file
csv_file_path = 'kakao_restaurants_updated.csv'
df = pd.read_csv(csv_file_path)

# Convert each row to a JSON object and store in a list
json_list = df.to_dict(orient='records')

# Save the list of JSON objects to a file
json_file_path = 'kakao_restaurants_updated1.json'
with open(json_file_path, 'w', encoding='utf-8') as json_file:
  json.dump(json_list, json_file, ensure_ascii=False, indent=4)

print(f"JSON file has been saved to {json_file_path}")