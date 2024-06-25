import requests

# API 요청 URL
api_url = 'https://place.map.kakao.com/1874178690'

# API 요청 헤더 (필요한 경우 추가 헤더를 포함해야 할 수 있음)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# API 요청 보내기
response = requests.get(api_url, headers=headers)

# 응답 JSON 데이터 파싱
data = response.json()

print(data)