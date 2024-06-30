import json
import time
import requests
import csv

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
        url = row[1]
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

    name = basic_info.get('placenamefull', '')
    category = basic_info.get('category', {}).get('catename', '')
    review_count = basic_info.get('feedback', {}).get('comntcnt', '')
    blog_review_count = basic_info.get('feedback', {}).get('blogrvwcnt', '')

    address_raw = basic_info.get('address', {})
    new_addr = address_raw.get('region').get('newaddrfullname', '')
    region = address_raw.get('newaddr', {}).get('newaddrfull', '')
    address = f"{new_addr} {region}"

    phone_number = basic_info.get('phonenum', '')

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

    return name, category, review_count, blog_review_count, address, phone_number, facility_data, operation_data, period_dict

def main():
    with open('kakao_api_detail_response.csv', mode='w', newline='', encoding='utf-8') as csv_file, open('kakao_restaurant_urls.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 헤더 건너뛰기

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        facility_keys, operation_keys, time_keys = collect_keys(reader, headers)

        header = ['id', 'url', 'name', 'category', 'review_count', 'blog_review_count', 'address', 'phone_number'] + facility_keys + time_keys + operation_keys
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header)

        csvfile.seek(0)
        reader = csv.reader(csvfile)
        next(reader)  # 헤더 건너뛰기

        id_counter = 0
        for row in reader:
            url = row[1]
            place_id = url.split('/')[-1]
            api_url = f'https://place.map.kakao.com/main/v/{place_id}'

            data = fetch_data(api_url, headers)
            if data:
                id_counter += 1
                name, category, review_count, blog_review_count, address, phone_number, facility_data, operation_data, period_dict = extract_data(data, facility_keys, operation_keys, time_keys)

                print(id_counter, name, category, review_count, blog_review_count, address, phone_number, facility_data.values(), operation_data.values(), period_dict.values())

                csv_writer.writerow([id_counter, url, name, category, review_count, blog_review_count, address, phone_number]
                                    + list(facility_data.values())
                                    + list(period_dict.values())
                                    + list(operation_data.values()))

                time.sleep(0.1)

print("Data extraction and CSV file creation complete.")

if __name__ == "__main__":
    main()