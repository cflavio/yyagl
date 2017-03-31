class Subject(object):

    def __init__(self):
        self.observers = []

    def attach(self, obs_meth, sort=10):
        self.observers += [(obs_meth, sort)]

    def detach(self, obs):
        observers = [_obs for _obs in self.observers if _obs[0] == obs]
        if not observers:
            raise Exception
        map(self.observers.remove, observers)

    def notify(self, meth, *args, **kwargs):
        try:
            meths = [obs for obs in self.observers if obs[0].__name__ == meth]
            sorted_observers = sorted(meths, key=lambda obs: obs[1])
            map(lambda obs: obs[0](*args, **kwargs), sorted_observers)
        except TypeError as err:
            eng.log('\n\nERROR: %s - %s\n%s\n\n' % (
                str(self), str(meth), str(err)))
            import traceback; traceback.print_stack()

    def destroy(self):
        self.observers = None


class Observer(object):
    pass
