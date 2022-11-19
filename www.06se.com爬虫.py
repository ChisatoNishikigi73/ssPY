import os

import requests
import lxml
from bs4 import BeautifulSoup
from textwrap import dedent
import re

start = 35737
end = 54972
raw_http = "https://www.06se.com"
d = ""


def get_raw_code(http):  # 获取网站源码
    return requests.get(http)


def list_useful_pages():  # 额外函数，可列出所有可用的网站
    ds = d + '/useful_pages.txt'
    with open(ds, 'a') as f:
        for i in range(5829, 54973):

            page = raw_http + "/" + str(i) + ".html"

            if is_used_pages(get_raw_code(page)):
                print(f'OK: {i}')
                f.write(f'OK: {i}\n')
            else:
                print(f'[ERROR]: {i}')
                f.write(f'[ERROR]: {i}\n')


def is_used_pages(raw_code):  # 判断是否是可用的网页
    status_code = raw_code.status_code
    a = raw_code.text.split(raw_http + "/")[1].split(".html")[0]
    if 199 < status_code < 300:
        print(f"[{a}] Page: [Get]")
        return True
    else:
        print(f"[{a}] Page: [Lost:[{status_code}]]")
        return False


def get_download_list(raw_code):  # 获取下载队列
    soup = BeautifulSoup(raw_code.text, 'lxml')
    data = soup.select(
        'body > main > div > div > article > div.article-content > div.theme-box.wp-posts-content.limit-height > p')

    res = re.compile('data-src="(.+?)"', re.S)  # 运用正则表达式过滤出图片路径地址
    reg = res.findall(str(data[0]))  # 匹配网页进行搜索出图片地址数组
    reg = '+ '.join(reg) + "+ "

    res = re.compile(';url=(.+?)"+ ', re.S)  # 二次筛选
    reg = res.findall(str(data[0]))

    return reg


def write_information(path, imf):  # 储存元数据，方便管理
    with open(path + '/information.txt', 'w+') as f:
        f.write(str(imf))


def get_web_information(raw_code):  # 获取网页信息
    # pages
    inf_pages = len(get_download_list(raw_code))

    # inf_id
    inf_id = raw_code.text.split(raw_http + "/")[1].split(".html")[0]

    soup = BeautifulSoup(raw_code.text, 'lxml')
    data = soup.select(
        'body > main > div.content-wrap > div > article > div.article-header.theme-box.clearfix.relative > h1')

    # inf_title
    inf_title = dedent(data[0].get_text())

    # inf_tags
    soup = BeautifulSoup(raw_code.text, 'lxml')
    data = soup.select(
        'body > main > div.content-wrap > div > article > div.article-content > div.theme-box.article-tags')
    inf_tags = str(data[0].get_text().split("# ")).split('[')[1].split(']')[0]

    inf = {'id': inf_id,
           'title': inf_title,
           'pages': str(inf_pages),
           'tags': inf_tags}
    return inf


def download_pic(http, path, p):  # 下载
    r = requests.get(http)
    with open(f'{path}/{p}.jpg', 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    print("start")
    # get useful pages
    # list_useful_pages()

    # main
    for i in range(start, end + 1):
        page = raw_http + "/" + str(i) + ".html"
        raw_code = get_raw_code(page)
        if is_used_pages(raw_code):
            imf = get_web_information(raw_code)

            d_path = d + "/" + imf.get('title')
            os.mkdir(d_path)  # 创建文件夹

            write_information(d_path, imf)

            print('Id: ' + imf.get('id'))
            print('Title: ' + imf.get('title'))
            print('Pages: ' + imf.get('pages'))
            print('Tags: ' + imf.get('tags'))

            dl = get_download_list(raw_code)  # 获取下载列表

            num = 1
            for w in dl:
                print(f'Downloading:({imf.get("id")}/{end}){str(num)}/{imf.get("pages")}')
                download_pic(w, d_path, num)
                num = num + 1
