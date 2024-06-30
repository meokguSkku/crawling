import json
import time
import requests
import csv

# 결과를 저장할 CSV 파일 생성 및 헤더 작성
with open('kakao_api_detail_response.csv', mode='w', newline='', encoding='utf-8') as csv_file:

    # 원본 CSV 파일 읽기
    with open('kakao_restaurant_urls.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 헤더 건너뛰기

        # API 요청 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        facility_keys = set()
        operation_infos = set()
        time_keys = set()

        # 첫 번째 루프: 시설 정보 key 값 수집
        for row in reader:
            url = row[1]  # url이 CSV의 두 번째 열에 있다고 가정
            place_id = url.split('/')[-1]
            api_url = f'https://place.map.kakao.com/main/v/{place_id}'

            # API 요청
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()

                facility_info = data.get('basicInfo', {}).get('facilityInfo', {})
                facility_keys.update(facility_info.keys())

                operation_info = data.get('basicInfo', {}).get('operationInfo',{})
                operation_infos.update(operation_info.keys())

                open_hour = data.get('basicInfo', {}).get('openHour', {})
                try:
                    period_list = open_hour.get('periodList', [])[0].get('timeList', [])
                    for period in period_list:
                        time_keys.update(period.keys())
                except:
                    pass
                print("진행중")
                time.sleep(0.1)
            else:
                print(f"Failed to fetch data for URL {url} with status code {response.status_code}")

        facility_keys = list(facility_keys)
        operation_infos = list(operation_infos)
        time_keys = list(time_keys)

        header = ['id', 'url', 'name', 'category', 'review_count', 'blog_review_count', 'address', 'phone_number'] + facility_keys + operation_infos + time_keys

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header)

        # CSV 파일 다시 읽기
        csvfile.seek(0)
        reader = csv.reader(csvfile)
        next(reader)  # 헤더 건너뛰기

        # 두 번째 루프, 각 URL에 대해 API 요청 및 데이터 처리
        id = 0
        for row in reader:
            url = row[1]  # url이 CSV의 두 번째 열에 있다고 가정
            place_id = url.split('/')[-1]
            api_url = f'https://place.map.kakao.com/main/v/{place_id}'

            # API 요청
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()

                # 필요한 데이터 추출
                id = id + 1
                name = data.get('basicInfo', {}).get('placenamefull', '')
                category = data.get('basicInfo', {}).get('category', {}).get('catename', '')
                review_count = data.get('basicInfo', {}).get('feedback', {}).get('comntcnt', '')
                blog_review_count = data.get('basicInfo', {}).get('feedback', {}).get('blogrvwcnt', '')

                # 분리된 주소 합치기
                address_raw = data.get('basicInfo', {}).get('address', {})
                new_addr = address_raw.get('region').get('newaddrfullname', '')
                region = address_raw.get('newaddr', {}).get('newaddrfull', '')
                address = f"{new_addr} {region}"

                open_hour = data.get('basicInfo', {}).get('openHour', {})
                period_dict = {}
                try:
                    period_list = open_hour.get('periodList', [])[0].get('timeList', [])
                    for i, period in enumerate(period_list):
                        for key,value in period.items():
                            period_dict[f"{key}_{i+1}"] = value
                except:
                    period_dict = {key: '' for key in time_keys}

                facility_info = data.get('basicInfo', {}).get('facilityInfo', {})
                facility_data = {key: facility_info.get(key, '') for key in facility_keys}

                operation_info = data.get('basicInfo', {}).get('operationInfo', {})
                operation_data = {key: operation_info.get(key, '') for key in operation_infos}

                phone_number = data.get('basicInfo', {}).get('phonenum', '')

                # 추출한 데이터를 CSV에 쓰기
                print(id, name, category, review_count, blog_review_count, address, phone_number, facility_data.values(), period_dict.values(), operation_data.values())

                csv_writer.writerow([id, url, name, category, review_count, blog_review_count, address, phone_number]
                                    + list(facility_data.values())
                                    + list(operation_data.values())
                                    + list(period_dict.values()))

                time.sleep(0.1)
            else:
                print(f"Failed to fetch data for URL {url} with status code {response.status_code}")

print("Data extraction and CSV file creation complete.")