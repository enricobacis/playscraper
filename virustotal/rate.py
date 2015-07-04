from contextlib import contextmanager
from threading import Timer, Semaphore
from functools import wraps
from weakref import WeakSet


class Limiter():
    """Class used to limit the rate of something. See method wait."""

    def __init__(self, limit, every):
        """Initialize the limiter to limit/every requests."""
        self._semaphore = Semaphore(limit)
        self._timers = WeakSet()
        self._limit = limit
        self._every = every

    @contextmanager
    def wait(self):
        """Block until the rate is compliant. Use with with statement."""
        self._semaphore.acquire()
        yield
        timer = Timer(self._every, self._semaphore.release)
        self._timers.add(timer)
        timer.start()

    def __del__(self):
        """Cancel all the active timers."""
        for timer in self._timers:
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

