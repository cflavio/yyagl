from os import system, remove
from .build import exec_cmd


def __get_img_fmt(fname):
    cmd = 'identify -verbose "%s" | grep alpha' % fname
    alpha = exec_cmd(cmd).strip()
    geometry = exec_cmd('identify -verbose "%s" | grep Geometry' % fname)
    split_dim = lambda geom: geom.split()[1].split('+')[0].split('x')
    size = [int(dim) for dim in split_dim(geometry)]
    return alpha, size


def __build_img(fname):
    png = fname[:-3] + 'png'
    alpha, size = __get_img_fmt(fname)
    sizes = [2**i for i in range(0, 12)]
    floor_pow = lambda img_sz: max([siz for siz in sizes if siz <= img_sz])
    width, height = map(floor_pow, size)
    system('convert "%s"[0] -resize %dx%d! "%s"' % (fname, width, height, png))
    if png.endswith('_png.png'):
        return
    cmd = 'nvcompress -bc3 {alpha} -nomips "%s" "%sdds"' % (png, fname[:-3])
    system(cmd.format(alpha='-alpha' if alpha else ''))
    remove(png)


def build_images(target, source, env):
    map(lambda fname: __build_img(fname), [str(src) for src in source])
