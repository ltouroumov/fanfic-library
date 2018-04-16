import re
import importlib


class AdapterException(BaseException):
    pass


class BaseAdapter:
    def __init__(self, base_url):
        self.base_url = self.normalize_url(base_url)

    def normalize_url(self, url):
        raise NotImplementedError()

    def fetch_metadata(self):
        raise NotImplementedError()

    def fetch_threadmarks(self, fanfic):
        raise NotImplementedError()

    def fetch_chapters(self, fanfic):
        raise NotImplementedError()

    def get_content(self, fanfic_id, post_id):
        raise NotImplementedError()


class AdapterRegistry:
    def __init__(self):
        self.adapters = {}
        self.patterns = []

    def add(self, *match_patterns):
        def decorator(cls):
            self.adapters[cls.__name__] = cls
            self.patterns += [
                (re.compile(pattern), cls.__name__)
                for pattern in match_patterns
            ]

            return cls

        return decorator

    def find(self, url):
        for pattern, key in self.patterns:
            if pattern.match(url):
                adapter = self.adapters[key]
                return adapter(url)


registry = AdapterRegistry()


default_adapters = (
    'fanfic_library.adapter.xenforo',
    'fanfic_library.adapter.ffn',
)


def create_adapter(thread_url):
    return registry.find(thread_url)


def load_all(extra_adapters=None):
    if extra_adapters:
        all_adapters = default_adapters + extra_adapters
    else:
        all_adapters = default_adapters

    for adapter in all_adapters:
        importlib.import_module(adapter)
