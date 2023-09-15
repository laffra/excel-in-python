cache = {}

def memoize(function):
    def inner(*args):
        try:
            value = cache[args[0]]
        except KeyError:
            value = cache[args[0]] = function(*args)
        return value
    return inner


def clear(key):
    try:
        del cache[key]
    except:
        pass