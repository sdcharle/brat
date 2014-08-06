"""
Just as an exercise, let's consider how this solution would look using processes instead of threads.
We do not want a new process started for each email that we need to send,
so instead we could use the Pool class from the multiprocessing module.
This class creates a specified number of processes (which are forks of the main process)
and all those processes wait to receive jobs to run, given to the pool via the apply_async method.
This could be an interesting approach for a busy site, but we will stay with the threads for now.
"""
from threading import Thread

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper