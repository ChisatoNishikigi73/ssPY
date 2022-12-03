import os

import requests
import lxml
from bs4 import BeautifulSoup
from textwrap import dedent
import re

start = 583
end = 8623
raw_http = "https://www.pandadiu.com"
pyid = 1
d = "/Users/kawaaanime/Documents/虚拟磁盘/爬虫资源/www.pandadiu.com爬虫"
_type = 3


def get_raw_code(http):  # 获取网站源码
    return requests.get(http)


def list_useful_pages():  # 额外函数，可列出所有可用的网站
    ds = d + '/useful_pages.txt'
    with open(ds, 'a') as f:
        for i in range(0, 54973):

            page = raw_http + "/" + str(i) + ".html"

            if is_used_pages(get_raw_code(page), 0):
                print(f'OK: {i}')
                f.write(f'OK: {i}\n')
            else:
                print(f'[ERROR]: {i}')
                f.write(f'[ERROR]: {i}\n')


def is_used_pages(raw_code, a):  # 判断是否是可用的网页
    try:
        soup = BeautifulSoup(raw_code.text, 'lxml')
        data = soup.select(
            'body > div > div.content.guery')
        sta = data[0].get_text()
        if soup == '该信息不存在' or sta == '您要查看的信息不存在或者还未通过审批！' or sta == '您的会话已过期，请重新登录。' or sta == 'templates/default/content/show3.html is not exists!':
            print(f"[{a}] Page: [Lost:[{sta}]]")
            return False
        else:
            print(f"[{a}] Page: [Get]")
            return True
    except:
        print(f"[{a}] Page: [Get]")
        return True


def get_download_list(raw_code):  # 获取下载队列
    soup = BeautifulSoup(raw_code.text, 'lxml')
    data = soup.select(
        'body > main > div.show_main > div.show_cos > div.con')

    if len(data) == 0:
        return []

    res = re.compile('<img src="(.+?)" ', re.S)  # 运用正则表达式过滤出图片路径地址
    reg = res.findall(str(data[0]))  # 匹配网页进行搜索出图片地址数组

    return reg


def write_information(path, imf):  # 储存元数据，方便管理
    with open(path + '/information.txt', 'w+') as f:
        f.write(str(imf))


def get_web_information(raw_code, id):  # 获取网页信息
    soup = BeautifulSoup(raw_code.text, 'lxml')

    # pages
    inf_pages = len(get_download_list(raw_code))
    if not inf_pages:
        return []

    # inf_date
    data = soup.select(
        'body > main > div.show_main > div.show_cos > div.title > div > span:nth-child(2)')
    inf_date = data[0].get_text().split('发布日期：')[1]

    # inf_id
    inf_id = id.split('show-31-')[1].split('-1')[0]

    # inf_title
    data = soup.select(
        'body > main > div.show_main > div.show_cos > div.title > h1')

    inf_title = dedent(data[0].get_text())

    # inf_tags
    data = soup.select(
        'body > main > div.show_main > div.show_cos > div.footer > div.tag')

    res = re.compile('<a href="(.+?)/a>', re.S)  # 运用正则表达式过滤出图片路径地址
    reg = res.findall(str(data[0]))  # 匹配网页进行搜索出图片地址数组
    res = re.compile('k">(.+?)<', re.S)
    inf_tags = res.findall(str(data[0]))
    try:
        a = False
        b = 1
        while not a:
            data = soup.select(
                'body > main > div.show_main > div.show_cos > div.con')

            data = soup.select(
                f'p:nth-child({b})')
            print(data[0].get_text())
            if len(data) == 0:
                a = True
            else:
                b = b + 1
                inf_tags.append(data[0].get_text())
    except:
        inf_tags = inf_tags




    print(inf_tags)

    inf = {'site': raw_http,
           'page_site': raw_code.url,
           'date': inf_date,
           'pyid': str(pyid),
           'id': f'{inf_id}',
           'type': _type,
           'title': inf_title,
           'pages': str(inf_pages),
           'tags': str(inf_tags)}
    return inf


def download_pic(http, path, p):  # 下载
    r = requests.get(http)
    with open(f'{path}/{p}.jpg', 'wb') as f:
        f.write(r.content)


def main(use_list=False):
    for i in range(start, end + 1):
        id = f'show-31-{i}-1'
        page = f'{raw_http}/{id}.html'

        raw_code = get_raw_code(page)

        if use_list or (is_used_pages(raw_code, id)):
            imf = get_web_information(raw_code, id)
            if not imf:
                print(f'[{id}] Page: [None]')
                continue
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


if __name__ == '__main__':

    # get useful pages
    # list_useful_pages()

    # main
    main(use_list=False)
