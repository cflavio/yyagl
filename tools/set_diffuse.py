from os import listdir


def __set_diffuse(fpath):
    out_lines = []
    with open(fpath) as fin:
        for line in fin.readlines():
            out_lines = __process_line(line, out_lines)
    with open(fpath, 'w') as fin:
        map(lambda outl: fin.write(outl + '\n'), out_lines)


def __process_line(line, out_lines):
    if not line.strip().startswith('<Scalar> diff'):
        return out_lines + [line.rstrip()]
    else: return out_lines + [line.split(' { ')[0] + ' { 1.000000 }']


map(__set_diffuse, [fname for fname in listdir('.') if fname.endswith('.egg')])
