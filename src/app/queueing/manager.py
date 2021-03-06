"""

app/queueing/manager.py

written by: Oliver Cordes 2019-03-10
changed by: Oliver Cordes 2019-03-11

"""

from app import db
from flask import current_app

from app.models import *


class Manager(object):
    def __init__(self):
        pass


    def old_entries(self):
        # walk through all entries

        qes = QueueElement.query.all()

        for qe in qes:
            # check positive, if nothing positive matches,
            # remove the element from the queue



            image = qe.image

            # check if image was removed during other processes...
            if image != None:

                #if image.project.status == Project.PROJECT_RENDERING:
                #    continue

                if image.project.status == Project.PROJECT_OPEN:
                    image.state = Image.IMAGE_STATE_UNKNOWN

                # remove from queue if finished or unknown
                if image.state in (Image.IMAGE_STATE_QUEUED, Image.IMAGE_STATE_RENDERING):
                    continue

            db.session.delete(qe)

        db.session.commit()



    def new_entries(self):
        current_app.logger.info('QM: looking for new entries')
        # walk through all
        projects = Project.query.filter(Project.status==Project.PROJECT_RENDERING).all()

        # projects has now all Projects which are open for rendering
        for project in projects:
            print(project.name)

            # walk through all images to check if there are not finished

            # use a direct db query instead of looping over all project images
            images = Image.query.filter(Image.project_id==project.id).filter(Image.state==Image.IMAGE_STATE_UNKNOWN).all()

            for image in images:
                qe = QueueElement(image_id=image.id, worker_id=-1, state=QueueElement.QUEUE_ELEMENT_QUEUED)

                db.session.add(qe)

                # sets the image status to queued
                image.state = Image.IMAGE_STATE_QUEUED

                current_app.logger.info('QM: added image id=%i to queue' % image.id)

        # finally commit all new elements
        db.session.commit()

        current_app.logger.info('QM: new entries finished')



    def _real_update(self):
        current_app.logger.info('QM: update started')
        # check for existing entries
        self.old_entries()
        # check for new entries
        self.new_entries()
        current_app.logger.info('QM: update finished')


    def update(self):
        # probably wrapping around with a locking mechanism
        self._real_update()



    def next(self, user_id):
        # get all possible QueueElements
        qes = QueueElement.query.filter(QueueElement.state==QueueElement.QUEUE_ELEMENT_QUEUED)

        for qe in qes:
            if qe.image.user_id == user_id:
                return qe

        return None
