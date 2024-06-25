import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

csv_file = open('kakao_restaurant_urls.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'url'])

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

inputBox = driver.find_element(By.CSS_SELECTOR, "input[id='search.keyword.query']")
search_keyword = "성균관대역 음식점"
inputBox.send_keys(search_keyword)
search_button = driver.find_element(By.CSS_SELECTOR, "button[id='search.keyword.submit']")
driver.execute_script("arguments[0].click();", search_button)
time.sleep(1)

restaurant_id = 1

for _ in range(12):
    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div[id='info.body']")
    scroll_increment = 3500
    driver.execute_script("arguments[0].scrollTop += arguments[1];", scrollable_div, scroll_increment)
    try:
        # 특정 요소 확인
        more_button = driver.find_element(By.ID, "info.search.place.more")
        if more_button.is_displayed():
            driver.execute_script("arguments[0].click();", more_button)
            break

        time.sleep(10)
        break
    except:
        continue
    time.sleep(1)  # 스크롤 완료를 위해 잠시 대기
element = driver.find_element(By.CSS_SELECTOR, "a[id='info.search.page.no1']")
driver.execute_script("arguments[0].click();", element)
time.sleep(6)
id = 1
for i in range(7):
    for p in range(5):  # 5페이지까지
        scrollable_div = driver.find_element(By.CSS_SELECTOR, "div[id='info.body']")

        restaurant_names = set()
        restaurant_categories = set()
        reviews = set()
        # 요소를 스크롤할 때의 높이 설정

        restaurant_names = driver.find_elements(By.XPATH, "//a[contains(@class, 'link_name')]")
        restaurant_categories = driver.find_elements(By.XPATH,
                                                     "//div[@class='head_item clickArea']//span[@class='subcategory clickable']")
        reviews = driver.find_elements(By.XPATH, "//div[contains(@class, 'rating clickArea')]//em[@class='num']")

        print(len(restaurant_names), len(restaurant_categories), len(reviews))

        more_review_buttons = driver.find_elements(By.CSS_SELECTOR, "a.moreview")

        hrefs = [button.get_attribute('href') for button in more_review_buttons]
        time.sleep(2)

        for h in hrefs:
            csv_writer.writerow([id, h])
            id += 1
        if (p+2)%5 == 1:
            next_chapter = driver.find_element(By.ID, "info.search.page.next")
            driver.execute_script("arguments[0].click();", next_chapter)
            time.sleep(6)
            continue
        next_page_button = driver.find_element(By.CSS_SELECTOR, f"#info\\.search\\.page\\.no{p+2}")
        driver.execute_script("arguments[0].click();", next_page_button)



