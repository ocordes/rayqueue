"""

client/files.py

written by: Oliver Cordes 2019-03-07
changed by: Oliver Cordes 2019-03-07

"""

import shutil
import os

class File(object):

    """
    get_by_id

    download a file with ID=id from the server and stores in the
    given directory

    :param id:         id of the file on the server
    :param directory;  directory to save the file in
    """
    @staticmethod
    def get_by_id(session, id, directory):
        path = '/files/id/{}'.format(id)
        status_code, filename, raw_file = session.file_request(path)

        full_filename = os.path.join(directory, filename)

        status = True
        try:
            with open(full_filename, 'wb') as out_file:
                shutil.copyfileobj(raw_file, out_file)
        except:
            status = False

        return status, full_filename




    @staticmethod
    def get_by_name(session, name):
        pass
