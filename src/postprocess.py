import time, threading, queue
import logging


def enqueue(processor, *args):
	global _task_queue
	# logging.debug("queueing %s with %s", processor, args)
	_task_queue.put( (processor, args) )

def _process_queue(queue):
	while True:
		processor, args = queue.get()
		logging.debug("calling %s with %d arguments: %s", processor, len(args), args)
		try:
			processor(*args)
		except:
			logging.exception("")
		queue.task_done()
		# logging.debug("processed 1 item, %d remain in queue", queue.qsize())

_task_queue = queue.Queue()
_processor = threading.Thread(target = _process_queue, name = 'PostProcessor', args = (_task_queue,))
_processor.daemon = True
_processor.start()
logging.info("started post-processing thread %s", _processor)
