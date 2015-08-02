from contextlib import contextmanager
from threading import Timer, Semaphore
from functools import wraps

def __daemonic_timer(delay, fn):
    """Start a daemon timer that is killed if the program ends"""
    timer = Timer(delay, fn)
    timer.setDaemon(True)
    timer.start()

def ratelimit(limit, every):
    """Decorator to limit invocations. *limit* calls per *every* seconds."""
    def limitdecorator(fn):
        semaphore = Semaphore(limit)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            semaphore.acquire()
            result = fn(*args, **kwargs)
            __daemonic_timer(every, semaphore.release)
            return result
        return wrapper
    return limitdecorator

@contextmanager
def ratelimiter(semaphore, releaseafter):
    """Acquires the semaphore, executes user part and starts the timer for
       releasing the semaphore. Use it with with statement."""
    semaphore.acquire()
    yield
    __daemonic_timer(releaseafter, semaphore.release)

