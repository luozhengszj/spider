import pandas as pd

from pyecharts import Bar

data = pd.read_csv(r'D:\develop\python\spider\tourist1.csv')
data.drop(['_id','more_url','describe'],axis=1,inplace=True)

# city       NaN
# describe   NaN
# hot_num    NaN
# image      NaN
# level      NaN
# more_url   NaN
# name       NaN
# price      NaN
# province   NaN

def draw_bar():
    bar_data = data.sort_values(by=['hot_num'],ascending=False)
    bar_data_y = bar_data[bar_data[u'hot_num']>1000][:30]['hot_num']
    bar_data_x = bar_data[bar_data[u'hot_num']>1000][:30]['name']+'('+bar_data[bar_data[u'hot_num']>1000][:30]['province']+')'
    bar = Bar("旅游热点TOP30", "")
    bar.add("热点", bar_data_x,bar_data_y)
    # bar.print_echarts_options() # 该行只为了打印配置项，方便调试时使用
    bar.render()

def draw_word_cloud():
    new_data =data.dropna(subset=['describe'])
    json = new_data['describe'].tolist()
    all_comment = ' '.join(json)
    print(all_comment)
    import re
    pattern = r'[^\w\s]'
    replace = ''
    all_comment = re.sub(pattern, replace, all_comment)
    all_comment = all_comment.lower()
    from collections import Counter
    word_list = all_comment.split(' ')
    wordCount_dict = Counter(word_list)
    print(wordCount_dict )

def main():
    draw_bar()

if __name__ == '__main__':
    main()