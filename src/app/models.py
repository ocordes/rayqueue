"""

app/models.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-03-18

"""

import os
import uuid

from app import db, login
from app.utils.files import save_md5file

from flask import current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from hashlib import md5
from datetime import datetime
from time import time
import jwt



PROJECT_TYPE_IMAGE      = 0
PROJECT_TYPE_ANIMATION  = 1

FILE_UNKNOWN            = 0
FILE_BASE_FILE          = 1
FILE_MODEL              = 2
FILE_RENDERED_IMAGE     = 3
FILE_LOGFILE            = 4


FILE_TYPES = { FILE_UNKNOWN: 'unknown',
               FILE_BASE_FILE: 'base_files',
               FILE_MODEL: 'models',
               FILE_RENDERED_IMAGE: 'images',
               FILE_LOGFILE: 'logfiles'
             }



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # some internal and private fields
    is_active = db.Column(db.Boolean, default=False)
    administrator  = db.Column(db.Boolean, default=False)

    # relationships
    projects = db.relationship('Project', backref='owner', lazy='dynamic')
    files = db.relationship('File', backref='owner', lazy='dynamic')
    images = db.relationship('Image', backref='owner', lazy='dynamic')
    queueelemets = db.relationship('QueueElement', backref='worker', lazy='dynamic')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    def get_email_verify_token(self, expires_in=600):
        return jwt.encode(
            {'email_verify': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    @staticmethod
    def verify_email_verify_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['email_verify']
        except:
            return
        return User.query.get(id)


    def __repr__(self):
        return '<User {}>'.format(self.username)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(64), index=True, unique=True)
    version = db.Column(db.String(10))
    is_public = db.Column(db.Boolean, default=False)
    project_type = db.Column(db.Integer)
    status = db.Column(db.Integer)

    # relationships
    #files = db.relationship('File', backref='project', lazy='dynamic')
    files = db.relationship('File', #backref='project', lazy='dynamic',
                                primaryjoin="Project.id==File.project_id")

    base_files = db.relationship('File',
                                  primaryjoin="and_(Project.id==File.project_id, File.file_type=='%s')"% (FILE_BASE_FILE))

    images = db.relationship('Image', # backref='project2', lazy='dynamic', foreign_keys='Image.project_id')
                             primaryjoin="Project.id==Image.project_id", backref='project' )

    # static variables
    PROJECT_OPEN            = 0
    PROJECT_RENDERING       = 1
    PROJECT_FINISHED        = 2


    PROJECT_STATES = { PROJECT_OPEN: 'Open',
                       PROJECT_RENDERING: 'Rendering',
                       PROJECT_FINISHED: 'Finished',
                     }


    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'created': self.timestamp.isoformat() + 'Z',
            'version': self.version,
            'is_public': self.is_public,
            'project_type': self.project_type,
            'state': self.status,
            #'base_files' : [i.id for i in self.base_files],
            'base_files': [i.to_dict() for i in self.base_files],
            }
        return data


    @property
    def state2str(self):
        return self.PROJECT_STATES.get(self.status, 'Unknown (dict error)')


    def __repr__(self):
        return '<Project {}>'.format(self.name)


    def remove_files(self):
        complete = True
        msgs = []
        for ffile in self.files:
            ret, msg = ffile.remove()
            if ret == False:
                msgs.append('{} not removed ({})'.format(ffile.name, msg))
                complete = False
            else:
                db.session.delete(ffile)

        return complete, msgs


    def number_of_open_images(self):
        # use the database count method to get the numbers
        return Image.query.filter(Image.project_id==self.id).filter(Image.state<Image.IMAGE_STATE_FINISHED).count()


    def number_of_finished_images(self):
        # use the database count method to get the numbers
        return Image.query.filter(Image.project_id==self.id).filter(Image.state==Image.IMAGE_STATE_FINISHED).count()


    @staticmethod
    def correct_version(version):
        avail_versions = [ '3.7', '3.8', '3.6']
        default_version = '3.7'

        if version in avail_versions:
            return version
        else:
            return default_version


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    size = db.Column(db.BigInteger)
    md5sum = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    file_type = db.Column(db.Integer)


    def __repr__(self):
        return '<File {}>'.format(self.name)


    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'md5sum': self.md5sum,
        }
        return data;


    def full_filename(self):
        directory = FILE_TYPES[self.file_type]
        full_dir = os.path.join(current_app.config['DATA_DIR'], directory)
        return os.path.join(full_dir, self.name)


    def remove(self):
        filename = self.full_filename()
        if os.access(filename, os.R_OK):
            try:
                os.remove(filename)
            except:
                return True, 'File error'
            return True, 'OK'
        else:
            return False, 'Access error/not found'



    def check(self):
        pass


    @staticmethod
    def save_file(src, name, ftype, project):
        id = uuid.uuid4()
        dir = FILE_TYPES[ftype]
        dfilename = '{}_{}'.format(id, name)
        full_dir = os.path.join(current_app.config['DATA_DIR'], dir )
        os.makedirs(full_dir, exist_ok = True)   # no problems if full_dir exists
        filename = os.path.join(full_dir, dfilename)

        md5sum, size = save_md5file(src, filename)

        return File(name=dfilename,
                    md5sum=md5sum,
                    size=size,
                    user_id=project.user_id,
                    project_id=project.id,
                    file_type=ftype)



class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    finished = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    state = db.Column(db.Integer, default=-1)
    # files referenced by ID
    model = db.Column(db.Integer, default=-1)
    render_image = db.Column(db.Integer, default=-1)
    log_file = db.Column(db.Integer, default=-1)


    queueelement = db.relationship('QueueElement', backref='image', lazy='dynamic')

    # static variables
    IMAGE_STATE_UNKNOWN     = -1
    IMAGE_STATE_QUEUED      = 0
    IMAGE_STATE_RENDERING   = 1
    IMAGE_STATE_FINISHED    = 2

    IMAGE_STATES = { IMAGE_STATE_UNKNOWN: 'Unknown',
                     IMAGE_STATE_QUEUED: 'Queued',
                     IMAGE_STATE_RENDERING: 'Rendering',
                     IMAGE_STATE_FINISHED: 'Finished',
                   }


    def __repr__(self):
        return '<Image {}>'.format(self.id)


    @property
    def state2str(self):
        return self.IMAGE_STATES.get(self.state, 'Unknown (dict error)')


    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'created': self.created.isoformat() + 'Z',
            'model_id': self.model,
            'state': self.state
            }
        if self.render_image != -1:
            data['render_image_id'] = self.render_image
            data['finished'] = self.finished.isoformat() + 'Z',
        if self.log_file != -1:
            data['log_file_id'] = self.log_file
        return data


    def remove_file(self, id):
        fid = File.query.get(id)
        ret, retmsg = fid.remove()
        if ret:
            # file was remove successfully
            # remove from database
            msg = 'Remove \'{}\' from BaseFiles'.format(fid.name)
            db.session.delete(fid)
        else:
            msg = 'Removing \'{}\' failed ({})'.format(fid.name, retmsg)
        flash(msg)
        current_app.logger.info(msg)
        db.session.commit()

        return ret


    def remove(self):
        complete = True
        msgs = []
        ids = [ id for id in (self.model, self.render_image, self.log_file) if id != -1]
        print(ids)
        for id in ids:
            ffile = File.query.get(id)
            ret, msg = ffile.remove()
            if ret == False:
                msgs.append('{} not removed ({})'.format(ffile.name, msg))
                complete = False
            else:
                db.session.delete(ffile)

        return complete, msgs


class QueueElement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.Integer, default=-1)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    requested = db.Column(db.DateTime, index=True)


    # static variables
    QUEUE_ELEMENT_UNKNOWN   = -1
    QUEUE_ELEMENT_QUEUED    = 0
    QUEUE_ELEMENT_HOLD      = 1
    QUEUE_ELEMENT_RENDERING = 2
    QUEUE_ELEMENT_FINISHED  = 3

    QUEUE_ELEMENT_STATES = { QUEUE_ELEMENT_UNKNOWN: 'Unknown',
                             QUEUE_ELEMENT_QUEUED: 'Queued',
                             QUEUE_ELEMENT_HOLD: 'Hold',
                             QUEUE_ELEMENT_RENDERING: 'Rendering',
                             QUEUE_ELEMENT_FINISHED: 'Finished',
                           }

    def __repr__(self):
        return '<QueueElement {}>'.format(self.id)


    @property
    def state2str(self):
        return self.QUEUE_ELEMENT_STATES.get(self.state, 'Unknown (dict error)')


    @property
    def project(self):
        #image = Image.query.get(self.image_id)
        return self.image.project_id


    @staticmethod
    def check_image(image_id):
        image = QueueElement.query.filter_by(image_id=image_id).first()
        return image is not None
