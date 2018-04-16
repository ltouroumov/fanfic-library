import math
import time
from collections import namedtuple
from datetime import datetime
from os import path
from hashlib import md5 as hash_func
from pprint import pprint

import requests
from bs4 import BeautifulSoup

CACHE_DIR = 'cache'

Threadmark = namedtuple('Threadmark',
                        field_names=['post_id', 'title', 'words', 'likes', 'author', 'publish_date'])


def fetch_cached(url, params=None, **kwargs):
    cache_key = hash_func((url + repr(params)).encode('utf-8')).hexdigest()
    cache_file = path.join(CACHE_DIR, cache_key)

    if path.exists(cache_file):
        with open(cache_file, mode="rb") as fd:
            return fd.read()
    else:
        res = requests.get(url, params, **kwargs)
        with open(cache_file, mode="wb+") as fd:
            fd.write(res.content)

        return res.content


def fetch_threadmarks(thread_url):
    threadmarks_url = "%s/threadmarks" % thread_url

    content = fetch_cached(threadmarks_url)
    doc = BeautifulSoup(content, "html.parser")

    threadmark_list = doc.select('div.threadmarkList ol li.threadmarkListItem')
    threadmarks = [Threadmark(post_id=el.a['data-previewurl'].split('/')[1],
                              title=el.a.string.strip(),
                              words=int(el['data-words']),
                              likes=int(el['data-likes']),
                              author=el['data-content-author'],
                              publish_date=datetime.fromtimestamp(int(el['data-content-date'])))
                   for el in threadmark_list]

    return threadmarks


def fetch_chapters(thread_url, threadmark_count):
    reader_url = "%s/reader" % thread_url
    page_count = int(math.ceil(threadmark_count / 10))

    for page in range(1, page_count + 1):
        print("Fetch Page ...", page)
        content = fetch_cached(reader_url, params={'page': page})
        doc = BeautifulSoup(content, "html.parser")
        post_list = doc.select('li.message.hasThreadmark')
        for post_el in post_list:
            post_id = post_el['id'].split('-')[1]
            print("Post:", post_id)
            post_content = post_el.find('article')

            with open('out/posts/%s.html' % post_id, mode="w+") as fd:
                fd.write(post_content.prettify())

        time.sleep(5)


def main():
    threads = [
        'https://forums.spacebattles.com/threads/harry-and-the-shipgirls-a-hp-kancolle-snippet-collection.413375',
        'https://forums.spacebattles.com/threads/harry-and-the-shipgirls-prisoner-of-shipping-a-hp-kancolle-snippet-collection.630637'
    ]

    threadmarks = fetch_threadmarks(threads[0])
    print("Threadmarks:", len(threadmarks))
    fetch_chapters(threads[0], len(threadmarks))


if __name__ == '__main__':
    main()
