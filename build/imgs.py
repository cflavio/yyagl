from os import system, remove
from .build import exec_cmd


def bld_images(target, source, env):
    map(__bld_img, [str(src) for src in source])


def __bld_img(fname):
    pngname = fname[:-3] + 'png'
    alpha, size = __get_img_alpha_and_size(fname)
    sizes = [2**i for i in range(0, 12)]
    floor_pow = lambda img_sz: max([siz for siz in sizes if siz <= img_sz])
    width, height = map(floor_pow, size)
    cmd_tmpl = 'convert "%s"[0] -resize %dx%d! "%s"'
    system(cmd_tmpl % (fname, width, height, pngname))
    if pngname.endswith('_png.png'): return
    cmd_tmpl = 'nvcompress -bc3 {alpha} -nomips "%s" "%sdds"'
    cmd = cmd_tmpl % (pngname, fname[:-3])
    system(cmd.format(alpha='-alpha' if alpha else ''))
    remove(pngname)


def __get_img_alpha_and_size(fname):
    alpha = exec_cmd('identify -verbose "%s" | grep alpha' % fname).strip()
    geom = exec_cmd('identify -verbose "%s" | grep Geometry' % fname)
    dim_split = lambda _geom: _geom.split()[1].split('+')[0].split('x')
    return alpha, [int(dim) for dim in dim_split(geom)]
