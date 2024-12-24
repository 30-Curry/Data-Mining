#-*-coding:utf8-*-
import requests

parmas = {  # 传参是数据
    'type': 'movie',
    'tag': '热门',
    'page_limit': 50,
    'page_start': 0,
}

header = {  # 请求头
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}

url = 'https://movie.douban.com/j/search_subjects'  # 请求地址
result = requests.get(url, headers=header, params=parmas)  # 传参并发起请求
result.encoding = result.raise_for_status()  # 设置编码格式
html = result.text  # 获取数据的文本格式
print(html)

html = result.json()
data_all=html['subjects']
for data in data_all:
    print('{}({})'.format(data['title'],data['url']))
