from contextlib import contextmanager
from threading import Timer, Semaphore
from functools import wraps

def ratelimit(limit, every):
    """Decorator to limit invocations. *limit* calls per *every* seconds."""
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
    """Acquires the semaphore, executes user part and starts the timer for
       releasing the semaphore. Use it with with statement."""
    semaphore.acquire()
    yield
    Timer(releaseafter, semaphore.release).start()

