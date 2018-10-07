import os
import re

from requests import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from taobao.config import *

brower = webdriver.Chrome()
wait = WebDriverWait(brower, 10)


def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        else:
            return None
    except RequestException:
        print('请求图片失败.')
        return None

def save_image(content):
    file_path = '{0}\{1}.{2}'.format(os.getcwd()+"\image","登陆二维码",'png')
    print(file_path)
    with open(file_path,'wb') as f:
        f.write(content)
        f.close()


def search():
    url = '''https://login.taobao.com/member/login.jhtml?redirectURL=http://s.taobao.com/search?&initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&
    search_type=item&ssid=s5-e&commend=all&imgfile=&q='''+KEYWORD+'''&suggest=0_1&_input_charset=utf-8&
    wq=ip&suggest_query=ip&source=suggest'''
    brower.get(url)
    image = wait.until(
         EC.presence_of_element_located((By.CSS_SELECTOR, "#J_QRCodeImg > img"))
    )
    data = re.search('img.alicdn(.*?).png',brower.page_source)
    if data:
        imageurl = 'http://img.alicdn'+data.group(1)+'.png'
        print(imageurl)
        download_image(imageurl)
    # brower.get(url)
    # input = wait.until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
    # )
    # submit = wait.until(
    #     EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button"))
    # )
    # input.send_keys('')

def main():
    search()

if __name__ == '__main__':
    main()
    # brower.close()