import struct, sys, os, os.path
from pathologic import *

# convert from unix time to Win32 FILETIME
def unix_to_win32(time):
    time *= 10000000                # convert from seconds to 100-nanosecond intervals
    time += 11644473600000 * 10000  # change epoch from 1 Jan 1970 to 1 Jan 1601
    return int(time)                # double to int

# get necessary metadata about a file in a path
def get_file_data(path, f):
    filesize = os.path.getsize(path+f)
    timemodified = os.path.getmtime(path+f)
    return FileData(f, filesize, timemodified)

# generate the VFS header for a file
def gen_file_header(fd, offset):
    file_name_len = len(fd.filename).to_bytes(1, 'little')
    file_name = fd.filename.encode('iso8859-1')
    format_string = '<c%ds2iq' % len(fd.filename)
    return struct.pack(format_string, file_name_len, file_name, fd.len, offset, unix_to_win32(fd.timemodified))

# generate the VFS header for a directory
def gen_dir_header(dir):
    if dir.dirname:
        dir_name_len = len(dir.dirname).to_bytes(1, 'little')
        file_name = dir.dirname.encode('iso8859-1')
        format_string = '<c%ds2i' % len(dir.dirname)
        return struct.pack(format_string, dir_name_len, file_name, len(dir.subdirs), len(dir.files))
    else:
        return struct.pack('<2i', len(dir.subdirs), len(dir.files))

# get a Directory tuple representing a directory to write to a VFS file
def get_tree(dirname='', curdir='./'):
    listdir = os.listdir(curdir)
    dirs = list(filter(lambda x: os.path.isdir(curdir+x), listdir))
    files = list(map(lambda x: get_file_data(curdir, x), filter(lambda x: os.path.isfile(curdir+x), listdir)))
    files = sorted(files, key=lambda x: x.len)
    return Directory(dirname, [get_tree(x, curdir+x+'/') for x in dirs], files)

# get the length, in bytes, of the header section of the VFS file for the given directory
def get_headers_length(tree):
    # the length of the headers section is calculated as:
    # - 4 bytes for the magic number;
    # - 8 bytes for the root directory subdirectory count and file count;
    # - for each file: 1 byte for the name length, [length] bytes for the file name,
    #   4 bytes for the file size, 4 bytes for the offset and 8 bytes for the last modified time,
    #   totalling 17+[length] bytes;
    # - for each subdirectory: 1 byte for the name length, [length] bytes for the directory name,
    #   4 bytes for the subdirectory count and 4 bytes for the file count, totalling 9+[length] bytes.
    dir_info_len = 12 # if root, has magic number instead of directory name
    if tree.dirname:
        dir_info_len = len(tree.dirname) + 9

    namelens = sum([len(x.filename) for x in tree.files])
    return dir_info_len + 17*len(tree.files) + namelens + sum([get_headers_length(x) for x in tree.subdirs])

# write VFS headers to the file pointed to by fh
def write_tree_headers(fh, dir, curoffset=0):
    if curoffset == 0:
        curoffset = get_headers_length(dir)
    fh.write(gen_dir_header(dir))
    for f in dir.files:
        fh.write(gen_file_header(f, curoffset))
        curoffset += f.len
    for d in dir.subdirs:
        write_tree_headers(fh, d, curoffset)

# write files to the VFS file pointed to by fh
def write_tree_files(fh, tree, curdir='./'):
    for f in tree.files:
        print(curdir + f.filename)
        buf = None
        with open(curdir+f.filename, 'rb') as g:
            buf = g.read()
        fh.write(buf)
    for dir in tree.subdirs:
        write_tree_files(fh, dir, curdir+dir.dirname+'/')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        dir_name = sys.argv[1]
        file_name = sys.argv[2]

        root_dir = os.getcwd()
        os.chdir(dir_name)
        tree = get_tree()
        with open(root_dir+'/'+file_name, 'wb') as vfs:
            vfs.write(struct.pack('<i', 0x4331504C)) # write magic number
        
            print(get_headers_length(tree))
            write_tree_headers(vfs, tree)
            write_tree_files(vfs, tree)
        
        sys.exit() 
    else:
        printerr("Usage: vfs_pack.py <directory to pack> <output file>")