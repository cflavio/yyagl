class ObsInfo:

    def __init__(self, mth, sort, args):
        self.mth = mth
        self.sort = sort
        self.args = args

    def __repr__(self): return str(self.mth)


class Subject:

    def __init__(self):
        self.observers = {}

    def attach(self, obs_meth, sort=10, rename='', args=None):
        args = args or []
        onm = rename or obs_meth.__name__
        if onm not in self.observers: self.observers[onm] = []
        self.observers[onm] += [ObsInfo(obs_meth, sort, args)]
        sorted_obs = sorted(self.observers[onm], key=lambda obs: obs.sort)
        self.observers[onm] = sorted_obs

    def detach(self, obs_meth, lambda_call=None):
        if isinstance(obs_meth, str):
            onm = obs_meth
            observers = [obs for obs in self.observers[onm]
                         if obs.mth == lambda_call]
        else:
            onm = obs_meth.__name__
            observers = [obs for obs in self.observers[onm]
                         if obs.mth == obs_meth]
        if not observers: raise Exception
        list(map(self.observers[onm].remove, observers))

    def notify(self, meth, *args, **kwargs):
        if meth not in self.observers: return  # no obs for this notification
        for obs in self.observers[meth][:]:
            if obs in self.observers[meth]:  # if an obs removes another one
                try:
                    act_args = obs.args + list(args)
                    obs.mth(*act_args, **kwargs)
                except SystemError:
                    print('Quit')
                    import sys; sys.exit()

    def observing(self, obs_meth):
        if callable(obs_meth): obs_meth = obs_meth.__name__
        return obs_meth in self.observers and self.observers[obs_meth]

    def destroy(self): self.observers = None


class Observer: pass
