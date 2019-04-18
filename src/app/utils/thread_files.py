"""

app/utils/thread_files.py

written by: Oliver Cordes 2019-04-18
changed by: Oliver Cordes 2019-04-18


"""

import os

from threading import Thread
from flask import current_app

from app import db
from app.models import *


"""
remove_files_from_list

brute forced removal of all files in the filenames list
"""
def remove_files_from_list(app, filenames):
    with app.app_context():
        for f in filenames:
            if os.access(f, os.R_OK):
                try:
                    os.remove(f)
                except:
                    current_app.logger.info('Can\'t remove \'%s\'' % f)


def collect_file_files(ffile):
    l = []
    l.append(ffile.full_filename())
    if ffile.file_type == FILE_RENDERED_IMAGE:
        l.append(ffile.full_icon_name())
    db.session.delete(ffile)
    return l


def collect_file_images(image):
    l = []
    ids = [ id for id in (image.model, image.render_image, image.log_file) if id != -1]
    print(ids)
    for id in ids:
        ffile = File.query.get(id)
        l += collect_file_files(ffile)
    db.session.delete(image)
    return l


"""
remove_project_images

removes all files and objects from the database, it does very quickly
gathering all files and removes the objects from the database, removal
of the disk files will be taken in a seperate thread because this is
time consuming ...
"""
def remove_project_images(project):
    # remove the database objects and collects all filenames
    filenames = []
    for image in project.images:
        filenames += collect_file_images(image)
    db.session.commit()


    Thread(target=remove_files_from_list,
            args=(current_app._get_current_object(), filenames)).start()
