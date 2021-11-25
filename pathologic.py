import struct
import xml.dom.minidom
import codecs
import sys
from collections import namedtuple

File = namedtuple('File', ['filename', 'len', 'offset', 'timemodified'])
FileData = namedtuple("FileData", ['filename', 'len', 'timemodified'])
Directory = namedtuple('Directory', ['dirname', 'subdirs', 'files'])
DirectoryHeader = namedtuple('DirectoryHeader', ['dirname', 'numdirs', 'numfiles'])

# acts like print, but prints to stderr rather than stdout
def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def read_bytes(f, count):
    return f.read(count)

def read_int(f):
    b = f.read(4)
    return struct.unpack('<i', b)[0]

def read_int8(f):
    return ord(f.read(1))

def read_filetime(f):
    b = f.read(8)
    thelong = struct.unpack('<q', b)[0]
    thelong -= 11644473600000 * 10000   # change epoch from 1 Jan 1601 to 1 Jan 1970
    return thelong / 10000000           # convert from 100-nanosecond intervals to seconds

def read_string(f, n):
    b = f.read(n)
    return b.decode('iso8859-1')

def read_maindat(infile):
    """
        Format of the main.dat string file (all numbers are little-endian):

        +--------------------------------+-------------------------------+--------------------+------------------   ...   --------------+----------------------+------- ...
        |  Number of strings (4 bytes)   |          ID (4 bytes)         | Len (1 or 2) bytes | First string (UCS-2) little-endian      |  Len (1 or 2) bytes  |  Second string ...
        +--------------------------------+-------------------------------+--------------------+------------------   ...   --------------+----------------------+------- ...

    """
    strings = []

    with open(infile, 'rb') as f:
        count = read_int(f)
        for i in range(count):
            id = read_int(f)
            byte1 = ord(f.read(1))
            if byte1 & 0x80:
                byte2 = ord(f.read(1))
                len = (byte1 & 0x7f) + (byte2 << 7)
            else:
                len = byte1

            strings.append((id, f.read(len * 2).decode("utf-16")))

    strings.sort(key=lambda str: str[0])

    return strings

def read_maindat_xml(infile):
    dom = xml.dom.minidom.parse(infile)
    strings = dom.getElementsByTagName('string');

    return [(string.getAttribute('id'), string.firstChild and string.firstChild.data or '') for string in strings]

def write_int(g, n):
    g.write(struct.pack('<I', n))

def write_str(g, str):
    g.write(str.encode('utf-16-le'))

def write_str_len(g, len):
    if len < 0x80:
        g.write(struct.pack('B', len))
    else:
        g.write(struct.pack('B', (len & 0x7f) + 0x80))
        g.write(struct.pack('B', (len >> 7)))

def write_maindat_xml(strings, outfile):
    def write_helper(g):
        g.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<strings>\r\n".encode("utf-8"))

        for (id, string) in strings:
            g.write((u"<string id=\"%s\"><![CDATA[%s]]></string>\r\n" % (id, string)).encode("utf-8"))
        g.write("</strings>\r\n".encode("utf-8"))

    try:
        write_helper(outfile)
    except AttributeError:
        with codecs.open(outfile, "wb") as g:
            write_helper(g)

def write_maindat(strings, out):
    write_int(out, len(strings))

    for str in strings:
        write_int(out, int(str[0]))

        write_str_len(out, len(str[1]))
        write_str(out, str[1])
