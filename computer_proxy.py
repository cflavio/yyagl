from functools import wraps


def compute_once(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        self = args[0]
        key = function.__name__, args  # add support for kwargs
        if key not in self._buffered_vals:
            self._buffered_vals[key] = function(*args, **kwargs)
        return self._buffered_vals[key]
    return wrapper


def once_a_frame(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        self = args[0]
        key = function.__name__, args  # add support for kwargs
        if key not in self._buffered_vals_frm:
            self._buffered_vals_frm[key] = function(*args, **kwargs)
        return self._buffered_vals_frm[key]
    return wrapper


class ComputerProxy(object):

    def __init__(self):
        eng.attach_obs(self.on_start_frame)
        # there are issues if the object has another on_start_frame
        self._buffered_vals = {}
        self._buffered_vals_frm = {}

    def on_start_frame(self):
        self._buffered_vals_frm = {}

    def destroy(self):
        eng.detach_obs(self.on_start_frame)
        self._buffered_vals = self._buffered_vals_frm = None
