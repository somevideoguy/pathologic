from __future__ import print_function

import sys, os.path, os
from pathologic import *

"""
    Reads the header data for a single file.
    The layout is (strings are ISO 8859-1 encoded (I think); ints are little-endian):
    +------------------+--------------+--------------------------+-------------+--------------------+
    | File name length |  File name   |        File size         | File offset | Last modified date |
    +------------------+--------------+--------------------------+-------------+--------------------+
    |      1 byte      |   n bytes    |         4 bytes          |   4 bytes   |      8 bytes       |
    +------------------+--------------+--------------------------+-------------+--------------------+
    |    8-bit int     |    string    |        32-bit int        | 32-bit int  |   Win32 FILETIME   |
    +------------------+--------------+--------------------------+-------------+--------------------+
"""
def read_file_header(f):
    filename_len = read_int8(f)
    filename = read_string(f, filename_len)
    len = read_int(f)
    offset = read_int(f)
    time = read_filetime(f)
    return File(filename=filename, len=len, offset=offset, timemodified=time)

"""
    Reads the header data for a single directory.
    The layout is (strings are ISO 8859-1 encoded (I think); ints are little-endian):
    +-----------------+--------------+--------------------------+-----------------+
    | Dir name length |   Dir name   |    Number of subdirs     | Number of files |
    +-----------------+--------------+--------------------------+-----------------+
    |     1 byte      |   n bytes    |         4 bytes          |     4 bytes     |
    +-----------------+--------------+--------------------------+-----------------+
    |    8-bit int    |    string    |        32-bit int        |   32-bit int    |
    +-----------------+--------------+--------------------------+-----------------+

    If the directory is the root directory, then instead of the 1+n bytes for the directory name, there is a 4-byte magic number.
    As an ASCII string, the magic number is "LP1C"; as a 32-bit little-endian int, it is 0x4331504C.
"""
def read_directory_header(f, isroot, curdir):
    dirname = curdir
    if isroot:
        assert read_int(f) == 0x4331504C, 'Magic number mismatch' # verify the file format by checking the magic number
    else:
        dirname_len = read_int8(f)
        dirname = read_string(f, dirname_len) + "/"
    num_dirs = read_int(f)
    num_files = read_int(f)
    return DirectoryHeader(dirname, num_dirs, num_files)



# recursively get file and subdirectory information
def get_tree(f, isroot=True, curdir='./'):
    # read the header for this directory
    dirdata = read_directory_header(f, isroot, curdir)
    print('%s\t%d files\t%d subdirectories' % (dirdata.dirname, dirdata.numfiles, dirdata.numdirs))

    # read each file's header
    files = []
    for i in range(dirdata.numfiles):
        files.append(read_file_header(f))
    
    # recursively make a Directory tuple for each subdirectory of this directory
    subdirs = []
    for i in range(dirdata.numdirs):
        subdirs.append(get_tree(f, False))
    
    return Directory(dirdata.dirname, subdirs, files)

# recursively write the files to the disk
def write_tree(fh, tree, curdir='./'):
    # make the directory, if it doesn't exist
    try:
        os.mkdir(curdir)
    except:
        pass
    
    # write each file
    for f in tree.files:
        file_path = curdir + f.filename
        print('%s\t%d bytes' % (file_path, f.len))
        fh.seek(f.offset)
        with open(file_path, 'wb') as g:
            g.write(fh.read(f.len))
        os.utime(file_path, (f.timemodified, f.timemodified))
    
    # recursively write each directory to the disk
    for dir in tree.subdirs:
        write_tree(fh, dir, curdir+dir.dirname)
        

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        if not os.path.isfile(file_name):
            printerr('%s does not exist.' % file_name)
            sys.exit()
        
        dir_to_create = os.path.splitext(file_name)[0]
        try:
            os.mkdir(dir_to_create)
        except FileExistsError:
            pass

        with open(file_name, 'rb') as f:
            os.chdir(dir_to_create)

            print('Getting tree...')
            tree = get_tree(f)

            print('Writing files...')
            write_tree(f, tree)
    else:
        printerr('Usage: vfs_parser.py <file to unpack>')
