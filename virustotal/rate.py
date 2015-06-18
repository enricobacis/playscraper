from threading import Semaphore, Timer

def ratelimit(limit, every):
	def limitdecorator(fn):
		semaphore = Semaphore(limit)
		def _timeout():
			semaphore.release()
		def _fn(*args, **kwargs):
			semaphore.acquire()
			result = fn(*args, **kwargs)
			Timer(every, _timeout).start()
			return result
		return _fn
	return limitdecorator

