import json
import random
from _md5 import md5

import time
from lxml import etree

import click
import os
import requests

headers = {
    "Origin": "https://www.instagram.com/",
    "Referer": "https://www.instagram.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Host": "www.instagram.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, sdch, br",
    "accept-language": "zh-CN,zh;q=0.8",
    "X-Instragram-AJAX": "1",
    "X-Requested-With": "XMLHttpRequest",
    "Upgrade-Insecure-Requests": "1",
}

BASE_URL = "https://www.instagram.com"

proxy = {'http': '127.0.0.1:1087', 'https': '127.0.0.1:1087'}


def spiders(query):
    folder = query.replace('.', '-')
    click.echo('开始')
    res = requests.session()

    if not os.path.exists('./images/%s' % folder):
        os.mkdir('./images/%s' % folder)

    new_imgs_url = []

    temp_url = BASE_URL + '/explore/tags/' + query + '/'
    headers.update({'Referer': temp_url})
    request = res.get(temp_url, headers=headers, proxies=proxy)
    html = etree.HTML(request.content.decode())
    all_a_tags = html.xpath('//script[@type="text/javascript"]/text()')
    for a_tag in all_a_tags:
        if a_tag.strip().startswith('window'):
            data = a_tag.split('= {')[1][:-1]
            js_data = json.loads('{' + data, encoding='utf-8')
            edges = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_top_posts"]["edges"]
            for edge in edges:
                new_imgs_url.append(edge["node"]["display_url"])
    translate(new_imgs_url, query)


def translate(new_imgs_url, path):
    download(path, new_imgs_url)


def download(path, urls):
    ss = requests.session()
    temp_url = BASE_URL + '/explore/tags/' + path + '/'
    folder = path.replace('.', '-')
    header = {
        "Referer": temp_url,
        "Origin": "https://www.instagram.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/60.0.3112.113 Safari/537.36",
        'Connection': 'keep-alive'
    }
    pp = ss.get(temp_url, headers=header, proxies=proxy)
    try:
        count = 0
        all_count = len(urls)
        while count < all_count:
            url = urls[count]
            if '\n' in url:
                url = urls[count][:-1]
            file_md5 = md5()
            file_md5.update(url.encode('utf-8'))
            file_name = file_md5.hexdigest()
            if os.path.exists('./images/%s/%s.jpg' % (folder, file_name)):
                count += 1
                continue
            time.sleep(2)
            res = ss.get(url, proxies=proxy)
            if res.status_code == 200:
                with open('./images/%s/%s.jpg' % (folder, file_name), mode='wb') as f:
                    f.write(res.content)
                    count += 1
            else:
                ss.close()
                ss = requests.session()
                pp = ss.get(temp_url, headers=header, proxies=proxy)
            if count % 100 == random.randrange(20, 50):
                ss.close()
                ss = requests.session()
                pp = ss.get(temp_url, headers=header, proxies=proxy)
        click.echo('完成!')
    except Exception as e:
        raise e
    finally:
        ss.close()


if __name__ == "__main__":
    input_ins = click.prompt("请输入tag", None)
    spiders(input_ins)