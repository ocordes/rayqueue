"""

rq_client/projects.py

written by: Oliver Cordes 2019-02-12
changed by: Oliver Cordes 2019-03-17

"""

from rq_client.baseobjects import BaseObject
from rq_client.files import File


PROJECT_TYPE_IMAGE     = 0
PROJECT_TYPE_ANIMATION = 1


class Project(BaseObject):
    def update(self, session):
        status, data = session.request('/project/%i' % self.id,
                                        request_type=session.rsession.get )

        if status == 200:
            self._set_attributes(data)
        else:
            print('Update of image failed!')


    def filtervalue(self, name, value):
        if name == 'base_files':
            return [File(i) for i in value]

        return value


    def status(self):
        if self.state == 0:
            return 'Queued'
        elif self.state == 1:
            return 'Rendering'
        elif self.state == 2:
            return 'Finished'
        else:
            return 'Unknown'


    def clear_images(self, session):
        endpoint = '/image/%i/clear' % self.id

        status, data = session.request(endpoint, request_type=session.rsession.post)

        return status == 200
        

    def _command(self, session, command ):
        endpoint = '/project/%i/%s' % (self.id, command)

        status, data = session.request(endpoint, request_type=session.rsession.post)

        return status == 200


    def start_rendering(self, session):
        return self._command(session, 'start')


    def reset(self, session):
        return self._command(session, 'reset')


    @staticmethod
    def query(session, id):
        status, data = session.request('/project/%i' % id, request_type=session.rsession.get )

        if status == 200:
            return Project(data=data)
        else:
            return None


    @staticmethod
    def queryall(session):
        projects = []
        status, data = session.request('/projects', request_type=session.rsession.get)

        if status == 200:
            for project in data:
                p = Project(data=project)
                projects.append(p)

        return projects
