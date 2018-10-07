import json
import re

import os
import pymongo
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing import Pool

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from Jiepai.config import *
import requests

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab',
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print('请求索引页失败.')
        return None


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    image_pattern = re.compile('gallery: JSON.parse\("(.*?)"\),', re.S)
    image_patternbase_data = re.compile('articleInfo: (.*?)tagInfo:', re.S)
    result = re.search(image_pattern, html)
    images = []
    if result:
        data = re.findall("url_list(.*?)\"},", html)
        for item in data:
            image = item[15:-1].replace('\\', '')
            download_image(image)
            images.append(image)
    else:
        data = re.search(image_patternbase_data, html)
        if data:
            data = data.group(1).strip()[:-1]
            data = re.findall("http:.*?&quot", data)
            for item in data:
                image = item[:-5]
                download_image(image)
                images.append(image)
    return {
        'title': title,
        'url': url,
        'images': images
    }


def get_page_detail(url):
    data = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=data)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print('请求索引页失败.')
        return None


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到mongodb成功')
    else:
        print('存储到mongodb失败')


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
    file_path = '{0}\{1}.{2}'.format(os.getcwd() + "\image", md5(content).hexdigest(), 'jpg')
    print(file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(offset):
    html = get_page_index(offset, KEY_WORD)
    for url in parse_page_index(html):
        if url != None:
            html = get_page_detail(url)
            if html:
                result = parse_page_detail(html, url)
                if result: save_to_mongo(result)


if __name__ == '__main__':
    groups = [x * 20 for x in range(GROUP_START, GROUP_END + 1)]
    pool = Pool()
    pool.map(main, groups)
