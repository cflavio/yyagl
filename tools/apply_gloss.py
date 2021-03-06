import sys

if len(sys.argv) != 2:
    print('Usage: apply_gloss.py filename.egg')
    sys.exit(0)


def __process_line(idx, line, _out_lines):
    if line.strip() != '<Scalar> envtype { GLOSS }':
        mth = __process_nongloss_line
    else: mth = __process_gloss_line
    return mth(idx, line, _out_lines)


def __process_nongloss_line(idx, line, _out_lines):
    is_scal = line.strip().startswith('<Scalar> alpha-file { ')
    if not idx or not (line.strip() == _out_lines[-1].strip() and is_scal):
        _out_lines += [line.rstrip()]
    return _out_lines


def __process_gloss_line(idx, line, _out_lines):
    _out_lines += [line.rstrip()]
    outl = ''
    for char in line:
        if char == ' ': outl += ' '
        else: break
    outl += '<Scalar> alpha-file { %s }' % lines[idx - 1].strip()
    return _out_lines + [outl]


out_lines = []
with open(sys.argv[1]) as fin:
    lines = fin.readlines()
    for _idx, _line in enumerate(lines):
        out_lines = __process_line(_idx, _line, out_lines)


with open(sys.argv[1], 'w') as fout:
    list(map(lambda outl: fout.write(outl + '\n'), out_lines))
