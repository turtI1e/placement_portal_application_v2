from app import cache

def get_cached_or_set(key, func, timeout=300):
    value = cache.get(key)
    if value is None:
        value = func()
        cache.set(key, value, timeout=timeout)
    return value
