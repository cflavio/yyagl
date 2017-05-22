import sys

if len(sys.argv) != 2:
    print 'Usage: apply_gloss.py filename.egg'
    sys.exit(0)

output_lines = []
with open(sys.argv[1]) as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip() != '<Scalar> envtype { GLOSS }':
            if not i or not (line.strip() == output_lines[-1].strip() and line.strip().startswith('<Scalar> alpha-file { ')):
                output_lines += [line.rstrip()]
        else:
            output_lines += [line.rstrip()]
            outl = ''
            for char in line:
                if char == ' ':
                    outl += ' '
                else:
                    break
            outl += '<Scalar> alpha-file { ' + lines[i - 1].strip() + ' }'
            output_lines += [outl]

with open(sys.argv[1], 'w') as f:
    map(lambda outl: f.write(outl + '\n'), output_lines)
