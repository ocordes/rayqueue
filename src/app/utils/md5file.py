"""

app/utils/md5file.py

written by: Oliver Cordes 2019-02-21
changed by: Oliver Cordes 2019-02-21


"""

import hashlib


"""
save_md5file

saves a stream src to dst, which can be a filename or stream

:param src: the src stream
:param dst: the destination, filename or stream

:rvalue: the md5 checksum of the saved data

"""
def save_md5file(src, dst):
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


    if isinstance(dst, str):
        outf.close()

    return md5.hexdigest()
