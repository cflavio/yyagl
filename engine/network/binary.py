from struct import Struct, calcsize, unpack


class BinaryData:

    @staticmethod
    def pack(lst):
        acc_fmt = '!'
        acc_elems = []
        acc_header = ''
        acc_header = BinaryData._header_lst(lst, acc_header)
        lst = [acc_header] + lst
        acc_fmt, acc_elems = BinaryData._pack_lst(lst, acc_fmt, acc_elems)
        msg_struct = Struct(acc_fmt)
        msg_data = msg_struct.pack(*acc_elems)
        return msg_struct.size, msg_data

    def _header_elm(elm, acc_header):
        if elm is None: add = 'n'
        elif type(elm) == bool: add = 'b'
        elif type(elm) == int: add ='i'
        elif type(elm) == float: add ='f'
        elif type(elm) == str: add = 's'
        elif type(elm) == dict: add = '{}'
        elif type(elm) in [tuple, list]: add = BinaryData._header_lst(elm, acc_header)
        return acc_header + add

    def _header_lst(elm, acc_header):
        add = '('
        for sub_elm in elm:
            add += BinaryData._header_elm(sub_elm, acc_header)
        add += ')'
        return acc_header + add

    def _pack_lst(lst, acc_fmt, acc_elems):
        add_fmt, add_elems = '', []
        for sub_elm in lst:
            elm_fmt, elm_elems = BinaryData._pack_elm(sub_elm, '', [])
            add_fmt += elm_fmt
            add_elems += elm_elems
        return acc_fmt + add_fmt, acc_elems + add_elems

    def _pack_elm(elm, acc_fmt, acc_elems):
        if elm is None:
            add_fmt =''
            add_elems = []
        elif type(elm) == bool:
            add_fmt ='?'
            add_elems = [elm]
        elif type(elm) == int:
            add_fmt ='i'
            add_elems = [elm]
        elif type(elm) == float:
            add_fmt ='f'
            add_elems = [elm]
        elif type(elm) == str:
            b_str = bytes(elm, 'utf-8')
            add_fmt = 'i%ds' % len(b_str)
            add_elems = [len(b_str), b_str]
        elif type(elm) in [tuple, list]:
            add_fmt, add_elems = BinaryData._pack_lst(elm, '', [])
        elif type(elm) == dict: add_fmt, add_elems = '', []
        return acc_fmt + add_fmt, acc_elems + add_elems

    @staticmethod
    def unpack(data):
        header_length, data = BinaryData.unpack_helper('!i', data)
        header_length = header_length[0]
        header, data = BinaryData.unpack_helper('!%ds' % header_length, data)
        header = header[0].decode('utf-8')
        vals = []
        curr_lst = vals

        def parent(sublist, lst):
            if sublist in lst: return lst
            for _subl in [elm for elm in lst if type(elm) == list]:
                if parent(sublist, _subl): return parent(sublist, _subl)
        for elm in header:
            if elm == '(':
                curr_lst += [[]]
                curr_lst = curr_lst[-1]
            elif elm == ')':
                curr_lst = parent(curr_lst, vals)
            elif elm == '{': pass
            elif elm == '}': curr_lst += [{}]
            else:
                val, data = BinaryData._unpack_elm(elm, data)
                curr_lst += [val]
        return vals[0]

    @staticmethod
    def _unpack_elm(elm, data):
        if elm == 'n':
            val, data = [None], data
            val = val[0]
        elif elm == 'b':
            val, data = BinaryData.unpack_helper('!?', data)
            val = val[0]
        elif elm == 'i':
            val, data = BinaryData.unpack_helper('!i', data)
            val = val[0]
        elif elm == 'f':
            val, data = BinaryData.unpack_helper('!f', data)
            val = val[0]
        elif elm == 's':
            s_len, data = BinaryData.unpack_helper('!i', data)
            val, data = BinaryData.unpack_helper('!%ds' % s_len, data)
            val = val[0].decode('utf-8')
        return val, data

    @staticmethod
    def unpack_helper(fmt, data):
        size = calcsize(fmt)
        return unpack(fmt, data[:size]), data[size:]
