import json
import os

import requests
import lxml
from bs4 import BeautifulSoup

from utils.DownloadUtils import download_pic

# 看我看我

# 请先按照以下几步设置基本参数
# 1，在23行填写您的pivix cookie
# 2，在28行填写保存图片的目录
# 3，设置275行参数
# 4，期待吧期待吧...~

headers = {
    'Referer': 'https://www.pixiv.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
    'Cookie': '',
    'accept-language': 'ja-JP,jp;q=0.9'
}

pyid = 3
path = ""


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


def get_download_list(url, page):  # 获取下载队列 TODO:make it better
    a = 0
    reg = []
    while a < page:
        reg.append(url.replace('p0', f'p{a}'))
        a = a + 1

    return reg


def write_information(path, inf):  # 快速浏览信息
    with open(path + '/information.txt', 'w+') as f:
        inf_format = json.dumps(inf, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        f.write(str(inf_format))


def write_metadata(path, inf):  # 储存元数据，方便管理
    with open(path + '/metadata.txt', 'w+') as f:
        inf_format = json.dumps(inf, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        f.write(str(inf_format))


def get_metadata(http_path, _id):
    raw_http = requests.get(http_path, headers=headers)
    soup = BeautifulSoup(raw_http.text, 'lxml')
    raw_data = soup.find(attrs={"id": "meta-preload-data"})['content']

    raw_json = json.loads(raw_data)
    # print(
    # str(raw_json).replace("'", '"').replace("False", "false").replace('True', 'true').replace('None', '_json[""]'))

    _json = raw_json["illust"][_id]
    return _json


def get_web_information(_id, _json):  # 获取网页信息

    _tags = _json["tags"]
    _meta = _json["extraData"]["meta"]
    _urls = _json["urls"]

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

    inf = {
        'py_meta': {
            'pyid': pyid,
        },
        'basic_information': {
            'id': _id,
            "title": _json["title"],
            "authorName": _json["userName"],
            "description": _json["description"],
            "createDate": _json["createDate"],
            "alt": _json["alt"],
            "pageCount": _json["pageCount"],
        },
        'meta': {
            "title": _meta["title"],
            "authorName": _json["userName"],
            "description": _meta["description"],
            "canonical": _meta["canonical"],
            "descriptionHeader": _meta["descriptionHeader"]
        },
        'information': {
            "illustId": _json["illustId"],
            "illustTitle": _json["illustTitle"],
            "illustComment": _json["illustComment"],
            "id": _json["id"],
            "title": _json["title"],
            "description": _json["description"],
            "illustType": _json["illustType"],
            "createDate": _json["createDate"],
            "uploadDate": _json["uploadDate"],
            "restrict": _json["restrict"],
            "xRestrict": _json["xRestrict"],
            "sl": _json["sl"],
            "alt": _json["alt"],
            "userId": _json["userId"],
            "userName": _json["userName"],
            "userAccount": _json["userAccount"],
            "likeData": _json["likeData"],
            "width": _json["width"],
            "height": _json["height"],
            "pageCount": _json["pageCount"],
            "bookmarkCount": _json["bookmarkCount"],
            "likeCount": _json["likeCount"],
            "commentCount": _json["commentCount"],
            "responseCount": _json["responseCount"],
            "viewCount": _json["viewCount"],
            "bookStyle": _json["bookStyle"],
            "isHowto": _json["isHowto"],
            "isOriginal": _json["isOriginal"],
            "imageResponseCount": _json["imageResponseCount"],
            "pollData": _json["pollData"],
            "seriesNavData": _json["seriesNavData"],
            "descriptionBoothId": _json["descriptionBoothId"],
            "descriptionYoutubeId": _json["descriptionYoutubeId"],
            "comicPromotion": _json["comicPromotion"],
            "fanboxPromotion": _json["fanboxPromotion"],
            "isBookmarkable": _json["isBookmarkable"],
            "bookmarkData": _json["bookmarkData"],
            "contestData": _json["contestData"],
            "isUnlisted": _json["isUnlisted"],
            "request": _json["request"],
            "commentOff": _json["commentOff"],
            "aiType": _json["aiType"]
        },
        'urls': {
            "original": _urls["original"]
        }
    }
    return inf


def mode_author(author_id, do_write_metadata):
    raw_http = requests.get(f"https://www.pixiv.net/ajax/user/{author_id}/profile/all", headers=headers)

    # 取得画师的所有插图id与链接
    artworks_paths = []
    data = json.loads(raw_http.text)
    if data['error']:
        print('未找到用户')
        return
    artworks_ids = list(data['body']['illusts'])
    for id in artworks_ids:
        artworks_paths.append("https://www.pixiv.net/artworks/" + id)

    print(f"已找到该用户下的{len(artworks_ids)}张插图（漫画暂时未计入内）")
    temp = requests.get(f'https://www.pixiv.net/users/{author_id}', headers=headers)

    soup = BeautifulSoup(temp.text, 'lxml')
    temp_author_name = soup.find(attrs={"property": "twitter:title"})['content']
    if not os.path.exists(path + '/' + temp_author_name):
        os.mkdir(path + '/' + temp_author_name)
    mode_artworks(artworks_ids, do_write_metadata, is_in_func=True, artworks_path_s=artworks_paths)


def mode_tag():
    print('唔。没写好。。。')


def mode_artworks(artworks_id_s, do_write_metadata, is_in_func=False, artworks_path_s=None):
    if artworks_path_s is None:
        artworks_path_s = []

    if not is_in_func:
        artworks_path = "https://www.pixiv.net/artworks/" + artworks_id_s[0]
        artworks_ids = [artworks_id_s[0]]
        artworks_paths = [artworks_path]
    else:
        artworks_ids = artworks_id_s
        artworks_paths = artworks_path_s

    # 爬取信息并下载
    a = 0
    while a < len(artworks_ids):
        meta = get_metadata(artworks_paths[a], artworks_ids[a])
        inf = get_web_information(artworks_ids[a], meta)

        t_path = str(inf.get('information').get('alt'))
        t_path = t_path.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_') \
            .replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        if not is_in_func:
            t_path = path + '/' + t_path
        else:
            t_path = path + '/' + str(inf.get('information').get('userName')) + '/' + t_path

        if os.path.exists(t_path):
            print(f'({artworks_ids[a]})文件夹已存在，已自动跳过，如图片无法打开请删除重新下载')
        else:
            os.mkdir(t_path)
            page = int(inf.get('basic_information').get('pageCount'))
            dl = get_download_list(str(inf.get('urls').get('original')), page)
            b = 0
            while b < page:
                print(
                    f"({artworks_ids[a]})正在下载{inf.get('information').get('userName')}->"
                    f"{inf.get('information').get('alt')}({b + 1}/{page})"
                )
                p_name = f"{inf.get('information').get('alt')}-{b + 1}"
                p_name = p_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?',
                                                                                                                 '_') \
                    .replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

                download_pic(dl[b], t_path, p_name, headers)
                b = b + 1

            write_information(t_path, inf)
            if do_write_metadata:
                write_metadata(t_path, meta)

        a = a + 1


def main(use_list=False, mode='', value=None, do_write_metadata=False):
    if value is None:
        value = []
    if mode == 'author':
        mode_author(int(value[0]), do_write_metadata)
    elif mode == 'tag':
        mode_tag()
    elif mode == 'artwork':
        mode_artworks(value, do_write_metadata=True)


def getJsonKey(json_data):
    key_list = []
    # 递归获取字典中所有key
    for key in json_data.keys():
        if type(json_data[key]) == type({}):
            getJsonKey(json_data[key])
        key_list.append(key)
    return key_list


if __name__ == '__main__':
    main(use_list=False, mode="", value=[""], do_write_metadata=True)

# use_list 使用已有的下载列表
# mode 爬虫模式 artwork->单个作品 author->用户的所有作品 tag->标签（暂无）
# do_write_metadata 是否保存metadata（便于二次整理）
