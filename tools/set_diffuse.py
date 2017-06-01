from os import listdir


def set_diffuse(fpath):
    out_lines = []
    with open(fpath) as f_in:
        lines = f_in.readlines()
        for line in lines:
            if not line.strip().startswith('<Scalar> diff'):
                out_lines += [line.rstrip()]
            else:
                outl = line.split(' { ')[0] + ' { 1.000000 }'
                out_lines += [outl]

    with open(fpath, 'w') as f_in:
        map(lambda outl: f_in.write(outl + '\n'), out_lines)


for fname in listdir('.'):
    if fname.endswith('.egg'):
        set_diffuse(fname)
