class BlockReplacer(object):

    def __init__(self, out_lines, start_line, end_line, new_lines):
        self.out_lines = out_lines
        self.start_line = start_line
        self.end_line = end_line
        self.new_lines = new_lines
        self.is_replacing = False

    def process_line(self, line):
        if self.is_replacing and line.rstrip() == self.end_line:
            self.is_replacing = False
            return True
        if line.rstrip() == self.start_line:
            self.out_lines += self.new_lines
            self.is_replacing = True
        return self.is_replacing


class Fixer(object):

    def __init__(self):
        self.out_lines = []
        with open('track.egg') as fin:
            self.lines = fin.readlines()
        self.replacers = []
        new_lines = [
            '<Texture> MASKOBJTrack {\n',
            '  "./tex/MASKOBJTrack.jpg"\n',
            '  <Scalar> combine-rgb { INTERPOLATE }\n',
            '  <Scalar> combine-rgb-source0 { PREVIOUS }\n',
            '  <Scalar> combine-rgb-operand0 { SRC-COLOR }\n',
            '  <Scalar> combine-rgb-source1 { LAST_SAVED_RESULT }\n',
            '  <Scalar> combine-rgb-operand1 { SRC-COLOR }\n',
            '  <Scalar> combine-rgb-source2 { TEXTURE }\n',
            '  <Scalar> combine-rgb-operand2 { SRC-COLOR }\n',
            '  <Scalar> minfilter { LINEAR_MIPMAP_LINEAR }\n',
            '  <Scalar> magfilter { LINEAR_MIPMAP_LINEAR }\n',
            '  <Scalar> wrap { REPEAT }\n',
            '}\n']
        rep = BlockReplacer(self.out_lines, '<Texture> MASKOBJTrack {', '}', new_lines)
        self.replacers += [rep]

        new_lines = [
            '<Texture> TEXREPOBJTrack1 {\n',
            '  "./tex/snowbackground.jpg"\n',
            '  <Scalar> envtype { MODULATE }\n']
        rep = BlockReplacer(self.out_lines, '<Texture> TEXREPOBJTrack1 {', '  <Scalar> envtype { MODULATE }', new_lines)
        self.replacers += [rep]

        new_lines = [
            '<Texture> TEXREPOBJTrack2 {\n',
            '  "./tex/Tileable ice ground texture.jpg"\n',
            '  <Scalar> envtype { MODULATE }\n',
            '  <Scalar> saved-result { 1 }\n']
        rep = BlockReplacer(self.out_lines, '<Texture> TEXREPOBJTrack2 {', '  <Scalar> envtype { MODULATE }', new_lines)
        self.replacers += [rep]

        new_lines = [
            '      <TRef> { TEXREPOBJTrack1 }\n',
            '      <TRef> { MASKOBJTrack }\n']
        rep = BlockReplacer(self.out_lines, '      <TRef> { MASKOBJTrack }', '      <TRef> { TEXREPOBJTrack1 }', new_lines)
        self.replacers += [rep]

        for line in self.lines:
            if not any(rep.process_line(line) for rep in self.replacers):
                self.out_lines += [line]
        with open('track_fixed.egg', 'w') as fout:
            map(lambda outl: fout.write(outl), self.out_lines)


Fixer()
