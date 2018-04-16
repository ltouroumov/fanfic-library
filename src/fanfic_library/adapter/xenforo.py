import math
import os
import re
import time
from datetime import datetime
from os import path

import requests
from bs4 import BeautifulSoup
from fanfic_library.adapter import BaseAdapter, AdapterException, registry
from fanfic_library.cache import http, thread
from fanfic_library.data import Fanfic, Threadmark


@registry.add(r'^https://forums.spacebattles.com/')
class XenForoAdapter(BaseAdapter):
    URL_PATTERN = re.compile(r'^(?P<normalized>https://forums\.(?P<domain>\w+)\.com/threads/(?P<slug>[^.]+)\.(?P<id>\d+)/).*$')

    def normalize_url(self, url):
        match = self.URL_PATTERN.match(url)
        if match:
            return match.group('normalized')
        else:
            raise AdapterException("URL cannot be normalized", url)

    def fetch_metadata(self):
        content = http.get(self.base_url)
        doc = BeautifulSoup(content, "html.parser")

        title = doc.find('h1').string.strip()

        return Fanfic(title=title, thread_url=self.base_url)

    def fetch_threadmarks(self, fanfic_id):
        threadmarks_url = "%sthreadmarks" % self.base_url

        print("Threadmarks URL:", threadmarks_url)

        content = http.get(threadmarks_url)
        doc = BeautifulSoup(content, "html.parser")

        threadmark_list = doc.select('div.threadmarkList ol li.threadmarkListItem')
        threadmarks = [Threadmark(post_id=el.a['data-previewurl'].split('/')[1],
                                  fanfic_id=fanfic_id,
                                  title=el.a.string.strip(),
                                  words=int(el['data-words']),
                                  likes=int(el['data-likes']),
                                  author=el['data-content-author'],
                                  published=datetime.fromtimestamp(int(el['data-content-date'])))
                       for el in threadmark_list]

        return threadmarks

    def fetch_chapters(self, thread_id, threadmark_count):
        reader_url = "%s/reader" % self.base_url
        page_count = int(math.ceil(threadmark_count / 10))

        for page in range(1, page_count + 1):
            print("Fetch Page ...", page)
            content = http.get(reader_url, params={'page': page})
            doc = BeautifulSoup(content, "html.parser")
            post_list = doc.select('li.message.hasThreadmark')
            for post_el in post_list:
                post_id = post_el['id'].split('-')[1]
                print("Post:", post_id)
                post_content = post_el.find('article')

                thread.store_post(thread_id, post_id, post_content.prettify())

            time.sleep(1)

    def get_content(self, fanfic_id, post_id):
        return thread.fetch_post(fanfic_id, post_id)

