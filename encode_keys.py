import argparse
import codecs

from pathologic import *

def parse_args():
    parser = argparse.ArgumentParser(description="Recreates the Pathologic strings file from an XML input.")
    parser.add_argument('-i', '--infile', required=True)
    parser.add_argument('-o', '--outfile', required=True)

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    with open(args.outfile, 'wb') as out:
        with open(args.infile, 'rb') as inf:
            strings = read_maindat_xml(inf)
            write_maindat(strings, out)
