from yaml import load, dump
from collections import Mapping


class DctFile(object):

    def __init__(self, fpath, default_dct={}):
        self.fpath = fpath
        try:
            with open(fpath) as yaml_file:
                file_dct = load(yaml_file)
            self.dct = self.__update(default_dct, file_dct)
        except IOError:
            self.dct = default_dct

    @staticmethod
    def __update(dct, upd):
        for key, val in upd.iteritems():
            if isinstance(val, Mapping):
                dct[key] = DctFile.__update(dct.get(key, {}), val)
            else:
                dct[key] = upd[key]
        return dct

    def store(self):
        with open(self.fpath, 'w') as yaml_file:
            dump(self.dct, yaml_file, default_flow_style=False)

    def __getitem__(self, arg):
        return self.dct[arg]

    def __setitem__(self, arg, val):
        self.dct[arg] = val

    def __delitem__(self, arg):
        del self.dct[arg]
