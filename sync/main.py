import os
import json
import glob
import sys

import selenium
import traceback
import requests
from selenium import webdriver
from selenium.webdriver import Firefox, FirefoxOptions, Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select

site_name = "card_rakuten"
config = json.load(open("config.json", "r", encoding="utf-8"))
# 楽天カードログインURL
login_url = config[site_name]["login_url"]
# 楽天カードユーザーID
user_id = config[site_name]["user_id"]
# 楽天カードパスワード
password = config[site_name]["password"]
# 楽天カード第２パスワード
password2 = config[site_name]["password2"]
# 対象カードの末尾４桁 (例:1234)
main_card_num = config[site_name]["card_num"]
# 明細ダウンロード先の一時フォルダ
download_dir_path = '/app/results'
download_dir_path = "results"

# main_card_numで指定したカードを選択する関数
def select_card(browser, select_card_num, p = None):
   # 現在選択中のカードIDをとってくる。選択できて入れえば終わり。
   WebDriverWait(browser, 10).until(
     ec.presence_of_element_located((By.XPATH, '//*[@id="j_idt609"]/div[2]/div/div[2]/div'))
   )
   current_card_num_element = browser.find_element(By.XPATH, '//*[@id="j_idt609"]/div[2]/div/div[2]/div')
   card_num_str = current_card_num_element.get_attribute('innerHTML')
   splited_card_num = card_num_str.split(' - ')
   if len(splited_card_num) != 4:
       raise Exception('Invalid CardID Format')
   card_num = splited_card_num[3]
   print(f'Current Selected CardNum=[{card_num}]')
   if select_card_num == card_num:
       print(f'{select_card_num} is selected!')
       return
   # 現在選択しているカードじゃないやつを選ぶ
   card_selector = Select(browser.find_element(By.XPATH, '//*[@id="j_idt609:card"]'))
   if p is None:
       p = 0
   if p == len(card_selector.options):
       raise Exception('Not found card...')
   card_value_to_try = card_selector.options[p].get_attribute('value')
   print(f'Selecting...value={card_value_to_try}')
   card_selector.select_by_value(card_value_to_try)
   # 正しいカードが選択できるまで再帰的にトライする
   select_card(browser, select_card_num, p + 1)

def login(browser):
    browser.get(login_url)

    browser.save_screenshot("captures/login-screen.png")
    # ID自動入力
    e = browser.find_element(By.ID, "user_id")
    e.clear()
    e.send_keys(user_id)
    browser.save_screenshot("captures/login-screen_send_keys.png")
    next_button = browser.find_element(By.ID, "cta001")
    next_button.click()
    WebDriverWait(browser, 10).until(
      ec.presence_of_element_located((By.ID, "password_current"))
    )
    browser.save_screenshot("captures/login-screen_after_click.png")

    e = browser.find_element(By.ID, "password_current")
    e.clear()
    e.send_keys(password)
    next_button = browser.find_element(By.ID, "cta011")
    next_button.click()

    #wait until redirected to https://www.rakuten-card.co.jp/e-navi/members/index.xhtml
    WebDriverWait(browser, 10).until(
      ec.url_matches('https://www.rakuten-card.co.jp/e-navi/members/index.xhtml')
    )
    browser.save_screenshot("captures/logined.png")
    print('-> Logged in')

def access_meisai(browser):
    url = 'https://www.rakuten-card.co.jp/e-navi/members/statement/index.xhtml?tabNo={}'.format(i)
    browser.get(url)

def get_meisai_title(browser):
    title_element = browser.find_element(By.XPATH, "//*[@id='js-payment-calendar-btn']/span")
    title = title_element.get_attribute('innerHTML')
    print(f'meisai_title={title}')
    return title

def get_meisai_csv_url(browser):
    csv_link_tag = browser.find_element(By.CLASS_NAME, 'stmt-csv-btn')
    href = csv_link_tag.get_attribute('href')
    return href

def get_cookies(browser):
    c = {}
    for cookie in browser.get_cookies():
        name = cookie['name']
        value = cookie['value']
        c[name] = value
    return c

options = ChromeOptions()
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("window-size=1920,1080")
browser = Chrome(options=options)

try:
    login(browser)
    # 直近三ヶ月のカード利用明細へアクセス
    for i in range(3):
        # 明細ページへ遷移
        access_meisai(browser)
        # カード番号を指定
        select_card(browser, main_card_num)
        # 明細のタイトル名を取得
        meisai_title = get_meisai_title(browser)
        # ダウンロードリンクの取得
        meisai_csv_url = get_meisai_csv_url(browser)
        # requestsで使うためのCookie情報取り出し
        c = get_cookies(browser)
        # CSVダウンロードパス
        download_path = os.path.join(download_dir_path, f'{meisai_title}.csv')
        print(f'Downloading... {download_dir_path}')
        # requestsを利用してデータのダウンロード
        r = requests.get(meisai_csv_url, cookies=c)
        with open(download_path, 'wb') as f:
                f.write(r.content)
except Exception as e:
    print(traceback.format_exc())

browser.quit()