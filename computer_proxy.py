from functools import wraps


def compute_once(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        self = args[0]
        key = fun.__name__, args  # add support for kwargs
        if key not in self.buffered_vals:
            self.buffered_vals[key] = fun(*args, **kwargs)
        return self.buffered_vals[key]
    return wrapper


def once_a_frame(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        self = args[0]
        key = fun.__name__, args  # add support for kwargs
        if key not in self.buffered_vals_frm:
            self.buffered_vals_frm[key] = fun(*args, **kwargs)
        return self.buffered_vals_frm[key]
    return wrapper


class ComputerProxy(object):

    def __init__(self):
        self.eng.attach_obs(self.on_start_frame)
        # there are issues if the object has another on_start_frame
        self.buffered_vals, self.buffered_vals_frm = {}, {}

    def on_start_frame(self):
        self.buffered_vals_frm = {}

    def destroy(self):
        self.eng.detach_obs(self.on_start_frame)
        self.buffered_vals = self.buffered_vals_frm = None
