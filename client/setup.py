"""

setup.py

for rq_client python package


written by: Oliver Cordes 2019-04-01
changed by: Oliver Cordes 2019-04-30

"""

from setuptools import setup

from rq_client import __version__

setup(
    name='rq_client',
    version=__version__,
    packages=['rq_client'],
    install_requires=[
       'requests',
       'psutil>=5.6.2'
    ]
)
