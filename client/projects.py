"""

client/projects.py

written by: Oliver Cordes 2019-02-12
changed by: Oliver Cordes 2019-02-12

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
        status, data = session.raw_request('/projects', bearer=True)

        projects = []
        for project in data:
            p = Project(data=project)
            projects.append(p)

        return projects
