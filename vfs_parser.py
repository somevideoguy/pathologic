from __future__ import print_function

import sys, struct, os.path, os
from collections import namedtuple
from pathologic import *

File = namedtuple('File', ['filename', 'len', 'offset'])

def read_header(f):
    filename_len = ord(f.read(1))
    filename = f.read(filename_len)
    len = read_int(f)
    offset = read_int(f)
    f.read(8)
    return File(filename=filename, len=len, offset=offset)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        dir_to_create = os.path.splitext(file_name)[0]

        try:
            os.mkdir(dir_to_create)
        except:
            pass

        with open(sys.argv[1], 'rb') as f:
            os.chdir(dir_to_create)

            print(read_bytes(f, 4))
            print(read_int(f))
            num_files = read_int(f)

            headers = []
            for i in range(num_files):
                headers.append(read_header(f))

            for header in headers:
                print(header)
                f.seek(header.offset)
                with open(header.filename, 'wb') as g:
                    g.write(f.read(header.len))
