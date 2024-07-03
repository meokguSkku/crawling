import json
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

def extract_facility_keys(data):
    return extract_keys(data, ['basicInfo', 'facilityInfo'])

def extract_operation_keys(data):
    return extract_keys(data, ['basicInfo', 'operationInfo'])

def extract_time_keys(data):
    time_keys = set()
    open_hour = data.get('basicInfo', {}).get('openHour', {})
    try:
        period_list = open_hour.get('periodList', [])[0].get('timeList', [])
        for i, period in enumerate(period_list):
            for key in period.keys():
                time_keys.add(f"{key}_{i+1}")
    except:
        pass
    return time_keys

def collect_keys(reader, headers):
    facility_keys, operation_keys, time_keys = set(), set(), set()
    for row in reader:
        url = row[9]  # URL 열 위치
        if url == '':
            continue
        place_id = url.split('/')[-1]
        api_url = f'https://place.map.kakao.com/main/v/{place_id}'

        data = fetch_data(api_url, headers)
        if data:
            facility_keys.update(extract_facility_keys(data))
            operation_keys.update(extract_operation_keys(data))
            time_keys.update(extract_time_keys(data))

        print("진행중")
        time.sleep(0.1)
    return sorted(facility_keys), sorted(operation_keys), sorted(time_keys)

def extract_data(data, facility_keys, operation_keys, time_keys):
    basic_info = data.get('basicInfo', {})

    facility_info = basic_info.get('facilityInfo', {})
    facility_data = {key: facility_info.get(key, '') for key in facility_keys}

    operation_info = basic_info.get('operationInfo', {})
    operation_data = {key: operation_info.get(key, '') for key in operation_keys}

    open_hour = basic_info.get('openHour', {})
    period_dict = {key: '' for key in time_keys}
    try:
        period_list = open_hour.get('periodList', [])[0].get('timeList', [])
        for i, period in enumerate(period_list):
            for key, value in period.items():
                period_dict[f"{key}_{i+1}"] = value
    except:
        pass

    return facility_data, operation_data, period_dict

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
        facility_keys, operation_keys, time_keys = collect_keys(reader, headers)
        new_columns = facility_keys + time_keys + operation_keys

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
            facility_data, operation_data, period_dict = extract_data(data, facility_keys, operation_keys, time_keys)

            for key, value in facility_data.items():
                df.at[idx, key] = value
            for key, value in period_dict.items():
                df.at[idx, key] = value
            for key, value in operation_data.items():
                df.at[idx, key] = value

            print(f"Updated row {idx+1}")

            time.sleep(0.1)

    df.to_csv('kakao_restaurants.csv', index=False)

print("Data extraction and CSV file creation complete.")

if __name__ == "__main__":
    main()
