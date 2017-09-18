import sys

if len(sys.argv) != 2:
    print 'Usage: apply_gloss.py filename.egg'
    sys.exit(0)


def __process_line(idx, line, out_lines):
    if line.strip() != '<Scalar> envtype { GLOSS }':
        return __process_nongloss_line(idx, line, out_lines)
    else:
        return __process_gloss_line(idx, line, out_lines)


def __process_nongloss_line(idx, line, out_lines):
    is_scal = line.strip().startswith('<Scalar> alpha-file { ')
    if not idx or not (line.strip() == out_lines[-1].strip() and is_scal):
        out_lines += [line.rstrip()]
    return out_lines


def __process_gloss_line(idx, line, out_lines):
    out_lines += [line.rstrip()]
    outl = ''
    for char in line:
        if char == ' ': outl += ' '
        else: break
    outl += '<Scalar> alpha-file { %s }' % lines[idx - 1].strip()
    return out_lines + [outl]


out_lines = []
with open(sys.argv[1]) as fin:
    lines = fin.readlines()
    for idx, line in enumerate(lines):
        out_lines = __process_line(idx, line, out_lines)


with open(sys.argv[1], 'w') as fout:
    map(lambda outl: fout.write(outl + '\n'), out_lines)
