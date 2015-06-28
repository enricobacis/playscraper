from contextlib import contextmanager
from threading import Timer, Semaphore
from functools import wraps
from weakref import WeakSet

class Limiter():
    def __init__(self, limit, every):
        self.semaphore = Semaphore(limit)
        self.timers = WeakSet()
        self.limit = limit
        self.every = every

    @contextmanager
    def wait(self):
        self.semaphore.acquire()
        yield
        timer = Timer(self.every, self.semaphore.release)
        self.timers.add(timer)
        timer.start()

    def __del__(self):
        for timer in self.timers:
            timer.cancel()


def ratelimit(limit, every):
    """Decorator to limit invocations. *limit* calls per *every* seconds."""
    def limitdecorator(fn):
        limiter = Limiter(limit, every)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with limiter.wait():
                return fn(*args, **kwargs)
        return wrapper
    return limitdecorator

