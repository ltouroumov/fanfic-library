import time
from pprint import pprint

import re
from bs4 import BeautifulSoup
from fanfic_library.adapter import BaseAdapter, AdapterException, registry
from fanfic_library.cache import http, thread
from fanfic_library.data import Fanfic, Threadmark


@registry.add(r'^https://(www\.)?fanfiction\.net/')
class FanFictionAdapter(BaseAdapter):
    URL_PATTERN = re.compile(r'^(?P<normalized>https://www\.fanfiction\.net/s/(?P<id>\d+)/)(1/(?P<slug>[^.]+))?.*$')

    def normalize_url(self, url):
        match = self.URL_PATTERN.match(url)
        if match:
            return match.group('normalized')
        else:
            raise AdapterException("URL cannot be normalized", url)

    def extract_url(self, *groups):
        match = self.URL_PATTERN.match(self.base_url)
        if match:
            return match.group(*groups)
        else:
            raise AdapterException("URL cannot be normalized", self.base_url)

    def fetch_metadata(self):
        content = http.get(self.base_url)
        doc = BeautifulSoup(content, "html.parser")

        fic_id = self.extract_url('id')

        profile_top = doc.select_one('div#profile_top')

        title = profile_top.select_one('b.xcontrast_txt').string.strip()
        author = profile_top.select_one('a.xcontrast_txt').string.strip()
        summary = profile_top.select_one('div.xcontrast_txt').string.strip()

        meta_txt = profile_top.select_one('span.xgray').get_text()
        rating, language, categories, characters, chapters, wordcount, *rest = [item.strip() for item in meta_txt.split('-')]

        return Fanfic(thread_id=fic_id,
                      thread_type='fanfiction.net',
                      title=title,
                      author=author,
                      words=parse_wordcount(wordcount),
                      tags=categories,
                      language=language,
                      status='Complete' if 'Complete' in rest else None,
                      summary=summary,
                      thread_url=self.base_url)

    def fetch_threadmarks(self, fanfic):
        content = http.get(self.base_url)
        doc = BeautifulSoup(content, 'html5lib')

        chapters = doc.select_one('#chap_select').select('option')
        return [Threadmark(post_id=int(el['value']),
                           fanfic_id=fanfic.id,
                           title=el.string.strip(),
                           words=0)
                for el in chapters]

    def fetch_chapters(self, fanfic):
        threadmark_count = len(fanfic.threadmarks)
        for chapter_num in range(1, threadmark_count + 1):
            chapter_url = "%s%d/" % (self.base_url, chapter_num)
            print("Fetch Chapter ...", chapter_num, chapter_url)
            content = http.get(chapter_url)
            doc = BeautifulSoup(content, "html5lib")
            story_text = doc.select_one('div.storytext')
            thread.store_post(fanfic.thread_key, chapter_num, story_text.prettify())

            time.sleep(1)

    def get_content(self, thread_key, post_id):
        return thread.fetch_post(thread_key, post_id)


def parse_wordcount(wordcount):
    the_number = wordcount.split(': ')[1]
    the_int = re.sub(r'[^0-9]+', '', the_number)
    return int(the_int)

