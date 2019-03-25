"""

client/images.py

written by: Oliver Cordes 2019-03-07
changed by: Oliver Cordes 2019-03-09

"""

from client.baseobjects import BaseObject

class Image(BaseObject):
    def status(self):
        if self.state == 0:
            return 'Queued'
        elif self.state == 1:
            return 'Rendering'
        elif self.state == 2:
            return 'Finished'
        else:
            return 'Unknown'


    @staticmethod
    def create(session, project_id, modelfile):
        endpoint = '/image/%i/model' % project_id
        status, data = session.file_upload(endpoint, modelfile)
        if status == 200:
            id = data['id']
        else:
            print('Error while image creation: %s' % data['detail'])
            id = -1
        return id


    @staticmethod
    def upload_render_image(session, image_id, imagefile):
        endpoint = '/image/%i/image' % image_id
        status, data = session.file_upload(endpoint, imagefile)
        if status == 200:
            id = data['id']
        else:
            id = -1
        return id


    @staticmethod
    def upload_log_file(session, image_id, logfile):
        endpoint = '/image/%i/logfile' % image_id
        status, data = session.file_upload(endpoint, logfile)
        if status == 200:
            id = data['id']
        else:
            id = -1
        return id


    @staticmethod
    def query(session, image_id):
        endpoint = '/image/%i' % image_id
        status, data = session.request(endpoint, request_type=session.rsession.get)

        if status == 200:
            return Image(data=data)

        return None


    @staticmethod
    def queue_next(session):
        endpoint = '/queue/next'
        status, data = session.request(endpoint, request_type=session.rsession.get)

        if status == 200:
            if data.get('msg') == None:
                return Image(data=data)

        return None
