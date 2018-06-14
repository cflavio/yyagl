from collections import Mapping
from yaml import load, dump
from .gameobject import GameObject


class DctFile(GameObject):

    def __init__(self, fpath, default_dct={}, persistent=True):
        GameObject.__init__(self)
        self.fpath = fpath
        self.persistent = persistent
        try:
            with open(fpath) as fyaml: fdct = load(fyaml)
            self.dct = self.__add_default(default_dct, fdct)
        except IOError: self.dct = default_dct

    @staticmethod
    def __add_default(dct, upd):
        for key, val in upd.iteritems():
            if isinstance(val, Mapping):
                dct[key] = DctFile.__add_default(dct.get(key, {}), val)
            else: dct[key] = upd[key]
        return dct

    def store(self):
        self.eng.log('storing %s' % self.fpath)
        if not self.persistent: return
        with open(self.fpath, 'w') as fyaml:
            dump(self.dct, fyaml, default_flow_style=False)

    def __getitem__(self, arg): return self.dct[arg]

    def __setitem__(self, arg, val): self.dct[arg] = val

    def __delitem__(self, arg): del self.dct[arg]
