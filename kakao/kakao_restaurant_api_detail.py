import time
import requests
import csv
import pandas as pd

def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for URL {url} with status code {response.status_code}")
        return None

def extract_keys(data, key_path):
    keys = set()
    target = data
    for key in key_path:
        target = target.get(key, {})
        if not target:
            break
    else:
        if isinstance(target, list):
            for item in target:
                keys.update(item.keys())
        else:
            keys.update(target.keys())
    return keys

def extract_operation_times(data):
    open_hour = data.get('basicInfo', {}).get('openHour', {})
    time_dict = {}
    try:
        for period in open_hour.get('periodList', []):
            for time in period.get('timeList', []):
                days = time.get('dayOfWeek', '').split(',')
                start_time = time.get('timeSE', '').split(' ~ ')[0]
                end_time = time.get('timeSE', '').split(' ~ ')[1]
                for day in days:
                    time_dict[f"{day}_start"] = start_time
                    time_dict[f"{day}_end"] = end_time
    except:
        pass
    return time_dict

def collect_keys(reader, headers):
    time_keys = set()
    for row in reader:
        url = row[9]  # URL 열 위치
        if url == '':
            continue
        place_id = url.split('/')[-1]
        api_url = f'https://place.map.kakao.com/main/v/{place_id}'

        data = fetch_data(api_url, headers)
        if data:
            time_keys.update(extract_operation_times(data).keys())

        print("진행중")
        time.sleep(0.1)
    return sorted(time_keys)

def extract_data(data, time_keys):
    time_data = extract_operation_times(data)
    return {key: time_data.get(key, '') for key in time_keys}

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    df = pd.read_csv('kakao_restaurants.csv')
    new_columns = []

    # 파일을 한 번 읽어서 필요한 키들을 수집합니다.
    with open('kakao_restaurants.csv', mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 헤더 건너뛰기
        time_keys = collect_keys(reader, headers)
        new_columns = time_keys

    # 필요한 열이 없는 경우 추가합니다.
    for column in new_columns:
        if column not in df.columns:
            df[column] = ''

    # 각 행을 업데이트합니다.
    for idx, row in df.iterrows():
        url = row['url']
        if url == '':
            continue
        place_id = url.split('/')[-1]
        api_url = f'https://place.map.kakao.com/main/v/{place_id}'

        data = fetch_data(api_url, headers)
        if data:
            time_data = extract_data(data, time_keys)
            for key, value in time_data.items():
                df.at[idx, key] = value

            print(f"Updated row {idx+1}")

            time.sleep(0.1)

    df.to_csv('kakao_restaurants.csv', index=False)

print("Data extraction and CSV file creation complete.")

if __name__ == "__main__":
    main()