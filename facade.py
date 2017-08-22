class Facade(object):

    def _fwd_mth(self, mth_name, tgt_mth):

        def fun(*args, **kwargs):
            return tgt_mth(*args, **kwargs)
        setattr(self, mth_name, fun)

    def _fwd_prop(self, prop_name, tgt_prop):
        setattr(self.__class__, prop_name, property(lambda self: tgt_prop))

    def _fwd_mth_lazy(self, mth_name, tgt_mth):

        def fun(*args, **kwargs):
            return tgt_mth(self)(*args, **kwargs)
        setattr(self, mth_name, fun)

    def _fwd_prop_lazy(self, prop_name, tgt_prop):
        setattr(self.__class__, prop_name, property(lambda self: tgt_prop(self)))
