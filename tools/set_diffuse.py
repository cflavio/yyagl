import os


def set_diffuse(_file):
    output_lines = []
    with open(_file) as f:
        lines = f.readlines()
        for line in lines:
            if not line.strip().startswith('<Scalar> diff'):
                output_lines += [line.rstrip()]
            else:
                outl = line.split(' { ')[0] + ' { 1.000000 }'
                output_lines += [outl]

    with open(_file, 'w') as f:
        map(lambda outl: f.write(outl + '\n'), output_lines)


for _file in os.listdir('.'):
    if _file.endswith('.egg'):
        set_diffuse(_file)
