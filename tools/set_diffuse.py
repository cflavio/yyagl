import os


def set_diffuse(eggfile):
    output_lines = []
    with open(eggfile) as file_:
        lines = file_.readlines()
        for line in lines:
            if not line.strip().startswith('<Scalar> diff'):
                output_lines += [line.rstrip()]
            else:
                outl = line.split(' { ')[0] + ' { 1.000000 }'
                output_lines += [outl]

    with open(eggfile, 'w') as file_:
        map(lambda outl: file_.write(outl + '\n'), output_lines)


for _file in os.listdir('.'):
    if _file.endswith('.egg'):
        set_diffuse(_file)
