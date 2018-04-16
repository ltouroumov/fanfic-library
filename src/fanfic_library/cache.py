import os
import re
import requests
from os import path
from hashlib import md5


class HttpCache:
    def __init__(self):
        self.cache_dir = None
        self.hash_key = md5

    def setup(self, cache_dir):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def make_key(self, key_data):
        return md5(key_data.encode('utf-8')).hexdigest()

    def file_from_key(self, key):
        parts = re.findall(r'.{3}', key)
        file_path = path.join(self.cache_dir, *parts)
        print("File:", file_path)
        os.makedirs(path.dirname(file_path), exist_ok=True)
        return file_path

    def get(self, url, params=None, **kwargs):
        cache_key = self.make_key(url + repr(params))
        cache_file = self.file_from_key(cache_key)

        if path.exists(cache_file):
            with open(cache_file, mode="rb") as fd:
                return fd.read()
        else:
            res = requests.get(url, params, **kwargs)
            with open(cache_file, mode="wb+") as fd:
                fd.write(res.content)

            return res.content


http = HttpCache()


class ThreadCache:
    def __init__(self):
        self.cache_dir = None

    def setup(self, cache_dir):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def store_post(self, thread_id, post_id, contents):
        file_name = path.join(self.cache_dir, 'threads/%d/posts/%s.html' % (thread_id, post_id))
        print("Storing Post:", file_name)
        os.makedirs(path.dirname(file_name), exist_ok=True)
        with open(file_name, mode="w+") as fd:
            fd.write(contents)

    def fetch_post(self, thread_id, post_id):
        file_name = path.join(self.cache_dir, 'threads/%d/posts/%s.html' % (thread_id, post_id))
        print("Fetching Post:", file_name)
        if not path.exists(file_name):
            return None

        with open(file_name, mode="r") as fd:
            return fd.read()


thread = ThreadCache()
