import csv
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

csv_file = open('kakao_restaurants.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'name', 'category','review_count','address','rating','rating_count', 'phone_number', 'operate_time'])

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

user_agent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
options.add_argument(user_agent)

options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--remote-allow-origins=*")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://map.kakao.com/"
driver.get(url)
time.sleep(6)

search_box = driver.find_element(By.CSS_SELECTOR, "input[id='search.keyword.query']")
search_keyword = "성균관대역 음식점"
search_box.send_keys(search_keyword)
search_button = driver.find_element(By.CSS_SELECTOR, "button[id='search.keyword.submit']")
driver.execute_script("arguments[0].click();", search_button)
time.sleep(1)

location_fix = driver.find_element(By.CSS_SELECTOR, "span[id='search.keyword.currentmap']")
driver.execute_script("arguments[0].click();",location_fix)

naver_map_crawling_path = '../restaurants.csv'
restaurants_df = pd.read_csv(naver_map_crawling_path)

restaurant_names = restaurants_df['name'].tolist()

id = 1
for name in restaurant_names:
    search_box.clear()
    search_box.send_keys(name)

    search_box.send_keys(Keys.RETURN)

    time.sleep(2)

    restaurant_names = set()
    category = set()
    number_of_review = set()
    review_score = set()

    #평점 매긴 사람 수
    number_of_score = set()
    operate_time = set()

    try:
        restaurant_names = driver.find_element(By.XPATH, "//a[contains(@class, 'link_name')]")
    except:
        id+=1
        continue
    category = driver.find_element(By.XPATH,"//div[@class='head_item clickArea']//span[@class='subcategory clickable']")
    number_of_review = driver.find_element(By.XPATH, "//em[contains(@data-id, 'numberofreview')]")

    address = driver.find_element(By.XPATH,"//p[@data-id='address']")

    review_score = driver.find_element(By.XPATH, "//em[contains(@data-id, 'scoreNum')]")
    number_of_score = driver.find_element(By.XPATH, "//a[contains(@data-id, 'numberofscore')]")
    number_of_score_text=''
    if '건' in number_of_score.text:
        number_of_score_text = number_of_score.text.replace('건', '').strip()

    phone_number = driver.find_element(By.XPATH, "//span[@data-id='phone']")

    operate_time = driver.find_element(By.XPATH, "//a[contains(@data-id, 'periodTxt')]")

    operate_time_text=operate_time.text
    # 휴게시간 휴게시간일 기준으로 왼쪽으로 영업시간 오른쪽은 휴게시간일듯..
    if '영업시간' in operate_time.text:
        operate_time_text = operate_time.text.replace('영업시간','').strip()



    csv_writer.writerow([id, restaurant_names.text, category.text, number_of_review.text, address.text, review_score.text,number_of_score_text, phone_number.text, operate_time_text ])
    id += 1


    time.sleep(2)
csv_file.close()



