#!/usr/bin/env python

from client.api import Session
from client.projects import Project
from client.files import File

import time


# main
rq = Session(username='ocordes', password='cTower',
                base_url='http://localhost:4555/api', verbose=True)

if rq.login():
    print('Login successful!')
    #ret = rq.raw_request('/projects', bearer=True)
    #print(ret)

    #time.sleep(20)

    projects = Project.query(rq)

    for p in projects:
        print(p.name)
        print(p.created)
        print(p.id)
        print(p.is_public)
        print(p.project_type)
        print(p.state)


    #time.sleep(20)
    #status, filename = File.get_by_id(rq, 3, '.')
    #print(status)
    #print(filename)

    #projects[0].clear_images(rq)
    print(projects[0].start_rendering(rq))
    print(projects[0].reset(rq))
