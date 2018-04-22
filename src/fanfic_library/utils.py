from collections import OrderedDict


def make_ordered_dict(iterable, key):
    odict = OrderedDict()

    for elem in iterable:
        elem_key = key(elem)
        odict[elem_key] = elem

    return odict


def format_word_count(word_count):
    if word_count < 1000:
        return "%d" % word_count
    elif word_count < 10000:
        return "%.1f K" % (word_count / 1000)
    elif word_count < 1000000:
        return "%d K" % (word_count // 1000)
    else:
        return "%.2f M" % (word_count / 1000000)


def or_else(val1, val2):
    if val1:
        return val1
    else:
        return val2
