"""

app/models.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-02-21

"""

import os
import uuid

from app import db, login
from app.utils.md5file import save_md5file

from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from hashlib import md5
from datetime import datetime
from time import time
import jwt


FILE_UNKNOWN   = 0
FILE_BASE_FILE = 1

FILE_TYPES = { FILE_UNKNOWN: 'unknown',
               FILE_BASE_FILE: 'base_files'
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
    files = db.relationship('File', backref='project', lazy='dynamic')

    base_files = db.relationship('File',
                                  primaryjoin="and_(Project.id==File.project_id, File.file_type=='%s')"% (FILE_BASE_FILE))


    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'created': self.timestamp.isoformat() + 'Z',
            'version': self.version,
            'is_public': self.is_public,
            'project_type': self.project_type,
            'status': self.status
            }
        return data


    def __repr__(self):
        return '<Project {}>'.format(self.name)


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
    md5sum = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    file_type = db.Column(db.Integer)


    def __repr__(self):
        return '<File {}>'.format(self.name)


    @staticmethod
    def save_file(src, name, ftype, project):
        id = uuid.uuid4()
        dir = FILE_TYPES[ftype]
        dfilename = '{}_{}'.format(id, name)
        full_dir = os.path.join(current_app.config['DATA_DIR'], dir )
        os.makedirs(full_dir, exist_ok = True)   # no problems if full_dir exists
        filename = os.path.join(full_dir, dfilename)

        md5sum = save_md5file(src, filename)

        return File(name=dfilename,
                    md5sum=md5sum,
                    user_id=project.user_id,
                    project_id=project.id,
                    file_type=ftype)
