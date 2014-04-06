import sys, argparse, xml.dom.minidom, codecs, struct

def parse_args():
	parser = argparse.ArgumentParser(description="Recreates the Pathologic strings file from an XML input.")
	parser.add_argument('-i', '--infile', required=True)
	parser.add_argument('-o', '--outfile', required=True)

	return parser.parse_args()

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

if __name__ == '__main__':
	args = parse_args()

	dom = xml.dom.minidom.parse(args.infile)

	with open(args.outfile, 'wb') as out:
		strings = dom.getElementsByTagName('string');

		write_int(out, len(strings))
		for str in strings:
			write_int(out, int(str.getAttribute('id')))

			if str.firstChild is None:
				write_str_len(out, 0)
			else:
				data = str.firstChild.data
				write_str_len(out, len(data))
				write_str(out, data)
