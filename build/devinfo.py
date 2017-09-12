from itertools import product
from os import system
from .build import bld_dpath, branch, exec_cmd, devinfo_fpath


def bld_devinfo(target, source, env):
    for (fname, cond), src in product(env['DEV_CONF'].items(), source):
        with open(('%s%s.txt') % (bld_dpath, fname), 'a') as fout:
            __process(src, cond, fout)
    names = ' '.join([fname + '.txt' for fname in env['DEV_CONF']])
    rmnames = ' '.join(['{dstpath}%s.txt' % fnm for fnm in env['DEV_CONF']])
    cmd = 'tar -czf {fout} -C {dstpath} ' + names + ' && rm ' + rmnames
    fpath = devinfo_fpath.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                                 version=branch)
    system(cmd.format(dstpath=bld_dpath, fout=fpath))


def __clean_pylint(pylint_out):
    clean_output, skipping = '', False
    err_str = 'No config file found, using default configuration'
    lines = [line for line in pylint_out.split('\n') if line != err_str]
    for line in lines:
        start_skip = 'Traceback (most recent call last):'
        end_skip = 'RuntimeError: maximum recursion depth exceeded while '
        if any(line.startswith(ev_skip) for ev_skip in [start_skip, end_skip]):
            skipping = line.startswith(start_skip)
        elif not skipping: clean_output += line + '\n'
    return clean_output


def __process(src, cond, fout):
    if cond(src): return
    fout.write('    ' + str(src) + '\n')
    out_pylint = __clean_pylint((exec_cmd('pylint -r n -d C0111 ' + str(src))))
    out_pyflakes = exec_cmd('pyflakes ' + str(src))
    out_pep8 = exec_cmd('pep8 ' + str(src))
    outs = [out.strip() for out in [out_pylint, out_pyflakes, out_pep8]]
    map(lambda out: fout.write(out + '\n'), [out for out in outs if out])
    fout.write('\n')
