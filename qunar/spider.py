import pymongo
from urllib.parse import urlencode
from pyquery import PyQuery as pq

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from qunar.config import *

# brower = webdriver.Chrome()
brower = webdriver.PhantomJS(service_args=SERVICE_ARGS)
brower.set_window_size(1400,900)
wait = WebDriverWait(brower, 10)
base_url = 'http://piao.qunar.com/ticket/list.htm?'
count_page= 0

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def search(KEY_WORD,page):
    print('正在爬取'+KEY_WORD)
    try:
        data = {
            'keyword': KEY_WORD,
            'region':'',
            'from': 'mps_search_suggest',
            'page': page
        }
        queries = urlencode(data)
        url = base_url+queries
        brower.get(url)
        get_tourist()

    except TimeoutException:
        return search(KEY_WORD,page)

def get_tourist():
    hot = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#order-by-popularity"))
    )
    hot.click()
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#search-list .sight_item"))
    )
    html = brower.page_source
    doc = pq(html)
    items = doc('#search-list .sight_item').items()
    for item in items:
        tourist = {
            'name':item.find('.sight_item_caption .name').text(),
            'level': item.find('.level').text().strip(),
            'more_url':'http://piao.qunar.com'+item.find('.sight_item_about .sight_item_caption .name').attr('href').strip(),
            'province':item.find('.area').text()[1:-1].strip().split('·')[0],
            'city':item.find('.area').text()[1:-1].strip().split('·')[1],
            'image':item.find('.loading a .img_opacity').attr('data-original'),
            'describe': item.find('.intro').attr('title'),
            'hot_num': item.find('.hot_num').text(),
            'price': item.find('.sight_item_price').text()[1:-1].strip(),
        }
        print(tourist)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储Mongo成功',result)
    except Exception:
        print('存储Mongo失败', result)

def main():
    for key_word in KEY_WORD:
        for i in range(1,GROUP_COUNT):
            search(key_word,i)
            import time
            time.sleep(2)


if __name__ == '__main__':
    main()
    brower.close()
