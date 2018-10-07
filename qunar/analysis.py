import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from PIL import Image
from os import path
from pyecharts import Map

data = pd.read_csv(r'D:\develop\python\spider\tourist1.csv')
data.drop(['_id', 'more_url'], axis=1, inplace=True)

# 根据省、市统计销量和
province_num = data.groupby(['province']).agg('sum').reset_index()
city_num = data.groupby(['city']).agg('sum').reset_index()


def draw_bar():
    bar_data = data.sort_values(by=['hot_num'], ascending=False)
    bar_data_y = bar_data[bar_data[u'hot_num'] > 1000][:30]['hot_num']
    bar_data_x = bar_data[bar_data[u'hot_num'] > 1000][:30]['name'] + '(' + bar_data[bar_data[u'hot_num'] > 1000][:30][
        'province'] + ')'

    # 指定默认字体
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

    # 解决保存图像是负号'-'显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False

    # 解决Seaborn中文显示问题
    sns.set(font='SimHei')

    # 设置seaborn样式
    sns.set_context('talk')

    # 新建绘画窗口,独立显示绘画的图片
    plt.figure(figsize=(15, 10))

    # 绘图样式
    sns.barplot(bar_data_x, bar_data_y)

    # 获取或设置当前刻度线位置和标签的x限制
    plt.xticks(rotation=90)

    # 下方文字等，自适应
    plt.tight_layout()
    plt.show()


def draw_level():
    # 省份与景区评级
    data['level_sum'] = 1
    var = data.groupby(['province', 'level']).level_sum.sum()
    var.unstack().plot(kind='bar', figsize=(35, 10), stacked=False, color=['red', 'blue', 'green', 'yellow'])

    # 中文出现方法块的解决办法
    plt.rcParams['font.sans-serif'] = ['SimHei']

    # 中文字体设置
    plt.rcParams['axes.unicode_minus'] = False
    plt.legend()
    plt.tight_layout()
    plt.show()


def get_location(geocoding):
    from qunar.config import RESTAPI_KEY
    url = 'http://restapi.amap.com/v3/geocode/geo?key=' + str(RESTAPI_KEY) + '&address=' + str(geocoding)
    response = requests.get(url)
    if response.status_code == 200:
        answer = response.json()
        try:
            location = answer['geocodes'][0]['location']
        except Exception:
            location = 0
    return location


def draw_map():
    province_num['province'].apply(lambda x: get_location(x))
    city_num['city'].apply(lambda x: get_location(x))
    map = Map('省份景点销量热力图', title_color='#fff', title_pos='center', width=1200, height=600, background_color='#404a59')
    map.add('', province_num['province'], province_num['hot_num'], maptype='china', visual_range=[5000, 80000],
            is_visualmap=True,
            visual_text_color='#000', is_label_show=True)
    map.render(path='./static/省份景点销量热力图.static')


def draw_word_cloud():
    import re
    import jieba
    import numpy as np
    from wordcloud import WordCloud, STOPWORDS
    new_data = data.dropna(subset=['describe'])
    json_data = new_data['describe'].tolist()
    test_data = ''.join(json_data)

    # 去掉非中文
    pattern = '[^\u4e00-\u9fa5]*'
    final_text = re.sub(pattern, '', test_data)
    default_mode = jieba.cut(final_text)
    text = ' '.join(default_mode)
    alice_mask = np.array(Image.open(r'.\static\qq.jpg'))
    stop_words = set(STOPWORDS)
    font_name = path.join(r'D:\develop\python\spider\SimHei.ttf')

    # delete_word
    stop_words.add('delete_word')
    wc = WordCloud(
        # 设置字体，不指定就会出现乱码,这个字体文件需要下载
        font_path=font_name,
        background_color='white',
        max_words=2000,
        mask=alice_mask,
        stopwords=stop_words)

    # generate word cloud
    wc.generate(text)

    # store to file
    wc.to_file('.\static\词云.jpg')

    # show
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()


def main():
    draw_word_cloud()
    draw_bar()
    draw_level()
    draw_map()


if __name__ == '__main__':
    main()
