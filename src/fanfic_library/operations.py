import itertools
from pprint import pprint

from fanfic_library import utils
from fanfic_library.adapter import create_adapter
from fanfic_library.data import session, Fanfic


def create_from_thread_url(thread_url):
    adapter = create_adapter(thread_url)

    canonical_url = adapter.normalize_url(thread_url)

    result = session.query(Fanfic).filter(Fanfic.thread_url == canonical_url).first()
    if result:
        update_metadata(result)
        return False, result
    else:
        fanfic = adapter.fetch_metadata()
        session.add(fanfic)
        session.commit()
        word_count = update_threadmarks(adapter, fanfic)
        fanfic.words = utils.or_else(word_count, fanfic.words)
        session.commit()

        return True, fanfic


def update_metadata(fanfic):
    adapter = create_adapter(fanfic.thread_url)
    cur_fanfic = adapter.fetch_metadata()
    fanfic.update_with(cur_fanfic)
    word_count = update_threadmarks(adapter, fanfic)
    fanfic.words = utils.or_else(word_count, fanfic.words)
    session.commit()


def update_threadmarks(adapter, fanfic):
    old_threadmarks = utils.make_ordered_dict(fanfic.threadmarks, key=lambda tm: tm.post_id)
    cur_threadmarks = adapter.fetch_threadmarks(fanfic)
    new_threadmarks = []

    for cur_tm in cur_threadmarks:
        old_tm = old_threadmarks.get(cur_tm.post_id, None)
        if old_tm is None:
            new_threadmarks.append(cur_tm)
        elif hash(cur_tm) != hash(old_tm):
            old_tm.update_with(cur_tm)

    session.add_all(new_threadmarks)

    return sum(tm.words for tm in itertools.chain(old_threadmarks.values(), new_threadmarks))


def fetch_chapters(fanfic):
    adapter = create_adapter(fanfic.thread_url)
    adapter.fetch_chapters(fanfic)
