class Facade(object):

    # def _fwd_mth(self, mth_name, tgt_mth):
    #     def fun(*args, **kwargs): return tgt_mth(*args, **kwargs)
    #     setattr(self, mth_name, fun)

    # def _fwd_prop(self, prop_name, tgt_prop):
    #     setattr(self.__class__, prop_name, property(lambda self: tgt_prop))

    def __init__(self, prop_lst=[], mth_lst=[]):
        map(lambda args: self.__fwd_prop(*args), prop_lst)
        map(lambda args: self.__fwd_mth(*args), mth_lst)
        # try detecting if the forwarded item is a prop or a method, so we can
        # pass only a single list

    def __fwd_mth(self, mth_name, tgt_mth):
        def fun(*args, **kwargs): return tgt_mth(self)(*args, **kwargs)
        setattr(self, mth_name, fun)

    def __fwd_prop(self, prop_name, tgt_prop):
        setattr(self.__class__, prop_name, property(tgt_prop))

    def destroy(self): pass
