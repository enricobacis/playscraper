from contextlib import contextmanager
from threading import Timer, Semaphore
from functools import wraps
from weakref import WeakSet


class Limiter():
    """Class used to limit the rate of something. See method wait."""

    def __init__(self, limit, every):
        """Initialize the limiter to limit/every requests."""
        self.semaphore = Semaphore(limit)
        self.timers = WeakSet()
        self.limit = limit
        self.every = every

    @contextmanager
    def wait(self):
        """Block until the rate is compliant. Use with with statement."""
        self.semaphore.acquire()
        yield
        timer = Timer(self.every, self.semaphore.release)
        self.timers.add(timer)
        timer.start()

    def __del__(self):
        """Cancel all the active timers."""
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

