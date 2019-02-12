#!/usr/bin/env python

from client.api import Session
from client.projects import Project


# main
rq = Session(username='ocordes', password='cTower',
                base_url='http://localhost:4555/api')

if rq.login():
    #ret = rq.raw_request('/projects', bearer=True)
    #print(ret)

    projects = Project.query(rq)

    for p in projects:
        print(p.name)
        print(p.created)
        print(p.id)
        print(p.is_public)
        print(p.project_type)
        print(p.status)
