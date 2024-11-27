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

def to_float_or_int_or_str(value):
    """
    Convert a string to a float or int.
    """
    if '.' in value and all([c.isdigit() for c in value.split('.')]):
        return float(value)
    elif '.' not in value and all([c.isdigit() for c in value]):
        return int(value)
    elif any([not c.isdigit() for c in value]):
        return value
