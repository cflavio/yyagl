import sys

if len(sys.argv) != 2:
    print 'Usage: apply_gloss.py filename.egg'
    sys.exit(0)

out_lines = []
with open(sys.argv[1]) as f_in:
    lines = f_in.readlines()
    for idx, line in enumerate(lines):
        if line.strip() != '<Scalar> envtype { GLOSS }':
            is_scal = line.strip().startswith('<Scalar> alpha-file { ')
            if not idx or not (line.strip() == out_lines[-1].strip()
                               and is_scal):
                out_lines += [line.rstrip()]
        else:
            out_lines += [line.rstrip()]
            outl = ''
            for char in line:
                if char == ' ':
                    outl += ' '
                else:
                    break
            outl += '<Scalar> alpha-file { %s }' % lines[idx - 1].strip()
            out_lines += [outl]

with open(sys.argv[1], 'w') as f_out:
    map(lambda outl: f_out.write(outl + '\n'), out_lines)
