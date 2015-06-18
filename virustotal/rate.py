from contextlib import contextmanager
from threading import Semaphore, Timer

def ratelimit(limit, every):
    def limitdecorator(fn):
        semaphore = Semaphore(limit)
        def _fn(*args, **kwargs):
            semaphore.acquire()
            result = fn(*args, **kwargs)
            Timer(every, semaphore.release).start()
            return result
        return _fn
    return limitdecorator

@contextmanager
def ratelimiter(semaphore, releaseafter):
    semaphore.acquire()
    yield
    Timer(releaseafter, semaphore.release).start()

