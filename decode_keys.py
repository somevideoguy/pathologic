import argparse

from pathologic import *

def parse_args():    
    parser = argparse.ArgumentParser(description='Extracts the data from the Pathologic string file (Strings/main.dat).')
    parser.add_argument('-i', metavar='INFILE', default='main.dat')
    parser.add_argument('-o', metavar='OUTFILE', default=None)
    #parser.add_argument('-l', '--lang', metavar='LANGUAGE', choices=['ru', 'en'], required=True, help='the string file language (en, ru)')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    infile = args.i
    outfile = args.o or (infile + '.xml')
    #lang = args.lang

    strings = read_maindat(infile)
    write_maindat_xml(strings, outfile)
