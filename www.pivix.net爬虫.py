import json
import os

import requests
import lxml
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

from utils.DownloadUtils import download_pic

# 看我看我

# 请先按照以下几步设置基本参数
# 1，在24行填写您的pivix cookie
# 2，在29行填写保存图片的目录
# 3，设置206行参数
# 如果要按照用户id爬取图片：mode="author", value=画师的id
# 4，没了，还没做好

headers = {
    'Referer': 'https://www.pixiv.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
    'Cookie': '在这里填写cookie',
    'accept-language': 'ja-JP,jp;q=0.9'
}

pyid = 3
path = "C:/Users/lxr20/Pictures/Camera Roll"


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


def write_information(path, inf):  # 储存元数据，方便管理
    with open(path + '/metadata.txt', 'w+') as f:
        inf_format = json.dumps(inf, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        f.write(str(inf_format))


def get_web_information(http_path, _id):  # 获取网页信息
    raw_http = requests.get(http_path, headers=headers)
    soup = BeautifulSoup(raw_http.text, 'lxml')

    raw_data = soup.find(attrs={"id": "meta-preload-data"})['content']

    raw_json = json.loads(raw_data)

    _json = raw_json["illust"][_id]

    illust_id = _json["illustId"]
    illust_title = _json["illustTitle"]
    illust_comment = _json["illustComment"]
    __id = _json["id"]
    title = _json["title"]
    description = _json["description"]
    illust_type = _json["illustType"]
    create_date = _json["createDate"]
    upload_date = _json["uploadDate"]
    restrict = _json["restrict"]
    x_restrict = _json["xRestrict"]
    sl = _json["sl"]
    origin_pic_url = _json["urls"]["original"]

    _tags = _json["tags"]

    author_name = _json["userName"]
    author_account = _json["userAccount"]
    alt = _json["alt"]

    author_id = _tags["authorId"]

    # to get this fxxxxk tags i spend for 2hours!!!!!
    tags = []
    tags_translate = []
    for _tag in _tags["tags"]:
        _tag = str(_tag).replace("'", '"').replace("False", "false").replace("True", "true")
        _temp = json.loads(_tag)

        a = _temp["tag"]  # 原tag

        try:
            a_t = _temp["translation"]  # 首选语言翻译tag
            a_t = str(a_t).split("': '")[1].split("'}")[0]
            tags_translate.append(a_t)
        except:
            tags_translate = []

        tags.append(a)

    inf = {'site': raw_http.url,
           'pyid': pyid,
           'alt': alt,
           'author': author_name,
           'author_account': author_account,
           'author_id': author_id,
           'raw_id': _id,
           "illustId": illust_id,
           "illustTitle": illust_title,
           "illustComment": illust_comment,
           "id": __id,
           "title": title,
           "description": description,
           "illustType": illust_type,
           "createDate": create_date,
           "uploadDate": upload_date,
           "restrict": restrict,
           "xRestrict": x_restrict,
           "sl": sl,
           "origin_pic_url": origin_pic_url,
           "tags": tags,
           "tags_translate": tags_translate
           }
    return inf


def mode_author(author_id):
    raw_http = requests.get(f"https://www.pixiv.net/ajax/user/{author_id}/profile/all", headers=headers)

    # 取得画师的所有插图id与链接
    pic_paths = []
    data = json.loads(raw_http.text)
    pic_ids = list(data['body']['illusts'])
    for id in pic_ids:
        pic_paths.append("https://www.pixiv.net/artworks/" + id)

    print(f"已找到该用户下的{len(pic_ids)}张插图（漫画暂时未计入内）")
    temp = requests.get(f'https://www.pixiv.net/users/{author_id}', headers=headers)
    soup = BeautifulSoup(temp.text, 'lxml')
    temp_author_name = soup.find(attrs={"property": "twitter:title"})['content']
    if not os.path.exists(path + '/' + temp_author_name):
        os.mkdir(path + '/' + temp_author_name)

    # 爬取信息并下载
    a = 0
    while a < len(pic_ids):
        inf = get_web_information(pic_paths[a], pic_ids[a])

        t_path = inf.get('alt')
        t_path = t_path.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_') \
            .replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        t_path = path + '/' + inf.get('author') + '/' + t_path

        if os.path.exists(t_path):
            print(f'({pic_ids[a]})文件夹已存在，已自动跳过，如图片无法打开请删除重新下载')
        else:
            os.mkdir(t_path)

            print(f"正在下载{inf.get('author')}->{inf.get('alt')}")
            write_information(t_path, inf)

            download_pic(inf.get('origin_pic_url'), t_path, inf.get('alt'), headers)
        a = a + 1


def mode_tag():
    print('唔。没写好。。。')


def main(use_list=False, mode='', value="209263"):
    if mode == 'author':
        mode_author(int(value))
    if mode == 'tag':
        mode_tag()


def getJsonKey(json_data):
    key_list = []
    # 递归获取字典中所有key
    for key in json_data.keys():
        if type(json_data[key]) == type({}):
            getJsonKey(json_data[key])
        key_list.append(key)
    return key_list


if __name__ == '__main__':
    main(use_list=False, mode="author", value="author id")
