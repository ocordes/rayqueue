"""

client/projects.py

written by: Oliver Cordes 2019-02-12
changed by: Oliver Cordes 2019-03-07

"""



class Project(object):
    def __init__(self,data=None):
        if data is not None:
            self._set_attributes(data)


    def _set_attributes( self, adict ):
        for name, value in adict.items():
            setattr( self, name, value )


    @staticmethod
    def query(session):
        projects = []
        status, data = session.request('/projects', request_type=session.rsession.get)

        if status == 200:
            for project in data:
                p = Project(data=project)
                projects.append(p)

        return projects
