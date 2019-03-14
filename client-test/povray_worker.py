from client.api import Session
from client.projects import Project
from client.files import File
from client.images import Image

import time
import os


class PovrayWorker(object):
    def __init__(self, session, tempdir='.' ):
        self._session = session

        self._image = None

        self._tempdir = tempdir


    def _check_tmpdir(self):
        if os.access(self._tempdir, os.R_OK):
            return

        try:
            os.mkdir(self._tempdir)
        except:
            self._tempdir = '.'


    def _next_image(self):
        self._image = Image.queue_next(self._session)

        if self._image is None:
            return

        # get project description
        self._project = Project.query(self._session, self._image.project_id)

        if self._project is None:
            return


    def _download_extract_file(self, fileid, msg, subdir='.'):
        dir = os.path.join(self._tempdir, subdir)
        status, filename = File.get_by_id(self._session, fileid, dir)

        print('Downloaded \'%s\' file: %s (%s)' % (msg, filename, (status and 'OK' or 'Fail' )) )

        return status



    def _download_extract_files(self):
        if self._download_extract_file(self._image.model_id, 'Model') == False:
            return False


        return True


    def run(self):
        self._check_tmpdir()  # creates a tempdir
        self._next_image()

        if (self._image is None) or (self._project is None) :
            return False

        if self._download_extract_files():
            print('All files downloaded correctly')
        else:
            print('Files are not downloaded correctly')
        return False


# main
rq = Session(username='ocordes', password='cTower',
                base_url='http://localhost:4555/api', verbose=True)


if rq.login() == False:
    print('Error logging into the RQ API! Program exits!')
    os.exit(-1)

print('successfully logged into the RQ API')

pw = PovrayWorker(rq, 'worker')
ret = pw.run()
