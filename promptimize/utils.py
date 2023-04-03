def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False
