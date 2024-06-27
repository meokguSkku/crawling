import json
import time

import requests
import csv

# 결과를 저장할 CSV 파일 생성 및 헤더 작성
with open('kakao_url_response.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['id', 'url', 'name', 'category', 'review_count', 'blog_review_count', 'address', 'phone_number', 'operation_info'])

    # 원본 CSV 파일 읽기
    with open('kakao_restaurant_urls.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 헤더 건너뛰기

        # API 요청 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # 각 URL에 대해 API 요청 및 데이터 처리
        for row in reader:
            url = row[1]  # url이 CSV의 두 번째 열에 있다고 가정
            place_id = url.split('/')[-1]
            api_url = f'https://place.map.kakao.com/main/v/{place_id}'

            # API 요청
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()

                # 필요한 데이터 추출
                id = data.get('basicInfo', {}).get('cid', '')
                name = data.get('basicInfo', {}).get('placenamefull', '')

                category = data.get('basicInfo', {}).get('category', {}).get('catename', '')

                review_count = data.get('basicInfo', {}).get('feedback', {}).get('comntcnt', '')
                blog_review_count = data.get('basicInfo', {}).get('feedback', {}).get('blogrvwcnt', '')

                #분리된 주소 합치기.
                address_raw = data.get('basicInfo', {}).get('address', '')
                new_addr = address_raw.get('region').get('newaddrfullname', '')
                region = address_raw.get('newaddr', {}).get('newaddrfull', '')
                address = f"{new_addr} {region}"

                open_hour = data.get('basicInfo', {}).get('openHour', {})
                try:
                    operation_time = open_hour.get('periodList', [])[0].get('timeList', [])
                except:
                    operation_time = open_hour.get('openhourDisplayText')


                operation_time_json = json.dumps(operation_time, ensure_ascii=False)
                open_hour_json = json.dumps(open_hour, ensure_ascii=False)

                facility_info = data.get('basicInfo', {}).get('facilityInfo', {})

                wifi = facility_info.get('wifi', '')
                pet = facility_info.get('pet', '')
                nursery = facility_info.get('nursery', '')
                smoking_room = facility_info.get('smokingroom', '')

                #시설정보와 (예약,배달,포장)의 정보는 Dictionary형태가 아닌 Json형태로 정보가 반환됨.
                facility_info_json = json.dumps(facility_info, ensure_ascii=False)


                operation_info = data.get('basicInfo', {}).get('operationInfo',{})
                operation_info_json = json.dumps(operation_info, ensure_ascii=False)

                phone_number = data.get('basicInfo', {}).get('phonenum', '')

                # 추출한 데이터를 CSV에 쓰기
                print(id, name, category, review_count, blog_review_count, address, phone_number, facility_info_json, operation_info_json, operation_time_json)
                csv_writer.writerow([id, url, name, category, review_count, blog_review_count, address, phone_number, wifi,pet,nursery,smoking_room, operation_info_json, operation_time_json])
                time.sleep(2)
            else:
                print(f"Failed to fetch data for URL {url} with status code {response.status_code}")

print("Data extraction and CSV file creation complete.")
