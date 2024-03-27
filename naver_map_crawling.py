import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

csv_file = open('restaurants.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['name', 'category', 'review_count', 'address', 'rating', 'number', 'image_url'])

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

user_agent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
options.add_argument(user_agent)

options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--remote-allow-origins=*")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://map.naver.com/p/search/%EC%84%B1%EA%B7%A0%EA%B4%80%EB%8C%80%EC%97%AD%20%EC%9D%8C%EC%8B%9D%EC%A0%90?c=15.00,0,0,0,dh"
driver.get(url)
time.sleep(12)

searchIFrame = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
driver.switch_to.frame(searchIFrame)
time.sleep(1)

for _ in range(5):  # 6페이지까지
    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.mFg6p")

    scroll_div = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div[1]")
    for _ in range(10):
        driver.execute_script("arguments[0].scrollBy(0,2000);", scroll_div)
        time.sleep(2)

    restaurant_names = driver.find_elements(By.XPATH, "//ul/li/div[1]/a[1]/div/div/span[1]")
    restaurant_categories = driver.find_elements(By.XPATH,
                                                 "//div[contains(@class, 'place_bluelink')]//span[@class='KCMnt']")
    reviews = driver.find_elements(By.XPATH, "//div[contains(@class, 'Dr_06')]//span[@class='h69bs']")

    print(len(restaurant_names))

    for i, name in enumerate(restaurant_names):
        review = reviews[i].text.replace("리뷰 ", "")
        category = restaurant_categories[i].text.replace("\"", "")
        print(name.text, category, review)

        name.click()
        time.sleep(1)

        driver.switch_to.default_content()
        time.sleep(1)
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, "iframe#entryIframe"))
        time.sleep(1)

        driver.find_element(By.CLASS_NAME, "_UCia").click()  # 주소 자세히 클릭
        time.sleep(1)

        address = driver.find_element(By.CLASS_NAME, "nQ7Lh").text
        address = address.replace("복사", "")
        address = address.replace("도로명", "")
        print(address)

        try:
            rating = driver.find_element(By.CLASS_NAME, "LXIwF").text.split("\n")[1]
        except:
            rating = ""

        try:
            number = driver.find_element(By.CLASS_NAME, "xlx7Q").text
        except:
            number = ""

        try:
            style_attribute = driver.find_element(By.XPATH, "//div[contains(@class, 'K0PDV')]").get_attribute('style')
            match = re.search(r'url\("([^"]+)"\)', style_attribute)
            if match:
                image_url = match.group(1)
            else:
                image_url = ""
        except:
            image_url = ""

        print(rating, number, image_url)

        driver.switch_to.default_content()
        time.sleep(1)
        driver.switch_to.frame(searchIFrame)
        time.sleep(1)

        csv_writer.writerow([name.text, category, review, address, rating, number, image_url])

    driver.find_element(By.XPATH, "//a[.//span[contains(text(), '다음페이지')]]").click()

    time.sleep(2)

csv_file.close()
