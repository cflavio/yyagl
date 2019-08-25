import sys
from os.path import dirname
from collections import Mapping
from yaml import load, dump
from .gameobject import GameObject
from yyagl.lib.builder import LibP3d


class DctFile(GameObject):

    def __init__(self, fpath, default_dct={}, persistent=True):
        GameObject.__init__(self)
        if sys.platform == 'darwin' and LibP3d.runtime():
            fpath = dirname(__file__) + fpath
        self.fpath = fpath
        self.persistent = persistent
        try:
            with open(fpath) as fyaml: fdct = load(fyaml)
            self.dct = self.__add_default(default_dct, fdct)
        except IOError: self.dct = default_dct

    @staticmethod
    def __add_default(dct, upd):
        for key, val in upd.items():
            if isinstance(val, Mapping):
                dct[key] = DctFile.__add_default(dct.get(key, {}), val)
            else: dct[key] = upd[key]
        return dct

    @staticmethod
    def deepupdate(d, u):
        for k, v in u.items():
            if isinstance(v, Mapping): d[k] = DctFile.deepupdate(d.get(k, {}), v)
            else: d[k] = v
        return d

    def store(self):
        self.eng.log('storing %s' % self.fpath)
        if not self.persistent: return
        with open(self.fpath, 'w') as fyaml:
            dump(self.dct, fyaml, default_flow_style=False)

    def __getitem__(self, arg): return self.dct[arg]

    def __setitem__(self, arg, val): self.dct[arg] = val

    def __delitem__(self, arg): del self.dct[arg]
