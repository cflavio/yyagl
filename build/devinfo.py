from os import system
from .build import bld_dir, branch, exec_cmd, devinfo_file


def build_devinfo(target, source, env):
    for fname, cond in env['DEV_CONF'].items():
        for src in source:
            with open(('%s%s.txt') % (bld_dir, fname), 'a') as outfile:
                __process(src, cond, outfile)
    names = ''.join([fname + '.txt ' for fname in env['DEV_CONF']])
    rmnames = ''.join(['{path}%s.txt ' % fname for fname in env['DEV_CONF']])
    bld_cmd = 'tar -czf {out_name} -C {path} ' + names + ' && rm ' + rmnames
    fpath = devinfo_file.format(path=bld_dir, name=env['APPNAME'],
                                version=branch)
    system(bld_cmd.format(path=bld_dir, out_name=fpath))


def __clean_pylint(pylint_out):
    clean_output = ''
    skipping = False
    err_str = 'No config file found, using default configuration'
    lines = [line for line in pylint_out.split('\n') if line != err_str]
    for line in lines:
        if line == 'Traceback (most recent call last):':
            skipping = True
        elif line == 'RuntimeError: maximum recursion depth exceeded ' + \
                     'while calling a Python object':
            skipping = False
        elif not skipping:
            clean_output += line + '\n'
    return clean_output


def __process(src, cond, outfile):
    if cond(src):
        return
    outfile.write('    '+str(src)+'\n')
    out_pylint = __clean_pylint((exec_cmd('pylint -r n -d C0111 '+str(src))))
    out_pyflakes = exec_cmd('pyflakes '+str(src))
    out_pep8 = exec_cmd('pep8 ' + str(src))
    outs = [out.strip() for out in [out_pylint, out_pyflakes, out_pep8]]
    map(lambda out: outfile.write(out+'\n'), [out for out in outs if out])
    outfile.write('\n')
