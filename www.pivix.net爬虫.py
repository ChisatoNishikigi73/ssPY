import json
import os

import requests
import lxml
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

from utils.DownloadUtils import download_pic, download_pic_without_hualihushao

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
    'Cookie': 'first_visit_datetime_pc=2022-05-08+16:48:57; p_ab_id=0; p_ab_id_2=7; p_ab_d_id=1116159261; yuid_b=OHGGVWY; privacy_policy_notification=0; adr_id=ftBSrPBkeYAMZgKjFrS862op0o4DgcQF6o231s6mSvXJPcTP; login_ever=yes; __utmz=235335808.1653750096.3.2.utmcsr=accounts.pixiv.net|utmccn=(referral)|utmcmd=referral|utmcct=/; cto_bundle=5Kklbl9VVDhUQlhGN0Z4VnVkM3pKaHdxalc3cmMlMkZCYjhtVllRbDVHaWtQbXE5M3B3aUJ0S2tmSGVjY1VVeVk3ZEk1QVYyWkp5ajhkTTM5ZGwzSXNCNEVCUlZJJTJGNlUxJTJCY1RZdFh5WnljbjNiN1JvU1ZES2JYZlN1aTlva3RwVk9zSm9jRWpGMWRXa29HbTdqV1IyQ29aOXBNaUElM0QlM0Q; __utmc=235335808; a_type=1; __utmv=235335808.|2=login ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=82169731=1^9=p_ab_id=0=1^10=p_ab_id_2=7=1^11=lang=zh=1; __utma=235335808.1226528258.1651996155.1658312947.1658312961.5; _ga=GA1.2.1226528258.1651996155; _ga_75BBYNYN9J=GS1.1.1658318869.2.1.1658320344.0; device_token=60a02e91e9471ae7ac56fde4dd827ce0; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; p_b_type=1; PHPSESSID=88138202_guW2QV5JWKbpUUXa6DPqg4h3nQTvKhnn; privacy_policy_agreement=5; c_type=22; b_type=0; __cf_bm=WlbS55t2WIDT.DY4xCO0RAIVSlCz52kWfkPhEpof0NU-1670131410-0-AXwVRRb/V6SydxTC7Squ61uQpQrn4TAm1ofdbmZoj5Fkg4dHyNehhYvxqvgHxvFSkBIUpwwU0/rnIqPGDkJMep4AypZefFo0FqLNie5CeMV2r6BWBNb0UYDeXY6AL5wusymdQ0452AcFDgixM5Cd3yNlVsgUvINt/WHve/5H27GLUU62xsETcGW8WF7+8HSMEvdnNbaDtCI5gsmBYccMpuU=; tag_view_ranking=vm3O8ATOGG~bL1ApaFBTu~Jxg8TkZQdK~RTJMXD26Ak~ZNRc-RnkNl~nWC-P2-9TI~q1r4Vd8vYK~zyKU3Q5L4C~8buMDtT-ku~j3leh4reoN~E6USWSAVMi~Ie2c51_4Sp~EA1nr9Hm18~PiKFMvIHS1~wC-YDaMscU~a7FYtDkb3F~wioq3KHpEK~9QhWZjeOmv~U9A9K0M8Oi~bqWQiQeNku~CRliPr1uKR~YJa1AYRvMw~DxtiQJj6de~vuzltsubQd~KvAGITxIxH~98c-9jH-Jp~dDVC9t_E1h~lH5YZxnbfC~dUhrZMpRPB~5H5jwYRKk2~QZh6FpjOHZ~Gcv5xjGZY3~d_iiHeHbdZ~zZSmJjkoF7~4ZEPYJhfGu~Mg6bq-SpX8~wBkXLfToxH~jMzRcTuF76~Lt-oEicbBr~jpIZPQ502H~Pk1xsLC9nL~pac41t5DOn~xx7VVwZNwa~IsmCxf13RP~K4vd3ajDHN~Ib0YGS-7FI~gHhGuI3hqJ~YGP_o2g7RI~Qa2ijP_TT3~8e-OBkgs0n~HY55MqmzzQ~MSNRmMUDgC~sOHNr0eXHD',
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
    #     str(raw_json).replace("'", '"').replace("False", "false").replace('True', 'true').replace('None', '_json[""]'))

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
        meta = get_metadata(pic_paths[a], pic_ids[a])
        inf = get_web_information(pic_ids[a], meta)

        t_path = str(inf.get('information').get('alt'))
        t_path = t_path.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_') \
            .replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        t_path = path + '/' + str(inf.get('information').get('userName')) + '/' + t_path

        if os.path.exists(t_path):
            print(f'({pic_ids[a]})文件夹已存在，已自动跳过，如图片无法打开请删除重新下载')
        else:
            os.mkdir(t_path)
            page = int(inf.get('basic_information').get('pageCount'))
            dl = get_download_list(str(inf.get('urls').get('original')), page)
            b = 0
            while b < page:
                print(
                    f"({pic_ids[a]})正在下载{inf.get('information').get('userName')}->"
                    f"{inf.get('information').get('alt')}({b}/{page})"
                )
                p_name = f"{inf.get('information').get('alt')}-{b+1}"
                p_name = p_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?','_')\
                    .replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

                download_pic(dl[b], t_path, p_name, headers)
                b = b + 1

            write_information(t_path, inf)
            if do_write_metadata:
                write_metadata(t_path, meta)

        a = a + 1


def mode_tag():
    print('唔。没写好。。。')


def main(use_list=False, mode='', value="209263", do_write_metadata=False):
    if mode == 'author':
        mode_author(int(value), do_write_metadata)
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
    main(use_list=False, mode="author", value="19037720", do_write_metadata=True)
