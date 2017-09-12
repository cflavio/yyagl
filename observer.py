class Subject(object):

    def __init__(self):
        self.observers = {}

    def attach(self, obs_meth, sort=10, rename='', redirect=None, args=[]):
        if rename:
            obs_meth.__name__ = rename
        onm = obs_meth if isinstance(obs_meth, str) else obs_meth.__name__
        if onm not in self.observers:
            self.observers[onm] = []
        self.observers[onm] += [(obs_meth, sort, redirect, args)]
        sorted_obs = sorted(self.observers[onm], key=lambda obs: obs[1])
        self.observers[onm] = sorted_obs

    def detach(self, obs_meth):
        onm = obs_meth.__name__
        observers = [obs for obs in self.observers[onm] if obs[0] == obs_meth]
        if not observers:
            raise Exception
        map(self.observers[onm].remove, observers)

    def notify(self, meth, *args, **kwargs):
        if meth not in self.observers:
            return  # it there aren't observers for this notification
        for obs in self.observers[meth]:
            if obs in self.observers[meth]:
                # if an observer removes another one
                act_args = obs[3] + list(args)
                cb_meth = obs[2] or obs[0]
                cb_meth(*act_args, **kwargs)

    def destroy(self):
        self.observers = None


class Observer(object):
    pass
