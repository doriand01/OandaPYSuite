from threading import Thread
import multiprocess


def run_as_thread(func):
    """
    Decorator function to run a function as a thread.
    """
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def run_as_process_for_static_method(func):
    """
    Decorator function to run a function as a process.
    """
    def wrapper(*args, **kwargs):
        process = multiprocess.Process(target=func, args=args, kwargs=kwargs)
        process.start()
        return process
    return wrapper


def run_as_process_for_instance_method(func):
    """
    Decorator function to run a function as a process.
    """
    def wrapper(self, *args, **kwargs):
        process = multiprocess.Process(target=func, args=(self, *args), kwargs=kwargs)
        process.start()
        return process
    return wrapper


