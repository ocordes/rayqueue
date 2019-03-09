"""

client/projects.py

written by: Oliver Cordes 2019-02-12
changed by: Oliver Cordes 2019-03-09

"""

from client.baseobjects import BaseObject


PROJECT_TYPE_IMAGE     = 0
PROJECT_TYPE_ANIMATION = 1

class Project(BaseObject):
    def clear_images(self, session):
        if self.project_type == PROJECT_TYPE_IMAGE:
            endpoint = '/image/%i/clear' % self.id

            status, data = session.request(endpoint, request_type=session.rsession.post)

            return status == 200
        else:
            return False
            

    @staticmethod
    def query(session):
        projects = []
        status, data = session.request('/projects', request_type=session.rsession.get)

        if status == 200:
            for project in data:
                p = Project(data=project)
                projects.append(p)

        return projects
