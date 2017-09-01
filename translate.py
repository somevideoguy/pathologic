import os, os.path, sys, xlrd, codecs, locale, xml.etree.ElementTree as ET
import xml.sax.saxutils as SU

data = []

def read_strings(path):
    et = ET.parse(path)
    strings = et.findall('string')
    return [(str.attrib['id'], str.text) for str in strings]

def build_dict(string_list):
    result = dict()
    for str in string_list:
        result[str[0]] = str
    return result

def process_xslx(path):
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_index(0)

    if sheet.cell(1, 0).ctype == 1:
        rows = process_type1(sheet)
        return rows
    else:
        process_type2(sheet)
        return []

def process_type1(sheet):
    rows = []
    for row_idx in xrange(1, sheet.nrows):
        row = [sheet.cell(row_idx, col_idx).value for col_idx in xrange(0, sheet.ncols)]
        row[0] = 500000 + int(row[0].lstrip('+-'))
        rows.append(row)

    return rows

def process_type2(sheet):
    pass

def visit(dirpath, dirnames, filenames):
    rows = []
    for file in filenames:
        if os.path.splitext(file)[1] == '.xlsx':
            rows.extend(process_xslx(os.path.join(dirpath, file)))
    return rows

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
gen = SU.XMLGenerator(sys.stdout, 'utf-8')

dir = sys.argv[1]
rows = []
for (dirpath, dirnames, filenames) in os.walk(dir):
    rows.extend(visit(dirpath, dirnames, filenames))

rows.sort(lambda x, y: cmp(x[0], y[0]))

sys.stdout.write('<strings>\n')

for row in rows:
    sys.stdout.write('\t<string id="%d">' % row[0])
    sys.stdout.write('<![CDATA[' + row[4] + ']]>')
    sys.stdout.write('</string>\n')

sys.stdout.write('</strings>\n')
