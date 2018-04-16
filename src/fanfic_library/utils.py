from collections import OrderedDict


def make_ordered_dict(iterable, key):
    odict = OrderedDict()

    for elem in iterable:
        elem_key = key(elem)
        odict[elem_key] = elem

    return odict


def or_else(val1, val2):
    if val1:
        return val1
    else:
        return val2
