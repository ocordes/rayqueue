"""

app/utils/files.py

written by: Oliver Cordes 2019-02-25
changed by: Oliver Cordes 2019-03-02


"""


import hashlib

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
