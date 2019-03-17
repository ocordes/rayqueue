from client.api import Session
from client.projects import Project
from client.files import File
from client.images import Image

import time
import os

import tarfile
import configparser


class PovrayWorker(object):

    base_files_dir = 'base_files'
    model_dir      = 'model'

    def __init__(self, session, tempdir='.', default_libs=None ):
        self._session = session

        self._image = None

        self._tempdir = tempdir
        self._default_libs = default_libs


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


    def _create_master_ini(self, base_files_dirs):
        fname = os.path.join(self._tempdir, self.model_dir, 'master.ini')
        print('Generating master ini file ...')
        with open(fname,'w') as master_file:
            master_file.write('; POVRAY master file\n')
            if self._default_libs is not None:
                for dir in self._default_libs:
                    master_file.write('Library_Path="%s"\n' % dir)
            for dir in base_files_dirs:
                master_file.write('Library_Path="%s"\n' % dir)

        print( 'Master file \'%s\' successfully written!' % fname)


    def _read_input_directories(self, subdir='.'):
        dirs = []
        path = os.path.join(self._tempdir, subdir)
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.endswith('.ini') and entry.is_file():
                    print(entry.name)
                    fname = os.path.join(path, entry.name)
                    config = configparser.ConfigParser()
                    config.read(fname)
                    dir = config.get('DEFAULT', 'DIR', fallback=None)
                    if dir is not None:
                        dirs.append(os.path.join(subdir, dir))

        return dirs


    def _extract(self, filename, subdir):
        dir = os.path.join(self._tempdir, subdir)

        if tarfile.is_tarfile(filename):
            with tarfile.open(filename) as tar:
                tar.extractall(dir)
        return True


    def _download_extract_file(self, fileid, msg, subdir='.', md5sum=None):
        dir = os.path.join(self._tempdir, 'downloads')
        try:
            os.mkdir(dir)
        except:
            pass

        # if md5sum is not provided, ask the database
        if md5sum is None:
            dbfile = File.get_db_by_id(self._session, fileid)
            md5sum = dbfile.md5sum

        status, filename = File.get_by_id(self._session, fileid, dir, md5sum=md5sum)

        print('Downloaded \'%s\' file: %s (%s)' % (msg, filename, (status and 'OK' or 'Fail' )) )

        if status:
            status = self._extract(filename, subdir)
        return status



    def _download_extract_files(self):
        if self._download_extract_file(self._image.model_id,
                                        'Model',
                                        subdir=self.model_dir ) == False:
            return False

        for ffile in self._project.base_files:
            if self._download_extract_file(ffile.id,
                                            'BaseFiles',
                                            subdir=self.base_files_dir,
                                            md5sum=ffile.md5sum) == False:
                return False

        return True


    def _povray_execute(self):
        # povray model/master.ini -w640 -h480 -imodel/scene.pov -oscene.png
        pass


    def run(self):
        self._check_tmpdir()  # creates a tempdir
        self._next_image()

        if (self._image is None) or (self._project is None) :
            return False

        if self._download_extract_files():
            print('All files downloaded correctly')
        else:
            print('Files are not downloaded correctly')

        basefiles_dirs = self._read_input_directories(subdir=self.base_files_dir)


        self._create_master_ini(basefiles_dirs)

        return False


# main
rq = Session(username='ocordes', password='cTower',
                base_url='http://localhost:4555/api', verbose=True)


if rq.login() == False:
    print('Error logging into the RQ API! Program exits!')
    os.exit(-1)

print('successfully logged into the RQ API')


default_libs = ['/Users/ocordes/software/PovrayCommandLineMacV2',
                '/Users/ocordes/software/PovrayCommandLineMacV2/ini',
                '/Users/ocordes/software/PovrayCommandLineMacV2/include']

pw = PovrayWorker(rq, 'worker', default_libs=default_libs)
ret = pw.run()
