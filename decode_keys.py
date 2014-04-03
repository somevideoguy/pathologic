import sys, struct, codecs, argparse

"""
    Format of the main.dat string file (all numbers are little-endian):

    +--------------------------------+-------------------------------+--------------------+------------------   ...   --------------+----------------------+------- ...
    |  Number of strings (4 bytes)   |          ID (4 bytes)         | Len (1 or 2) bytes | First string (UCS-2) little-endian      |  Len (1 or 2) bytes  |  Second string ...
    +--------------------------------+-------------------------------+--------------------+------------------   ...   --------------+----------------------+------- ...

"""

def parse_args():    
    parser = argparse.ArgumentParser(description='Extracts the data from the Pathologic string file (Strings/main.dat).')
    parser.add_argument('-i', metavar='INFILE', default='main.dat')
    parser.add_argument('-o', metavar='OUTFILE', default=None)
    #parser.add_argument('-l', '--lang', metavar='LANGUAGE', choices=['ru', 'en'], required=True, help='the string file language (en, ru)')

    return parser.parse_args()

def read_bytes(f, count):
    return f.read(count)

def read_int(f):
    b = f.read(4)
    return struct.unpack('<i', b)[0]

def decode_file(infile, outfile):
    with open(infile, 'rb') as f:
        count = read_int(f)
        for i in xrange(count):
            id = read_int(f)
            byte1 = ord(f.read(1))
            if byte1 & 0x80:
                byte2 = ord(f.read(1))
                len = (byte1 & 0x7f) + (byte2 << 7)
            else:
                len = byte1
                
            strings.append((id, f.read(len * 2).decode("utf-16")))

    strings.sort(key=lambda str: str[0])
    with codecs.open(outfile, "wb") as g:
        g.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<strings>\r\n".encode("utf-8"))

        for (id, string) in strings:
            g.write((u"<string id=\"%s\"><![CDATA[%s]]></string>\r\n" % (id, string)).encode("utf-8"))
        g.write("</strings>\r\n".encode("utf-8"))

if __name__ == '__main__':
    args = parse_args()

    infile = args.i
    outfile = args.o or (infile + '.xml')
    #lang = args.lang
    strings = []

    decode_file(infile, outfile)
