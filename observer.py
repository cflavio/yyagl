class Subject(object):

    def __init__(self):
        self.observers = []

    def attach(self, obs_meth, sort=10, rename=''):
        if rename:
            obs_meth.__name__ = rename
        self.observers += [(obs_meth, sort)]

    def detach(self, obs_meth):
        observers = [obs for obs in self.observers if obs[0] == obs_meth]
        if not observers:
            raise Exception
        map(self.observers.remove, observers)

    def notify(self, meth, *args, **kwargs):
        meths = [obs for obs in self.observers if obs[0].__name__ == meth]
        sorted_observers = sorted(meths, key=lambda obs: obs[1])
        # TODO: make a sorted list at attach
        # map(lambda obs: obs[0](*args, **kwargs), sorted_observers)
        for obs in sorted_observers:
            if obs in self.observers:  # if an observer removes another one
                obs[0](*args, **kwargs)

    def destroy(self):
        self.observers = None


class Observer(object):
    pass
