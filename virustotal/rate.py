from contextlib import contextmanager
from threading import Timer, Semaphore
from functools import wraps

def ratelimit(limit, every):
    def limitdecorator(fn):
        semaphore = Semaphore(limit)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            semaphore.acquire()
            result = fn(*args, **kwargs)
            Timer(every, semaphore.release).start()
            return result
        return wrapper
    return limitdecorator

@contextmanager
def ratelimiter(semaphore, releaseafter):
    semaphore.acquire()
    yield
    Timer(releaseafter, semaphore.release).start()

