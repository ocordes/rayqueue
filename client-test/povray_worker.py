"""

written by: Oliver Cordes 2019-03-06
changed by: Oliver Cordes 2019-04-20

"""

from rq_client.api import Session
from rq_client.projects import Project
from rq_client.files import File
from rq_client.images import Image

import time
import os
import shutil

import tarfile
import configparser
import subprocess


class PovrayWorker(object):

    base_files_dir = 'base_files'
    model_dir      = 'model'

    def __init__(self,
                    session,
                    tempdir='.',
                    default_libs=None,
                    max_cores=None ):
        self._session = session

        self._image = None
        self._image_name = None

        self._tempdir = tempdir
        self._default_libs = default_libs

        self._max_cores = None

        if self._max_cores is not None:
            try:
                self._max_cores = int(self._max_cores)
            except:
                self._max_cores = None

        self._logfile = None
        self._logfile_name = None
        self._has_base_files = False


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
            return False

        # get project description
        self._project = Project.query(self._session, self._image.project_id)

        if self._project is None:
            print('Image requested, but in a unreliable situation')
            # discard request if possible
            return False

        return True


    def _create_master_ini(self, base_files_dirs):
        fname = os.path.join(self._tempdir, self.model_dir, 'master.ini')
        print('Generating master ini file ...', file=self._logfile)
        with open(fname,'w') as master_file:
            master_file.write('; POVRAY master file\n')
            if self._default_libs is not None:
                for dir in self._default_libs:
                    master_file.write('Library_Path="%s"\n' % dir)
            for dir in base_files_dirs:
                master_file.write('Library_Path="%s"\n' % dir)

        print( 'Master file \'%s\' successfully written!' % fname, file=self._logfile)


    def _read_input_directories(self, subdir='.'):
        dirs = []
        if self._has_base_files:
            path = os.path.join(self._tempdir, subdir)
            with os.scandir(path) as it:
                for entry in it:
                    if entry.name.endswith('.ini') and entry.is_file():
                        print('Processing %s ...' % entry.name, file=self._logfile)
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

        print('Downloaded \'%s\' file: %s (%s)' % (msg, filename, (status and 'OK' or 'Fail' )), file=self._logfile )

        if status:
            status = self._extract(filename, subdir)
            os.remove(filename)
        return status



    def _download_extract_files(self):
        if self._download_extract_file(self._image.model_id,
                                        'Model',
                                        subdir=self.model_dir ) == False:
            return False

        self._has_base_files = False
        for ffile in self._project.base_files:
            if self._download_extract_file(ffile.id,
                                            'BaseFiles',
                                            subdir=self.base_files_dir,
                                            md5sum=ffile.md5sum) == False:
                return False
            self._has_base_files = True

        return True


    def _load_scene_ini(self):
        filename = os.path.join(self._tempdir, self.model_dir, 'scene.ini')

        config = configparser.ConfigParser()
        try:
            config.read(filename)
            return config['DEFAULT']
        except:
            return None




    def _povray_execute(self):
        data = self._load_scene_ini()
        if data is None:
            print('No scene.ini file found. No rendering!', file=self._logfile)
            return
        # povray model/master.ini -w640 -h480 -imodel/scene.pov -oscene.png

        self._image_name = os.path.join(self.model_dir, data.get('outfile', 'scene.png'))


        options = ''
        if self._max_cores is not None:
            options += ' +WT%i' % self._max_cores

        command = '{} {} -w{} -h{} -i{} -o{} {}'.format('povray',
                                                     os.path.join(self.model_dir, 'master.ini'),
                                                     data.get('width', '640'),
                                                     data.get('height', '480'),
                                                     os.path.join(self.model_dir, data.get('scene', 'scene.pov')),
                                                     self._image_name,
                                                     options
                                                    )
        print('Executing: %s' % command, file=self._logfile)
        cmd = '(cd {};{})'.format(self._tempdir, command)
        p = subprocess.Popen(cmd, shell=True, bufsize=-1, close_fds=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        for line in p.stdout:
            #print(line.decode("utf-8") ,file=self._logfile)
            self._logfile.write(line.decode('utf-8'))


        return_code = p.wait()


        print('povray returns with exit code: {}'.format(return_code), file=self._logfile)

        return return_code


    def _upload_files(self):
        filename = os.path.join(self._tempdir, self._image_name)
        if os.access(filename, os.R_OK):
            result = Image.upload_render_image(self._session, self._image.id, filename)
            if result == -1:
                print('Image upload failed!')
            model_dir = os.path.join(self._tempdir, self.model_dir)
            shutil.rmtree(model_dir,ignore_errors=True)
        if os.access(self._logfile_name, os.R_OK):
            result = Image.upload_log_file(self._session, self._image.id, self._logfile_name)
            if result == -1:
                print('Logfile upload failed!')
            # remove file
            os.remove(self._logfile_name)


    def _upload_error_code(self, error_code):
        result = Image.image_finish(self._session, self._image.id, error_code)
        if result == -1:
            print('Error code upload failed!')


    def run_single_image(self):
        # start logging
        self._logfile_name = os.path.join(self._tempdir, 'scene.log')
        self._logfile = open(self._logfile_name, 'w')

        print('----------------------------------------------------------------------------',
                file=self._logfile)

        if (self._image is None) or (self._project is None) :
            return False

        print('----------------------------------------------------------------------------',
                file=self._logfile)

        if self._download_extract_files():
            print('All files downloaded correctly', file=self._logfile)
        else:
            print('Files are not downloaded correctly', file=self._logfile)

        print('----------------------------------------------------------------------------',
                file=self._logfile)

        basefiles_dirs = self._read_input_directories(subdir=self.base_files_dir)

        self._create_master_ini(basefiles_dirs)

        print('----------------------------------------------------------------------------',
                file=self._logfile)

        error_code = self._povray_execute()

        print('----------------------------------------------------------------------------',
                file=self._logfile)
        print('Worker finished: file uploading!', file=self._logfile)

        self._logfile.close()

        self._upload_files()

        self._upload_error_code(error_code)

        print('Files uploaded!')

        return False


    def run(self):
        self._check_tmpdir()  # creates a tempdir

        running = True
        sleep_time = 0
        max_sleep_time = 60
        try:
            while running:
                work_todo = self._next_image()
                if work_todo:
                    print('Process request ...')
                    self.run_single_image()
                    print('Done.')
                    sleep_time = 0
                else:
                    sleep_time += 5
                    if sleep_time > max_sleep_time:
                        sleep_time = max_sleep_time
                    print('Sleeping for (%i seconds) ...' % sleep_time)
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            running = False

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
pw.run()
