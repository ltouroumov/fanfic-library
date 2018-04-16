import re
from bs4 import BeautifulSoup
from fanfic_library.adapter import BaseAdapter, AdapterException, registry
from fanfic_library.cache import http
from fanfic_library.data import Fanfic


@registry.add(r'^https://(www\.)?fanfiction\.net/')
class FanFictionAdapter(BaseAdapter):
    URL_PATTERN = re.compile(r'^(?P<normalized>https://www\.fanfiction\.net/s/(?P<id>\d+)(/1/(?P<slug>[^.]+))?).+$')

    def normalize_url(self, url):
        match = self.URL_PATTERN.match(url)
        if match:
            return match.group('normalized')
        else:
            raise AdapterException("URL cannot be normalized", url)

    def fetch_metadata(self):
        content = http.get(self.base_url)
        doc = BeautifulSoup(content, "html.parser")

        title = doc.select_one('div#profile_top b.xcontrast_txt').string.strip()

        return Fanfic(title=title, thread_url=self.base_url)
