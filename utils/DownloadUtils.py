import requests
from tqdm import tqdm


def download_pic(http, path, p, headers=None):  # 下载pic
    if headers is None:
        headers = []

    r = requests.get(http, headers=headers, stream=True)
    content_size = int(r.headers['Content-Length'])

    with open(f'{path}/{p}.jpg', 'wb') as f:
        for data in tqdm(
                iterable=r.iter_content(1),
                total=content_size,
                unit='byte',
                desc='下载中'):
            f.write(data)


def download_pic_without_hualihushao(http, path, p, headers=None):  # 下载pic
    if headers is None:
        headers = []

    r = requests.get(http, headers=headers)
    with open(f'{path}/{p}.jpg', 'wb') as f:
        f.write(r.content)
