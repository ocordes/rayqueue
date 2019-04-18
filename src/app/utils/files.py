"""

app/utils/files.py

written by: Oliver Cordes 2019-02-25
changed by: Oliver Cordes 2019-04-18


"""


import hashlib
import os

from PIL import Image

size = (256, 256)

"""
size2human

returns a human readable string for the size

:param size:  the size (of a file) in bytes
:rvalue:      the human readable string

"""
def size2human(size):
    # backup part, if size is not properly saved ...
    if size is None:
        return 'None'

    if size < 1024:
        return '%ib' % size

    size /= 1024.
    if size < 1024:
        return '%.1fKb' % size

    size /= 1024.
    if size < 1024:
        return '%.1fMb' % size

    size /= 1024.
    return '%.1fGb' % size



"""
save_md5file

saves a stream src to dst, which can be a filename or stream

:param src: the src stream
:param dst: the destination, filename or stream

:rvalue: the md5 checksum of the saved data
:rvalue: the size of the file

"""
def save_md5file(src, dst):
    size = 0
    md5 = hashlib.md5()
    if isinstance(dst, str):
        outf = open(dst,'wb')
    else:
        outf = dst

    block_size = 128  # useful size of chunks for md5 hashing
    while True:
        data = src.read(block_size)
        if not data:
            break

        md5.update(data)
        outf.write(data)
        size += len(data)

    if isinstance(dst, str):
        outf.close()

    return md5.hexdigest(), size



"""
create_thumbnail
"""

def create_thumbnail(filename, srcdir, destdir):
    outfile = os.path.splitext(filename)[0] + '.thumbnail.png'
    outname = os.path.join(destdir, outfile)
    try:
        im = Image.open(os.path.join(srcdir,filename))
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(outname)
    except:
        outname = None

    return outname


"""
sizeofimage

returns the width, height of an image
"""
def sizeofimage(filename):
    with Image.open(filename) as im:
        return im.size



"""
read_logfile

reads a logfile and return a string representing the complete file!
"""

def read_logfile(filename):
    logfile_data = 'Empty logfile'
    print(filename)
    try:
        with open(filename, 'r') as f:
            logfile_data = f.read()
    except:
        logfile_data = 'Error reading logfile'

    return logfile_data



# demo test code
if __name__ == '__main__':
    import sys

    #for i in sys.argv[1:]:
    #    print(i)
    #    fname = create_thumbnail(i,'.','.')
    #    print(fname)
    width, height = sizeofimage(sys.argv[1])
    print('%i x %i' % (width, height))
