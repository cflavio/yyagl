import sys
from logging import info
from os.path import dirname
from collections.abc import Mapping
from json import load, dumps
from yyagl.gameobject import GameObject
from yyagl.lib.builder import LibP3d


class DctFile(GameObject):

    def __init__(self, fpath, default_dct=None, persistent=True):
        GameObject.__init__(self)
        default_dct = default_dct or {}
        if sys.platform == 'darwin' and LibP3d.runtime():
            fpath = dirname(__file__) + '/' + fpath
        self.fpath = fpath
        self.persistent = persistent
        try:
            with open(fpath) as json: fdct = load(json)
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
    def deepupdate(dct, new_dct):
        for key, val in new_dct.items():
            if isinstance(val, Mapping):
                dct[key] = DctFile.deepupdate(dct.get(key, {}), val)
            else: dct[key] = val
        return dct

    def store(self):
        info('storing %s' % self.fpath)
        if not self.persistent: return
        json_str = dumps(self.dct, sort_keys=True, indent=4,
                         separators=(',', ': '))
        with open(self.fpath, 'w') as json: json.write(json_str)

    def __getitem__(self, arg): return self.dct[arg]

    def __setitem__(self, arg, val): self.dct[arg] = val

    def __delitem__(self, arg): del self.dct[arg]
