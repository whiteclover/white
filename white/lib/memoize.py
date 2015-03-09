#!/usr/bin/env python
# 2015 Copyright (C) White
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from time import time, sleep
from collections import OrderedDict
from itertools import islice
from contextlib import contextmanager
from functools import wraps
from threading import RLock, Thread


class UnknowCacheType(Exception): pass

def memoize(type='memoize', *a, **kw):
    def _memoize(f):
        if type == 'lra':
            cache_limit = kw.get('cache_limt', 1000)
            cache = LRACache(f, cache_limit)
        elif type == 'memoize':
            lifetime = kw.get('lifetime', 300)
            cache = MemoizeCache(f, lifetime)
        elif type== 'lru':
            cache = LRUCache(f, *a, **kw)
        else:
            raise UnKnowCacheType('Unknow cache type %s' %(type))

        _memoize_mgr.add(cache)

        f.cache = cache
        _memoized = wraps(f)(lambda *args, **kwargs: cache(*args, **kwargs))
        _memoized.cache = cache
        return _memoized
 
    return _memoize


class MemozieMananger(object):

    def __init__(self):
        self.caches = []
        self.empty_cache_worker = None

    def add(self, cache):
        if isinstance(cache, LRUCache) and cache.cache.thread_clear:
            if not self.empty_cache_worker:
                self.empty_cache_worker = EmptyCacheWorker()
                self.empty_cache_worker.ready = True
                self.empty_cache_worker.start()
            self.empty_cache_worker.add(cache.cache)
        self.caches.append(cache)


_memoize_mgr = MemozieMananger()


class CacheNullValue(object):
    pass
 
_Null = CacheNullValue()
 

class LRACache(object):
 
    def __init__(self, callback, cache_limit=1000):
        self._cache = {}
        self._queue = []
        self.callback = callback
        self.cache_limit = cache_limit
        self._lock = RLock()
        self.__name__ = self.callback.__name__
 
    def __getitem__(self, name):
        with self._lock:
            return self._cache.get(name, _Null)
    get = __getitem__
 
    def __setitem__(self, name, value):
        with self._lock:
            if len(self._queue) >= self.cache_limit:
                del self._cache[self._queue.pop(0)]
            self._queue.append(name)
            self._cache[name] = value
    set = __setitem__

    def __callback__(self, *args, **kwargs):
        key = repr(args, kwargs)
        data = self.get(key)
        if data != _Null:
            return data
        data = self.callback(*args, **kwargs)
        self.set(key, data)
        return data

    def flush(self):
        self._cache = {}
        self._queue = []


class MemoizeCache(object):

    def __init__(self, callback, lifetime=5*60):
        self.callback = callback
        self.__name__ = self.callback.__name__
        self.memo = {}
        self.lifetime = lifetime
        self._lock = RLock()

    def clear(self, *args, **kw):
        key = repr((args, kw))
        self.memo.pop(key, None)

    def flush(self):
        with self._lock:
            self.memo = {}

    def __call__(self, *args, **kw):
        key = repr((args, kw))
        with self._lock:
            cache = self.memo.get(key, None)
            if cache is None:
                value = self.callback(*args, **kw)
                self.memo[key] = (value, time() + self.lifetime)
                return value
            else:
                if cache[1] < time():
                    value = self.callback(*args, **kw)
                    self.memo[key] = (value, time() + self.lifetime)
                    return value
                return cache[0]


class EmptyCacheWorker(Thread):
    daemon = True

    def __init__(self, peek_duration=60):
        self.caches = []
        self.ref = weakref.ref(cache)
        self.ready = False
        self.peek_duration = peek_duration
        Thread.__init__(self)

    def run(self):
        while self.ready:
            for c in self.caches:
                next_expire = c.cleanup()
                if (next_expire is None):
                    sleep(self.peek_duration)
                else:
                    sleep(next_expire+1)


def synchronized(func):
    """
    If the LRUCacheDict is concurrent, then we should lock in order to avoid
    conflicts with threading, or the ThreadTrigger.
    """
    def decorated(self, *args, **kwargs):
        if self.concurrent:
            with self._rlock:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    decorated.__name__ == func.__name__
    return decorated


class LRUCacheDict(object):
    """ A dictionary-like object, supporting LRU caching semantics.
    """
    def __init__(self, max_size=1024, lifetime=15*60, thread_clear=False, concurrent=False):
        self.max_size = max_size
        self.lifetime = lifetime

        self.__values = {}
        self.__expire_times = OrderedDict()
        self.__access_times = OrderedDict()
        self.thread_clear = thread_clear
        self.concurrent = concurrent or thread_clear
        if self.concurrent:
            self._rlock = RLock()
        self.thread_clear = thread_clear

    @synchronized
    def size(self):
        return len(self.__values)

    @synchronized
    def flush(self):
        """
        Flush the dict.
        """
        self.__values.clear()
        self.__expire_times.clear()
        self.__access_times.clear()

    @synchronized
    def  __contains__(self, key):
        """
        This method should almost NEVER be used. The reason is that between the time
        has_key is called, and the key is accessed, the key might vanish.
        You should ALWAYS use a try: ... except KeyError: ... block.
        """
        return self.__values.has_key(key)

    @synchronized
    def __setitem__(self, key, value):
        t = int(time())
        self.__delete__(key)
        self.__values[key] = value
        self.__access_times[key] = t
        self.__expire_times[key] = t + self.lifetime
        self.cleanup()

    @synchronized
    def __getitem__(self, key):
        t = int(time())
        del self.__access_times[key]
        self.__access_times[key] = t
        self.cleanup()
        return self.__values[key]

    @synchronized
    def __delete__(self, key):
        if key in self.__values:
            del self.__values[key]
            del self.__expire_times[key]
            del self.__access_times[key]

    clear = __delete__

    @synchronized
    def cleanup(self):
        if self.lifetime is None:
            return None
        t = int(time())
        #Delete expired
        next_expire = None
        for k in self.__expire_times.iterkeys():
            if self.__expire_times[k] < t:
                self.__delete__(k)
            else:
                next_expire = self.__expire_times[k]
                break

        #If we have more than self.max_size items, delete the oldest
        while (len(self.__values) > self.max_size):
            for k in self.__access_times.iterkeys():
                self.__delete__(k)
                break
        if not (next_expire is None):
            return next_expire - t
        else:
            return None

class LRUCache(object):
    """
    A memoized function, backed by an LRU cache.

    """
    def __init__(self, callback, *arg, **kw):

        self.cache = LRUCacheDict(*args, **kw)
        self.callback = callback
        self.__name__ = self.callback.__name__

    def __call__(self, *args, **kwargs):
        key = repr((args, kwargs))
        try:
            return self.cache[key]
        except KeyError:
            value = self.callback(*args, **kwargs)
            self.cache[key] = value
            return value

    def clear(self, key):
        self.cache.clear(key)

    def flush(self):
        self.cache.flush()