from yaml import load, dump
import collections


class DictFile(object):

    def __init__(self, path, default_dct={}):
        self.path = path
        try:
            with open(path) as yaml_file:
                file_dct = load(yaml_file)
            self.dct = self.__update(default_dct, file_dct)
        except IOError:
            self.dct = default_dct

    @staticmethod
    def __update(d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = DictFile.__update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def store(self):
        with open(self.path, 'w') as yaml_file:
            dump(self.dct, yaml_file, default_flow_style=False)

    def __getitem__(self, arg):
        return self.dct[arg]

    def __setitem__(self, arg, val):
        self.dct[arg] = val

    def __delitem__(self, arg):
        del self.dct[arg]
